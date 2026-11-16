"""Earley chart parser producing a labeled constituency tree."""

from __future__ import annotations

from dataclasses import dataclass

from .grammar import Grammar, Rule
from .tokenizer import tokenize
from .tree import Tree


@dataclass(frozen=True)
class ParseResult:
    sentence: str
    tokens: tuple[str, ...]
    tree: Tree | None

    @property
    def accepted(self) -> bool:
        return self.tree is not None

    def output(self) -> str:
        return self.tree.bracketed() if self.tree else "()"


@dataclass(frozen=True)
class _State:
    rule: Rule
    dot: int
    origin: int
    children: tuple[Tree | str, ...] = ()

    @property
    def complete(self) -> bool:
        return self.dot >= len(self.rule.rhs)

    @property
    def next_symbol(self) -> str | None:
        return None if self.complete else self.rule.rhs[self.dot]


class EarleyParser:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

    def parse(self, sentence: str) -> ParseResult:
        trees = self.parse_trees(sentence, limit=1)
        return ParseResult(sentence, tuple(tokenize(sentence)), trees[0] if trees else None)

    def parse_trees(self, sentence: str, limit: int = 2) -> tuple[Tree, ...]:
        """Return up to ``limit`` distinct trees (two suffice to detect ambiguity).

        Bound derivations per chart item so nullable/recursive cycles terminate.
        A predictor also consumes already-completed nullable items: their agenda
        entries may have run before the new waiting item was discovered.
        """
        if limit < 1:
            raise ValueError("limit must be positive")
        tokens = tuple(tokenize(sentence))
        n = len(tokens)
        chart: list[list[_State]] = [[] for _ in range(n + 1)]
        seen: list[set[_State]] = [set() for _ in range(n + 1)]
        counts: list[dict[tuple[Rule, int, int], int]] = [{} for _ in range(n + 1)]
        nullable: list[dict[str, list[_State]]] = [{} for _ in range(n + 1)]

        def add(position: int, state: _State) -> None:
            key = (state.rule, state.dot, state.origin)
            if state not in seen[position] and counts[position].get(key, 0) < limit:
                seen[position].add(state)
                counts[position][key] = counts[position].get(key, 0) + 1
                chart[position].append(state)
                if state.complete and state.origin == position:
                    nullable[position].setdefault(state.rule.lhs, []).append(state)

        # Synthetic start production avoids special cases for the grammar start.
        augmented = Rule("@START", (self.grammar.start,))
        add(0, _State(augmented, 0, 0))

        for i in range(n + 1):
            cursor = 0
            while cursor < len(chart[i]):
                state = chart[i][cursor]
                cursor += 1
                symbol = state.next_symbol

                if symbol is not None and self.grammar.is_nonterminal(symbol):
                    # Predictor
                    for rule in self.grammar.rules_for(symbol):
                        candidate = _State(rule, 0, i)
                        add(i, candidate)
                    for completed in list(nullable[i].get(symbol, ())):
                        add(i, _State(state.rule, state.dot + 1, state.origin,
                                      state.children + (Tree(symbol, completed.children),)))

                elif state.complete:
                    # Completer. Keep rule-order/agenda order deterministic.
                    node = Tree(state.rule.lhs, state.children)
                    for waiting in list(chart[state.origin]):
                        if waiting.next_symbol == state.rule.lhs:
                            candidate = _State(
                                waiting.rule,
                                waiting.dot + 1,
                                waiting.origin,
                                waiting.children + (node,),
                            )
                            add(i, candidate)

                elif i < n and symbol == tokens[i]:
                    # Scanner
                    candidate = _State(
                        state.rule,
                        state.dot + 1,
                        state.origin,
                        state.children + (tokens[i],),
                    )
                    add(i + 1, candidate)

        # Require a completed augmented item at the final input position.
        trees = []
        for state in chart[n]:
            if state.rule == augmented and state.complete and state.origin == 0:
                child = state.children[0]
                if isinstance(child, Tree) and child.leaves() == list(tokens):
                    if child not in trees:
                        trees.append(child)
        return tuple(trees[:limit])
