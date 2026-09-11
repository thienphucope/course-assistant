"""Syntactic-analysis stage and its stable output contract.

Implement a general CFG parser here (the sample uses Earley) rather than a list
of keyword checks.  ``parse`` must always return ``ParseResult``: accepted input
contains a full tree spanning every token, rejected input contains ``tree=None``.
Rule order should define deterministic tie-breaking when a sentence is
ambiguous.  Chart state internals may change without affecting later stages.
"""

from __future__ import annotations

from dataclasses import dataclass

from .grammar import Grammar
from .tree import Tree


@dataclass(frozen=True)
class ParseResult:
    """Observable result of parsing exactly one sentence."""

    sentence: str
    tokens: tuple[str, ...]
    tree: Tree | None

    @property
    def accepted(self) -> bool:
        return self.tree is not None

    def output(self) -> str:
        return self.tree.bracketed() if self.tree else "()"


class EarleyParser:
    """General chart parser supporting recursion, ambiguity, and epsilon rules."""

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

    def parse(self, sentence: str) -> ParseResult:
        """Run predictor, scanner, and completer until a full parse is found."""
        raise NotImplementedError("Implement the Earley chart algorithm")
