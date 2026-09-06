#!/usr/bin/env sh
# Build the self-contained article and copy the PDF beside the TeX source.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
mkdir -p build
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error karst.tex
elif command -v pdflatex >/dev/null 2>&1; then
  for pass in 1 2 3; do
    pdflatex -output-directory=build -interaction=nonstopmode -halt-on-error karst.tex
  done
else
  printf '%s\n' 'Install pdfLaTeX (and preferably latexmk) before building.' >&2
  exit 1
fi
if grep -E 'Undefined control sequence|There were undefined references|Overfull' build/karst.log; then
  printf '%s\n' 'The build has unresolved references or overflowing content; inspect the log.' >&2
  exit 1
fi
cp build/karst.pdf karst.pdf
printf '%s\n' 'Built karst.pdf'
