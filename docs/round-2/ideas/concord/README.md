# Concord: A Query-Directed Proof Language with a Verified Symbolic Core

Second-iteration proposal prepared for Vladimir Reshetnikov, 5 September 2026
Pacific time. The PDF contains 37 pages, including references and appendices.

## Main files

- `concord.pdf`: the complete article.
- `concord.tex`: self-contained LaTeX source, with embedded bibliography.
- `source-register.json`: exact repository revisions, inspected source ranges,
  public references, and review limitations.
- `checks.py`: standard-library Python exact-arithmetic sanity checks.
- `checks.json`: supplied results; all 459 finite checks passed.
- `validation.json`: build, rendering, and validation scope.
- `build.sh`: convenience build script for a Unix-like shell.
- `SHA256SUMS`: hashes of the supplied files, excluding the checksum file itself.

## Main proposal

Concord makes a mathematically specified query the common interface for proof
steps, exact symbolic computation, approximate computation, and data selection.
Its answers retain the relation actually established, including domain, branch,
precision, locality, and residual obligations. The article develops definition
packages, observation-directed representations, a finite-jet precision calculus,
and a residual certificate for an implicit formal series. Worked examples cover
binomial inversion, autonomous derivatives, Abel coefficients, root selection,
radical denesting, complete solution sets, and numerical enclosures.

Both requested Brainstorm synthesis reports were read closely. Direct code
review was limited to the committed ProveIt and Leant sources listed in the
source register. The nine individual first-round proposals were not each
independently reread. Uncommitted working-tree features described by the
syntheses are attributed to those reports, not presented as newly executed.

## Rebuild the PDF

Use a reasonably complete TeX Live or MiKTeX installation with `latexmk`,
Latin Modern, TikZ, tcolorbox, listings, and the standard packages named in the
source. No downloaded fonts or external graphics are needed.

    latexmk -pdf -interaction=nonstopmode -halt-on-error concord.tex

Alternatively, run `pdflatex` repeatedly until references settle. The supplied
`build.sh` keeps LaTeX intermediate files under `.build/` and copies the PDF here.
PDF metadata, TeX package versions, and layout may change on another toolchain;
bit-for-bit reproducibility is not claimed.

## Run the finite checks

Python 3.10 or later; no third-party Python packages are needed.

    python3 checks.py --output checks.json

The checks comprise 441 finite binomial-kernel instances, five implicit-series
residual coefficients, four Abel coefficient polynomial identities, seven
negative neighbors, and two exact root-enclosure inequalities. Any failed check
raises an exception and stops the program.

These are exact finite sanity checks, NOT formally verified algorithms, Lean
proofs, a language implementation, or a proof of a universal theorem. The
mathematical propositions in the article have paper proofs. No ProveIt or Leant
build was run during this review, and no Concord compiler was implemented.

## Validation of the delivered document

The source compiled with pdfTeX through latexmk. Its final log contained no
LaTeX warnings, overfull/underfull boxes, missing glyphs, or unresolved references.
Every PDF page was rasterized; contact sheets and selected full-size pages were
visually reviewed. Original repository sources, first-round report files, and
font files are not redistributed in this archive.
