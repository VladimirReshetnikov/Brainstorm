# Motive: Concise Mathematical Reasoning with Kernel-Checked Elaboration

A language-design study prepared for Vladimir Reshetnikov, dated September 5, 2026.

## Contents

- `motive.pdf`: the 30-page article, with linked contents, bibliography, worked examples, semantics, architecture, evaluation plan, and appendices.
- `motive.tex`: self-contained LaTeX source, including the bibliography and TikZ architecture diagram.
- `sources.json`: pinned repository revisions, inspected files/ranges, and external primary references.
- `SHA256SUMS.txt`: SHA-256 checksums for the other package files.

## Rebuilding the PDF

Use a reasonably complete TeX Live or MiKTeX installation. From this directory, run:

```sh
pdflatex -interaction=nonstopmode -halt-on-error motive.tex
pdflatex -interaction=nonstopmode -halt-on-error motive.tex
```

Alternatively, run `latexmk -pdf motive.tex` if latexmk is installed.
No BibTeX invocation, external graphics, shell escape, or custom font files are required. The document uses standard packages including amsmath, amssymb, amsthm, mathtools, lmodern, microtype, geometry, listings, booktabs, tabularx, longtable, enumitem, TikZ, tcolorbox, fancyhdr, xurl, hyperref, and bookmark.

## Scope and verification status

Motive is a provisional design name, not a claim of an existing or uniquely named product. The proposed syntax and service interfaces are illustrative. The paper reviews source at explicitly recorded ProveIt and Leant revisions, but does not claim to rebuild either repository, execute their proof searches, or provide a working Motive compiler. The relative soundness argument is a mathematical design argument, not a machine-checked metatheory.

The LaTeX source was compiled to PDF; all pages were rendered for visual review, and the final compilation had no LaTeX warnings. There are no measured compression, performance, or usability results. The benchmark and conformance sections are prospective plans.
