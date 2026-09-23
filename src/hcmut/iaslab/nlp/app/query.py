"""Deterministic execution of semantic frames against the normalized KB.

This stage turns semantic intent and slots into a traceable lookup; it must not
re-interpret the original sentence.  Every execution returns ``QueryResult``,
including unsupported, missing-data, and unresolved-context cases.  Preserve
``query`` and ``sources`` because they explain why an answer is grounded.  New
storage backends or ranking strategies can sit behind this contract while the
pipeline and renderer remain unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from .entities import EntityLexicon
from .kb import KnowledgeBase
from .semantic import SemanticFrame
from .tokenizer import normalized_phrase


@dataclass
class QueryResult:
    """Structured success or failure returned for every semantic request."""

    query: str
    found: bool
    kind: str
    data: Any = None
    sources: list[str] = field(default_factory=list)
    reason: str | None = None

    @property
    def status(self) -> str:
        """Expose a simple lookup outcome without losing the specific kind."""
        if self.kind in {"OUT_OF_SCOPE", "UNSUPPORTED_INTENT", "MISSING_CONTEXT"}:
            return self.kind
        return "FOUND" if self.found else "NOT_FOUND"


class QueryEngine:
    """Route intents to domain-specific, read-only KB lookups."""

    def __init__(self, kb: KnowledgeBase, lexicon: EntityLexicon | None = None) -> None:
        self.kb = kb
        self.lexicon = lexicon

    def execute(self, frame: SemanticFrame) -> QueryResult:
        """Execute one normalized frame and never fabricate absent knowledge."""
        if frame.intent == "UNKNOWN":
            return QueryResult(
                query="NONE",
                found=False,
                kind="OUT_OF_SCOPE",
                reason="The sentence was not recognized by the course grammar.",
            )
        if frame.intent == "MISSING_CONTEXT":
            return QueryResult(
                query="NONE",
                found=False,
                kind="MISSING_CONTEXT",
                reason="The question refers to an unresolved earlier entity.",
            )
        handlers = {
            "GET_COURSE_INFO": self._course_info,
            "GET_SCHEDULE": self._schedule,
            "GET_TOPIC": self._topic,
            "GET_LO": self._lo,
            "GET_ASSIGNMENT": self._assignment,
            "GET_DEADLINE": self._deadline,
            "GET_RESOURCE": self._resource,
            "GET_RULE": self._rule,
        }
        handler = handlers.get(frame.intent)
        if handler is not None:
            return handler(frame)
        return QueryResult(
            query="NONE",
            found=False,
            kind="UNSUPPORTED_INTENT",
            reason=f"Intent {frame.intent} has no KB handler yet.",
        )

    def _course_info(self, frame: SemanticFrame) -> QueryResult:
        field = frame.slots.get("field")
        entity = frame.entity
        if field in {"duration", "time"}:
            query = f"KB.course.exam_format[{entity}]"
            if entity not in {"MIDTERM", "FINAL"}:
                return _missing("EXAM_DURATION" if field == "duration" else "EXAM_TIME", query)
            value = self.kb.course.get("exam_format", {}).get(entity.lower())
            if field == "time":
                # The file gives duration and format, not a calendar exam date.
                return _missing("EXAM_TIME", query, "No exam date/time in course_info.txt.")
            if not value:
                return _missing("EXAM_DURATION", query)
            return _found("EXAM_DURATION", query, {"exam": entity, "format": value},
                          ["course_info.txt:exam_format"])
        query = f"KB.course[{field}]"
        if entity != self.kb.course.get("course_id"):
            return _missing("COURSE_FIELD", query)
        field_keys = {"credits": "credits", "parts": "main_parts",
                      "description": "course_description", "assessment": "assessment",
                      "instructor": "instructor"}
        source_key = field_keys.get(field)
        if source_key is None:
            return _missing("COURSE_FIELD", query)
        value = self.kb.course.get(source_key)
        if not value:
            return _missing("COURSE_FIELD", query, f"No {source_key} in course_info.txt.")
        return _found("COURSE_FIELD", query, {"field": field, "value": value},
                      [f"course_info.txt:{source_key}"])

    def _schedule(self, frame: SemanticFrame) -> QueryResult:
        if "week" in frame.slots or re.fullmatch(r"WEEK_\d{2}", frame.entity or ""):
            week_id = frame.slots.get("week") or frame.entity
            query = f"KB.weeks[{week_id}]"
            record = self.kb.weeks.get(week_id)
            return (_found("SCHEDULE_WEEK", query, record, [_week_source(week_id)])
                    if record else _missing("SCHEDULE_WEEK", query))
        if "chapter" in frame.slots:
            chapter_id = frame.slots["chapter"]
            query = f"KB.chapter_weeks[{chapter_id}]"
            week_ids = self.kb.chapter_weeks.get(chapter_id, [])
            records = [self.kb.weeks[week_id] for week_id in week_ids]
            return (_found("SCHEDULE_CHAPTER", query, records,
                           [_week_source(week_id) for week_id in week_ids])
                    if records else _missing("SCHEDULE_CHAPTER", query))
        if "topics" in frame.slots:
            topics = frame.slots["topics"]
            query = f"KB.weeks[topics={','.join(topics)}]"
            if not isinstance(topics, list) or len(topics) != 2:
                return _missing("SCHEDULE_TOPICS", query)
            matching = [record for record in self.kb.weeks.values()
                        if all(self._week_has_topic(record, topic) for topic in topics)]
            return (_found("SCHEDULE_TOPICS", query, {"topics": topics, "weeks": matching},
                           [_week_source(record["week_id"]) for record in matching])
                    if matching else _missing("SCHEDULE_TOPICS", query))
        return _missing("SCHEDULE_WEEK", "KB.weeks[?]", "Missing schedule slot.")

    def _topic(self, frame: SemanticFrame) -> QueryResult:
        field = frame.slots.get("field")
        chapter_id = frame.slots.get("chapter")
        topic_id = frame.slots.get("topic")
        if chapter_id:
            query = f"KB.topics[{chapter_id}]"
            chapter = self.kb.topics.get(chapter_id)
            kind = {"overview": "TOPIC_OVERVIEW", "methods": "TOPIC_METHODS",
                    "relation": "TOPIC_RELATION"}.get(field, "TOPIC_OVERVIEW")
            if chapter is None:
                return _missing(kind, query)
            if field == "relation":
                matches = self._topic_chapters(topic_id)
                if chapter_id not in {record["chapter_id"] for record in matches}:
                    return _missing(kind, f"{query}.contains[{topic_id}]")
                aliases = self._aliases("TOPIC", topic_id)
                evidence = next(
                    (subtopic for subtopic in chapter["subtopics"]
                     if any(_contains(subtopic, alias) for alias in aliases)),
                    chapter["summary"],
                )
                return _found(kind, f"{query}.contains[{topic_id}]",
                              {"chapter": chapter, "topic": topic_id, "evidence": evidence},
                              [f"topics.txt:{chapter_id}"])
            if field == "methods" and not chapter.get("subtopics"):
                return _missing(kind, query)
            return _found(kind, query, chapter, [f"topics.txt:{chapter_id}"])
        if topic_id:
            query = f"KB.topics[topic={topic_id}]"
            chapters = self._topic_chapters(topic_id)
            if not chapters:
                return _missing("TOPIC_LOCATION" if field == "location" else "TOPIC_CHAPTERS", query)
            sources = [f"topics.txt:{record['chapter_id']}" for record in chapters]
            if field == "location":
                weeks = [record for record in self.kb.weeks.values()
                         if self._week_has_topic(record, topic_id)]
                sources.extend(_week_source(record["week_id"]) for record in weeks)
                return _found("TOPIC_LOCATION", query,
                              {"topic": topic_id, "chapters": chapters, "weeks": weeks}, sources)
            return _found("TOPIC_CHAPTERS", query,
                          {"topic": topic_id, "chapters": chapters}, sources)
        return _missing("TOPIC_CHAPTERS", "KB.topics[?]")

    def _lo(self, frame: SemanticFrame) -> QueryResult:
        lo_id = frame.slots.get("lo") or frame.entity
        query = f"KB.course.learning_outcomes[{lo_id}]"
        for key in ("detailed_learning_outcomes", "learning_outcomes"):
            value = self.kb.course.get(key, {}).get(lo_id)
            if value:
                return _found("LO", query, {"lo": lo_id, "description": value},
                              [f"course_info.txt:{lo_id}"])
        return _missing("LO", query)

    def _assignment(self, frame: SemanticFrame) -> QueryResult:
        assignment_id = frame.slots.get("assignment")
        field = frame.slots.get("field")
        query = f"KB.assignment[{assignment_id}]"
        if assignment_id != self.kb.assignment.get("assignment_id"):
            return _missing("ASSIGNMENT_OVERVIEW", query)
        if field == "overview":
            goal = self.kb.assignment.get("goal")
            if not goal:
                return _missing("ASSIGNMENT_OVERVIEW", query)
            return _found("ASSIGNMENT_OVERVIEW", query, self.kb.assignment,
                          ["assignments.txt:goal", "assignments.txt:PART I–IV"])
        part_id = frame.slots.get("part")
        kind = {"description": "ASSIGNMENT_PART", "feature": "ASSIGNMENT_FEATURE",
                "output": "ASSIGNMENT_OUTPUT"}.get(field, "ASSIGNMENT_PART")
        query += f".parts[{part_id}]"
        part = self.kb.assignment.get("parts", {}).get(part_id)
        if not part:
            return _missing(kind, query)
        if field == "output" and not part.get("suggested_outputs"):
            return _missing(kind, query, "No output list for this assignment part.")
        if field == "feature":
            feature = frame.slots.get("feature", "")
            evidence_terms = {
                "hỏi đáp": ("question answering", "qa"),
                "ngữ cảnh": ("context",),
                "đánh giá": ("evaluation",),
            }.get(feature, (feature,))
            part_text = " ".join([part.get("title", ""),
                                  *part.get("requirements", []),
                                  *part.get("minimum_requirements", [])]).casefold()
            if not any(term in part_text for term in evidence_terms):
                return _missing(kind, query, "Feature is not supported by the part record.")
        return _found(kind, query, part, [f"assignments.txt:{part_id}"])

    def _deadline(self, frame: SemanticFrame) -> QueryResult:
        assignment_id = frame.slots.get("assignment") or frame.entity
        query = f"KB.assignment[{assignment_id}].deadline"
        if assignment_id != self.kb.assignment.get("assignment_id"):
            return _missing("DEADLINE", query)
        deadline = self.kb.assignment.get("deadline")
        if not deadline:
            return _missing("DEADLINE", query, "No specific deadline in assignments.txt.")
        return _found("DEADLINE", query, deadline, ["assignments.txt:deadline"])

    def _resource(self, frame: SemanticFrame) -> QueryResult:
        topic_id = frame.slots.get("topic") or frame.entity
        query = f"KB.resources[topic={topic_id}]"
        if not isinstance(topic_id, str):
            return _missing("RESOURCE", query)
        terms = topic_id.lower().split("_")
        matches = [record for record in self.kb.resources
                   if all(_contains(" ".join([record.get("title", ""),
                                               record.get("usage", "")]), term)
                          for term in terms)]
        return (_found("RESOURCE", query, {"topic": topic_id, "resources": matches},
                       [f"resources.txt:{record['resource_id']}" for record in matches])
                if matches else _missing("RESOURCE", query))

    def _rule(self, frame: SemanticFrame) -> QueryResult:
        rule_id = frame.slots.get("rule") or frame.entity
        query = f"KB.regulations[{rule_id}]"
        value = self.kb.regulations.get(rule_id)
        kind = "RULE_PERMISSION" if frame.slots.get("field") == "permission" else "RULE_POLICY"
        if not value:
            return _missing(kind, query)
        data = {"rule": rule_id, "text": value}
        sources = [f"regulations.txt:{rule_id}"]
        if rule_id == "LLM_RAG":
            status = self.kb.assignment.get("extension", {}).get("status")
            if status:
                data["extension_status"] = status
                sources.append("assignments.txt:LLM/RAG EXTENSION")
        return _found(kind, query, data, sources)

    def _aliases(self, family: str, canonical_id: str) -> list[str]:
        if self.lexicon is None:
            return [normalized_phrase(canonical_id.replace("_", " "))]
        return [alias for alias, target in self.lexicon.sections.get(family, {}).items()
                if target == canonical_id]

    def _topic_chapters(self, topic_id: str) -> list[dict[str, Any]]:
        if not isinstance(topic_id, str):
            return []
        aliases = self._aliases("TOPIC", topic_id)
        direct = [record for record in self.kb.topics.values()
                  if any(_contains(keyword, alias) for keyword in record.get("keywords", [])
                         for alias in aliases)]
        if direct:
            return direct
        return [record for record in self.kb.topics.values()
                if any(_contains(" ".join([record.get("title", ""),
                                           record.get("summary", ""),
                                           *record.get("subtopics", [])]), alias)
                       for alias in aliases)]

    def _week_has_topic(self, record: dict[str, Any], topic_id: str) -> bool:
        aliases = self._aliases("TOPIC", topic_id)
        for phrase in record.get("topics", []):
            if self.lexicon is not None:
                all_matches = [(target, len(alias))
                               for alias, target in self.lexicon.sections.get("TOPIC", {}).items()
                               if _contains(phrase, alias)]
                if all_matches:
                    longest = max(length for _, length in all_matches)
                    if any(target == topic_id and length == longest
                           for target, length in all_matches):
                        return True
            elif any(_contains(phrase, alias) for alias in aliases):
                return True
        return False


def _contains(text: str, phrase: str) -> bool:
    """Find a normalized whole phrase without matching CFG inside PCFG."""
    haystack = normalized_phrase(text)
    needle = normalized_phrase(phrase)
    return bool(needle and re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", haystack))


def _week_source(week_id: str) -> str:
    return f"schedule.txt:WEEK {int(week_id[5:]):02d}"


def _found(kind: str, query: str, data: Any, sources: list[str]) -> QueryResult:
    return QueryResult(query=query, found=True, kind=kind, data=data, sources=sources)


def _missing(kind: str, query: str, reason: str = "No matching KB fact.") -> QueryResult:
    return QueryResult(query=query, found=False, kind=kind, reason=reason)
