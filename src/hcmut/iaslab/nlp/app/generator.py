"""Bounded, deterministic and branch-balanced CFG sentence generator."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

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

    def generate(
        self, limit: int = 1000, max_tokens: int = 32
    ) -> tuple[list[str], GeneratorStats]:
        if limit < 0 or max_tokens < 1:
            raise ValueError(
                "limit must be non-negative and max_tokens must be positive"
            )
        requested = min(int(limit), 10_000)
        if requested == 0:
            return [], GeneratorStats(int(limit), 0, 0, int(limit) > 0)

        # Discover intent branches and seed one derivation queue per Q_* branch.
        branches = sorted(nt for nt in self.grammar.nonterminals if nt.startswith("Q_"))
        start_rules = self.grammar.rules_for(self.grammar.start)
        seeds: list[tuple[str, tuple[str, ...]]] = []
        for branch in branches:
            for rule in start_rules:
                if "QUESTION" in rule.rhs:
                    rhs = tuple(branch if x == "QUESTION" else x for x in rule.rhs)
                    seeds.append((branch, rhs))
        if not seeds:
            seeds = [(self.grammar.start, (self.grammar.start,))]

        results: list[str] = []
        unique: set[str] = set()
        explored = 0
        truncated = int(limit) > 10_000
        # Round-robin one branch at a time to prevent early branches monopolizing output.
        per_branch_target = max(
            1, (requested + max(1, len(seeds)) - 1) // max(1, len(seeds))
        )
        global_state_cap = 250_000
        queues = []
        for branch, seed in seeds:
            queues.append((branch, deque([seed]), set([seed]), 0))

        while queues and len(results) < requested and explored < global_state_cap:
            progressed = False
            next_queues = []
            for branch, queue, seen_forms, produced_here in queues:
                if len(results) >= requested:
                    next_queues.append((branch, queue, seen_forms, produced_here))
                    continue
                if not queue or produced_here >= per_branch_target:
                    if queue:
                        truncated = True
                    continue
                form = queue.popleft()
                explored += 1
                progressed = True

                # Expand the leftmost non-terminal, preserving grammar rule order.
                index = next(
                    (
                        i
                        for i, sym in enumerate(form)
                        if self.grammar.is_nonterminal(sym)
                    ),
                    None,
                )
                if index is None:
                    sentence = detokenize(list(form))
                    if sentence and sentence not in unique:
                        unique.add(sentence)
                        results.append(sentence)
                        produced_here += 1
                    next_queues.append((branch, queue, seen_forms, produced_here))
                    continue

                symbol = form[index]
                for rule in self.grammar.rules_for(symbol):
                    expanded = form[:index] + rule.rhs + form[index + 1 :]
                    terminal_count = sum(
                        not self.grammar.is_nonterminal(x) for x in expanded
                    )
                    if terminal_count > max_tokens:
                        truncated = True
                        continue
                    if expanded not in seen_forms:
                        seen_forms.add(expanded)
                        queue.append(expanded)
                next_queues.append((branch, queue, seen_forms, produced_here))
            queues = next_queues
            if not progressed:
                break

        if queues or explored >= global_state_cap or len(results) >= requested:
            truncated = truncated or bool(queues)
        # A grammar without Q_* branches is handled by a general start-symbol expansion.
        if not branches and not results:
            queue = deque([(self.grammar.start,)])
            seen = {(self.grammar.start,)}
            while queue and len(results) < requested and explored < global_state_cap:
                form = queue.popleft()
                explored += 1
                index = next(
                    (i for i, x in enumerate(form) if self.grammar.is_nonterminal(x)),
                    None,
                )
                if index is None:
                    sentence = detokenize(list(form))
                    if sentence and sentence not in unique:
                        unique.add(sentence)
                        results.append(sentence)
                    continue
                for rule in self.grammar.rules_for(form[index]):
                    nxt = form[:index] + rule.rhs + form[index + 1 :]
                    if (
                        sum(not self.grammar.is_nonterminal(x) for x in nxt)
                        <= max_tokens
                        and nxt not in seen
                    ):
                        seen.add(nxt)
                        queue.append(nxt)
        return results[:requested], GeneratorStats(
            int(limit), len(results[:requested]), explored, truncated
        )
