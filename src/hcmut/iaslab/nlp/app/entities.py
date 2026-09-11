"""Entity lexicon and canonical-ID normalization boundary.

Surface forms such as ``tuần 3``, ``week 03``, or future synonyms should resolve
to one stable ID such as ``WEEK_03``.  Grammar decides where an entity may occur;
this module decides what that mention means.  Keep aliases data-driven and keep
IDs stable because semantics, dialogue state, query routing, tests, and output
all exchange them.  New entity families can be added without changing parsing.
"""

from __future__ import annotations

from pathlib import Path


class EntityLexicon:
    """Load alias tables and expose deterministic canonicalization methods."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.sections: dict[str, dict[str, str]] = {}

    @classmethod
    def from_file(cls, path: str | Path) -> "EntityLexicon":
        """Load and validate a UTF-8 entity-alias file."""
        raise NotImplementedError("Implement entity lexicon loading")

    def resolve(self, family: str, phrase: str) -> str | None:
        """Resolve ``phrase`` within an entity family to a canonical ID."""
        raise NotImplementedError("Implement generic alias resolution")

    def resolve_week(self, phrase: str) -> str | None:
        raise NotImplementedError("Normalize week mentions to WEEK_NN")

    def resolve_chapter(self, phrase: str) -> str | None:
        raise NotImplementedError("Normalize chapter mentions to CHNN")

    def resolve_topic(self, phrase: str) -> str | None:
        raise NotImplementedError("Normalize topic aliases")

    def resolve_lo(self, phrase: str) -> str | None:
        raise NotImplementedError("Normalize learning outcomes to LOx.y")

    def resolve_assignment_part(self, phrase: str) -> str | None:
        raise NotImplementedError("Normalize assignment sections to PART_I..PART_IV")

    def resolve_resource_topic(self, phrase: str) -> str | None:
        raise NotImplementedError("Normalize requested resource topics")

    def resolve_rule(self, phrase: str) -> str | None:
        raise NotImplementedError("Normalize regulation and policy topics")
