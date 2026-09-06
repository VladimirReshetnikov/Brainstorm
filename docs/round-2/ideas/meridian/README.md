# Meridian: A Mathematical Language with Certified Computation

A second-iteration design proposal for Vladimir Reshetnikov's Brainstorm campaign.
Prepared September 5, 2026 (Pacific time).

## Files

- `meridian.pdf`: the rendered article.
- `meridian.tex`: self-contained LaTeX source with embedded bibliography.
- `check_examples.py`: exact-arithmetic sanity checks for worked examples.
- `example_checks.json`: recorded outcome of those checks (27/27 passed).
- `source_manifest.json`: pinned repository revisions, reviewed source paths, and
  inspection boundaries.
- `build.sh`: PDF build script.
- `SHA256SUMS`: checksums of the deliverable files other than this checksum file.

## Build the PDF

Use a standard TeX Live or MiKTeX installation containing pdfLaTeX, Latin Modern,
AMS mathematics, microtype, geometry, booktabs, longtable, tabularx, ragged2e,
listings, enumitem, fancyhdr, titlesec, needspace, tocloft, TikZ/PGF, tcolorbox, xurl,
and hyperref. These are ordinary distribution packages; no private fonts or
external image files are required.

On a Unix-like system:

```sh
sh build.sh
```

Or invoke the command directly (including on Windows with an installed TeX
system):

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error meridian.tex
```

If latexmk is unavailable, run pdfLaTeX three times to resolve references and
the table of contents. This package was compiled with pdfLaTeX. Exact PDF bytes
may vary between TeX distributions; the source and semantics do not depend on
external build downloads.

## Run the arithmetic checks

Python 3.10 or newer is sufficient; no third-party Python packages are needed.

```sh
python3 check_examples.py --json example_checks.json
```

The recorded execution reports `27/27 exact-arithmetic checks passed`. Checks
include polynomial identities, Lambert recurrence coefficients, a Catalan jet
residual, rational square-root enclosures, and selected negative neighbors.

## Evidence status

This is a proposal, not an implemented proof language or a deployed verified CAS.
All Meridian surface syntax and protocol sketches are explicitly illustrative.
The repository review was static and pinned to the revisions in the manifest.
ProveIt and Leant were not built or run during this review, and no newly written
Lean theorem in this package has been kernel-checked. The Python program is not
a formally verified checker; its finite tests do not establish the correctness
of an implementation of Meridian. Universal mathematical arguments are given in
the article itself.

The 23 adversarial implementation tests in the article are proposed acceptance
requirements, separate from the 27 executed arithmetic checks.

Repository URLs in the bibliography point to exact revisions. Official manuals
are cited as accessed on September 5, 2026; moving documentation does not imply
compatibility with a repository's pinned toolchain.
