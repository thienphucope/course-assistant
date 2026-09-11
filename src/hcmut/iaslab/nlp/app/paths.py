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
        """Search parent directories for the project markers, independent of cwd."""
        raise NotImplementedError("Implement robust project-root discovery")

    @classmethod
    def from_root(cls, root: str | Path) -> "ProjectPaths":
        """Construct all canonical paths from an explicit project root."""
        resolved = Path(root).expanduser().resolve()
        return cls(
            root=resolved,
            source=resolved / "src",
            data=resolved / "data",
            grammar=resolved / "data" / "grammar.cfg",
            kb=resolved / "data" / "kb",
            scaffolding=resolved / "data" / "scaffolding",
            input=resolved / "input",
            output=resolved / "output",
        )
