# Nine Blueprints for a Mathematician's Proof Language over Lean

A unified review, convergence analysis, and assessment of the nine
independent design reports under `docs/ideas` (MathStep, Contour, Loom,
MPL, Mosaic, Motive, Outline, Reason, Spine).

## Contents

- `unified_report.pdf` — the review.
- `unified_report.tex` — self-contained LaTeX source (embedded bibliography,
  no external figures, Latin Modern fonts only).
- `feature_matrix.csv` — the 40-commitment × 9-report matrix from Section 4
  (`Y` explicit, `P` partial/implied, `N` absent).
- `tools/audit_proveit.py` — heuristic text-level tactic-classification audit
  of a Lean corpus, used in Section 3.
- `tools/audit_results.json`, `tools/audit_summary.txt` — its output on the
  ProveIt `Analysis/FabiusFunction/Lean/FabiusFunction` subtree (1,004 files)
  and on the 23 files sampled by the reports.
- `build.sh` — builds the PDF with `latexmk`.

## Building

    latexmk -pdf -interaction=nonstopmode -halt-on-error unified_report.tex

or run `bash build.sh`. Requires a standard TeX Live / MiKTeX with amsmath,
booktabs, tabularx, longtable, xcolor, enumitem, listings, fancyhdr,
titlesec, needspace, xurl, tikz, tcolorbox, pifont, hyperref, bookmark.

## Reproducing the audit

    python tools/audit_proveit.py <ProveIt>/Analysis/FabiusFunction/Lean/FabiusFunction \
        --sample <the 23 files listed in Appendix C of the report>

The audit was run against a local ProveIt checkout at commit
`7c4e3f109405b9805b35d27ae96bf09c7ee5f3d5` (newer than the commit
`24ce8bd7...` the reports pin; all sampled files are present at both).
It is a heuristic over source text, not an InfoTree analysis; see
Section 3.4 and Appendix C of the report for its limitations.

## Status

This is a synthesis of design documents plus a corpus measurement. No proof
language was implemented and no Lean code was compiled for it.
