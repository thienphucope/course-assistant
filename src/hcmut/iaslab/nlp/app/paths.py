"""Centralized project-path discovery with no dependency on current directory.

All file locations flow through ``ProjectPaths`` so CLI, Docker, tests, and IDE
runs behave identically.  Discovery should locate a recognizable project root;
``from_root`` supports explicit roots in tests and deployments.  Keep paths
configurable so data can later move to package resources, object storage, or a
database without scattering path arithmetic across domain modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Canonical locations required to assemble and run the application."""

    root: Path
    source: Path
    data: Path
    grammar: Path
    kb: Path
    scaffolding: Path
    input: Path
    output: Path

    @classmethod
    def discover(cls) -> "ProjectPaths":
        """Find src/ from the current directory or the installed module path."""
        for starting_point in (Path.cwd().resolve(), Path(__file__).resolve()):
            for ancestor in (starting_point, *starting_point.parents):
                for candidate in (ancestor, ancestor / "src"):
                    if ((candidate / "data" / "grammar.cfg").is_file()
                            and (candidate / "input" / "sentences.txt").is_file()
                            and (candidate / "run.py").is_file()):
                        return cls.from_root(candidate)
        raise FileNotFoundError("Cannot find src/ with data/grammar.cfg and input/sentences.txt")

    @classmethod
    def from_root(cls, root: str | Path) -> "ProjectPaths":
        """Construct all canonical paths from an explicit project root."""
        resolved = Path(root).expanduser().resolve()
        return cls(
            root=resolved,
            source=resolved,
            data=resolved / "data",
            grammar=resolved / "data" / "grammar.cfg",
            kb=resolved / "data" / "kb",
            scaffolding=resolved / "data" / "scaffolding",
            input=resolved / "input",
            output=resolved / "output",
        )
