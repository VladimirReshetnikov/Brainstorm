# Mathematical Intent, Formal Evidence

A proof-language design informed by ProveIt and Leant.

## Contents

- article.pdf: 35-page article (including cover, contents, and references).
- article.tex: self-contained LaTeX source with embedded bibliography.
- SOURCE_MANIFEST.json: the repository revisions and source files used.
- README.md: this file.

## Build

With TeX Live and latexmk installed, run:

    latexmk -pdf -interaction=nonstopmode -halt-on-error article.tex

The document uses standard packages listed in its preamble and Latin Modern
fonts from the TeX distribution. No separate bibliography processor, external
figures, external source files, or bundled font files are required.

## Scope and status

The article is a language-design proposal based on selected source inspection.
Its mathematical reconstructions are explained in the text. MPL is proposed
syntax, not an implemented compiler. No Lean build, independent kernel replay
of the repository, compiler verification, performance benchmark, or user study
was performed for this article. The accompanying PDF was compiled from the
included LaTeX and visually reviewed.

The reviewed ProveIt revision is 24ce8bd743eaab64a91ce90725ea00f498d319d2.
The final Leant README and selection-wrapper inspection uses
3a40904be8a410d832d9ab6900b3d3e7b425eccb. The earlier detailed internals
inspection uses c36adf114035fb2fba6c276b63944cc613b31668.

The document is dated September 5, 2026, Pacific time. A source revision or PDF
creation timestamp on September 6 UTC is compatible with that local date.
