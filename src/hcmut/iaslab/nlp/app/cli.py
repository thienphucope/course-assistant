"""Command-line boundary for interactive, batch, generation, and evaluation use.

The CLI translates user arguments into application calls; it must not contain
NLP rules or KB parsing.  Keep commands scriptable with meaningful exit codes
and route all paths through ``ProjectPaths``.  Additional HTTP/UI adapters can
reuse the same ``CourseAssistant`` without importing this module.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .evaluate import evaluate_cases, load_evaluation_cases, render_evaluation
from .generator import SentenceGenerator
from .grammar import Grammar
from .paths import ProjectPaths
from .pipeline import CourseAssistant


def build_parser() -> argparse.ArgumentParser:
    """Declare the stable user-facing command surface."""
    parser = argparse.ArgumentParser(prog="course-assistant")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project root")
    commands = parser.add_subparsers(dest="command", required=True)

    ask = commands.add_parser("ask", help="process one question")
    ask.add_argument("question", nargs="+")
    ask.add_argument("--no-context", action="store_true")

    generate = commands.add_parser("generate", help="generate questions from the CFG")
    generate.add_argument("--limit", type=int, default=1000)
    generate.add_argument("--max-tokens", type=int, default=32)

    evaluate = commands.add_parser("evaluate", help="run an evaluation fixture")
    evaluate.add_argument("cases", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Dispatch a parsed command and return a process exit code."""
    args = build_parser().parse_args(argv)
    paths = ProjectPaths.from_root(args.root)

    if args.command == "ask":
        result = CourseAssistant.from_paths(paths).process(
            " ".join(args.question), use_context=not args.no_context
        )
        print(result.answer)
        return 0

    if args.command == "generate":
        grammar = Grammar.from_file(paths.grammar)
        sentences, stats = SentenceGenerator(grammar).generate(args.limit, args.max_tokens)
        print("\n".join(sentences))
        return 0 if stats.produced == stats.requested else 2

    if args.command == "evaluate":
        assistant = CourseAssistant.from_paths(paths)
        summary = evaluate_cases(assistant, load_evaluation_cases(args.cases))
        print(render_evaluation(summary))
        return 0 if summary.passed == summary.total else 1

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
