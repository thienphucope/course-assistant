"""Deterministic execution of semantic frames against the normalized KB.

This stage turns semantic intent and slots into a traceable lookup; it must not
re-interpret the original sentence.  Every execution returns ``QueryResult``,
including unsupported, missing-data, and unresolved-context cases.  Preserve
``query`` and ``sources`` because they explain why an answer is grounded.  New
storage backends or ranking strategies can sit behind this contract while the
pipeline and renderer remain unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .kb import KnowledgeBase
from .semantic import SemanticFrame


@dataclass
class QueryResult:
    """Structured success or failure returned for every semantic request."""

    query: str
    found: bool
    kind: str
    data: Any = None
    sources: list[str] = field(default_factory=list)
    reason: str | None = None


class QueryEngine:
    """Route intents to domain-specific, read-only KB lookups."""

    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb

    def execute(self, frame: SemanticFrame) -> QueryResult:
        """Execute one normalized frame and never fabricate absent knowledge."""
        raise NotImplementedError("Implement intent dispatch and grounded KB queries")
