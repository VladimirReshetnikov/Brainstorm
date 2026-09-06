#!/usr/bin/env sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
command -v latexmk >/dev/null 2>&1 || { echo 'latexmk is required (TeX Live or MiKTeX).' >&2; exit 1; }
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else echo 'Python 3.9 or later is required.' >&2; exit 1
fi
latexmk -pdf -interaction=nonstopmode -halt-on-error locus.tex
"$PY" certificate_demo.py --json test-results.json
