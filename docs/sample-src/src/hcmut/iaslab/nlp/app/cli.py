"""Command-line interface for individual stages and the complete pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .evaluate import (
    evaluate_cases,
    load_dialogue_cases,
    load_evaluation_cases,
    render_dialogue_evaluation,
    render_evaluation,
)
from .generator import SentenceGenerator
from .output import ensure_output_dir, write_grammar, write_pipeline_outputs, write_samples
from .paths import PATHS, ProjectPaths
from .pipeline import CourseAssistant


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="course-assistant",
        description="Classical grammar-driven Course Assistant for CO3085",
    )
    parser.add_argument("--root", default=str(PATHS.root), help="project root (default: auto-detected)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    all_parser = subparsers.add_parser("all", help="generate every assignment output")
    all_parser.add_argument("--input", default="input/sentences.txt")
    all_parser.add_argument("--output", default="output")
    all_parser.add_argument("--samples", type=int, default=1000)

    parse_parser = subparsers.add_parser("parse", help="print parse trees")
    _add_question_source(parse_parser)

    answer_parser = subparsers.add_parser("answer", help="run the complete QA pipeline")
    _add_question_source(answer_parser)
    answer_parser.add_argument("--trace", action="store_true", help="show all intermediate stages")

    generate_parser = subparsers.add_parser("generate", help="generate valid questions")
    generate_parser.add_argument("--limit", type=int, default=100)
    generate_parser.add_argument("--output", default=None)

    eval_parser = subparsers.add_parser("evaluate", help="evaluate labelled queries and dialogues")
    eval_parser.add_argument("--output", default="output")

    subparsers.add_parser("interactive", help="interactive multi-turn conversation")
    return parser


def _add_question_source(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("questions", nargs="*")
    parser.add_argument("--input", default=None, help="UTF-8 file with one question per line")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    paths = ProjectPaths.from_root(args.root)
    assistant = CourseAssistant(paths)
    if args.command == "all":
        return _run_all(assistant, paths, args)
    if args.command == "parse":
        questions = _questions(args.questions, args.input, paths)
        for question in questions:
            print(assistant.parser.parse(question).output())
        return 0
    if args.command == "answer":
        questions = _questions(args.questions, args.input, paths)
        for result in (assistant.process(question) for question in questions):
            if args.trace:
                print(f"INPUT: {result.sentence}")
                print(f"PARSE: {result.parse.output()}")
                print(f"SEMANTIC: {result.raw_semantic.predicate}")
                if result.context_used:
                    print(f"RESOLVED: {result.semantic.predicate} ({result.context_used})")
                print(f"QUERY: {result.query.query}")
                print(f"SOURCE: {', '.join(result.query.sources) or '-'}")
            print(f"ANSWER: {result.answer}")
        return 0
    if args.command == "generate":
        sentences, stats = SentenceGenerator(assistant.grammar).generate(args.limit)
        rejected = [sentence for sentence in sentences if not assistant.parser.parse(sentence).accepted]
        if rejected:
            raise RuntimeError(f"Generator tạo {len(rejected)} câu không parse lại được")
        if args.output:
            target = _resolve(args.output, paths)
            target.parent.mkdir(parents=True, exist_ok=True)
            write_samples(target, sentences, stats)
        else:
            print("\n".join(sentences))
        print(f"Generated {stats.produced}/{stats.requested} valid sentences.", file=sys.stderr)
        return 0
    if args.command == "evaluate":
        output = ensure_output_dir(_resolve(args.output, paths))
        _write_evaluations(assistant, paths, output)
        print(f"Evaluation written to {output}")
        return 0
    if args.command == "interactive":
        return _interactive(assistant)
    return 2


def _run_all(assistant: CourseAssistant, paths: ProjectPaths, args: argparse.Namespace) -> int:
    output = ensure_output_dir(_resolve(args.output, paths))
    input_path = _resolve(args.input, paths)
    questions = _read_questions(input_path)

    write_grammar(output / "grammar.txt", assistant.grammar.source_text)
    samples, stats = SentenceGenerator(assistant.grammar).generate(args.samples)
    rejected = [sentence for sentence in samples if not assistant.parser.parse(sentence).accepted]
    if rejected:
        raise RuntimeError(f"Round-trip generator/parser thất bại với {len(rejected)} câu")
    write_samples(output / "samples.txt", samples, stats)

    assistant.reset_context()
    results = [assistant.process(question, use_context=True) for question in questions]
    write_pipeline_outputs(output, results)
    _write_evaluations(assistant, paths, output)
    print(
        f"Completed: {len(questions)} input questions, {len(samples)} generated samples, "
        f"9 output files in {output}"
    )
    return 0


def _write_evaluations(assistant: CourseAssistant, paths: ProjectPaths, output: Path) -> None:
    official_cases = load_evaluation_cases(paths.scaffolding / "sample_queries.txt")
    challenge_cases = load_evaluation_cases(paths.scaffolding / "challenge_queries.txt")
    official = evaluate_cases(assistant, official_cases, reset_context=True)
    challenge = evaluate_cases(assistant, challenge_cases, reset_context=True)
    (output / "evaluation.txt").write_text(render_evaluation(official, challenge), encoding="utf-8")

    dialogues = load_dialogue_cases(paths.scaffolding / "dialogues.txt")
    dialogue_report = render_dialogue_evaluation(assistant, dialogues)
    (output / "dialogue.txt").write_text(dialogue_report, encoding="utf-8")


def _questions(arguments: list[str], input_name: str | None, paths: ProjectPaths) -> list[str]:
    result = list(arguments)
    if input_name:
        result.extend(_read_questions(_resolve(input_name, paths)))
    if not result:
        raise ValueError("Hãy truyền câu hỏi hoặc --input FILE")
    return result


def _read_questions(path: Path) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy input: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]


def _resolve(value: str, paths: ProjectPaths) -> Path:
    path = Path(value)
    return path if path.is_absolute() else paths.root / path


def _interactive(assistant: CourseAssistant) -> int:
    print("CO3085 Course Assistant. Nhập /reset để xóa ngữ cảnh, /quit để thoát.")
    while True:
        try:
            question = input("Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not question:
            continue
        if question == "/quit":
            return 0
        if question == "/reset":
            assistant.reset_context()
            print("Đã xóa ngữ cảnh.")
            continue
        result = assistant.process(question)
        print(f"Trợ lý: {result.answer}")


if __name__ == "__main__":
    raise SystemExit(main())
