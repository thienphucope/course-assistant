"""CFG representation and validated loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import json


@dataclass(frozen=True)
class Rule:
    lhs: str
    rhs: tuple[str, ...]

    def display(self) -> str:
        return f"{self.lhs} -> {' '.join(self.rhs) if self.rhs else 'ε'}"


class GrammarError(ValueError):
    """Raised for malformed or inconsistent CFG input."""


_TOKEN = re.compile(r'"((?:[^"\\]|\\.)*)"|([A-Za-z_][A-Za-z0-9_]*)')


class Grammar:
    def __init__(self, start: str, rules: list[Rule], source_text: str = "") -> None:
        self.start = start
        self.rules = tuple(rules)
        self.source_text = source_text
        self.by_lhs = {
            lhs: tuple(rule for rule in self.rules if rule.lhs == lhs)
            for lhs in dict.fromkeys(rule.lhs for rule in self.rules)
        }
        self.nonterminals = frozenset(self.by_lhs)

    @classmethod
    def from_file(cls, path: str | Path) -> "Grammar":
        try:
            source = Path(path).read_text(encoding="utf-8")
        except OSError as exc:
            raise GrammarError(f"Cannot read grammar file: {path}") from exc
        return cls.from_text(source)

    @classmethod
    def from_text(cls, source: str) -> "Grammar":
        if not isinstance(source, str):
            raise TypeError("source must be str")
        start = None
        rules: list[Rule] = []
        for line_no, raw in enumerate(source.splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("%start"):
                parts = line.split()
                if len(parts) != 2 or not re.fullmatch(r"[A-Za-z_]\w*", parts[1]):
                    raise GrammarError(f"Line {line_no}: malformed %start")
                if start is not None:
                    raise GrammarError(f"Line {line_no}: duplicate %start")
                start = parts[1]
                continue
            if "->" not in line:
                raise GrammarError(f"Line {line_no}: expected '->'")
            lhs, rhs_text = (part.strip() for part in line.split("->", 1))
            if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", lhs):
                raise GrammarError(f"Line {line_no}: invalid non-terminal {lhs!r}")
            alternatives = []
            current = ""
            quoted = False
            escaped = False
            for ch in rhs_text:
                if ch == '"' and not escaped:
                    quoted = not quoted
                if ch == "|" and not quoted:
                    alternatives.append(current.strip())
                    current = ""
                else:
                    current += ch
                escaped = (ch == "\\") and not escaped
                if ch != "\\":
                    escaped = False
            if quoted:
                raise GrammarError(f"Line {line_no}: unterminated terminal quote")
            alternatives.append(current.strip())
            for alt in alternatives:
                if not alt:
                    rules.append(Rule(lhs, ()))
                    continue
                pos = 0
                symbols = []
                while pos < len(alt):
                    while pos < len(alt) and alt[pos].isspace():
                        pos += 1
                    if pos >= len(alt):
                        break
                    match = _TOKEN.match(alt, pos)
                    if not match:
                        raise GrammarError(
                            f"Line {line_no}: invalid symbol near {alt[pos:]!r}"
                        )
                    if match.group(1) is not None:
                        symbols.append(json.loads('"' + match.group(1) + '"'))
                    else:
                        symbols.append(match.group(2))
                    pos = match.end()
                rules.append(Rule(lhs, tuple(symbols)))
        if not start:
            raise GrammarError("Missing %start declaration")
        defined = {rule.lhs for rule in rules}
        if start not in defined:
            raise GrammarError(f"Start symbol {start!r} is not defined")
        for rule in rules:
            for symbol in rule.rhs:
                if re.fullmatch(r"[A-Z_][A-Z0-9_]*", symbol) and symbol not in defined:
                    raise GrammarError(
                        f"Undefined non-terminal {symbol!r} in {rule.display()}"
                    )
        return cls(start, rules, source)

    def rules_for(self, nonterminal: str) -> tuple[Rule, ...]:
        return self.by_lhs.get(nonterminal, ())

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self.nonterminals
