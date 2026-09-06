# Nine Workbenches: unified review of the round-2 reports

`unified_report.tex` / `unified_report.pdf` is a self-contained synthesis of the
nine second-round proposals under `docs/round-2/ideas/` (Locus, Accord, Cadence,
Concord, Facet, Meridian, Noema, Prism, Vantage). It summarizes what the first
round established, tallies 58 design commitments and the answers to the 22
round-1 questions across the nine reports, consolidates their nine adversarial
suites into 51 canonical mutations, checks the reports' toolchain assumptions
by running Lean, and closes with an assessment, a recommendation, per-report
cards, and questions for a third round.

## Files

| File | Content |
|---|---|
| `unified_report.tex`, `unified_report.pdf` | the report (embedded bibliography, standard packages only) |
| `feature_matrix.csv` | 58 commitments x 9 reports (Y explicit, P partial, N absent) |
| `negative_suite.csv` | 51 canonical mutations with the identifier of each report's own table row |
| `question_tally.csv` | modal answer and variation for each of the 22 questions |
| `tools/make_tables.py` | generates the three CSVs and prints the LaTeX table bodies |
| `experiments/lean/` | the Lean experiment files and verbatim compiler logs (see its README) |
| `build.sh` | `latexmk -pdf` wrapper |

## Build

    ./build.sh
    python tools/make_tables.py
