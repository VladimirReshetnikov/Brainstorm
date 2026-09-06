#!/usr/bin/env bash
# Rebuild the reference results and the article; no Lean toolchain is required.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v python3 >/dev/null 2>&1 || { echo 'python3 is required.' >&2; exit 1; }
command -v pdflatex >/dev/null 2>&1 || { echo 'pdflatex is required.' >&2; exit 1; }
python3 companions/trellis_reference.py --output companions/results.json
for pass in 1 2 3; do
  echo "pdfLaTeX pass ${pass}/3"
  pdflatex -interaction=nonstopmode -halt-on-error trellis.tex > "build-pass-${pass}.log"
done
if grep -Eq 'Overfull \\hbox|Overfull \\vbox|Missing character|undefined references|undefined citations|There were undefined|LaTeX Error' trellis.log; then
  echo 'PDF built, but layout/reference checks failed; inspect trellis.log.' >&2
  exit 1
fi
echo 'Built trellis.pdf. Reference tests passed; no Lean compiler or kernel was run.'
echo 'This rebuild does not update the delivered validation.json or SHA256SUMS.'
