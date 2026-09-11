"""Write every deliverable specified by the assignment."""

from __future__ import annotations

import json
from pathlib import Path

from .generator import GeneratorStats
from .pipeline import PipelineResult


def ensure_output_dir(path: str | Path) -> Path:
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)
    return output


def write_grammar(path: Path, source: str) -> None:
    path.write_text(source.rstrip() + "\n", encoding="utf-8")


def write_samples(path: Path, sentences: list[str], stats: GeneratorStats) -> None:
    if len(sentences) > 10_000:
        raise ValueError("samples.txt không được vượt quá 10.000 dòng")
    path.write_text("\n".join(sentences) + ("\n" if sentences else ""), encoding="utf-8")


def write_pipeline_outputs(output_dir: Path, results: list[PipelineResult]) -> None:
    parse_lines = [result.parse.output() for result in results]
    semantic_lines = []
    intent_lines = []
    query_lines = []
    answer_lines = []
    for index, result in enumerate(results, start=1):
        semantic = result.raw_semantic.predicate
        if result.context_used:
            semantic += f" => {result.semantic.predicate} [{result.context_used}]"
        semantic_lines.append(f"{index:03d}\t{semantic}")
        intent_lines.append(
            json.dumps(
                {
                    "id": index,
                    "question": result.sentence,
                    "intent": result.raw_semantic.intent,
                    "entity": result.detected_entity,
                    "resolved_intent": result.semantic.intent,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        query_lines.append(
            f"{index:03d}\t{result.query.query}\t"
            f"status={'FOUND' if result.query.found else 'NOT_FOUND'}\t"
            f"source={','.join(result.query.sources) or '-'}"
        )
        answer_lines.append(f"{index:03d}\tQ: {result.sentence}\n\tA: {result.answer}")
    _write_lines(output_dir / "parse-results.txt", parse_lines)
    _write_lines(output_dir / "semantic.txt", semantic_lines)
    _write_lines(output_dir / "intent-entity.txt", intent_lines)
    _write_lines(output_dir / "query.txt", query_lines)
    _write_lines(output_dir / "answer.txt", answer_lines)


def _write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

