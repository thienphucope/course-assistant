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
        """Resolve a context-dependent frame and return an explanatory trace."""
        raise NotImplementedError("Implement typed reference resolution and safe fallbacks")

    def update(self, frame: SemanticFrame, result: QueryResult) -> None:
        """Commit only useful entities from a successful grounded result."""
        raise NotImplementedError("Implement bounded, type-aware context updates")
