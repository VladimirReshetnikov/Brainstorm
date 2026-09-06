# Spine: A Proof Language for Mathematical Intent

A source-driven language-design article based on selected Lean proofs in
Vladimir Reshetnikov's ProveIt repository and the synthesis architecture of Leant.
Prepared September 5, 2026.

## Contents

- `Spine_Proof_Language.pdf`: the typeset article.
- `Spine_Proof_Language.tex`: complete editable LaTeX source, including bibliography
  and the architecture diagram. No separate figures or bibliography files are needed.
- `build.sh`: three-pass XeLaTeX build for a POSIX shell.
- `build.ps1`: the corresponding PowerShell build.
- `SHA256SUMS.txt`: checksums for the other distributed files.

## Scope

The article proposes a small Lean-compatible core of mathematical proof steps,
contextual obligations, domain methods, typed synthesis, and frozen certificates.
Its worked examples cover iterated Thue–Morse prefixes, characteristic-function
uniqueness under an affine recurrence, and coefficients of formal inverse germs.
It includes a conditional soundness argument, implementation stages, diagnostics,
trust policies, prior art, and a proposed evaluation protocol.

Repository snapshots:

- ProveIt: `24ce8bd743eaab64a91ce90725ea00f498d319d2`.
- Leant: `3a40904be8a410d832d9ab6900b3d3e7b425eccb`.

Exact source paths, inspected ranges, and linked references appear in Appendix C
and the bibliography.

This is a design study, not a completed Spine compiler. Proposed syntax and
pseudocode have not been executed as a proof language. The repository review was
static; the ProveIt and Leant test suites were not rerun. Existing-Lean excerpts
are distinguished from proposed syntax. No empirical compression numbers are
claimed. The PDF was compiled and its page layouts were inspected.

## Building

Use XeLaTeX, not pdfLaTeX. A full TeX Live or comparable installation should supply
`fontspec`, `unicode-math`, `amsmath`, `amsthm`, `mathtools`, `microtype`, `booktabs`,
`longtable`, `tabularx`, `enumitem`, `fvextra`, `tcolorbox`, TikZ, `titlesec`,
`fancyhdr`, `xurl`, `hyperref`, and `bookmark`.

Required fonts are Latin Modern Roman, Latin Modern Math, DejaVu Sans, and DejaVu
Sans Mono. The Latin Modern fonts are addressed by their standard OpenType file
names through the TeX distribution. DejaVu fonts must be discoverable by the font
system. Font files are not included in this archive. The PDF embeds the fonts
needed for ordinary viewing.

From this directory, run `./build.sh` on a POSIX system or `./build.ps1` in
PowerShell. The scripts require `xelatex` on PATH, build temporary files in
`.build`, and replace `Spine_Proof_Language.pdf` only after all passes succeed.

The equivalent manual command, run three times, is:

    xelatex -interaction=nonstopmode -halt-on-error Spine_Proof_Language.tex

Three passes resolve the table of contents, internal references, and bookmarks.
No shell escape, external assets, network access, or BibTeX run is needed.
