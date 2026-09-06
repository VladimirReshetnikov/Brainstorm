#!/usr/bin/env bash
# Rebuild the article and the finite tests. This does not check the Lean file.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v latexmk >/dev/null || { echo 'latexmk is required.' >&2; exit 1; }
command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 1; }
mkdir -p build
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build schist.tex
cp build/schist.pdf schist.pdf
python3 check_examples.py > checks.log 2>&1
cat checks.log
printf '\nBuilt schist.pdf; finite Python checks completed. Lean was not invoked.\n'
