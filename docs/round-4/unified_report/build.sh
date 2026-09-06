#!/usr/bin/env sh
# Build the round-4 unified report. Requires a TeX distribution with latexmk.
set -e
cd "$(dirname "$0")"
python tools/make_tables.py
latexmk -pdf -interaction=nonstopmode -halt-on-error unified_report.tex
latexmk -c unified_report.tex
