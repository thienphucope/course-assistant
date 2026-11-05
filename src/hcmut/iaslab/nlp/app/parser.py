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
        tokens = tuple(tokenize(sentence))
        n = len(tokens)
        chart: list[list[_State]] = [[] for _ in range(n + 1)]
        seen: list[set[_State]] = [set() for _ in range(n + 1)]

        # Synthetic start production avoids special cases for the grammar start.
        augmented = Rule("@START", (self.grammar.start,))
        chart[0].append(_State(augmented, 0, 0))
        seen[0].add(chart[0][0])

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
                        if candidate not in seen[i]:
                            seen[i].add(candidate)
                            chart[i].append(candidate)

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
                            if candidate not in seen[i]:
                                seen[i].add(candidate)
                                chart[i].append(candidate)

                elif i < n and symbol == tokens[i]:
                    # Scanner
                    candidate = _State(
                        state.rule,
                        state.dot + 1,
                        state.origin,
                        state.children + (tokens[i],),
                    )
                    if candidate not in seen[i + 1]:
                        seen[i + 1].add(candidate)
                        chart[i + 1].append(candidate)

        # Require a completed augmented item at the final input position.
        for state in chart[n]:
            if state.rule == augmented and state.complete and state.origin == 0:
                child = state.children[0]
                if isinstance(child, Tree) and child.leaves() == list(tokens):
                    return ParseResult(sentence, tokens, child)
        return ParseResult(sentence, tokens, None)
