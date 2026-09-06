#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "Python 3 is required." >&2; exit 1; }
command -v pdflatex >/dev/null || { echo "pdflatex (TeX Live) is required." >&2; exit 1; }
mkdir -p build
python3 experiments/checks.py > build/results.json
cp build/results.json experiments/results.json
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build obsidian.tex > "build/pass-${pass}.txt" 2>&1 || {
    tail -60 "build/pass-${pass}.txt" >&2
    exit 1
  }
done
cp build/obsidian.pdf obsidian.pdf
printf 'Built obsidian.pdf and reran the executable design probes.\n'
