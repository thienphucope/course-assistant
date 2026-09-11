"""Bounded sentence generation from the same CFG used by the parser.

Generation is required to demonstrate grammar coverage, not to invent a second
language definition.  Implement a deterministic breadth-first or fair
round-robin traversal, deduplicate sentences, cap token/state growth, and never
emit more than 10,000 lines.  ``GeneratorStats`` makes truncation visible rather
than silently pretending an infinite or very large grammar was exhausted.
"""

from __future__ import annotations

from dataclasses import dataclass

from .grammar import Grammar


@dataclass(frozen=True)
class GeneratorStats:
    """Accounting information for one bounded expansion run."""

    requested: int
    produced: int
    explored_forms: int
    truncated: bool


class SentenceGenerator:
    """Generate terminal sentences while controlling combinatorial explosion."""

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

    def generate(self, limit: int = 1000, max_tokens: int = 32) -> tuple[list[str], GeneratorStats]:
        """Return unique sentences and statistics under explicit safety bounds."""
        raise NotImplementedError("Implement bounded, balanced CFG expansion")
