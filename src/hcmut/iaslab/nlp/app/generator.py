"""Bounded sentence generation from the same CFG used by the parser.

Generation is required to demonstrate grammar coverage, not to invent a second
language definition.  Implement a deterministic breadth-first or fair
round-robin traversal, deduplicate sentences, cap token/state growth, and never
emit more than 10,000 lines.  ``GeneratorStats`` makes truncation visible rather
than silently pretending an infinite or very large grammar was exhausted.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .grammar import Grammar
from .tokenizer import detokenize


MAX_SENTENCES = 10_000
DEFAULT_MAX_STATES = 200_000


@dataclass(frozen=True)
class GeneratorStats:
    """Accounting information for one bounded expansion run."""

    requested: int
    produced: int
    explored_forms: int
    truncated: bool


class SentenceGenerator:
    """Generate terminal sentences while controlling combinatorial explosion."""

    def __init__(self, grammar: Grammar, max_states: int = DEFAULT_MAX_STATES) -> None:
        if max_states < 1:
            raise ValueError("max_states must be positive")
        self.grammar = grammar
        self.max_states = max_states

    def generate(self, limit: int = 1000, max_tokens: int = 32) -> tuple[list[str], GeneratorStats]:
        """Expand the leftmost nonterminal in breadth-first production order.

        A form is queued only once. Breadth-first traversal gives short
        derivations a chance before recursive rules grow them indefinitely.
        The state and token bounds make termination independent of the CFG.
        """
        if limit < 0 or max_tokens < 0:
            raise ValueError("limit and max_tokens must be nonnegative")
        if limit == 0:
            return [], GeneratorStats(limit, 0, 0, False)

        requested = limit
        target = min(limit, MAX_SENTENCES)
        minimum = _minimum_terminal_counts(self.grammar)
        start = (self.grammar.start,)
        if _minimum_length(start, self.grammar, minimum) > max_tokens:
            return [], GeneratorStats(requested, 0, 0, True)

        queue = deque([start])
        seen_forms = {start}
        seen_sentences: set[str] = set()
        sentences: list[str] = []
        explored = 0
        truncated = limit > MAX_SENTENCES

        while queue and len(sentences) < target:
            form = queue.popleft()
            explored += 1
            first_nonterminal = next(
                (index for index, symbol in enumerate(form)
                 if self.grammar.is_nonterminal(symbol)),
                None,
            )
            if first_nonterminal is None:
                sentence = detokenize(form)
                if sentence not in seen_sentences:
                    seen_sentences.add(sentence)
                    sentences.append(sentence)
                continue

            symbol = form[first_nonterminal]
            for rule in self.grammar.rules_for(symbol):
                child = form[:first_nonterminal] + rule.rhs + form[first_nonterminal + 1:]
                if child in seen_forms:
                    continue
                if _minimum_length(child, self.grammar, minimum) > max_tokens:
                    truncated = True
                    continue
                if len(seen_forms) >= self.max_states:
                    truncated = True
                    continue
                seen_forms.add(child)
                queue.append(child)

        # A full output count can still hide unexplored derivations; report it.
        truncated = truncated or bool(queue) or (len(sentences) >= target and target < requested)
        return sentences, GeneratorStats(requested, len(sentences), explored, truncated)


def _minimum_terminal_counts(grammar: Grammar) -> dict[str, float]:
    """Compute each symbol's shortest possible terminal yield by fixed point."""
    minimum = {symbol: float("inf") for symbol in grammar.nonterminals}
    changed = True
    while changed:
        changed = False
        for rule in grammar.rules:
            length = sum(minimum[s] if grammar.is_nonterminal(s) else 1 for s in rule.rhs)
            if length < minimum[rule.lhs]:
                minimum[rule.lhs] = length
                changed = True
    return minimum


def _minimum_length(form: tuple[str, ...], grammar: Grammar,
                    minimum: dict[str, float]) -> float:
    return sum(minimum[s] if grammar.is_nonterminal(s) else 1 for s in form)
