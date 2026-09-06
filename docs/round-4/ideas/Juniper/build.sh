#!/bin/sh
# Rebuild the self-contained Juniper article without shell escape.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if command -v latexmk >/dev/null 2>&1; then
    exec latexmk -pdf -interaction=nonstopmode -halt-on-error Juniper.tex
fi
if ! command -v pdflatex >/dev/null 2>&1; then
    printf '%s\n' 'Install TeX Live with pdfLaTeX and the packages listed in Juniper.tex.' >&2
    exit 1
fi
for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error Juniper.tex
done
