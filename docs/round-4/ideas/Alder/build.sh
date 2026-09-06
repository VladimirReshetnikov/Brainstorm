#!/usr/bin/env sh
# Run from any working directory; PYTHON may select a Python 3.10+ executable.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PYTHONDONTWRITEBYTECODE=1 "${PYTHON:-python3}" companion/test_alder.py
latexmk -pdf -interaction=nonstopmode -halt-on-error Alder.tex
