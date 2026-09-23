"""CFG representation and loader used by both parsing and generation.

``Grammar`` is the single source of syntactic truth: the parser recognizes its
rules and the generator expands those same rules.  Implement validation for the
start symbol, undefined non-terminals, malformed alternatives, epsilon rules,
and quoted terminals.  Do not place course facts here; those belong in the KB.
Keeping the file format human-editable makes new intents and paraphrases easy to
add without rewriting algorithms.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re

from .tokenizer import tokenize


_NONTERMINAL = re.compile(r"[A-Z][A-Z0-9_]*\Z")


@dataclass(frozen=True)
class Rule:
    """One production ``lhs -> rhs``; an empty ``rhs`` represents epsilon."""

    lhs: str
    rhs: tuple[str, ...]

    def display(self) -> str:
        return f"{self.lhs} -> {' '.join(self.rhs) if self.rhs else 'ε'}"


class GrammarError(ValueError):
    """Raised when a grammar cannot be parsed or violates its invariants."""


class Grammar:
    """Indexed, immutable-enough view of all CFG productions."""

    def __init__(self, start: str, rules: list[Rule], source_text: str = "") -> None:
        self.start = start
        self.rules = tuple(rules)
        self.source_text = source_text
        self.by_lhs = {
            lhs: tuple(rule for rule in self.rules if rule.lhs == lhs)
            for lhs in {rule.lhs for rule in self.rules}
        }
        self.nonterminals = frozenset(self.by_lhs)

    @classmethod
    def from_file(cls, path: str | Path) -> "Grammar":
        """Read UTF-8 CFG text and delegate to ``from_text``."""
        return cls.from_text(Path(path).read_text(encoding="utf-8-sig"))

    @classmethod
    def from_text(cls, source: str) -> "Grammar":
        """Parse, validate, and index the project CFG format."""
        start: str | None = None
        rules: list[Rule] = []

        for line_number, raw_line in enumerate(source.splitlines(), 1):
            line = _without_comment(raw_line).strip()
            if not line:
                continue
            if line.startswith("%start"):
                pieces = line.split()
                if len(pieces) != 2 or not _NONTERMINAL.fullmatch(pieces[1]):
                    raise GrammarError(f"Line {line_number}: expected '%start SYMBOL'")
                if start is not None:
                    raise GrammarError(f"Line {line_number}: duplicate %start declaration")
                start = pieces[1]
                continue
            if "->" not in line:
                raise GrammarError(f"Line {line_number}: expected a production with '->'")
            lhs_text, rhs_text = line.split("->", 1)
            lhs = lhs_text.strip()
            if not _NONTERMINAL.fullmatch(lhs):
                raise GrammarError(f"Line {line_number}: invalid nonterminal {lhs!r}")

            alternatives: list[list[str]] = [[]]
            for kind, value in _lex_rhs(rhs_text, line_number):
                if kind == "separator":
                    alternatives.append([])
                elif kind == "terminal":
                    if tokenize(value) != [value]:
                        raise GrammarError(
                            f"Line {line_number}: terminal {value!r} must be one canonical token"
                        )
                    alternatives[-1].append(value)
                elif value == "ε":
                    if alternatives[-1]:
                        raise GrammarError(f"Line {line_number}: epsilon must stand alone")
                    alternatives[-1].append(value)
                elif _NONTERMINAL.fullmatch(value):
                    alternatives[-1].append(value)
                else:
                    raise GrammarError(
                        f"Line {line_number}: quote terminal {value!r} or use a nonterminal"
                    )
            for symbols in alternatives:
                if "ε" in symbols:
                    if len(symbols) != 1:
                        raise GrammarError(f"Line {line_number}: epsilon must stand alone")
                    symbols = []
                rules.append(Rule(lhs, tuple(symbols)))

        if start is None:
            raise GrammarError("Missing %start declaration")
        defined = {rule.lhs for rule in rules}
        if start not in defined:
            raise GrammarError(f"Start symbol {start!r} has no production")
        for rule in rules:
            for symbol in rule.rhs:
                if _NONTERMINAL.fullmatch(symbol) and symbol not in defined:
                    raise GrammarError(f"Undefined nonterminal {symbol!r} in {rule.display()}")
        return cls(start, rules, source)

    def rules_for(self, nonterminal: str) -> tuple[Rule, ...]:
        return self.by_lhs.get(nonterminal, ())

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self.nonterminals


def _without_comment(line: str) -> str:
    """Remove a # comment, leaving hashes inside quoted terminals intact."""
    quoted = escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
        elif char == "\\" and quoted:
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif char == "#" and not quoted:
            return line[:index]
    return line


def _lex_rhs(rhs: str, line_number: int):
    """Yield (kind, value) pairs without losing quote information."""
    decoder = json.JSONDecoder()
    index = 0
    while index < len(rhs):
        char = rhs[index]
        if char.isspace():
            index += 1
        elif char == "|":
            yield "separator", char
            index += 1
        elif char == '"':
            try:
                value, consumed = decoder.raw_decode(rhs[index:])
            except json.JSONDecodeError as exc:
                raise GrammarError(f"Line {line_number}: malformed quoted terminal") from exc
            if not isinstance(value, str):
                raise GrammarError(f"Line {line_number}: expected a quoted terminal")
            yield "terminal", value
            index += consumed
            if index < len(rhs) and not (rhs[index].isspace() or rhs[index] == "|"):
                raise GrammarError(f"Line {line_number}: missing space after quoted terminal")
        else:
            end = index
            while end < len(rhs) and not (rhs[end].isspace() or rhs[end] == "|"):
                end += 1
            yield "symbol", rhs[index:end]
            index = end
