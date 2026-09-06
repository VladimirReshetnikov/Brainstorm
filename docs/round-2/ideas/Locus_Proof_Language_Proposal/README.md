# Locus: Mathematical Workspaces and Certified Computation

A second-round proof-language design for Vladimir Reshetnikov, dated
5 September 2026 (Pacific time).

## Contents

- `locus.pdf` — the 41-page article.
- `locus.tex` — self-contained LaTeX source, including references and the vector diagram.
- `certificate_demo.py` — executable exact-rational arithmetic demonstrator.
- `test-results.json` — the recorded successful execution: 24 test methods, no failures or errors.
- `source-register.json` — inspected repository file identities and external primary sources.
- `build.sh` and `build.ps1` — build and test commands for POSIX shells and PowerShell.
- `SHA256SUMS.txt` — SHA-256 integrity hashes of the other delivered files.

The proposal builds on both Brainstorm synthesis reports. It makes a shared,
semantically explicit mathematical workspace the next unit of language design.
Computational results carry exact relations to their inputs, including domains,
branches, formal precision, and enclosure guarantees. The worked examples cover
binomial inversion, local calculus, a ProveIt formal algebraic germ, radical
denesting, and certified rational root brackets. The appendices specify typed
interfaces, 28 planned integration regressions, and source provenance.

## Evidence scope

The language, adapters, and Lean computational packages are proposed designs,
not implemented or benchmarked products. ProveIt and Leant sources were inspected
statically; neither repository was built for this article. The displayed Locus
syntax and implementation signatures are schematic. Mathematical results in the
article have written proofs; no new Lean formalization is claimed.

The supplied Python companion WAS executed. It uses only exact integer/rational
arithmetic. Its 24 test methods include parameterized tests at jet precisions
1–24, coefficient checks through degree 24, and 702 finite binomial instances.
It also tests wrong branches, missing endpoints, insufficient precision, forged
radical enclosures, and algebraic-domain counterexamples. These finite tests do
not prove universal theorems or formally verify the Python implementation.

The 28 planned Lean integration regressions in Appendix B are a separate suite;
they are not claimed to have been executed by the Python program.

## Build the PDF

Use a TeX Live or MiKTeX installation providing `latexmk`, pdfLaTeX, Latin Modern,
and the packages named in the source preamble. The source needs no external
images or bibliography downloads. Fonts are referenced through the TeX
installation; no separate font files are distributed.

Run from this directory:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error locus.tex
```

The PDF was compiled with pdfLaTeX, all references resolved, and no overfull,
underfull, missing-character, or LaTeX-warning entries remained in the final log.
Rendered page images were inspected, including the tables, main mathematical
proofs, source register, and architecture diagram.

## Run the companion

Python 3.9 or later; standard library only:

```text
python certificate_demo.py --json test-results.json
```

Use `python3` or `py -3` as appropriate for the local installation. The program
returns a nonzero exit status if a test fails. Re-running it replaces the receipt
with the current interpreter version and outcomes. The delivered receipt records
the original execution environment, not a claimed minimum Python version test.

To build and test together, run `./build.sh` or `./build.ps1`. The PowerShell
script can also be invoked using the local execution policy approved on your
machine; the two commands above do not require executing a script file.

## Source provenance

The repository identifiers are Git **blob** SHAs identifying inspected file
contents, not commit SHAs. The URLs record the requested `main` paths. They do
not assert that the complete working trees described by earlier synthesis
reports were the same as the current remote sources. Source snapshots and
repository builds are not included in this archive.
