#!/bin/sh
set -eu
cd "$(dirname "$0")"
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error meridian.tex
elif command -v pdflatex >/dev/null 2>&1; then
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error meridian.tex
  done
else
  printf '%s\n' 'Install pdfLaTeX (TeX Live or MiKTeX) before building.' >&2
  exit 1
fi
