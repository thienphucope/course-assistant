"""Compositional conversion from parse trees to machine-readable meaning.

``SemanticFrame`` groups the three essential semantic outputs: an intent, a
canonical focus entity, and typed slots.  ``source_branch`` preserves the CFG
branch for debugging.  The interpreter should dispatch from labeled tree nodes
(for example ``Q_SCHEDULE_WEEK``), collect entities compositionally, and return
``UNKNOWN`` for missing/unsupported structures.  KB access is forbidden here;
meaning extraction and fact lookup are separate, testable concerns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .entities import EntityLexicon
from .tree import Tree


@dataclass
class SemanticFrame:
    """Normalized request exchanged by semantics, context, and query stages."""

    intent: str
    entity: str | None = None
    slots: dict[str, Any] = field(default_factory=dict)
    source_branch: str | None = None

    @property
    def predicate(self) -> str:
        """Render a compact, deterministic representation for grading/debugging."""
        values = dict(self.slots)
        if self.entity is not None and "entity" not in values:
            values = {"entity": self.entity, **values}
        arguments = ", ".join(f"{key}={_format_value(value)}" for key, value in values.items())
        return f"{self.intent}({arguments})"

    @classmethod
    def unknown(cls) -> "SemanticFrame":
        return cls(intent="UNKNOWN")


BRANCH_INTENTS: dict[str, str] = {
    "Q_COURSE_CREDITS": "GET_COURSE_INFO",
    "Q_COURSE_PARTS": "GET_COURSE_INFO",
    "Q_COURSE_DESCRIPTION": "GET_COURSE_INFO",
    "Q_COURSE_EXAM_DURATION": "GET_COURSE_INFO",
    "Q_COURSE_EXAM_TIME": "GET_COURSE_INFO",
    "Q_COURSE_ASSESSMENT": "GET_COURSE_INFO",
    "Q_INSTRUCTOR": "GET_INSTRUCTOR",
    "Q_SCHEDULE_WEEK": "GET_SCHEDULE",
    "Q_SCHEDULE_CHAPTER": "GET_SCHEDULE",
    "Q_SCHEDULE_TOPICS": "GET_SCHEDULE",
    "Q_TOPIC_BY_NAME": "GET_TOPIC",
    "Q_TOPIC_BY_CHAPTER": "GET_TOPIC",
    "Q_TOPIC_RELATION": "GET_TOPIC",
    "Q_LO": "GET_LO",
    "Q_ASSIGNMENT_OVERVIEW": "GET_ASSIGNMENT",
    "Q_ASSIGNMENT_PART": "GET_ASSIGNMENT",
    "Q_ASSIGNMENT_FEATURE": "GET_ASSIGNMENT",
    "Q_ASSIGNMENT_OUTPUT": "GET_ASSIGNMENT",
    "Q_DEADLINE": "GET_DEADLINE",
    "Q_RESOURCE": "GET_RESOURCE",
    "Q_RULE": "GET_RULE",
    "Q_CONTEXT_TOPIC_RELATION": "CONTEXT_DEPENDENT",
    "Q_CONTEXT_NEXT_CHAPTER": "CONTEXT_DEPENDENT",
    "Q_CONTEXT_ASSIGNMENT_OUTPUT": "CONTEXT_DEPENDENT",
    "Q_CONTEXT_RESOURCE": "CONTEXT_DEPENDENT",
    "Q_CONTEXT_LO_CHAPTER": "CONTEXT_DEPENDENT",
}


FEATURE_TO_PART: dict[str, str] = {
    "parser": "PART_I",
    "semantic": "PART_II",
    "hỏi đáp": "PART_II",
    "ngữ cảnh": "PART_III",
    "đánh giá": "PART_IV",
}


class SemanticInterpreter:
    """Interpret labeled CFG subtrees into canonical semantic frames."""

    def __init__(self, lexicon: EntityLexicon) -> None:
        self.lexicon = lexicon

    def interpret(self, tree: Tree | None) -> SemanticFrame:
        """Map a complete tree to meaning without consulting the knowledge base."""
        if tree is None:
            return SemanticFrame.unknown()

        question = tree.first("QUESTION")
        if question is None:
            return SemanticFrame.unknown()

        branch = next((child for child in question.children if isinstance(child, Tree) and child.label.startswith("Q_")), None)
        if branch is None or branch.label not in BRANCH_INTENTS:
            return SemanticFrame.unknown()

        handler = getattr(self, f"_handle_{branch.label.lower()}", None)
        if handler is None:
            return SemanticFrame.unknown()

        frame: SemanticFrame = handler(branch)
        frame.source_branch = branch.label
        return frame

    @staticmethod
    def _phrase(node: Tree | None) -> str:
        """Flatten leaves of a constituent subtree into a single space-separated string."""
        return " ".join(node.leaves()) if node is not None else ""

    # =========================================================================
    # Group 1: Course Information & Instructor (7 branches)
    # =========================================================================

    def _handle_q_course_credits(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="GET_COURSE_INFO",
            entity="CO3085",
            slots={"course": "CO3085", "field": "CREDITS"},
        )

    def _handle_q_course_parts(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="GET_COURSE_INFO",
            entity="CO3085",
            slots={"course": "CO3085", "field": "MAIN_PARTS"},
        )

    def _handle_q_course_description(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="GET_COURSE_INFO",
            entity="CO3085",
            slots={"course": "CO3085", "field": "DESCRIPTION"},
        )

    def _handle_q_course_exam_duration(self, branch: Tree) -> SemanticFrame:
        exam_node = branch.first("EXAM_ENTITY")
        phrase = self._phrase(exam_node)
        exam = "MIDTERM" if phrase in {"midterm", "giữa kỳ"} else "FINAL"
        return SemanticFrame(
            intent="GET_COURSE_INFO",
            entity=exam,
            slots={"course": "CO3085", "field": "EXAM_DURATION", "exam": exam},
        )

    def _handle_q_course_exam_time(self, branch: Tree) -> SemanticFrame:
        exam_node = branch.first("EXAM_ENTITY")
        phrase = self._phrase(exam_node)
        exam = "MIDTERM" if phrase in {"midterm", "giữa kỳ"} else "FINAL"
        return SemanticFrame(
            intent="GET_COURSE_INFO",
            entity=exam,
            slots={"course": "CO3085", "field": "EXAM_TIME", "exam": exam},
        )

    def _handle_q_course_assessment(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="GET_COURSE_INFO",
            entity="CO3085",
            slots={"course": "CO3085", "field": "ASSESSMENT"},
        )

    def _handle_q_instructor(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="GET_INSTRUCTOR",
            entity="CO3085",
            slots={"course": "CO3085"},
        )

    # =========================================================================
    # Group 2: Schedule (3 branches)
    # =========================================================================

    def _handle_q_schedule_week(self, branch: Tree) -> SemanticFrame:
        week = self.lexicon.resolve_week(self._phrase(branch.first("WEEK_ENTITY")))
        return SemanticFrame(
            intent="GET_SCHEDULE",
            entity=week,
            slots={"week": week},
        )

    def _handle_q_schedule_chapter(self, branch: Tree) -> SemanticFrame:
        chapter = self.lexicon.resolve_chapter(self._phrase(branch.first("CHAPTER_ENTITY")))
        return SemanticFrame(
            intent="GET_SCHEDULE",
            entity=chapter,
            slots={"chapter": chapter},
        )

    def _handle_q_schedule_topics(self, branch: Tree) -> SemanticFrame:
        topic_nodes = [node for node in branch.walk() if node.label == "TOPIC_ENTITY"]
        topics: list[str] = [
            topic
            for node in topic_nodes
            if (topic := self.lexicon.resolve_topic(self._phrase(node))) is not None
        ]
        first_topic = topics[0] if topics else None
        return SemanticFrame(
            intent="GET_SCHEDULE",
            entity=first_topic,
            slots={"topics": topics},
        )

    # =========================================================================
    # Group 3: Topics & Chapters (3 branches)
    # =========================================================================

    def _handle_q_topic_by_name(self, branch: Tree) -> SemanticFrame:
        topic = self.lexicon.resolve_topic(self._phrase(branch.first("TOPIC_ENTITY")))
        return SemanticFrame(
            intent="GET_TOPIC",
            entity=topic,
            slots={"topic": topic},
        )

    def _handle_q_topic_by_chapter(self, branch: Tree) -> SemanticFrame:
        chapter = self.lexicon.resolve_chapter(self._phrase(branch.first("CHAPTER_ENTITY")))
        return SemanticFrame(
            intent="GET_TOPIC",
            entity=chapter,
            slots={"chapter": chapter},
        )

    def _handle_q_topic_relation(self, branch: Tree) -> SemanticFrame:
        chapter = self.lexicon.resolve_chapter(self._phrase(branch.first("CHAPTER_ENTITY")))
        relation = self.lexicon.resolve_topic(self._phrase(branch.first("TOPIC_ENTITY")))
        return SemanticFrame(
            intent="GET_TOPIC",
            entity=chapter,
            slots={"chapter": chapter, "relation": relation},
        )

    # =========================================================================
    # Group 4: Learning Outcomes (1 branch)
    # =========================================================================

    def _handle_q_lo(self, branch: Tree) -> SemanticFrame:
        lo = self.lexicon.resolve_lo(self._phrase(branch.first("LO_ENTITY")))
        return SemanticFrame(
            intent="GET_LO",
            entity=lo,
            slots={"lo": lo},
        )

    # =========================================================================
    # Group 5: Assignment & Deadlines (5 branches)
    # =========================================================================

    def _handle_q_assignment_overview(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="GET_ASSIGNMENT",
            entity="BTL01",
            slots={"assignment": "BTL01", "section": "OVERVIEW"},
        )

    def _handle_q_assignment_part(self, branch: Tree) -> SemanticFrame:
        part = self.lexicon.resolve_assignment_part(self._phrase(branch.first("ASSIGNMENT_PART")))
        return SemanticFrame(
            intent="GET_ASSIGNMENT",
            entity=part,
            slots={"assignment": "BTL01", "section": part},
        )

    def _handle_q_assignment_feature(self, branch: Tree) -> SemanticFrame:
        phrase = self._phrase(branch.first("ASSIGNMENT_FEATURE"))
        part = FEATURE_TO_PART.get(phrase)
        return SemanticFrame(
            intent="GET_ASSIGNMENT",
            entity=part,
            slots={"assignment": "BTL01", "section": part, "feature": phrase},
        )

    def _handle_q_assignment_output(self, branch: Tree) -> SemanticFrame:
        part = self.lexicon.resolve_assignment_part(self._phrase(branch.first("ASSIGNMENT_PART")))
        return SemanticFrame(
            intent="GET_ASSIGNMENT",
            entity=part,
            slots={"assignment": "BTL01", "section": part, "field": "OUTPUTS"},
        )

    def _handle_q_deadline(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="GET_DEADLINE",
            entity="BTL01",
            slots={"assignment": "BTL01"},
        )

    # =========================================================================
    # Group 6: Resources & Regulations (2 branches)
    # =========================================================================

    def _handle_q_resource(self, branch: Tree) -> SemanticFrame:
        topic = self.lexicon.resolve_resource_topic(self._phrase(branch.first("RESOURCE_TOPIC")))
        return SemanticFrame(
            intent="GET_RESOURCE",
            entity=topic,
            slots={"topic": topic},
        )

    def _handle_q_rule(self, branch: Tree) -> SemanticFrame:
        topic_node = branch.first("RULE_TOPIC")
        phrase = self._phrase(topic_node) if topic_node is not None else self._phrase(branch)
        rule = self.lexicon.resolve_rule(phrase)
        if rule is None and "chia sẻ bài làm" in self._phrase(branch):
            rule = "ASSIGNMENT_SHARING"
        return SemanticFrame(
            intent="GET_RULE",
            entity=rule,
            slots={"rule": rule},
        )

    # =========================================================================
    # Group 7: Context-dependent Questions (5 branches)
    # =========================================================================

    def _handle_q_context_topic_relation(self, branch: Tree) -> SemanticFrame:
        relation = self.lexicon.resolve_topic(self._phrase(branch.first("TOPIC_ENTITY")))
        return SemanticFrame(
            intent="CONTEXT_DEPENDENT",
            entity=None,
            slots={"action": "TOPIC_RELATION", "relation": relation},
        )

    def _handle_q_context_next_chapter(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="CONTEXT_DEPENDENT",
            entity=None,
            slots={"action": "NEXT_CHAPTER"},
        )

    def _handle_q_context_assignment_output(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="CONTEXT_DEPENDENT",
            entity=None,
            slots={"action": "ASSIGNMENT_OUTPUT"},
        )

    def _handle_q_context_resource(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="CONTEXT_DEPENDENT",
            entity=None,
            slots={"action": "CONTEXT_RESOURCE"},
        )

    def _handle_q_context_lo_chapter(self, branch: Tree) -> SemanticFrame:
        return SemanticFrame(
            intent="CONTEXT_DEPENDENT",
            entity=None,
            slots={"action": "LO_CHAPTER"},
        )


def _format_value(value: Any) -> str:
    """Format slot values deterministically for predicate rendering."""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(str(item) for item in value) + "]"
    return str(value)
