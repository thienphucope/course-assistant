"""Compatibility entry point matching the package layout of the supplied scaffold."""

from __future__ import annotations

from .cli import main


def run(**kwargs: object) -> int:
    samples = str(kwargs.get("samples", 1000))
    return main(["all", "--samples", samples])


def test(**kwargs: object) -> int:
    """Backward-compatible name used by the original sample app.json."""

    return run(**kwargs)

