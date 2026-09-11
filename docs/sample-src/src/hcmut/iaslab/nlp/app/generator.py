"""Bounded, deterministic sentence generation from the same CFG as the parser."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterator

from .grammar import Grammar
from .tokenizer import detokenize


@dataclass(frozen=True)
class GeneratorStats:
    requested: int
    produced: int
    explored_forms: int
    truncated: bool


class SentenceGenerator:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

    def generate(self, limit: int = 1000, max_tokens: int = 32) -> tuple[list[str], GeneratorStats]:
        if limit < 1 or limit > 10_000:
            raise ValueError("Số câu phải nằm trong khoảng 1..10000")
        branches = [rule.rhs[0] for rule in self.grammar.rules_for("QUESTION") if len(rule.rhs) == 1]
        if not branches:
            branches = [self.grammar.start]
        per_branch = max(1, (limit + len(branches) - 1) // len(branches))
        iterators = [self._terminal_sequences((branch,), per_branch * 3, max_tokens) for branch in branches]
        active = list(iterators)
        sentences: list[str] = []
        seen: set[str] = set()
        explored = 0

        while active and len(sentences) < limit:
            next_round: list[Iterator[tuple[str, ...]]] = []
            for iterator in active:
                try:
                    tokens = next(iterator)
                    explored += 1
                    variants = (tokens + ("?",), ("cho", "mình", "hỏi") + tokens + ("ạ", "?"))
                    for variant in variants:
                        sentence = detokenize(variant)
                        if sentence not in seen:
                            seen.add(sentence)
                            sentences.append(sentence)
                            if len(sentences) >= limit:
                                break
                    next_round.append(iterator)
                except StopIteration:
                    continue
                if len(sentences) >= limit:
                    break
            active = next_round
        stats = GeneratorStats(limit, len(sentences), explored, len(sentences) == limit and bool(active))
        return sentences, stats

    def _terminal_sequences(
        self, initial: tuple[str, ...], limit: int, max_tokens: int
    ) -> Iterator[tuple[str, ...]]:
        queue: deque[tuple[str, ...]] = deque([initial])
        visited: set[tuple[str, ...]] = {initial}
        yielded = 0
        state_cap = max(50_000, limit * 500)
        while queue and yielded < limit and len(visited) <= state_cap:
            form = queue.popleft()
            terminal_count = sum(not self.grammar.is_nonterminal(symbol) for symbol in form)
            if terminal_count > max_tokens:
                continue
            target_index = next(
                (index for index, symbol in enumerate(form) if self.grammar.is_nonterminal(symbol)), None
            )
            if target_index is None:
                yielded += 1
                yield form
                continue
            symbol = form[target_index]
            for rule in self.grammar.rules_for(symbol):
                expanded = form[:target_index] + rule.rhs + form[target_index + 1 :]
                if expanded not in visited:
                    visited.add(expanded)
                    queue.append(expanded)

