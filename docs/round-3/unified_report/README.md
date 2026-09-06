# Round 3 unified report

`unified_report.tex` (with `appendix.tex`) is a self-contained synthesis of the nine
round-3 reports under `docs/round-3/ideas/`, rendered to `unified_report.pdf`.

## Contents

- `unified_report.tex`, `appendix.tex`, `unified_report.pdf`: the report.
- `tools/make_tables.py`: the data behind every table (commitment matrix, negative
  suite, question tally, compiled Lean cores). Running it regenerates the CSV files
  and prints the counts quoted in the text.
- `feature_matrix.csv`, `negative_suite.csv`, `question_tally.csv`, `lean_cores.csv`.
- `experiments/lean/`: the seven shipped Lean cores as compiled by this review
  (`FiberAx`, `MoraineAx`, `TephraAx` have `#print axioms` lines appended; the other
  four are verbatim), the Mathlib supply probe `Supply3.lean` (whose final `mvcgen`
  example fails by design), the kernel-checked Frey exact-division file
  `FreyExact.lean`, the parallel synthesis's `SynthesisChecks.lean` and
  `AdequacyChecks.lean` recompiled here, and the complete compiler log of every run.

The report's Section 10 reconciles this review with the parallel synthesis under
`docs/round-3/synthesis/`, whose incorporation memo corrected several claims of the
first version of this report.

## Reproducing the Lean runs

From a checkout of ProveIt at commit 24ce8bd7 (toolchain `leanprover/lean4:v4.32.0`):

    lake env lean <path-to>/experiments/lean/<File>.lean

The two files importing Mathlib take several minutes on a cold import.

## Building the PDF

    sh build.sh

or `latexmk -pdf -interaction=nonstopmode -halt-on-error unified_report.tex`.
