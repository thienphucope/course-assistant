"""Repository-local launcher; installation is optional."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from hcmut.iaslab.nlp.app.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())

