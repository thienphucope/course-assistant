"""CFG representation and loader used by both parsing and generation.

``Grammar`` is the single source of syntactic truth: the parser recognizes its
rules and the generator expands those same rules.  Implement validation for the
start symbol, undefined non-terminals, malformed alternatives, epsilon rules,
and quoted terminals.  Do not place course facts here; those belong in the KB.
Keeping the file format human-editable makes new intents and paraphrases easy to
add without rewriting algorithms.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    """One production ``lhs -> rhs``; an empty ``rhs`` represents epsilon."""

    lhs: str
    rhs: tuple[str, ...]

    def display(self) -> str:
        return f"{self.lhs} -> {' '.join(self.rhs) if self.rhs else 'ε'}"


class GrammarError(ValueError):
    """Raised when a grammar cannot be parsed or violates its invariants."""


class Grammar:
    """Indexed, immutable-enough view of all CFG productions."""

    def __init__(self, start: str, rules: list[Rule], source_text: str = "") -> None:
        self.start = start
        self.rules = tuple(rules)
        self.source_text = source_text
        self.by_lhs = {
            lhs: tuple(rule for rule in self.rules if rule.lhs == lhs)
            for lhs in {rule.lhs for rule in self.rules}
        }
        self.nonterminals = frozenset(self.by_lhs)

    @classmethod
    def from_file(cls, path: str | Path) -> "Grammar":
        """Read UTF-8 CFG text and delegate to ``from_text``."""
        raise NotImplementedError("Implement the grammar file loader")

    @classmethod
    def from_text(cls, source: str) -> "Grammar":
        """Parse, validate, and index the project CFG format."""
        raise NotImplementedError("Implement CFG parsing and validation")

    def rules_for(self, nonterminal: str) -> tuple[Rule, ...]:
        return self.by_lhs.get(nonterminal, ())

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self.nonterminals
