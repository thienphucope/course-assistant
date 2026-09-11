"""Compatibility entry points for the lecturer-provided JSON launcher.

The historical scaffold calls a dotted function from ``conf/app.json``.  Keep
that adapter thin: argument parsing and workflow selection belong to ``cli``;
NLP logic belongs to pipeline stages.  New deployments should call the CLI or
``CourseAssistant`` directly, while existing grading scripts can keep using
``run``/``test``.
"""

from __future__ import annotations

from typing import Any


def run(**kwargs: Any) -> int:
    """Translate launcher keyword arguments into CLI arguments and execute."""
    from .cli import main

    argv = kwargs.get("argv")
    return main(list(argv) if argv is not None else None)


def test(**kwargs: Any) -> int:
    """Backward-compatible alias retained for the original assignment scaffold."""
    return run(**kwargs)
