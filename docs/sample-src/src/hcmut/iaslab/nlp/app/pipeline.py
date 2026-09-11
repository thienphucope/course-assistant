"""Wire all mandatory NLP stages into one observable pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .answer import AnswerGenerator
from .dialogue import DialogueContext
from .entities import EntityLexicon
from .grammar import Grammar
from .kb import KnowledgeBase
from .parser import EarleyParser, ParseResult
from .paths import PATHS, ProjectPaths
from .query import QueryEngine, QueryResult
from .semantic import SemanticFrame, SemanticInterpreter


@dataclass
class PipelineResult:
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
    def __init__(self, paths: ProjectPaths | None = None) -> None:
        self.paths = paths or PATHS
        self.grammar = Grammar.from_file(self.paths.grammar)
        self.parser = EarleyParser(self.grammar)
        self.lexicon = EntityLexicon(self.paths.scaffolding / "entities.txt")
        self.interpreter = SemanticInterpreter(self.lexicon)
        self.kb = KnowledgeBase.load(self.paths.kb)
        validation_errors = self.kb.validate()
        if validation_errors:
            raise ValueError("KB không hợp lệ:\n- " + "\n- ".join(validation_errors))
        self.query_engine = QueryEngine(self.kb)
        self.answer_generator = AnswerGenerator()
        self.context = DialogueContext()

    @classmethod
    def from_root(cls, root: str | Path) -> "CourseAssistant":
        return cls(ProjectPaths.from_root(root))

    def reset_context(self) -> None:
        self.context.reset()

    def process(self, sentence: str, use_context: bool = True) -> PipelineResult:
        parse = self.parser.parse(sentence)
        raw = self.interpreter.interpret(parse.tree)
        semantic, context_used = self.context.resolve(raw) if use_context else (raw, None)
        query = self.query_engine.execute(semantic)
        answer = self.answer_generator.generate(semantic, query)
        if use_context:
            self.context.update(semantic, query)
        return PipelineResult(sentence, parse, raw, semantic, query, answer, context_used)

