"""Deterministic Unicode-aware tokenization for Vietnamese questions."""

from __future__ import annotations

import re
import unicodedata


TOKEN_RE = re.compile(r"[^\W_]+(?:[./-][^\W_]+)*|[?!.:,;]", re.UNICODE)
LO_RE = re.compile(r"\bl\s*\.\s*o\s*\.\s*(\d+(?:\s*\.\s*\d+)?)", re.IGNORECASE)
SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize casing, Unicode and common LO spellings without losing accents."""

    normalized = unicodedata.normalize("NFC", text).strip().lower()
    normalized = (
        normalized.replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("–", "-")
        .replace("—", "-")
    )
    normalized = LO_RE.sub(lambda match: "lo" + re.sub(r"\s+", "", match.group(1)), normalized)
    return SPACE_RE.sub(" ", normalized)


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(normalize_text(text))


def normalized_phrase(text: str) -> str:
    return " ".join(token for token in tokenize(text) if token not in {"?", "!", ".", ",", ":", ";"})


def detokenize(tokens: list[str] | tuple[str, ...]) -> str:
    if not tokens:
        return ""
    text = " ".join(tokens)
    text = re.sub(r"\s+([?!.:,;])", r"\1", text)
    return text[0].upper() + text[1:]

