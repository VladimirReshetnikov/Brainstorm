# Facet: Mathematical Objects, Explicit Views, and Certified Computation

A second-round proof-language and verified-CAS design article prepared for
Vladimir Reshetnikov, dated 5 September 2026 (Pacific time).

## Contents

- `facet.pdf`: the rendered, 43-page article.
- `facet.tex`: self-contained LaTeX source, with embedded bibliography and TikZ diagram.
- `reference_checks.py`: standalone exact-arithmetic checks, requiring Python 3.9+.
- `reference-checks.json`: results from the delivered run (3,013 checks, ten groups).
- `source_manifest.json`: exact repository revisions, inspected files, and external references.
- `build-report.json`: PDF/source hashes and document-build validation results.
- `build.sh`, `build.ps1`: rebuild scripts for a shell or PowerShell.
- `SHA256SUMS`: checksums for the other files in the bundle.

The article distinguishes exact presentations, restricted observations, and
one-way abstractions; develops guarded and precision-sensitive view composition;
specifies verified algorithms and certificate-based CAS computation; and proposes
a Lean-owned boundary for Leant synthesis and exact displayed-edit replay.

Worked examples cover normalized EGF coefficients and Spivey's identity,
Touchard polynomial recurrence, local differentiation, binomial inversion,
guarded rational simplification, Sturm root isolation, and radical denesting.
The appendices answer all 22 next-round questions in the two synthesis reports
and specify 26 positive/negative-neighbor integration tests.

## Build

Install a LaTeX distribution with the ordinary packages used by `facet.tex`
(including Latin Modern, AMS packages, stmaryrd, TikZ, tcolorbox, listings,
hyperref, bookmark, and xurl). No external graphics or bibliography database
is required.

On a Unix-like shell:

```sh
./build.sh
```

On Windows with PowerShell:

```powershell
.\build.ps1
```

Or run the commands directly:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error facet.tex
python reference_checks.py --output reference-checks.json
```

Without `latexmk`, run `pdflatex` three times to resolve the table of contents,
references, and bookmarks. PDF byte hashes can change on rebuild because of
build timestamps and TeX-distribution differences; the supplied checksums apply
to the delivered files.

## Evidence status

This is a technical proposal, not an implemented Facet compiler. Illustrative
language syntax and proposed Lean interfaces are specifications. The repository
review was static, at the recorded revisions; no ProveIt build, Leant backend
run, or Lean proof compilation was performed for this article.

The companion checks use exact integers and rational arithmetic. They check
finite instances and illustrative certificate arithmetic, including an EGF
example in Q[epsilon]/(epsilon^2). They are not formally verified checkers and do
not turn finitely many examples into universal proofs. The paper gives the
mathematical arguments separately. The 26 integration tests in Appendix B are
proposed requirements for an implementation, not tests claimed to have run.

The delivered PDF was compiled with resolved references and no overfull or
underfull box warnings, then visually inspected. `build-report.json` records
validation of this delivered version; rebuilding does not automatically rewrite
that report or `SHA256SUMS`.
