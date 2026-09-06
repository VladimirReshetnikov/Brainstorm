# Mathematical Ideas, Checked Evidence

[Read the unified report](unified-report.pdf) · [Edit the TeX source](unified-report.tex)

This 30-page report compares and evaluates all nine proposals under `docs/ideas`, identifies
six shared commitments with a report-by-report evidence crosswalk, distinguishes
policy choices from superficial differences, and proposes a shared implementation
experiment and ten questions for the next iteration. It includes four mathematical
test cases with nearby invalid variants and a substantive review of Leant's
automatic term synthesis and proof tactic suggestions.

The report is a design synthesis and static source review. The proposed language
has not been implemented or benchmarked here. Neither reference repository was
built or modified. Reason's supplied 32-test simply typed companion suite was rerun
successfully; that result is distinct from Lean verification.

## Files and provenance

- `unified-report.tex` and `unified-report.pdf`: complete report, bibliography,
  crosswalk, and architecture diagram. The TeX needs no external figures or BibTeX.
- `convergence.json`: 54 explicit support cells, with source section numbers and
  one-based TeX line ranges. These count textual support, not empirical votes.
- `source-register.json`: input identities, reference repository revisions,
  working-tree distinctions, archived file fingerprints, and documentation URLs.
- `review-notes/`: three independent report-reading memos and two focused Leant
  implementation reviews, with exact source locators and stated limits.
- `evidence/leant-reviewed-source.zip`: only the selected Leant files used in the
  review, plus its license. The archive preserves uncommitted source needed to
  make the review reproducible; it is not a runnable checkout or a build receipt.
- `evidence/repl-protocol-source.zip`: selected cached REPL source and license
  documenting the separate `proofStatus` field. Availability of that cache does
  not establish which backend binary a particular Leant invocation uses.
- `validation.json`: final artifact checks and visual-review record.

Leant's HEAD was `3a40904be8a410d832d9ab6900b3d3e7b425eccb`, but its working tree
contained newer behavioral-synthesis work and a different Djex checkout. Statements
about those files refer to the captured source, not simply to HEAD. The three
ProveIt source spot checks matched committed content at
`7c4e3f109405b9805b35d27ae96bf09c7ee5f3d5` after newline normalization.

## Rebuild and verify

With pdfLaTeX on PATH, run from PowerShell:

```powershell
./build.ps1
python verify_report.py
```

The build uses three serial strict pdfLaTeX passes, disables shell escape, and
copies the PDF only after the final log has no unresolved references/citations,
missing glyphs, or overfull boxes. Standard TeX packages and Latin Modern fonts
are used; no network access or custom font files are required for the document
once the TeX packages are installed. `verify_report.py` requires `pypdf` and checks
source identities, local links, citations, archive integrity, and extracted PDF
content. It does not replace visual inspection.

For layout review, render all pages with Poppler, for example:

```powershell
New-Item -ItemType Directory -Force .qa | Out-Null
pdftoppm -r 85 -png unified-report.pdf .qa/page
```

Inspect every page, with denser mathematical, table, and bibliography pages at
higher resolution. `.build/` and `.qa/` are intentionally untracked intermediates.

`capture_sources.py` is a separate, deliberate provenance-refresh utility. It
reads the explicitly listed files under `C:/Leant` and `C:/ProveIt`, and the
recorded local REPL cache; it writes only inside this synthesis directory. Do not
run it as part of routine PDF rebuilding: recapturing a moving working tree would
change the evidence associated with the written review.
