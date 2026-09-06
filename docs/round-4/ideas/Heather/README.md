# Heather: Proof-Carrying Mathematical Interfaces

Fourth-round proof-language proposal, prepared for Vladimir Reshetnikov,
6 September 2026.

## Main deliverables

- `Heather.pdf`: the article.
- `Heather.tex`: self-contained LaTeX source with embedded bibliography.
- `companion/`: executed Python reference model, 18-test suite, five source
  examples, certificate data, and generated ordinary Lean proof candidates.
- `source_manifest.json`: source revision and document provenance ledger.

## Build the article

A standard TeX Live installation with pdfLaTeX, Latin Modern, and the packages
listed in the preamble is sufficient. No custom fonts or external figures are
required.

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error Heather.tex
```

Alternatively, run `pdflatex -interaction=nonstopmode -halt-on-error Heather.tex`
twice (a third pass may be needed after table-of-contents changes).

## Reproduce the experiment

See `companion/README.md`. The delivered run passed all 18 test methods under
Python 3.13.5. The finite test counts are not a count of formally proved theorems.
The written mathematical frame theorem and the executed program are different
forms of evidence.

## Validation boundary

The article was compiled as PDF. The generated Lean files were **not compiled**
in this environment. This package is not a native Lean elaborator, a verified
compiler, or an integration with Leant. It does not claim a new kernel theorem,
a full source-repository build, a productivity result, or a completed user study.
Historical Lean checks reported by the two source syntheses remain attributed to
those reports.

The project proposal recommends an elaborator-level, proof-carrying type interface
first. A kernel refinement primitive is considered as a later, measurement-driven
representation experiment, not asserted to be necessary.
