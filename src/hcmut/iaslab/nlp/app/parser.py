"""Syntactic-analysis stage and its stable output contract.

Implement a general CFG parser here (the sample uses Earley) rather than a list
of keyword checks.  ``parse`` must always return ``ParseResult``: accepted input
contains a full tree spanning every token, rejected input contains ``tree=None``.
Rule order should define deterministic tie-breaking when a sentence is
ambiguous.  Chart state internals may change without affecting later stages.
"""

from __future__ import annotations

from dataclasses import dataclass

from .grammar import Grammar, Rule
from .tokenizer import tokenize
from .tree import Tree, TreeChild


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
        tokens = tuple(tokenize(sentence))
        # An artificial start rule makes acceptance require one complete S tree
        # from position 0 through the final input token.
        rules = (*self.grammar.rules, Rule("__ROOT__", (self.grammar.start,)))
        root_index = len(rules) - 1
        rule_indices: dict[str, list[int]] = {}
        for index, rule in enumerate(self.grammar.rules):
            rule_indices.setdefault(rule.lhs, []).append(index)

        # A key identifies an Earley item. Its value records the first children
        # found for that item, preserving grammar rule order on ambiguity.
        Key = tuple[int, int, int]  # (rule index, dot, origin)
        chart: list[dict[Key, tuple[TreeChild, ...]]] = [
            {} for _ in range(len(tokens) + 1)
        ]
        chart[0][(root_index, 0, 0)] = ()

        for position in range(len(chart)):
            # Revisit a chart column until stable. This also handles epsilon:
            # a completed nullable rule may precede a newly predicted waiter.
            changed = True
            while changed:
                changed = False
                for (rule_index, dot, origin), children in list(chart[position].items()):
                    rule = rules[rule_index]
                    if dot == len(rule.rhs):
                        subtree = Tree(rule.lhs, children)
                        for (parent_index, parent_dot, parent_origin), parent_children in list(
                            chart[origin].items()
                        ):
                            parent = rules[parent_index]
                            if (
                                parent_dot < len(parent.rhs)
                                and parent.rhs[parent_dot] == rule.lhs
                            ):
                                key = (parent_index, parent_dot + 1, parent_origin)
                                if key not in chart[position]:
                                    chart[position][key] = parent_children + (subtree,)
                                    changed = True
                    else:
                        symbol = rule.rhs[dot]
                        if self.grammar.is_nonterminal(symbol):
                            for predicted_index in rule_indices[symbol]:
                                key = (predicted_index, 0, position)
                                if key not in chart[position]:
                                    chart[position][key] = ()
                                    changed = True
                        elif position < len(tokens) and symbol == tokens[position]:
                            key = (rule_index, dot + 1, origin)
                            chart[position + 1].setdefault(key, children + (symbol,))

        accepted = chart[-1].get((root_index, 1, 0))
        tree = accepted[0] if accepted and isinstance(accepted[0], Tree) else None
        return ParseResult(sentence=sentence, tokens=tokens, tree=tree)
