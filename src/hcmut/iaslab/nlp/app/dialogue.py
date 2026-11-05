"""Bounded local discourse state for optional multi-turn questions.

Context is more than a single ``last_x`` value: retain the latest entity by
semantic type so a chapter reference cannot accidentally resolve to an LO or an
assignment part.  ``resolve`` runs after raw semantics and before querying;
``update`` runs only after a grounded successful query.  Keep history bounded,
make reset explicit, and record why a reference resolved.  A future confidence-
scored or session-backed resolver can replace this local strategy.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .query import QueryResult
from .semantic import SemanticFrame


@dataclass
class DialogueContext:
    """Typed, per-conversation memory used to resolve anaphoric frames."""

    last_entity: str | None = None
    last_chapter: str | None = None
    last_assignment_part: str | None = None
    last_lo: str | None = None
    history: list[str] = field(default_factory=list)
    history_limit: int = 20

    def reset(self) -> None:
        """Remove all state at a session boundary."""
        self.last_entity = None
        self.last_chapter = None
        self.last_assignment_part = None
        self.last_lo = None
        self.history.clear()

    def resolve(self, frame: SemanticFrame) -> tuple[SemanticFrame, str | None]:
        """Resolve a context-dependent frame and return an explanatory trace.

        If the incoming frame is not context-dependent or if required typed context
        is missing, the original frame is returned unchanged with no trace string.
        """
        if frame.intent != "CONTEXT_DEPENDENT":
            return frame, None

        action = frame.slots.get("action")

        # 1. Topic relation reference
        if action == "TOPIC_RELATION" and self.last_chapter:
            resolved = SemanticFrame(
                intent="GET_TOPIC",
                entity=self.last_chapter,
                slots={"chapter": self.last_chapter, "relation": frame.slots.get("relation")},
                source_branch=frame.source_branch,
            )
            return resolved, f"tham chiếu gần nhất → {self.last_chapter}"

        # 2. Next chapter continuation
        if action == "NEXT_CHAPTER" and self.last_chapter:
            match = self.last_chapter[2:]
            if match.isdigit():
                next_number = int(match) + 1
                if next_number <= 12:
                    next_chapter = f"CH{next_number:02d}"
                    resolved = SemanticFrame(
                        intent="GET_TOPIC",
                        entity=next_chapter,
                        slots={"chapter": next_chapter},
                        source_branch=frame.source_branch,
                    )
                    return resolved, f"chương sau {self.last_chapter} → {next_chapter}"

        # 3. Assignment section output
        if action == "ASSIGNMENT_OUTPUT" and self.last_assignment_part:
            part = self.last_assignment_part
            resolved = SemanticFrame(
                intent="GET_ASSIGNMENT",
                entity=part,
                slots={"assignment": "BTL01", "section": part, "field": "OUTPUTS"},
                source_branch=frame.source_branch,
            )
            return resolved, f"phần BTL gần nhất → {part}"

        # 4. Chapter resource
        if action == "CONTEXT_RESOURCE" and self.last_chapter:
            chapter = self.last_chapter
            resolved = SemanticFrame(
                intent="GET_RESOURCE",
                entity=chapter,
                slots={"topic": chapter, "chapter": chapter},
                source_branch=frame.source_branch,
            )
            return resolved, f"chương gần nhất → {chapter}"

        # 5. Learning outcome chapter lookup\
        if action == "LO_CHAPTER" and self.last_lo:
            lo = self.last_lo
            resolved = SemanticFrame(
                intent="GET_TOPIC",
                entity=lo,
                slots={"lo": lo},
                source_branch=frame.source_branch,
            )
            return resolved, f"learning outcome gần nhất → {lo}"

        # Missing required context or unhandled action: return original frame
        return frame, None

    def update(self, frame: SemanticFrame, result: QueryResult) -> None:
        """Commit only useful entities from a successful grounded result."""
        if not result.found:
            return

        entity = frame.entity
        if entity:
            self.last_entity = entity
            self.history.append(entity)
            del self.history[:-self.history_limit]

            if entity.startswith("CH"):
                self.last_chapter = entity
            elif entity.startswith("PART_"):
                self.last_assignment_part = entity
            elif entity.startswith("LO"):
                self.last_lo = entity

        # Indirect inference from query results
        if result.kind == "SCHEDULE_WEEK" and isinstance(result.data, dict):
            chapter_id = result.data.get("chapter_id")
            if chapter_id and isinstance(chapter_id, str):
                self.last_chapter = chapter_id
        elif result.kind == "TOPIC_SEARCH" and isinstance(result.data, dict):
            chapters = result.data.get("chapters")
            if chapters and isinstance(chapters, list) and len(chapters) > 0:
                first_ch = chapters[0].get("chapter_id")
                if first_ch and isinstance(first_ch, str):
                    self.last_chapter = first_ch
