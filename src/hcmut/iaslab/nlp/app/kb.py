"""Load, normalize, index, and validate the supplied course knowledge base.

This module is the only place that understands the physical ``data/kb`` text
formats.  Convert them once into canonical in-memory records keyed by IDs such
as ``CH03`` and ``WEEK_03``; query code should not repeatedly parse raw text.
Validation must report broken cross-references, duplicate IDs, and missing
required fields early.  A later JSON/database adapter can implement the same
contract without changing semantics, dialogue, or answer generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class KnowledgeBase:
    """Normalized aggregate of every supported course-data collection."""

    course: dict[str, Any] = field(default_factory=dict)
    weeks: dict[str, dict[str, Any]] = field(default_factory=dict)
    chapter_weeks: dict[str, list[str]] = field(default_factory=dict)
    topics: dict[str, dict[str, Any]] = field(default_factory=dict)
    assignment: dict[str, Any] = field(default_factory=dict)
    resources: tuple[dict[str, Any], ...] = ()
    regulations: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, kb_dir: str | Path) -> "KnowledgeBase":
        """Read all required KB files and build canonical indexes."""
        raise NotImplementedError("Implement the loaders for the supplied KB text files")

    def validate(self) -> list[str]:
        """Return all structural/cross-reference errors; an empty list is valid."""
        raise NotImplementedError("Implement schema and referential-integrity checks")
