#!/usr/bin/env sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if command -v latexmk >/dev/null 2>&1; then
    latexmk -pdf -interaction=nonstopmode -halt-on-error vantage.tex
else
    for pass in 1 2 3; do
        pdflatex -interaction=nonstopmode -halt-on-error vantage.tex
    done
fi
if command -v python3 >/dev/null 2>&1; then
    python3 reference_checks.py --output reference-checks.json
else
    python reference_checks.py --output reference-checks.json
fi
