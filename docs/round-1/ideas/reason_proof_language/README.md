# Reason: A Proof Language of Mathematical Intent

A design study grounded in selected ProveIt examples and Leant's synthesis,
verification, and rewrite-design material. Prepared 5 September 2026.

## Contents

- `reason.pdf`: the 32-page article, including a contents page and references.
- `reason.tex`: complete LaTeX source with an embedded bibliography.
- `supplement/toy_checker.py`: a small executable evidence-boundary model.
- `supplement/test_toy_checker.py`: 32 regression tests for that model.
- `supplement/test-results.txt`: the test transcript from this session.

## Status and scope

Reason is a proposed language, not an implemented Lean extension. Its surface
syntax is illustrative. The article includes mathematical proofs and a relative
soundness argument, but does not claim a mechanized metatheory, a whole-repository
audit, Lean compilation of the examples, or measured formalization speedups.

The Python companion checks simply typed lambda terms with products. It is NOT a
Lean kernel, a dependent type theory, a natural-language parser, or a security
boundary. All 32 included tests passed. Those tests validate only the small
model's tested behavior; they do not validate a complete Reason implementation.

No Lean executable was available in this session, and neither repository was
compiled. The source review used selected files on `main` as accessed on
5 September 2026. No immutable commit identifier was established. The article's
bibliography and Appendix C record the source paths and relevant declarations.

## Rebuild the article

Use XeLaTeX with a reasonably complete TeX Live or MiKTeX installation:

    xelatex -interaction=nonstopmode -halt-on-error reason.tex
    xelatex -interaction=nonstopmode -halt-on-error reason.tex
    xelatex -interaction=nonstopmode -halt-on-error reason.tex

Alternatively:

    latexmk -xelatex -interaction=nonstopmode -halt-on-error reason.tex

No BibTeX, external figures, shell escape, or network access is needed. The source
prefers Linux Libertine O, Liberation Sans, and DejaVu Sans Mono, with Latin Modern
font-file fallbacks. Fonts are not included. Different fonts or TeX distributions
can change pagination. Packages include fontspec, amsmath, amssymb, amsthm,
mathtools, microtype, xcolor, booktabs, tabularx, longtable, enumitem, fvextra,
needspace, etoolbox, titlesec, fancyhdr, hyperref, and xurl.

## Run the companion tests

From this directory, using Python 3.10 or newer:

    python -m unittest discover -s supplement -p 'test_*.py' -v

Only the Python standard library is needed. Tests cover structural proof terms,
type and scope errors, sequential claim assembly, self/forward references,
exact-origin replay, altered certificates, and candidate-budget behavior.

## Attribution

The article contains a small attributed Lean excerpt from ProveIt, whose source
license is MIT No Attribution. Mathematical and architectural source references
are included in the article. The existing Leant native-rewrite study is explicitly
acknowledged as a precursor, not presented as an implementation delivered here.

## PDF validation

The delivered PDF compiled without unresolved references, missing-character
warnings, or overfull boxes in the final XeLaTeX pass. All pages were rendered and
visually inspected in contact sheets, with selected mathematical pages inspected
at full size. The final PDF contains 32 pages.
