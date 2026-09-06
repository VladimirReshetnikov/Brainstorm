#!/bin/sh
set -eu
CDPATH= cd "$(dirname "$0")"
if ! command -v latexmk >/dev/null 2>&1; then
    printf '%s\n' 'latexmk is required. Install it with a TeX distribution.' >&2
    exit 1
fi
latexmk -pdf -interaction=nonstopmode -halt-on-error gneiss.tex
if grep -Eq 'Overfull|Missing character|undefined references|undefined citations|Citation .* undefined|Reference .* undefined|multiply defined' gneiss.log; then
    printf '%s\n' 'Build completed, but the log contains a layout/reference error.' >&2
    exit 2
fi
printf '%s\n' 'Article built: gneiss.pdf'
