"""Compositional conversion from parse trees to machine-readable meaning.

``SemanticFrame`` groups the three essential semantic outputs: an intent, a
canonical focus entity, and typed slots.  ``source_branch`` preserves the CFG
branch for debugging.  The interpreter should dispatch from labeled tree nodes
(for example ``Q_SCHEDULE_WEEK``), collect entities compositionally, and return
``UNKNOWN`` for missing/unsupported structures.  KB access is forbidden here;
meaning extraction and fact lookup are separate, testable concerns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .entities import EntityLexicon
from .tree import Tree


@dataclass
class SemanticFrame:
    """Normalized request exchanged by semantics, context, and query stages."""

    intent: str
    entity: str | None = None
    slots: dict[str, Any] = field(default_factory=dict)
    source_branch: str | None = None

    @property
    def predicate(self) -> str:
        """Render a compact, deterministic representation for grading/debugging."""
        values = dict(self.slots)
        if self.entity is not None and "entity" not in values:
            values = {"entity": self.entity, **values}
        arguments = ", ".join(f"{key}={value}" for key, value in values.items())
        return f"{self.intent}({arguments})"

    @classmethod
    def unknown(cls) -> "SemanticFrame":
        return cls(intent="UNKNOWN")


class SemanticInterpreter:
    """Interpret labeled CFG subtrees into canonical semantic frames."""

    def __init__(self, lexicon: EntityLexicon) -> None:
        self.lexicon = lexicon

    def interpret(self, tree: Tree | None) -> SemanticFrame:
        """Map a complete tree to meaning without consulting the knowledge base."""
        raise NotImplementedError("Implement tree-label dispatch and slot composition")
