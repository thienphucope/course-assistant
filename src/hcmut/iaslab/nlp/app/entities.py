"""Entity lexicon and canonical-ID normalization boundary.

Surface forms such as ``tuần 3``, ``week 03``, or future synonyms should resolve
to one stable ID such as ``WEEK_03``.  Grammar decides where an entity may occur;
this module decides what that mention means.  Keep aliases data-driven and keep
IDs stable because semantics, dialogue state, query routing, tests, and output
all exchange them.  New entity families can be added without changing parsing.
"""

from __future__ import annotations

from pathlib import Path
import re

from .tokenizer import normalized_phrase


def _normalize(value: str) -> str:
    """Compare aliases using the same token spelling as parser tree leaves."""
    return normalized_phrase(value)


class EntityLexicon:
    """Load alias tables and expose deterministic canonicalization methods."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.sections: dict[str, dict[str, str]] = {}

    @classmethod
    def from_file(cls, path: str | Path) -> "EntityLexicon":
        """Load and validate a UTF-8 entity-alias file."""
        lexicon = cls(path)
        family: str | None = None
        for line_number, raw_line in enumerate(lexicon.path.read_text(encoding="utf-8-sig").splitlines(), 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                if not re.fullmatch(r"[A-Z][A-Z0-9_]*", line):
                    raise ValueError(f"Invalid entity section on line {line_number}: {line}")
                family = line
                lexicon.sections.setdefault(family, {})
                continue
            if family is None:
                raise ValueError(f"Entity alias precedes its section on line {line_number}")
            alias, canonical = (part.strip() for part in line.split("=", 1))
            if not alias or not canonical:
                raise ValueError(f"Incomplete entity alias on line {line_number}")
            table = lexicon.sections[family]
            key = _normalize(alias)
            if key in table and table[key] != canonical:
                raise ValueError(f"Conflicting entity alias on line {line_number}: {alias}")
            table[key] = canonical
            # A canonical ID can always be used directly, even if the file only
            # lists natural-language surface forms for it.
            table.setdefault(_normalize(canonical), canonical)
        return lexicon

    def resolve(self, family: str, phrase: str) -> str | None:
        """Resolve ``phrase`` within an entity family to a canonical ID."""
        return self.sections.get(family.upper(), {}).get(_normalize(phrase))

    def resolve_week(self, phrase: str) -> str | None:
        return self.resolve("WEEK", phrase)

    def resolve_chapter(self, phrase: str) -> str | None:
        return self.resolve("CHAPTER", phrase)

    def resolve_topic(self, phrase: str) -> str | None:
        return self.resolve("TOPIC", phrase)

    def resolve_lo(self, phrase: str) -> str | None:
        return self.resolve("LO", phrase)

    def resolve_assignment_part(self, phrase: str) -> str | None:
        return self.resolve("ASSIGNMENT_PART", phrase)

    def resolve_resource_topic(self, phrase: str) -> str | None:
        return self.resolve("RESOURCE_TOPIC", phrase)

    def resolve_rule(self, phrase: str) -> str | None:
        return self.resolve("RULE", phrase)
