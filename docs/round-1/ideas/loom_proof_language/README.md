# Loom: A Contract-Based Language for Human-Scale Formal Proofs

A design study prepared for Vladimir Reshetnikov, September 5, 2026.

## Contents

- `loom.pdf`: the typeset article (30 pages, including the cover and references).
- `loom.tex`: the complete, self-contained LaTeX source.
- `sources.json`: repository snapshots, inspected source files, and primary references.

## Rebuilding

Use a reasonably recent TeX Live or MiKTeX installation with pdfLaTeX and latexmk:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error loom.tex
```

Alternatively, run `pdflatex loom.tex` repeatedly until cross-references stabilize.
The bibliography is embedded in the source, so BibTeX and Biber are not required.
The article uses standard TeX packages, including newtx, inconsolata, microtype,
amsthm, mathtools, listings, booktabs, tabularx, longtable, enumitem, fancyhdr,
xurl, hyperref, bookmark, needspace, and etoolbox. No external images or downloaded
source files are required to build the PDF.

## Scope and status

The proposed Loom syntax and adapter interfaces are design sketches, not an
implemented compiler or a published API. The article supplies mathematical
reconstructions and conditional architectural arguments, not a machine-checked
soundness proof of an implementation. No Lean build, Leant test suite, or
compression/performance benchmark was run for this study.

The ProveIt review is a purposive sample of three modules. Leant observations
come from the relevant documentation and its verification scheduler source.
Exact repository revisions are recorded in `sources.json` and the article.
The existing mathematical results are attributed to their source development;
no novelty claim is made for those results.

The PDF was compiled successfully, checked for unresolved references and layout
warnings, and visually reviewed after rendering. These document checks do not
constitute verification of any proposed proof-language implementation.
