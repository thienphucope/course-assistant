"""Text-normalization boundary between raw questions and the CFG parser.

Implement Unicode/case/spacing normalization here and nowhere else.  The
contract is that ``tokenize`` returns terminals using exactly the same spelling
as ``grammar.cfg``; ``detokenize`` is the inverse used by sentence generation.
Future upgrades such as typo handling or word segmentation should preserve
canonical IDs and remain deterministic so parser tests stay reproducible.
"""

from __future__ import annotations

import re
import unicodedata


# A period or slash inside an identifier stays attached (lo2.5, llm/rag).
# Sentence punctuation remains a token so an unexpected suffix cannot vanish.
_TOKEN = re.compile(r"\w+(?:[./]\w+)*|[^\w\s]", re.UNICODE)


def _canonical(text: str) -> str:
    value = unicodedata.normalize("NFC", text).casefold()
    # The supplied questions spell learning outcomes L.O.2.5, while the CFG
    # uses the compact terminal lo2.5. Both denote the same surface token.
    value = re.sub(r"\bl\.\s*o\.\s*(?=\d)", "lo", value)
    return value


def normalize_text(text: str) -> str:
    """Return canonical text before token splitting."""
    return " ".join(_TOKEN.findall(_canonical(text)))


def tokenize(text: str) -> list[str]:
    """Convert one user utterance into grammar-compatible terminal tokens."""
    return _TOKEN.findall(_canonical(text))


def normalized_phrase(text: str) -> str:
    """Normalize an entity alias for lexicon lookup."""
    return normalize_text(text)


def detokenize(tokens: list[str] | tuple[str, ...]) -> str:
    """Join generated terminal tokens into a readable question."""
    value = " ".join(tokens)
    value = re.sub(r"\s+([?.!,;:])", r"\1", value)
    value = re.sub(r"([([{])\s+", r"\1", value)
    return value
