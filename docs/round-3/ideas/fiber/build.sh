#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode -halt-on-error fiber.tex
pdflatex -interaction=nonstopmode -halt-on-error fiber.tex
pdflatex -interaction=nonstopmode -halt-on-error fiber.tex
