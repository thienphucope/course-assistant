"""Translate semantic frames into deterministic knowledge-base lookups."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .kb import KnowledgeBase
from .semantic import SemanticFrame
from .tokenizer import normalize_text


TOPIC_SEARCH_TERMS = {
    "CFG": ("cfg", "context-free grammar"),
    "PCFG": ("pcfg", "probabilistic context-free grammar"),
    "DEPENDENCY_GRAMMAR": ("dependency grammar",),
    "FEATURES": ("feature", "features"),
    "AUGMENTED_GRAMMAR": ("augmented grammar", "augmented grammars"),
    "UNIFICATION": ("unification",),
    "POS_TAGGING": ("pos tagging", "part-of-speech tagging"),
    "LOGICAL_FORM": ("logical form",),
    "THEMATIC_ROLES": ("thematic role", "thematic roles"),
    "SELECTIONAL_RESTRICTION": ("selectional restriction", "selectional restrictions"),
    "SEMANTIC_NETWORK": ("semantic network", "semantic networks"),
    "WSD": ("wsd", "word sense disambiguation"),
    "SEMANTIC_GRAMMAR": ("semantic grammar", "semantic grammars"),
    "KNOWLEDGE_REPRESENTATION": ("knowledge representation",),
    "QUESTION_ANSWERING": ("qa", "question answering"),
    "LOCAL_DISCOURSE_CONTEXT": ("local discourse context", "discourse context"),
    "REFERENCE": ("reference",),
    "ANAPHORA": ("anaphora",),
    "CENTERING": ("centering",),
    "PARSING": ("parsing", "parser"),
}

LO_CHAPTER = {
    "LO1.1": "CH01",
    "LO2.1": "CH02",
    "LO2.2": "CH03",
    "LO2.3": "CH04",
    "LO2.4": "CH05",
    "LO2.5": "CH06",
    "LO3.1": "CH07",
    "LO3.2": "CH08",
    "LO3.3": "CH09",
    "LO3.4": "CH10",
    "LO4.1": "CH11",
    "LO4.2": "CH12",
}

RULE_KEYS = {
    "AI_USAGE": "AI_usage",
    "LLM_RAG": "LLM_RAG",
    "EXTERNAL_LIBRARIES": "external_libraries",
    "SOURCE_CODE": "source_code",
    "ACADEMIC_INTEGRITY": "academic_integrity",
    "ASSIGNMENT_SHARING": "assignment_sharing",
}

RESOURCE_TERMS = {
    "STATISTICAL_NLP": ("statistical",),
    "PYTHON_NLP": ("python",),
    "MACHINE_TRANSLATION": ("machine translation",),
    "WORLD_KNOWLEDGE": ("world knowledge", "knowledge and inference"),
    "SEMANTICS": ("speech and language processing", "natural language processing"),
    "CFG": ("foundational nlp", "speech and language processing"),
    "PARSING": ("foundational nlp", "speech and language processing", "natural language processing"),
}


@dataclass
class QueryResult:
    query: str
    found: bool
    kind: str
    data: Any = None
    sources: list[str] = field(default_factory=list)
    reason: str | None = None


class QueryEngine:
    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb

    def execute(self, frame: SemanticFrame) -> QueryResult:
        handler = getattr(self, f"_query_{frame.intent.lower()}", None)
        if handler is None:
            return QueryResult("NO_QUERY", False, "UNKNOWN", reason="intent không được hỗ trợ")
        return handler(frame)

    def _query_unknown(self, frame: SemanticFrame) -> QueryResult:
        return QueryResult("NO_QUERY", False, "UNKNOWN", reason="câu ngoài grammar hoặc ngoài miền")

    def _query_context_dependent(self, frame: SemanticFrame) -> QueryResult:
        return QueryResult("NO_QUERY", False, "UNRESOLVED_CONTEXT", reason="không đủ ngữ cảnh để phân giải tham chiếu")

    def _query_get_course_info(self, frame: SemanticFrame) -> QueryResult:
        field_name = frame.slots.get("field")
        query = f"KB.course[{field_name}]"
        if frame.slots.get("course", "CO3085") != "CO3085":
            return QueryResult(query, False, "COURSE_INFO", reason="không có môn học này")
        if field_name == "CREDITS":
            value = self.kb.course.get("credits")
            return QueryResult(query, value is not None, "COURSE_CREDITS", {"credits": value}, ["kb/course_info.txt"])
        if field_name == "MAIN_PARTS":
            value = self.kb.course.get("main_parts", [])
            return QueryResult(query, bool(value), "COURSE_PARTS", {"parts": value}, ["kb/course_info.txt"])
        if field_name == "DESCRIPTION":
            value = self.kb.course.get("course_description")
            return QueryResult(query, bool(value), "COURSE_DESCRIPTION", {"description": value}, ["kb/course_info.txt"])
        if field_name == "EXAM_DURATION":
            exam = str(frame.slots.get("exam", "")).lower()
            value = self.kb.course.get("exam_format", {}).get(exam)
            return QueryResult(query, bool(value), "EXAM_DURATION", {"exam": exam.upper(), "format": value}, ["kb/course_info.txt"])
        if field_name == "EXAM_TIME":
            return QueryResult(
                query, False, "EXAM_TIME",
                reason="KB chỉ có thời lượng, không có ngày hoặc tuần thi",
            )
        if field_name == "ASSESSMENT":
            value = self.kb.course.get("assessment", {})
            return QueryResult(query, bool(value), "ASSESSMENT", value, ["kb/course_info.txt"])
        return QueryResult(query, False, "COURSE_INFO", reason="thuộc tính môn học không tồn tại")

    def _query_get_schedule(self, frame: SemanticFrame) -> QueryResult:
        week = frame.slots.get("week")
        chapter = frame.slots.get("chapter")
        topics = [str(topic) for topic in frame.slots.get("topics", [])]
        if topics:
            records = []
            for record in self.kb.weeks.values():
                search_text = normalize_text(" ".join(_flatten_text(record))).replace("-", " ")
                if all(
                    any(
                        _whole_phrase(search_text, normalize_text(term).replace("-", " "))
                        for term in TOPIC_SEARCH_TERMS.get(topic, (topic.lower().replace("_", " "),))
                    )
                    for topic in topics
                ):
                    records.append(record)
            return QueryResult(
                f"KB.weeks.search_all({','.join(topics)})", bool(records), "SCHEDULE_TOPICS",
                {"topics": topics, "weeks": records}, ["kb/schedule.txt"] if records else [],
                "không tìm thấy tuần chứa đồng thời các chủ đề" if not records else None,
            )
        if week:
            record = self.kb.weeks.get(str(week))
            return QueryResult(
                f"KB.weeks[{week}]", bool(record), "SCHEDULE_WEEK", record,
                ["kb/schedule.txt"] if record else [], "tuần không có trong lịch" if not record else None,
            )
        if chapter:
            weeks = self.kb.chapter_weeks.get(str(chapter), [])
            return QueryResult(
                f"KB.chapter_weeks[{chapter}]", bool(weeks), "SCHEDULE_CHAPTER",
                {"chapter_id": chapter, "weeks": weeks}, ["kb/schedule.txt"] if weeks else [],
                "chương không có trong lịch" if not weeks else None,
            )
        return QueryResult("KB.schedule[missing_entity]", False, "SCHEDULE", reason="thiếu tuần hoặc chương")

    def _query_get_topic(self, frame: SemanticFrame) -> QueryResult:
        chapter = frame.slots.get("chapter")
        topic = frame.slots.get("topic")
        lo = frame.slots.get("lo")
        relation = frame.slots.get("relation")
        if lo:
            chapter = LO_CHAPTER.get(str(lo))
            record = self.kb.topics.get(chapter or "")
            return QueryResult(
                f"KB.lo_chapter[{lo}]", bool(record), "LO_CHAPTER",
                {"lo": lo, "chapter": record}, ["kb/course_info.txt", "kb/topics.txt"] if record else [],
                "không ánh xạ được learning outcome sang chương" if not record else None,
            )
        if chapter:
            record = self.kb.topics.get(str(chapter))
            if not record:
                return QueryResult(f"KB.topics[{chapter}]", False, "TOPIC_CHAPTER", reason="chương không tồn tại")
            if relation:
                related = self._topic_relation(record, str(relation))
                return QueryResult(
                    f"KB.topics[{chapter}].contains({relation})", True, "TOPIC_RELATION",
                    {"chapter": record, "relation": relation, "related": related}, ["kb/topics.txt"],
                )
            return QueryResult(f"KB.topics[{chapter}]", True, "TOPIC_CHAPTER", record, ["kb/topics.txt"])
        if topic:
            records = self._find_topic_records(str(topic))
            return QueryResult(
                f"KB.topics.search({topic})", bool(records), "TOPIC_SEARCH",
                {"topic": topic, "chapters": records}, ["kb/topics.txt"] if records else [],
                "không tìm thấy chủ đề" if not records else None,
            )
        return QueryResult("KB.topics[missing_entity]", False, "TOPIC", reason="thiếu chapter/topic")

    def _find_topic_records(self, topic: str) -> list[dict[str, Any]]:
        terms = TOPIC_SEARCH_TERMS.get(topic, (topic.lower(),))
        scored: list[tuple[int, int, dict[str, Any]]] = []
        for record in self.kb.topics.values():
            keyword_values = [normalize_text(item).replace("-", " ") for item in record.get("keyword_list", [])]
            search_text = normalize_text(" ".join(_flatten_text(record))).replace("-", " ")
            score = 0
            for term in terms:
                normalized_term = normalize_text(term).replace("-", " ")
                if normalized_term in keyword_values:
                    score = max(score, 10)
                elif _whole_phrase(search_text, normalized_term):
                    score = max(score, 2)
            if score:
                scored.append((score, int(record["chapter_number"]), record))
        if not scored:
            return []
        best = max(item[0] for item in scored)
        return [item[2] for item in sorted(scored, key=lambda item: (-item[0], item[1])) if item[0] == best]

    def _topic_relation(self, record: dict[str, Any], relation: str) -> bool:
        terms = TOPIC_SEARCH_TERMS.get(relation, (relation.lower(),))
        text = normalize_text(" ".join(_flatten_text(record))).replace("-", " ")
        return any(_whole_phrase(text, normalize_text(term).replace("-", " ")) for term in terms)

    def _query_get_lo(self, frame: SemanticFrame) -> QueryResult:
        lo = str(frame.slots.get("lo") or "")
        value = self.kb.course.get("learning_outcomes", {}).get(lo)
        return QueryResult(
            f"KB.learning_outcomes[{lo}]", bool(value), "LEARNING_OUTCOME",
            {"lo": lo, "description": value}, ["kb/course_info.txt"] if value else [],
            "learning outcome không tồn tại" if not value else None,
        )

    def _query_get_assignment(self, frame: SemanticFrame) -> QueryResult:
        section_id = frame.slots.get("section")
        if section_id == "OVERVIEW":
            data = {
                "assignment_id": self.kb.assignment.get("assignment_id"),
                "title": self.kb.assignment.get("title"),
                "goal": self.kb.assignment.get("goal"),
                "sections": list(self.kb.assignment.get("sections", {})),
            }
            return QueryResult("KB.assignment[BTL01]", True, "ASSIGNMENT_OVERVIEW", data, ["kb/assignments.txt"])
        section = self.kb.assignment.get("sections", {}).get(section_id)
        return QueryResult(
            f"KB.assignment.sections[{section_id}]", bool(section), "ASSIGNMENT_SECTION",
            {"section": section, "field": frame.slots.get("field"), "feature": frame.slots.get("feature")},
            ["kb/assignments.txt"] if section else [], "phần BTL không tồn tại" if not section else None,
        )

    def _query_get_deadline(self, frame: SemanticFrame) -> QueryResult:
        milestones = [
            {"week_id": week_id, "milestone": record["milestone"]}
            for week_id, record in self.kb.weeks.items()
            if record.get("milestone")
        ]
        return QueryResult(
            "KB.weeks[*].milestone", bool(milestones), "DEADLINE", milestones,
            ["kb/schedule.txt"] if milestones else [], "không có mốc BTL" if not milestones else None,
        )

    def _query_get_resource(self, frame: SemanticFrame) -> QueryResult:
        topic = str(frame.slots.get("topic") or "")
        chapter = frame.slots.get("chapter")
        if chapter or topic.startswith("CH"):
            records = [
                resource for resource in self.kb.resources
                if any(term in normalize_text(" ".join(_flatten_text(resource))) for term in ("foundational", "broad nlp", "natural language processing"))
            ][:3]
            query_topic = str(chapter or topic)
        else:
            terms = RESOURCE_TERMS.get(topic, (topic.lower().replace("_", " "),))
            scored: list[tuple[int, dict[str, Any]]] = []
            for resource in self.kb.resources:
                title = normalize_text(str(resource.get("title", "")))
                usage = normalize_text(str(resource.get("usage", "")))
                score = sum(3 if term in title else 1 if term in usage else 0 for term in terms)
                if score:
                    scored.append((score, resource))
            scored.sort(key=lambda item: -item[0])
            best = scored[0][0] if scored else 0
            records = [record for score, record in scored if score == best]
            query_topic = topic
        return QueryResult(
            f"KB.resources.search({query_topic})", bool(records), "RESOURCE", records,
            ["kb/resources.txt"] if records else [], "không tìm thấy tài liệu phù hợp" if not records else None,
        )

    def _query_get_rule(self, frame: SemanticFrame) -> QueryResult:
        rule_id = str(frame.slots.get("rule") or "")
        key = RULE_KEYS.get(rule_id)
        value = self.kb.regulations.get(key or "")
        return QueryResult(
            f"KB.regulations[{key or rule_id}]", bool(value), "RULE",
            {"rule_id": rule_id, "text": value}, ["kb/regulations.txt"] if value else [],
            "quy định không tồn tại" if not value else None,
        )

    def _query_get_instructor(self, frame: SemanticFrame) -> QueryResult:
        return QueryResult(
            "KB.course[instructor]", False, "INSTRUCTOR", reason="KB không cung cấp thông tin giảng viên"
        )


def _flatten_text(value: Any) -> list[str]:
    if isinstance(value, dict):
        result: list[str] = []
        for child in value.values():
            result.extend(_flatten_text(child))
        return result
    if isinstance(value, (list, tuple)):
        result = []
        for child in value:
            result.extend(_flatten_text(child))
        return result
    return [str(value)]


def _whole_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    pattern = rf"(?<![\w]){re.escape(phrase)}(?![\w])"
    return re.search(pattern, text, re.UNICODE) is not None
