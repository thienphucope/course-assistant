"""Bounded, deterministic and branch-balanced CFG sentence generator."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .grammar import Grammar, Rule
from .tokenizer import detokenize, tokenize


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

        # The course grammar permits both bare and polite question endings.
        # Canonicalize their surface form without inventing tokens for generic CFGs.
        question_style = (
            all(rule.rhs and rule.rhs[-1] == "SUFFIX"
                for rule in self.grammar.rules_for(self.grammar.start))
            and Rule("SUFFIX", ("END_MARK",)) in self.grammar.rules
            and Rule("SUFFIX", ("POLITE", "END_MARK")) in self.grammar.rules
            and Rule("END_MARK", ("?",)) in self.grammar.rules
        )

        def render(form, branch=None):
            tokens = list(form)
            if question_style:
                if tokens and tokens[-1] in {"?", "!", "."}:
                    tokens.pop()
                tokens.append("?")
                acronyms = {"nlp", "btl", "btl01", "cfg", "pcfg", "kb", "llm", "rag", "llm/rag"}
                tokens = [token.upper() if token in acronyms or
                          (token == "ai" and branch == "Q_RULE") else token for token in tokens]
            sentence = detokenize(tokens)
            return sentence[:1].upper() + sentence[1:]

        # Discover intent branches and seed one derivation queue per Q_* branch.
        branches = sorted({rule.rhs[0] for rule in self.grammar.rules_for("QUESTION")
                           if len(rule.rhs) == 1 and rule.rhs[0].startswith("Q_")})
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
        per_branch, extra = divmod(requested, len(seeds))
        global_state_cap = 250_000
        queues = []
        for index, (branch, seed) in enumerate(seeds):
            target = per_branch + int(index < extra)
            queues.append((branch, deque([seed]), set([seed]), 0, target))

        while queues and len(results) < requested and explored < global_state_cap:
            progressed = False
            next_queues = []
            for branch, queue, seen_forms, produced_here, target in queues:
                if len(results) >= requested:
                    next_queues.append((branch, queue, seen_forms, produced_here, target))
                    continue
                if not queue or produced_here >= target:
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
                    sentence = render(form, branch)
                    if sentence and sentence not in unique and len(tokenize(sentence)) <= max_tokens:
                        unique.add(sentence)
                        results.append(sentence)
                        produced_here += 1
                    next_queues.append((branch, queue, seen_forms, produced_here, target))
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
                next_queues.append((branch, queue, seen_forms, produced_here, target))
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
                    sentence = render(form)
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
