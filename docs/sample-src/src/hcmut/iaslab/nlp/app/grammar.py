"""Read the human-editable CFG used by both parser and generator."""

from __future__ import annotations

import shlex
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    lhs: str
    rhs: tuple[str, ...]

    def display(self) -> str:
        body = " ".join(self.rhs) if self.rhs else "ε"
        return f"{self.lhs} -> {body}"


class GrammarError(ValueError):
    pass


class Grammar:
    def __init__(self, start: str, rules: list[Rule], source_text: str = "") -> None:
        self.start = start
        self.rules = tuple(rules)
        self.source_text = source_text
        grouped: dict[str, list[Rule]] = defaultdict(list)
        for rule in rules:
            grouped[rule.lhs].append(rule)
        self.by_lhs = {lhs: tuple(items) for lhs, items in grouped.items()}
        self.nonterminals = frozenset(self.by_lhs)
        if start not in self.nonterminals:
            raise GrammarError(f"Start symbol {start!r} không có luật sinh")
        undefined = {
            symbol
            for rule in rules
            for symbol in rule.rhs
            if _looks_like_nonterminal(symbol) and symbol not in self.nonterminals
        }
        if undefined:
            names = ", ".join(sorted(undefined))
            raise GrammarError(f"Non-terminal chưa được định nghĩa: {names}")

    @classmethod
    def from_file(cls, path: str | Path) -> "Grammar":
        source = Path(path).read_text(encoding="utf-8")
        return cls.from_text(source)

    @classmethod
    def from_text(cls, source: str) -> "Grammar":
        start = "S"
        raw_rules: list[tuple[str, str, int]] = []
        for line_number, raw in enumerate(source.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("%start"):
                parts = line.split()
                if len(parts) != 2:
                    raise GrammarError(f"Dòng {line_number}: khai báo %start không hợp lệ")
                start = parts[1]
                continue
            if "->" not in line:
                raise GrammarError(f"Dòng {line_number}: thiếu ký hiệu ->")
            lhs, rhs_text = line.split("->", 1)
            lhs = lhs.strip()
            if not _looks_like_nonterminal(lhs):
                raise GrammarError(f"Dòng {line_number}: vế trái phải là NON_TERMINAL")
            for alternative in rhs_text.split("|"):
                raw_rules.append((lhs, alternative.strip(), line_number))

        rules: list[Rule] = []
        for lhs, rhs_text, line_number in raw_rules:
            if not rhs_text or rhs_text == "ε":
                rhs: tuple[str, ...] = ()
            else:
                try:
                    rhs = tuple(shlex.split(rhs_text, comments=False, posix=True))
                except ValueError as exc:
                    raise GrammarError(f"Dòng {line_number}: {exc}") from exc
            rules.append(Rule(lhs, rhs))
        if not rules:
            raise GrammarError("Grammar không có luật nào")
        return cls(start=start, rules=rules, source_text=source)

    def rules_for(self, nonterminal: str) -> tuple[Rule, ...]:
        return self.by_lhs.get(nonterminal, ())

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self.nonterminals


def _looks_like_nonterminal(symbol: str) -> bool:
    return bool(symbol) and symbol[0].isalpha() and symbol.upper() == symbol and symbol.replace("_", "").isalnum()
