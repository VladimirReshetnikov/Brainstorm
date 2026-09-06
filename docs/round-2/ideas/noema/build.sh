#!/usr/bin/env sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
for tool in python3 latexmk pdflatex; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "Missing required build tool: $tool" >&2
        exit 1
    fi
done
python3 certificate_demo.py --output experiment-results.json
latexmk -pdf -interaction=nonstopmode -halt-on-error noema.tex
