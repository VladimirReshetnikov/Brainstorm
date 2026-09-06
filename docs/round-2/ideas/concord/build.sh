#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
if ! command -v latexmk >/dev/null 2>&1; then
    echo "latexmk is required. Install a TeX distribution with the packages named in concord.tex." >&2
    exit 1
fi
mkdir -p .build
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=.build concord.tex
cp .build/concord.pdf concord.pdf
if command -v python3 >/dev/null 2>&1; then
    python3 checks.py --output checks.json
fi
printf '%s\n' 'Built concord.pdf. The supplied SHA256SUMS describes the original delivered files.'
