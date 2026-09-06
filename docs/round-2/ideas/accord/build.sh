#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python3 certificate_lab.py --report test-results.json
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error accord.tex
else
  pdflatex -interaction=nonstopmode -halt-on-error accord.tex
  pdflatex -interaction=nonstopmode -halt-on-error accord.tex
  pdflatex -interaction=nonstopmode -halt-on-error accord.tex
fi
