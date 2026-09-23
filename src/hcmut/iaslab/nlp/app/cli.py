"""Command-line boundary for interactive, batch, generation, and evaluation use.

The CLI translates user arguments into application calls; it must not contain
NLP rules or KB parsing.  Keep commands scriptable with meaningful exit codes
and route all paths through ``ProjectPaths``.  Additional HTTP/UI adapters can
reuse the same ``CourseAssistant`` without importing this module.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .evaluate import (EvaluationSummary, evaluate_cases, load_evaluation_cases,
                       render_evaluation_report)
from .entities import EntityLexicon
from .generator import SentenceGenerator
from .grammar import Grammar
from .output import (write_evaluation, write_grammar, write_parse_results, write_pipeline_outputs,
                     write_samples, write_semantic_results)
from .parser import EarleyParser
from .paths import ProjectPaths
from .pipeline import CourseAssistant
from .semantic import SemanticInterpreter


def build_parser() -> argparse.ArgumentParser:
    """Declare the stable user-facing command surface."""
    parser = argparse.ArgumentParser(prog="course-assistant")
    parser.add_argument("--root", type=Path, default=None,
                        help="project src/ root; discovered automatically if omitted")
    commands = parser.add_subparsers(dest="command", required=True)

    ask = commands.add_parser("ask", help="process one question")
    ask.add_argument("question", nargs="+")
    ask.add_argument("--no-context", action="store_true")
    ask.add_argument(
        "--trace", action="store_true", help="show every stage of the NLP pipeline"
    )

    generate = commands.add_parser("generate", help="generate questions from the CFG")
    generate.add_argument("--limit", type=int, default=1000)
    generate.add_argument("--max-tokens", type=int, default=32)

    part1 = commands.add_parser("part1", help="write the three Part I deliverables")
    part1.add_argument("--limit", type=int, default=10_000)
    part1.add_argument("--max-tokens", type=int, default=32)
    part1.add_argument("--input", type=Path, default=None)

    semantic = commands.add_parser("semantic", help="write semantic and intent/entity results")
    semantic.add_argument("--input", type=Path, default=None)

    batch = commands.add_parser("batch", help="write all Part I and II output files")
    batch.add_argument("--input", type=Path, default=None)
    batch.add_argument("--limit", type=int, default=10_000)
    batch.add_argument("--max-tokens", type=int, default=32)

    evaluate = commands.add_parser("evaluate", help="run an evaluation fixture")
    evaluate.add_argument("cases", type=Path, nargs="?",
                          help="optional one-file fixture; default runs core and challenge")
    evaluate.add_argument("--strict", action="store_true",
                          help="return exit code 1 when any declared case fails")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Dispatch a parsed command and return a process exit code."""
    args = build_parser().parse_args(argv)
    try:
        paths = ProjectPaths.discover() if args.root is None else ProjectPaths.from_root(args.root)
        return _dispatch(args, paths)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _dispatch(args: argparse.Namespace, paths: ProjectPaths) -> int:
    """Run a command against one resolved project root."""

    if args.command == "ask":
        result = CourseAssistant.from_paths(paths).process(
            " ".join(args.question), use_context=not args.no_context
        )
        if args.trace:
            print(f"Question: {result.sentence}")
            print(f"Tokens: {list(result.parse.tokens)}")
            print(f"Parse: {result.parse.output()}")
            print(f"Semantic: {result.semantic.predicate}")
            print(f"Intent: {result.detected_intent}")
            print(f"Entity: {result.detected_entity or '-'}")
            print(f"Query: {result.query.query}")
            print(f"KB result: {result.query.status}")
            print(f"Source: {', '.join(result.query.sources) or '-'}")
            print(f"Answer: {result.answer}")
        else:
            print(result.answer)
        return 0

    if args.command == "generate":
        grammar = Grammar.from_file(paths.grammar)
        sentences, stats = SentenceGenerator(grammar).generate(args.limit, args.max_tokens)
        print("\n".join(sentences))
        return 0 if stats.produced == stats.requested else 2

    if args.command == "part1":
        grammar = Grammar.from_file(paths.grammar)
        generated, stats = SentenceGenerator(grammar).generate(args.limit, args.max_tokens)
        input_path = _input_path(args.input, paths)
        questions = _read_questions(input_path)
        parser = EarleyParser(grammar)
        parses = [parser.parse(question) for question in questions]
        write_grammar(paths.output / "grammar.txt", grammar.source_text)
        write_samples(paths.output / "samples.txt", generated, stats)
        write_parse_results(paths.output / "parse-results.txt", parses)
        print(
            f"Part I: {len(generated)} generated, "
            f"{sum(result.accepted for result in parses)}/{len(parses)} parsed; "
            f"files in {paths.output}"
        )
        return 0

    if args.command == "semantic":
        grammar = Grammar.from_file(paths.grammar)
        lexicon = EntityLexicon.from_file(paths.scaffolding / "entities.txt")
        interpreter = SemanticInterpreter(lexicon)
        input_path = _input_path(args.input, paths)
        questions = _read_questions(input_path)
        parser = EarleyParser(grammar)
        parses = [parser.parse(question) for question in questions]
        frames = [interpreter.interpret(result.tree) for result in parses]
        write_semantic_results(paths.output, frames)
        mapped = sum(frame.intent not in {"UNKNOWN", "UNSUPPORTED"} for frame in frames)
        print(f"Semantic: {mapped}/{len(frames)} mapped; files in {paths.output}")
        return 0

    if args.command == "batch":
        assistant = CourseAssistant.from_paths(paths)
        grammar = assistant.components.parser.grammar
        questions = _read_questions(_input_path(args.input, paths))
        generated, stats = SentenceGenerator(grammar).generate(args.limit, args.max_tokens)
        results = [assistant.process(question, use_context=False) for question in questions]
        write_grammar(paths.output / "grammar.txt", grammar.source_text)
        write_samples(paths.output / "samples.txt", generated, stats)
        write_pipeline_outputs(paths.output, results)
        summaries = _default_evaluation(assistant, paths)
        write_evaluation(paths.output / "evaluation.txt", render_evaluation_report(summaries))
        found = sum(item.query.status == "FOUND" for item in results)
        not_found = sum(item.query.status == "NOT_FOUND" for item in results)
        outside = sum(item.query.status == "OUT_OF_SCOPE" for item in results)
        print(f"Batch: {len(questions)} questions, {sum(item.parse.accepted for item in results)} parsed, "
              f"{found} found, {not_found} not found, {outside} outside; "
              f"{len(generated)} generated; evaluation "
              f"{sum(item.passed for item in summaries)}/{sum(item.total for item in summaries)}; "
              f"files in {paths.output}")
        return 0

    if args.command == "evaluate":
        assistant = CourseAssistant.from_paths(paths)
        if args.cases is None:
            summaries = _default_evaluation(assistant, paths)
        else:
            source = _input_path(args.cases, paths)
            summaries = [evaluate_cases(assistant, load_evaluation_cases(source), source.name)]
        report = render_evaluation_report(summaries)
        write_evaluation(paths.output / "evaluation.txt", report)
        print(report, end="")
        return 1 if args.strict and any(item.passed != item.total for item in summaries) else 0

    raise AssertionError(f"Unhandled command: {args.command}")


def _read_questions(path: Path) -> list[str]:
    """Keep Part I and semantic output aligned to the same nonempty input lines."""
    questions = [
        line.strip()
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not questions:
        raise ValueError(f"No question lines in {path}")
    return questions


def _input_path(value: Path | None, paths: ProjectPaths) -> Path:
    """Resolve optional relative input against the explicit/discovered src root."""
    if value is None:
        return paths.input / "sentences.txt"
    return value if value.is_absolute() else paths.root / value


def _default_evaluation(assistant: CourseAssistant,
                        paths: ProjectPaths) -> list[EvaluationSummary]:
    """Keep development examples and team challenge scores separate."""
    sources = (
        ("Sample core + out-of-scope (gold_queries.txt)",
         paths.scaffolding / "gold_queries.txt"),
        ("Team challenge (challenge_queries.txt)",
         paths.scaffolding / "challenge_queries.txt"),
    )
    return [evaluate_cases(assistant, load_evaluation_cases(source), name)
            for name, source in sources]


if __name__ == "__main__":
    raise SystemExit(main())
