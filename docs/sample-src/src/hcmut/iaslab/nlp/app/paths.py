"""Path handling kept in one place so the project works from any cwd."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
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
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "pyproject.toml").is_file() and (parent / "data").is_dir():
                return cls.from_root(parent)
        raise RuntimeError("Không tìm thấy thư mục gốc của project")

    @classmethod
    def from_root(cls, root: str | Path) -> "ProjectPaths":
        resolved = Path(root).resolve()
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


PATHS = ProjectPaths.discover()

