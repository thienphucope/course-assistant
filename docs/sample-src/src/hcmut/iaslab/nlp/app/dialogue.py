"""History-list based local discourse resolution for the optional Part III."""

from __future__ import annotations

from dataclasses import dataclass, field

from .query import QueryResult
from .semantic import SemanticFrame


@dataclass
class DialogueContext:
    last_entity: str | None = None
    last_chapter: str | None = None
    last_assignment_part: str | None = None
    last_lo: str | None = None
    history: list[str] = field(default_factory=list)

    def reset(self) -> None:
        self.last_entity = None
        self.last_chapter = None
        self.last_assignment_part = None
        self.last_lo = None
        self.history.clear()

    def resolve(self, frame: SemanticFrame) -> tuple[SemanticFrame, str | None]:
        if frame.intent != "CONTEXT_DEPENDENT":
            return frame, None
        action = frame.slots.get("action")
        if action == "TOPIC_RELATION" and self.last_chapter:
            resolved = SemanticFrame(
                "GET_TOPIC", self.last_chapter,
                {"chapter": self.last_chapter, "relation": frame.slots.get("relation")},
                frame.source_branch,
            )
            return resolved, f"tham chiếu gần nhất → {self.last_chapter}"
        if action == "NEXT_CHAPTER" and self.last_chapter:
            number = int(self.last_chapter[2:]) + 1
            if number <= 12:
                chapter = f"CH{number:02d}"
                return SemanticFrame("GET_TOPIC", chapter, {"chapter": chapter}, frame.source_branch), f"chương sau {self.last_chapter} → {chapter}"
        if action == "ASSIGNMENT_OUTPUT" and self.last_assignment_part:
            part = self.last_assignment_part
            resolved = SemanticFrame(
                "GET_ASSIGNMENT", part,
                {"assignment": "BTL01", "section": part, "field": "OUTPUTS"},
                frame.source_branch,
            )
            return resolved, f"phần BTL gần nhất → {part}"
        if action == "CONTEXT_RESOURCE" and self.last_chapter:
            chapter = self.last_chapter
            resolved = SemanticFrame(
                "GET_RESOURCE", chapter, {"topic": chapter, "chapter": chapter}, frame.source_branch
            )
            return resolved, f"chương gần nhất → {chapter}"
        if action == "LO_CHAPTER" and self.last_lo:
            lo = self.last_lo
            resolved = SemanticFrame("GET_TOPIC", lo, {"lo": lo}, frame.source_branch)
            return resolved, f"learning outcome gần nhất → {lo}"
        return frame, None

    def update(self, frame: SemanticFrame, result: QueryResult) -> None:
        if not result.found:
            return
        entity = frame.entity
        if entity:
            self.last_entity = entity
            self.history.append(entity)
            del self.history[:-20]
        if entity and entity.startswith("CH"):
            self.last_chapter = entity
        if entity and entity.startswith("PART_"):
            self.last_assignment_part = entity
        if entity and entity.startswith("LO"):
            self.last_lo = entity
        if result.kind == "SCHEDULE_WEEK" and result.data.get("chapter_id"):
            self.last_chapter = result.data["chapter_id"]
        elif result.kind == "TOPIC_SEARCH" and result.data.get("chapters"):
            self.last_chapter = result.data["chapters"][0]["chapter_id"]

