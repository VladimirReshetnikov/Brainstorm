#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build moraine.tex > "build/pass${pass}.txt"
done
cp build/moraine.pdf moraine.pdf
(cd companion && python3 -m unittest -v test_length_contracts.py)
printf '\nArticle rebuilt as moraine.pdf. Lean reference file was not invoked.\n'
