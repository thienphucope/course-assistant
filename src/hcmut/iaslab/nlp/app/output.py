"""Serialization boundary for every assignment deliverable.

Keep file naming, UTF-8 encoding, stable ordering, and line limits here instead
of mixing them into NLP stages.  The writer consumes structured pipeline traces
and produces grammar, samples, parse, semantics, intent/entity, query, answer,
and evaluation artifacts.  Alternative JSON or web outputs can be added as new
serializers without changing the core pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

from .generator import GeneratorStats
from .parser import ParseResult
from .pipeline import PipelineResult
from .semantic import SemanticFrame


def ensure_output_dir(path: str | Path) -> Path:
    """Create and return the selected output directory."""
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)
    return output


def write_grammar(path: Path, source: str) -> None:
    """Write the same CFG text used for the run as UTF-8."""
    ensure_output_dir(path.parent)
    path.write_text(source, encoding="utf-8")


def write_samples(path: Path, sentences: list[str], stats: GeneratorStats) -> None:
    """Write at most 10,000 generated questions and validate the bound."""
    if len(sentences) > 10_000 or len(sentences) != stats.produced:
        raise ValueError("Generated sentence count is invalid")
    if len(set(sentences)) != len(sentences):
        raise ValueError("Generated sentences must be unique")
    if any("\n" in sentence or "\r" in sentence for sentence in sentences):
        raise ValueError("Each generated question must fit on one line")
    ensure_output_dir(path.parent)
    path.write_text("\n".join(sentences) + ("\n" if sentences else ""), encoding="utf-8")


def write_parse_results(path: Path, results: list[ParseResult]) -> None:
    """Write one bracketed tree or ``()`` for each input sentence."""
    ensure_output_dir(path.parent)
    lines = [result.output() for result in results]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_semantic_results(output_dir: Path, frames: list[SemanticFrame]) -> None:
    """Write one semantic predicate and one JSON intent/entity per input line."""
    ensure_output_dir(output_dir)
    semantic_lines = [frame.predicate for frame in frames]
    entity_lines = [
        json.dumps(
            {
                "intent": frame.intent,
                "entity": frame.entity,
                "slots": frame.slots,
                "source_branch": frame.source_branch,
            },
            ensure_ascii=False,
        )
        for frame in frames
    ]
    (output_dir / "semantic.txt").write_text(
        "\n".join(semantic_lines) + ("\n" if semantic_lines else ""), encoding="utf-8"
    )
    (output_dir / "intent-entity.txt").write_text(
        "\n".join(entity_lines) + ("\n" if entity_lines else ""), encoding="utf-8"
    )


def write_pipeline_outputs(output_dir: Path, results: list[PipelineResult]) -> None:
    """Write five aligned per-question files from one set of pipeline traces.

    Each nonempty line represents the same one-based input position in every
    file. Query and answer use JSON Lines so punctuation cannot break columns.
    """
    ensure_output_dir(output_dir)
    write_parse_results(output_dir / "parse-results.txt", [item.parse for item in results])
    write_semantic_results(output_dir, [item.semantic for item in results])
    query_lines: list[str] = []
    answer_lines: list[str] = []
    for line_number, item in enumerate(results, 1):
        query_lines.append(json.dumps({
            "line": line_number,
            "question": item.sentence,
            "query": item.query.query,
            "status": item.query.status,
            "kind": item.query.kind,
            "sources": item.query.sources,
            "reason": item.query.reason,
        }, ensure_ascii=False))
        answer_lines.append(json.dumps({
            "line": line_number,
            "question": item.sentence,
            "answer": item.answer,
            "sources": item.query.sources,
        }, ensure_ascii=False))
    (output_dir / "query.txt").write_text(
        "\n".join(query_lines) + ("\n" if query_lines else ""), encoding="utf-8"
    )
    (output_dir / "answer.txt").write_text(
        "\n".join(answer_lines) + ("\n" if answer_lines else ""), encoding="utf-8"
    )


def write_evaluation(path: Path, report: str) -> None:
    """Persist the reproducible assessment separately from question traces."""
    ensure_output_dir(path.parent)
    path.write_text(report, encoding="utf-8")
