# Round 4 unified report

`unified_report.tex` (with `appendix.tex`) is a self-contained synthesis of the nine
round-4 reports under `docs/round-4/ideas/`, rendered to `unified_report.pdf`.

## Contents

- `unified_report.tex`, `appendix.tex`, `unified_report.pdf`: the report.
- `tools/make_tables.py`: the data behind every table (commitment matrix, negative
  suite, question tally, compiled Lean files, companion reruns). Running it regenerates
  the CSV files and the `*_rows.tex` fragments the report inputs, and prints the counts
  quoted in the text.
- `feature_matrix.csv`, `negative_suite.csv`, `question_tally.csv`, `lean_files.csv`,
  `new_experiments.csv`, `companion_runs.csv`, and the generated `matrix_rows.tex`,
  `question_rows.tex`, `lean_rows.tex`, `run_rows.tex`, `suite_rows.tex`.
- `experiments/lean/`: the twenty Lean files shipped by the nine reports, copied verbatim
  and renamed `<Report>__<path>.lean`, each with the compiler log of this review's run;
  `summary.txt` with exit codes, elapsed milliseconds and diagnostic counts;
  `clover/` (Clover's core compiled to an olean and its generated examples checked
  against it); `patched/` (Heather's one failing export with its trailing `omega`
  removed, which then compiles); and the two files written here, `ListImage.lean`
  (core Lean, the four list-length frames) and `FreyRoutes.lean` (Mathlib; the generic
  routes exported by Laurel, Bryony and Sorrel instantiated with the round-3 Frey
  arithmetic), with their logs.
- `experiments/lean/codex/`: the seven follow-up Lean files of the parallel synthesis
  (`docs/round-4/synthesis/`) recompiled here, with logs and `summary.txt`.
- `experiments/companions/`: one log per companion command rerun by this review and
  `summary.txt` with exit codes and elapsed times.

The report's Section 10 reconciles this review with the parallel synthesis under
`docs/round-4/synthesis/`, whose review memos corrected several counts of the first
version of this report (four list theorems, not five, and not axiom-free; thirteen
generic export files, not fourteen; three cast identities and one conjunction in
`FreyRoutes.lean`) and whose adversarial probes are families S53–S57 of the suite.

## Reproducing the Lean runs

From a checkout of ProveIt at commit 24ce8bd7 (toolchain `leanprover/lean4:v4.32.0`):

    lake env lean <path-to>/experiments/lean/<File>.lean

The five Heather files and `FreyRoutes.lean` import Mathlib and take minutes on a cold
import. `Clover__companion__GeneratedExamples.lean` needs `CloverCore.olean` on
`LEAN_PATH`; `lean -o` refuses output paths outside the ProveIt root, so build it from a
subdirectory of that root.

## Reproducing the companion runs

Copy each report's archive to a scratch directory (several rewrite their result files)
and run the commands in `experiments/companions/summary.txt`. Heather's
`use_site_demo.py` needs `PYTHONUTF8=1` on a Windows default code page.

## Building the PDF

    sh build.sh

or `python tools/make_tables.py` followed by
`latexmk -pdf -interaction=nonstopmode -halt-on-error unified_report.tex`.
