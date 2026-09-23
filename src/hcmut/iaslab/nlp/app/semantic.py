"""Convert labeled parse trees into intent, canonical entity, and typed slots.

This module reads only the tree and entity aliases. Course facts belong in the
KB, so understanding a question cannot accidentally invent its answer.
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
        if (
            self.entity is not None
            and self.entity not in values.values()
            and "entity" not in values
        ):
            values = {"entity": self.entity, **values}
        arguments = ", ".join(f"{key}={value}" for key, value in values.items())
        return f"{self.intent}({arguments})"

    @classmethod
    def unknown(cls) -> "SemanticFrame":
        return cls(intent="UNKNOWN")


@dataclass(frozen=True)
class _SimpleMapping:
    """How one Q_* branch extracts its main entity from a named tree node."""

    intent: str
    node: str
    family: str
    slot: str
    field: str | None = None


_SIMPLE_BRANCHES: dict[str, _SimpleMapping] = {
    "Q_COURSE_CREDITS": _SimpleMapping("GET_COURSE_INFO", "COURSE_ENTITY", "COURSE", "course", "credits"),
    "Q_COURSE_PARTS": _SimpleMapping("GET_COURSE_INFO", "COURSE_ENTITY", "COURSE", "course", "parts"),
    "Q_COURSE_DESCRIPTION": _SimpleMapping("GET_COURSE_INFO", "COURSE_ENTITY", "COURSE", "course", "description"),
    "Q_COURSE_EXAM_DURATION": _SimpleMapping("GET_COURSE_INFO", "EXAM_ENTITY", "EXAM", "exam", "duration"),
    "Q_COURSE_EXAM_TIME": _SimpleMapping("GET_COURSE_INFO", "EXAM_ENTITY", "EXAM", "exam", "time"),
    "Q_INSTRUCTOR": _SimpleMapping("GET_COURSE_INFO", "COURSE_ENTITY", "COURSE", "course", "instructor"),
    "Q_SCHEDULE_WEEK": _SimpleMapping("GET_SCHEDULE", "WEEK_ENTITY", "WEEK", "week"),
    "Q_SCHEDULE_CHAPTER": _SimpleMapping("GET_SCHEDULE", "CHAPTER_ENTITY", "CHAPTER", "chapter"),
    "Q_TOPIC_BY_NAME": _SimpleMapping("GET_TOPIC", "TOPIC_ENTITY", "TOPIC", "topic", "chapter"),
    "Q_TOPIC_LOCATION": _SimpleMapping("GET_TOPIC", "TOPIC_ENTITY", "TOPIC", "topic", "location"),
    "Q_TOPIC_BY_CHAPTER": _SimpleMapping("GET_TOPIC", "CHAPTER_ENTITY", "CHAPTER", "chapter", "overview"),
    "Q_TOPIC_METHODS": _SimpleMapping("GET_TOPIC", "CHAPTER_ENTITY", "CHAPTER", "chapter", "methods"),
    "Q_LO": _SimpleMapping("GET_LO", "LO_ENTITY", "LO", "lo", "description"),
    "Q_LO_CONTENT": _SimpleMapping("GET_LO", "LO_ENTITY", "LO", "lo", "content"),
    "Q_ASSIGNMENT_OVERVIEW": _SimpleMapping("GET_ASSIGNMENT", "ASSIGNMENT_ENTITY", "ASSIGNMENT", "assignment", "overview"),
    "Q_DEADLINE": _SimpleMapping("GET_DEADLINE", "ASSIGNMENT_ENTITY", "ASSIGNMENT", "assignment", "deadline"),
    "Q_RESOURCE": _SimpleMapping("GET_RESOURCE", "RESOURCE_TOPIC", "RESOURCE_TOPIC", "topic"),
    "Q_RULE": _SimpleMapping("GET_RULE", "RULE_TOPIC", "RULE", "rule", "policy"),
    "Q_RULE_PERMISSION": _SimpleMapping("GET_RULE", "RULE_TOPIC", "RULE", "rule", "permission"),
}


class SemanticInterpreter:
    """Interpret labeled CFG subtrees into canonical semantic frames."""

    def __init__(self, lexicon: EntityLexicon) -> None:
        self.lexicon = lexicon

    def interpret(self, tree: Tree | None) -> SemanticFrame:
        """Interpret a Q_* subtree, never guessing meaning from raw text."""
        if tree is None:
            return SemanticFrame.unknown()

        branch = next((node for node in tree.walk() if node.label.startswith("Q_")), None)
        if branch is None:
            return SemanticFrame.unknown()

        mapping = _SIMPLE_BRANCHES.get(branch.label)
        if mapping is not None:
            entity = self._resolve(branch, mapping.node, mapping.family)
            if entity is None:
                return SemanticFrame.unknown()
            slots: dict[str, Any] = {mapping.slot: entity}
            if mapping.field is not None:
                slots["field"] = mapping.field
            return SemanticFrame(mapping.intent, entity, slots, branch.label)

        special = {
            "Q_COURSE_ASSESSMENT": self._course_assessment,
            "Q_SCHEDULE_TOPICS": self._schedule_topics,
            "Q_TOPIC_RELATION": self._topic_relation,
            "Q_ASSIGNMENT_PART": self._assignment_part,
            "Q_ASSIGNMENT_FEATURE": self._assignment_feature,
            "Q_ASSIGNMENT_OUTPUT": self._assignment_output,
        }.get(branch.label)
        if special is not None:
            return special(branch)

        # Dialogue branches are optional and require a separate context resolver.
        return SemanticFrame(intent="UNSUPPORTED", source_branch=branch.label)

    def _resolve(self, branch: Tree, node_label: str, family: str) -> str | None:
        node = branch.first(node_label)
        if node is None:
            return None
        return self.lexicon.resolve(family, " ".join(node.leaves()))

    def _course_assessment(self, branch: Tree) -> SemanticFrame:
        course = self.lexicon.resolve("COURSE", "NLP")
        if course is None:
            return SemanticFrame.unknown()
        return SemanticFrame("GET_COURSE_INFO", course,
                             {"course": course, "field": "assessment"}, branch.label)

    def _schedule_topics(self, branch: Tree) -> SemanticFrame:
        mentions = [node for node in branch.walk() if node.label == "TOPIC_ENTITY"]
        if len(mentions) != 2:
            return SemanticFrame.unknown()
        topics = [self.lexicon.resolve("TOPIC", " ".join(node.leaves())) for node in mentions]
        if any(topic is None for topic in topics):
            return SemanticFrame.unknown()
        return SemanticFrame("GET_SCHEDULE", topics[0], {"topics": topics}, branch.label)

    def _topic_relation(self, branch: Tree) -> SemanticFrame:
        chapter = self._resolve(branch, "CHAPTER_ENTITY", "CHAPTER")
        topic = self._resolve(branch, "TOPIC_ENTITY", "TOPIC")
        if chapter is None or topic is None:
            return SemanticFrame.unknown()
        return SemanticFrame("GET_TOPIC", chapter,
                             {"chapter": chapter, "topic": topic, "field": "relation"},
                             branch.label)

    def _assignment_part(self, branch: Tree) -> SemanticFrame:
        part = self._resolve(branch, "ASSIGNMENT_PART", "ASSIGNMENT_PART")
        assignment = self._resolve(branch, "ASSIGNMENT_ENTITY", "ASSIGNMENT")
        if part is None or assignment is None:
            return SemanticFrame.unknown()
        return SemanticFrame("GET_ASSIGNMENT", part,
                             {"assignment": assignment, "part": part, "field": "description"},
                             branch.label)

    def _assignment_feature(self, branch: Tree) -> SemanticFrame:
        feature_node = branch.first("ASSIGNMENT_FEATURE")
        assignment = self._resolve(branch, "ASSIGNMENT_ENTITY", "ASSIGNMENT")
        if feature_node is None or assignment is None:
            return SemanticFrame.unknown()
        feature = " ".join(feature_node.leaves())
        part = self.lexicon.resolve("ASSIGNMENT_FEATURE", feature)
        if part is None:
            return SemanticFrame.unknown()
        return SemanticFrame("GET_ASSIGNMENT", part,
                             {"assignment": assignment, "part": part,
                              "feature": feature, "field": "feature"}, branch.label)

    def _assignment_output(self, branch: Tree) -> SemanticFrame:
        part = self._resolve(branch, "ASSIGNMENT_PART", "ASSIGNMENT_PART")
        assignment = self.lexicon.resolve("ASSIGNMENT", "BTL")
        if part is None or assignment is None:
            return SemanticFrame.unknown()
        return SemanticFrame("GET_ASSIGNMENT", part,
                             {"assignment": assignment, "part": part, "field": "output"},
                             branch.label)
