"""Text-normalization boundary between raw questions and the CFG parser.

Implement Unicode/case/spacing normalization here and nowhere else.  The
contract is that ``tokenize`` returns terminals using exactly the same spelling
as ``grammar.cfg``; ``detokenize`` is the inverse used by sentence generation.
Future upgrades such as typo handling or word segmentation should preserve
canonical IDs and remain deterministic so parser tests stay reproducible.
"""

from __future__ import annotations


def normalize_text(text: str) -> str:
    """Return canonical text before token splitting."""
    raise NotImplementedError("Implement Unicode, case, punctuation, and whitespace normalization")


def tokenize(text: str) -> list[str]:
    """Convert one user utterance into grammar-compatible terminal tokens."""
    raise NotImplementedError("Implement tokenization against the terminals in grammar.cfg")


def normalized_phrase(text: str) -> str:
    """Normalize an entity alias for lexicon lookup."""
    raise NotImplementedError("Implement canonical phrase normalization")


def detokenize(tokens: list[str] | tuple[str, ...]) -> str:
    """Join generated terminal tokens into a readable question."""
    raise NotImplementedError("Implement punctuation-aware detokenization")
