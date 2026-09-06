#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error basalt.tex > "build-pass-${pass}.txt"
done
if grep -E 'There were undefined references|Citation .* undefined|Reference .* undefined|Overfull \\[hv]box|Missing character:' basalt.log; then
  echo 'Build needs citation or layout review.' >&2
  exit 1
fi
printf 'Built basalt.pdf successfully.\n'
