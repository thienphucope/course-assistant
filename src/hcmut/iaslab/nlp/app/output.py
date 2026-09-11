"""Serialization boundary for every assignment deliverable.

Keep file naming, UTF-8 encoding, stable ordering, and line limits here instead
of mixing them into NLP stages.  The writer consumes structured pipeline traces
and produces grammar, samples, parse, semantics, intent/entity, query, answer,
and evaluation artifacts.  Alternative JSON or web outputs can be added as new
serializers without changing the core pipeline.
"""

from __future__ import annotations

from pathlib import Path

from .generator import GeneratorStats
from .pipeline import PipelineResult


def ensure_output_dir(path: str | Path) -> Path:
    """Create and return the selected output directory."""
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)
    return output


def write_grammar(path: Path, source: str) -> None:
    """Write the exact grammar snapshot used for the run."""
    raise NotImplementedError("Implement deterministic UTF-8 grammar output")


def write_samples(path: Path, sentences: list[str], stats: GeneratorStats) -> None:
    """Write at most 10,000 generated questions and validate the bound."""
    raise NotImplementedError("Implement bounded samples.txt serialization")


def write_pipeline_outputs(output_dir: Path, results: list[PipelineResult]) -> None:
    """Write all per-question intermediate and final deliverables."""
    raise NotImplementedError("Implement stable serializers for the pipeline trace")
