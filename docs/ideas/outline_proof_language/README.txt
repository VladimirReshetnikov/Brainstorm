PROOFS AT THE SCALE OF IDEAS
An Intent-Directed, Lean-Checked Proof Language
A proposal inspired by ProveIt and Leant
Prepared for Vladimir Reshetnikov — September 5, 2026

CONTENTS
  outline_proof_language.pdf  — the 34-page article
  outline_proof_language.tex  — self-contained LaTeX source
  README.txt                 — this file and build instructions
  SOURCES.txt                — pinned repository paths and external references

STATUS AND SCOPE
Outline is a proposed language design, not an implemented compiler. The source
examples are specifications rather than executable Lean programs. The article
contains mathematical derivations, a paper relative-soundness argument, design
contracts, an implementation roadmap, and an evaluation protocol. It does not
claim empirical compression ratios, runtime improvements, or successful Lean
compilation of the proposed examples.

Selected public source files were reviewed at the commits listed in SOURCES.txt.
Neither repository was rebuilt for this report. The mathematical derivations
were not separately formalized and compiled in Lean during its preparation.
LaTeX compilation, PDF text checks, and visual layout inspection were completed.

BUILDING THE PDF
The bibliography is embedded in the .tex file; no .bib file is required.
With a standard TeX Live installation, run:

  latexmk -pdf -interaction=nonstopmode -halt-on-error outline_proof_language.tex

Alternatively run pdflatex repeatedly until references and contents stabilize:

  pdflatex -interaction=nonstopmode -halt-on-error outline_proof_language.tex
  pdflatex -interaction=nonstopmode -halt-on-error outline_proof_language.tex
  pdflatex -interaction=nonstopmode -halt-on-error outline_proof_language.tex

Required packages include Latin Modern, AMS packages, mathtools, geometry,
microtype, booktabs, tabularx, longtable, enumitem, xcolor, listings, etoolbox,
tcolorbox, fancyhdr, titlesec, xurl, hyperref, and cleveref. No shell escape,
network access, external illustration files, or separate bibliography tool is
needed to compile the article. Font files are not included.

READING MAP
Sections 1–3:   Repository observations and prior art.
Sections 4–5:   Language contract and proposed surface syntax.
Sections 6–9:   Worked mathematics and certified higher-level plans.
Sections 10–12: Core semantics, Leant-inspired synthesis, and trust boundaries.
Sections 13–15: Authoring interface, evaluation, and incremental implementation.
Section 16:    Conclusions.
Appendices:    Source inventory, grammar, evidence states, negative tests.

References in the PDF are clickable. Repository sources are pinned to commits;
online documentation and non-repository references were consulted on the
review date. A moving documentation URL is not a pinned repository dependency.
