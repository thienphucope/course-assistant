"""Deterministic Vietnamese-aware tokenizer shared by CFG and entity lookup."""

from __future__ import annotations

import re
import unicodedata

# Keep known compound/technical forms intact before punctuation is split.
_SPECIAL = re.compile(r"(?i)\bl\.o\.(\d+(?:\.\d+)*)\b")
_TOKEN_RE = re.compile(r"""(?ix)
    lo\d+(?:\.\d+)* |
    [\wÀ-ỹ]+(?:[-/.][\wÀ-ỹ]+)* |
    \d+(?:\.\d+)* |
    [?!.,:;]
    """)
_PUNCT = set("?!.,:;")


def normalize_text(text: str) -> str:
    """Apply NFC, lowercase, canonical technical spellings and whitespace."""
    if not isinstance(text, str):
        raise TypeError("text must be str")
    text = unicodedata.normalize("NFC", text).lower()
    text = _SPECIAL.sub(lambda m: "lo" + m.group(1), text)
    return " ".join(text.split())


def tokenize(text: str) -> list[str]:
    """Split text into grammar terminals, preserving compounds and punctuation."""
    normalized = normalize_text(text)
    return _TOKEN_RE.findall(normalized)


def normalized_phrase(text: str) -> str:
    """Canonical entity phrase; punctuation is discarded, words are retained."""
    return " ".join(token for token in tokenize(text) if token not in _PUNCT)


def detokenize(tokens: list[str] | tuple[str, ...]) -> str:
    """Join tokens with natural spacing around Vietnamese punctuation."""
    out = ""
    no_space_before = _PUNCT
    no_space_after = {"("}
    for raw in tokens:
        token = str(raw)
        if not token:
            continue
        if not out:
            out = token
        elif token in no_space_before or out.endswith("("):
            out += token
        else:
            out += " " + token
    return out
