"""Small immutable constituency-tree type."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Union


TreeChild = Union["Tree", str]


@dataclass(frozen=True)
class Tree:
    label: str
    children: tuple[TreeChild, ...] = ()

    def leaves(self) -> list[str]:
        result: list[str] = []
        for child in self.children:
            if isinstance(child, Tree):
                result.extend(child.leaves())
            else:
                result.append(child)
        return result

    def walk(self) -> Iterator["Tree"]:
        yield self
        for child in self.children:
            if isinstance(child, Tree):
                yield from child.walk()

    def first(self, label: str) -> "Tree | None":
        return next((node for node in self.walk() if node.label == label), None)

    def bracketed(self) -> str:
        if not self.children:
            return f"({self.label} ε)"
        content = " ".join(
            child.bracketed() if isinstance(child, Tree) else _escape_leaf(child)
            for child in self.children
        )
        return f"({self.label} {content})"


def _escape_leaf(value: str) -> str:
    if any(character.isspace() or character in "()" for character in value):
        return repr(value)
    return value

