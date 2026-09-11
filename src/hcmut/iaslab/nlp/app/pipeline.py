"""Composition root and observable end-to-end Course Assistant pipeline.

The call order is fixed and explicit: parse -> raw semantics -> optional context
resolution -> KB query -> answer -> context update.  ``PipelineResult`` retains
every intermediate artifact so evaluation and debugging do not need hidden
globals.  ``PipelineComponents`` enables dependency injection: stages can be
implemented, mocked, or upgraded independently while clients keep using the
``CourseAssistant`` facade.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .answer import AnswerGenerator
from .dialogue import DialogueContext
from .parser import EarleyParser, ParseResult
from .paths import ProjectPaths
from .query import QueryEngine, QueryResult
from .semantic import SemanticFrame, SemanticInterpreter


@dataclass(frozen=True)
class PipelineComponents:
    """Replaceable stage implementations required by the orchestrator."""

    parser: EarleyParser
    interpreter: SemanticInterpreter
    query_engine: QueryEngine
    answer_generator: AnswerGenerator
    context: DialogueContext


@dataclass
class PipelineResult:
    """Complete trace for one question, including pre/post-context semantics."""

    sentence: str
    parse: ParseResult
    raw_semantic: SemanticFrame
    semantic: SemanticFrame
    query: QueryResult
    answer: str
    context_used: str | None = None

    @property
    def detected_intent(self) -> str:
        return self.raw_semantic.intent

    @property
    def detected_entity(self) -> str | None:
        return self.semantic.entity or self.raw_semantic.entity


class CourseAssistant:
    """Stable application facade over independently replaceable NLP stages."""

    def __init__(self, components: PipelineComponents) -> None:
        self.components = components

    @classmethod
    def from_paths(cls, paths: ProjectPaths) -> "CourseAssistant":
        """Load files, validate them, construct stages, and wire dependencies."""
        raise NotImplementedError("Implement the production composition root")

    @classmethod
    def from_root(cls, root: str | Path) -> "CourseAssistant":
        return cls.from_paths(ProjectPaths.from_root(root))

    def reset_context(self) -> None:
        self.components.context.reset()

    def process(self, sentence: str, use_context: bool = True) -> PipelineResult:
        """Run one utterance through every stage and preserve the full trace."""
        parse = self.components.parser.parse(sentence)
        raw = self.components.interpreter.interpret(parse.tree)
        semantic, context_used = (
            self.components.context.resolve(raw) if use_context else (raw, None)
        )
        query = self.components.query_engine.execute(semantic)
        answer = self.components.answer_generator.generate(semantic, query)
        if use_context:
            self.components.context.update(semantic, query)
        return PipelineResult(sentence, parse, raw, semantic, query, answer, context_used)
