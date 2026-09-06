# Contour: A Human-Scale Proof Language over Lean

A detailed language-design study prepared for Vladimir Reshetnikov, dated 5 September 2026.

## Contents

- `contour.pdf`: the complete 38-page article.
- `contour.tex`: self-contained LaTeX source, including the bibliography.
- `grammar.ebnf`: the illustrative structural-core grammar from Appendix A.
- `source-manifest.json`: pinned repository revisions, inspected files, and source links.

## Scope and status

The article proposes a Lean-hosted mathematical proof language and develops four worked examples from ProveIt's FabiusFunction development. It discusses Leant integration, typed obligation graphs, theorem-backed mathematical transformations, certificate assembly, semantic ambiguity, proof replay, and an implementation and evaluation plan.

Contour is a design proposal, not an implemented compiler. The proposed proof-language examples are illustrative, not executable Lean code. The paper's certificate-assembly theorem is proved mathematically in the article, not mechanized here. ProveIt and Leant were inspected at the pinned revisions in the manifest; their build and test suites were not rerun. No automation success rate, speedup, or measured compression claim is made.

The EBNF describes the structural core rather than a complete parser. Its mathematical-expression grammar and registered method implementations are intentionally supplied by the proposed host architecture. The article explains the additional surface conveniences used in examples.

## Rebuilding the PDF

Use LuaLaTeX with a reasonably complete TeX Live or MiKTeX installation. The source uses the Linux Libertine O, DejaVu Sans, and DejaVu Sans Mono font families. Font files are not distributed in this archive. Install those families through the usual font or TeX package distribution, or change the three font selections in the preamble.

Run in this directory:

```text
lualatex -interaction=nonstopmode -halt-on-error contour.tex
lualatex -interaction=nonstopmode -halt-on-error contour.tex
lualatex -interaction=nonstopmode -halt-on-error contour.tex
```

No BibTeX run, external figures, shell escape, or network access is required. Additional passes settle the table of contents and cross-references.

## Artifact checks

The supplied PDF was compiled with LuaLaTeX and rendered with Poppler's `pdftoppm` for layout inspection. The final LaTeX log contains no errors, undefined references or citations, missing-character warnings, or overfull/underfull box warnings. These are document-production checks, not a claim of formal verification of the proposed language or its example translations.
