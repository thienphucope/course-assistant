"""Repository-local launcher for development without installing the package.

This wrapper only forwards to the package CLI.  It keeps imports and behavior
identical to the installed console entry point, which avoids maintaining a
second execution path.
"""

from pathlib import Path
import sys

# The submission layout puts the package under project/src/.
source = Path(__file__).resolve().parent / "src"
if (source / "hcmut").is_dir():
    sys.path.insert(0, str(source))

from hcmut.iaslab.nlp.app.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
