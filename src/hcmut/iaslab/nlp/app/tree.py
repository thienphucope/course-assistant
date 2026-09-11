"""Minimal immutable parse-tree data model shared by parser and semantics.

The parser produces ``Tree`` objects; the semantic interpreter consumes them.
Keeping the tree independent of the parsing algorithm makes it possible to
replace Earley with CYK, chart parsing, or an external parser without changing
downstream code.  The helpers here are intentionally complete infrastructure,
not assignment-specific grammar logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Union


TreeChild = Union["Tree", str]


@dataclass(frozen=True)
class Tree:
    """A constituency node whose children are nested nodes or terminal text."""

    label: str
    children: tuple[TreeChild, ...] = ()

    def leaves(self) -> list[str]:
        """Return terminal tokens from left to right."""
        values: list[str] = []
        for child in self.children:
            values.extend(child.leaves() if isinstance(child, Tree) else [child])
        return values

    def walk(self) -> Iterator["Tree"]:
        """Yield this node and then all descendants in pre-order."""
        yield self
        for child in self.children:
            if isinstance(child, Tree):
                yield from child.walk()

    def first(self, label: str) -> "Tree | None":
        """Return the first node with ``label``, or ``None`` when absent."""
        return next((node for node in self.walk() if node.label == label), None)

    def bracketed(self) -> str:
        """Serialize to the bracketed format required by ``parse-results.txt``."""
        if not self.children:
            return f"({self.label} ε)"
        body = " ".join(
            child.bracketed() if isinstance(child, Tree) else _escape_leaf(child)
            for child in self.children
        )
        return f"({self.label} {body})"


def _escape_leaf(value: str) -> str:
    return repr(value) if any(char.isspace() or char in "()" for char in value) else value
