# MathStep: A Proof Language of Mathematical Steps

A design grounded in ProveIt and Leant
Prepared for Vladimir Reshetnikov, 5 September 2026

## Contents

- `MathStep.pdf`: the 42-page article.
- `MathStep.tex`: complete, self-contained LaTeX source.
- `SOURCE_MANIFEST.json`: pinned repository revisions and the reviewed source files.

## Build the PDF

Use a TeX distribution with LuaLaTeX and latexmk:

```sh
latexmk -lualatex -interaction=nonstopmode -halt-on-error MathStep.tex
```

The bibliography and TikZ diagram are embedded in the source. No external
bibliography database or image files are needed. The document uses Linux
Libertine O, Lato, DejaVu Sans Mono, and Latin Modern Math. These fonts must be
installed locally; font files are not included in this archive. The relevant
font declarations near the start of MathStep.tex can be changed to alternatives
available in your TeX installation.

## Scope

MathStep is a proposed Lean-hosted declarative proof language, not an implemented
compiler. The article reviews four ProveIt modules and selected Leant synthesis
and verification boundaries, gives worked mathematical reconstructions, specifies
a core language and conditional soundness argument, and develops an implementation
and evaluation plan. Proposed syntax is identified as such. No full repository
build, prototype compiler execution, or comparative performance benchmark was
performed for this article.

The PDF was compiled with LuaLaTeX and checked for missing references, missing
citations, missing glyphs, overflow, and page layout. The bibliography contains
23 entries with source links. The article's appendix maps the worked examples
to exact repository declarations.

## Pinned repositories

ProveIt: 24ce8bd743eaab64a91ce90725ea00f498d319d2
Leant:   c36adf114035fb2fba6c276b63944cc613b31668

The inspected ProveIt revision specifies leanprover/lean4:v4.32.0. This is the
project's pinned toolchain, not a claim about the latest Lean release.
