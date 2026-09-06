#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if ! command -v latexmk >/dev/null 2>&1; then
    printf '%s\n' 'latexmk is required; install it with your TeX distribution.' >&2
    exit 1
fi
mkdir -p build
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build facet.tex
printf '%s\n' 'Built build/facet.pdf'
