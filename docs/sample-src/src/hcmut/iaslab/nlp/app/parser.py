"""An Earley chart parser that returns the first deterministic parse tree."""

from __future__ import annotations

from dataclasses import dataclass

from .grammar import Grammar
from .tokenizer import tokenize
from .tree import Tree, TreeChild


@dataclass(frozen=True)
class State:
    lhs: str
    rhs: tuple[str, ...]
    dot: int
    start: int
    end: int
    children: tuple[TreeChild, ...] = ()

    @property
    def complete(self) -> bool:
        return self.dot == len(self.rhs)

    @property
    def next_symbol(self) -> str | None:
        return None if self.complete else self.rhs[self.dot]

    @property
    def core(self) -> tuple[str, tuple[str, ...], int, int, int]:
        return self.lhs, self.rhs, self.dot, self.start, self.end

    def advance(self, child: TreeChild, end: int) -> "State":
        return State(self.lhs, self.rhs, self.dot + 1, self.start, end, self.children + (child,))

    def as_tree(self) -> Tree:
        if not self.complete:
            raise ValueError("Không thể tạo cây từ Earley state chưa hoàn tất")
        return Tree(self.lhs, self.children)


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


class EarleyParser:
    """General CFG parser with deterministic rule-order tie breaking."""

    AUGMENTED_START = "__START__"

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

    def parse(self, sentence: str) -> ParseResult:
        tokens = tuple(tokenize(sentence))
        chart: list[dict[tuple[object, ...], State]] = [dict() for _ in range(len(tokens) + 1)]

        def add(position: int, state: State) -> bool:
            if state.core in chart[position]:
                return False
            chart[position][state.core] = state
            return True

        start_state = State(self.AUGMENTED_START, (self.grammar.start,), 0, 0, 0)
        add(0, start_state)

        for position in range(len(chart)):
            agenda = list(chart[position].values())
            cursor = 0
            while cursor < len(agenda):
                state = agenda[cursor]
                cursor += 1

                if state.complete:
                    completed_tree = state.as_tree()
                    for previous in list(chart[state.start].values()):
                        if previous.next_symbol == state.lhs:
                            advanced = previous.advance(completed_tree, position)
                            if add(position, advanced):
                                agenda.append(advanced)
                    continue

                symbol = state.next_symbol
                if symbol is not None and self.grammar.is_nonterminal(symbol):
                    for rule in self.grammar.rules_for(symbol):
                        predicted = State(rule.lhs, rule.rhs, 0, position, position)
                        if add(position, predicted):
                            agenda.append(predicted)
                    continue

                if position < len(tokens) and symbol == tokens[position]:
                    add(position + 1, state.advance(tokens[position], position + 1))

        final_core = (self.AUGMENTED_START, (self.grammar.start,), 1, 0, len(tokens))
        final = chart[-1].get(final_core)
        tree = None
        if final and final.children and isinstance(final.children[0], Tree):
            tree = final.children[0]
        return ParseResult(sentence=sentence, tokens=tokens, tree=tree)

