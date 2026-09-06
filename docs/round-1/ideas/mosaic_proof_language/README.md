# Mosaic: Mathematical Intent, Explicit Obligations, and Kernel-Checked Proof

A proof-language design study grounded in ProveIt and Leant.
Research snapshot: September 5, 2026.

## Contents

- mosaic.pdf: the 32-page article, including references and appendices.
- mosaic.tex: self-contained LaTeX source; bibliography is included inline.
- sources.json: bibliographic URLs and pinned repository revisions.
- build.sh: a small build helper using latexmk and pdfLaTeX.
- SHA256SUMS: checksums of the other files in this directory.

## Rebuild

Run `bash build.sh` in this directory, or:

    latexmk -pdf -interaction=nonstopmode -halt-on-error mosaic.tex

A reasonably complete TeX Live or MiKTeX installation is required. The source
uses standard packages and Latin Modern fonts; no external images or separate
bibliography file are required. No font files are distributed in the archive.

## Status and interpretation

This is a design proposal, not an implemented proof language. All Mosaic
listings are illustrative syntax. The article gives mathematical derivations,
a core semantic model with a conditional soundness argument, a Lean-first
architecture, a Leant integration design, and an evaluation roadmap.

No Lean compilation, machine-checked replacement of a repository proof,
benchmark, or user study was performed for this article. The PDF was compiled
and visually inspected. The repository study used selected files and sections,
not a whole-repository correctness or security audit.

The main mathematical source files are SharpFlatness.lean, Regularity.lean,
and FloorSqrtSum.lean. The double-counting proof in the article is a proposed
alternative to the source's successor-step proof, not a description of it.

ProveIt revision: 24ce8bd743eaab64a91ce90725ea00f498d319d2
Leant revision:   c36adf114035fb2fba6c276b63944cc613b31668

The original repositories and prior-art sources are cited in the PDF and
listed in sources.json. No third-party repository source archive is bundled.
