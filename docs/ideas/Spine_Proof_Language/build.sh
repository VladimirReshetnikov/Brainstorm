#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
command -v xelatex >/dev/null 2>&1 || {
  printf '%s\n' 'XeLaTeX was not found on PATH. See README.md for prerequisites.' >&2
  exit 1
}
mkdir -p "$root/.build"
for pass in 1 2 3; do
  printf 'XeLaTeX pass %s/3\n' "$pass"
  xelatex -interaction=nonstopmode -halt-on-error \
    -output-directory="$root/.build" "$root/Spine_Proof_Language.tex"
done
cp -- "$root/.build/Spine_Proof_Language.pdf" "$root/Spine_Proof_Language.pdf"
printf 'Built %s\n' "$root/Spine_Proof_Language.pdf"
