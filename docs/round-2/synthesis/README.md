# Mathematical Objects, Certified Computation

[Read the report](unified-report.pdf) · [TeX source](unified-report.tex) ·
[Convergence map](convergence.json) · [Validation receipt](validation.json)

This **29-page, self-contained report** evaluates all nine second-round proposals:
Accord, Cadence, Concord, Facet, Locus, Meridian, Noema, Prism, and Vantage.
It explains the relevant inherited ideas directly, so neither first-round
synthesis is a prerequisite.

The report contains an executive assessment, distinct contributions and limits
for each proposal, a common semantic model, worked mathematical cases, Leant
provider integration principles, a staged implementation and evaluation plan,
ten next-iteration questions, and all 22 earlier questions restated with current
answers. The appendix gives 72 proposal-level convergence cells; the JSON map
preserves 241 supporting source citations and their qualifications.

The current branch was fast-forwarded to fetched `main` at
`f333ff6cefc8b1f5c9aae79613d10ef95a7ba928` before synthesis. That import renamed
the earlier material under `docs/round-1/` and supplied the new packages under
`docs/round-2/ideas/`. This work changes the new synthesis package and repository
navigation only. Original reports and `C:\ProveIt` / `C:\Leant` remain read-only.

## What the evidence establishes

- **Source provenance:** [source-register.json](source-register.json) pins all
  70 tracked files in the nine input packages to exact Git blobs and records
  separate SHA-256 hashes for checkout bytes. Prior syntheses are classified
  separately. Input PDF page counts are metadata checks, not assertions that
  their PDF and TeX were rebuilt together during this review.
- **Critical review:** three [reading memos](review-notes) cover the full reports,
  mathematics, companions, source qualifications, and discriminating experiments.
  All nine explicitly propose the eight broad commitments. This agreement is
  correlated by shared sources and is not independent empirical validation.
- **Companion reproduction:** all nine Python programs completed successfully
  under Python 3.14.4 with bytecode disabled. Their evidence is retained in the
  three named directories under [evidence](evidence). Counts are deliberately
  not aggregated: Accord 25 test methods; Cadence 267 checks; Concord 459 checks;
  Facet 1,100 checks; Locus 24 test methods; Meridian 27 tests; Noema 25 test
  methods; Prism 2,475 checks; Vantage 3,013 checks in ten groups. Several test
  methods internally enumerate many instances.
- **Additional finite checks:** [the synthesis math script](evidence/math/synthesis-math-checks.py)
  checks six groups of exact examples, including the nonunit residual, derivative
  precision, coefficient recurrences, and reversed telescoping bounds. These are
  finite sanity checks, not generic theorem proofs.
- **Focused Lean evidence:** [eight declarations](evidence/lean/FocusedChecks.lean)
  establish guarded real cancellation and the fixed-index binomial counterexample.
  Lean 4.32.0 accepted them using existing cached mathlib dependencies. Axiom
  audits report only `propext`, `Classical.choice`, and `Quot.sound`.
  [The receipt and reproduction instructions](evidence/lean/README.md) record
  exact versions, command, input hashes, and output. No repository build or
  dependency download occurred.
- **This PDF:** three serial strict pdfLaTeX passes, checks for unresolved
  references/missing glyphs/overflow, source-and-PDF hash binding, all 29 pages
  rendered and visually reviewed, plus larger views of the residual theorem,
  calculus, and convergence appendix.

No implemented proof language, Lean-verified CAS subsystem, end-to-end Leant
integration, universal formalization of the report's mathematics, or measured
productivity improvement is claimed. Leant implementation observations inherited
from earlier source reviews remain attributed historical evidence.

## Build and inspect

Requirements: PowerShell, pdfLaTeX with the listed TeX packages, Python with
`pypdf` and Pillow, and Poppler (`pdftoppm`). The successful build used MiKTeX
pdfTeX 1.40.29, Python 3.14.4, and pypdf 6.13.2.

From the repository root:

```powershell
& docs/round-2/synthesis/build.ps1
python -B docs/round-2/synthesis/scripts/verify_sources.py
python -B docs/round-2/synthesis/scripts/render_review.py
```

The build runs exactly three strict passes and copies the PDF only after log and
input-stability checks. Both TeX inputs (`unified-report.tex` and the generated
`crosswalk-table.tex`) are bound in `.build/build-receipt.json`. Intermediates
and page images remain in ignored `.build/` and `.qa/` directories.

The committed `evidence/pdf-build-receipt.json` and `pdf-build-log.txt` preserve
the final reviewed build. `evidence/visual-review.json` identifies the PDF and
pages actually reviewed. After a rebuild, review the new rendered PDF and update
these evidence files before running the document verifier; it intentionally
rejects a visual-review receipt for a different PDF.
The local `.gitattributes` preserves exact artifact bytes, including tool-output
line endings, so committing and checking out the evidence does not invalidate
its recorded hashes. Captured evidence retains original tool whitespace.

```powershell
python -B docs/round-2/synthesis/scripts/verify_report.py
```

This writes `validation.json` after checking source provenance, references and
local links, the 72-cell appendix, PDF content and build hashes, Lean source/log
receipt consistency, and visual-review coverage. It does not rerun Lean or the
companions and does not prove the mathematical prose. It requires the pinned
Git objects and records byte-level checkout identity separately from canonical
Git identity; line-ending changes can require a new checkout receipt.

The isolated Lean rerun is optional and has its own existing-cache prerequisites:

```powershell
& docs/round-2/synthesis/evidence/lean/check.ps1
```

Read its README before rerunning. It uses a direct Lean invocation with cached
imports and writes only its local log/receipt. The companion commands are in the
lane receipts or adjacent README; they direct generated output into synthesis
evidence directories rather than overwriting the input packages.

The crosswalk table can be regenerated from `convergence.json` using
`evidence/facet-locus-meridian/generate_crosswalk_table.py`. Regenerating source
registers is a deliberate provenance update, not a way to suppress a failed
source-identity check. Some original READMEs name checksum files absent from the
import; the register captures the files actually present and leaves the originals
unchanged.
