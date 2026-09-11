#!/usr/bin/env bash
# Small developer helper; domain behavior remains in the Python package.

set -euo pipefail

case "${1:-}" in
  check)
    python -m compileall -q hcmut run.py setup.py
    ;;
  help)
    python run.py --help
    ;;
  *)
    echo "Usage: ./util.sh {check|help}" >&2
    exit 2
    ;;
esac
