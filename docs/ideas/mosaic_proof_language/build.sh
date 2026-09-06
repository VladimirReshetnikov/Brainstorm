#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if ! command -v latexmk >/dev/null 2>&1; then
  printf '%s\n' 'latexmk is required; install it with your TeX distribution.' >&2
  exit 1
fi
latexmk -pdf -interaction=nonstopmode -halt-on-error mosaic.tex
