# Trellis — third-round proof-language proposal

**Property-Rich Mathematics with Proof-Explicit Elaboration**  
Prepared for Vladimir Reshetnikov, 6 September 2026.

The 37-page article develops a property- and behavior-oriented authoring layer
that elaborates to ordinary Lean. Its central distinction is between selecting
meaning-bearing mathematical structures and inferring propositions about fixed
objects in those structures. The recommended first implementation extends the
elaborator, not Lean's trusted kernel.

## Files

- `trellis.pdf`: the complete article.
- `trellis.tex`: self-contained LaTeX source with an embedded bibliography.
- `companions/trellis_reference.py`: exact rational affine-certificate checker
  and request-binding reference implementation, using only Python's standard
  library.
- `companions/results.json`: results from 31 executed tests (9 acceptance and
  22 rejection cases).
- `source_register.json`: repository revisions, observed Git blob identities,
  file-specific reading scope, and external primary sources.
- `validation.json`: document-build and inspection results.
- `SHA256SUMS`: hashes of the delivered files other than the checksum file.
- `build.sh`: rerun the companion and rebuild the PDF with three pdfLaTeX passes.

## What the article contains

The article reviews both round-two syntheses, including their reciprocal
corrections, and distinguishes inherited architecture from the proposed
additions. It gives a complete small refinement calculus with a relative
translation argument; a finite grounded qualifier closure algorithm and its
termination/relative-completeness theorem; behavioral weakening and dependent
composition rules; and a mathematical soundness proof for an affine-inequality
certificate format.

Worked examples are drawn from ProveIt's Fabius/Rvachev regularity and
stationary-phase developments, and from the FLT repository's Frey package and
final contradiction. The Leant discussion uses the actual verification,
behavioral-selection, and Length-contract interfaces. The final sections cover
kernel-extension tradeoffs, a semantic document view, implementation boundaries,
paired failure tests, replay, and an evaluation plan that gives ordinary Lean
the same libraries and services.

## Evidence and limitations

The supplied Python tests were executed and passed. The PDF was compiled from
the supplied TeX, rendered, and visually inspected. No Lean compiler or kernel
was run, no repository was rebuilt, and no Leant executable was invoked for this
article. The proposed surface syntax is not an implemented Lean extension.

The mathematical proofs in the article are written proofs, not machine-checked
Lean declarations. The Python checker is an executable reference specification,
not formally verified code or a production parser for arbitrary untrusted
messages. Its scope-prefix example is deliberately narrower than dependent
context transport in Lean. A rejected certificate does not necessarily refute
its underlying mathematical proposition. The 31 cases are not a claim to have
executed the syntheses' entire 51-family mutation catalogue.

No measured proof-compression, productivity, inference-performance, or usability
gain is claimed. Every source example inspected for the design is development
material, not a held-out evaluation task. Source-repository build claims remain
attributed to their authors.

## Reproduction

The companion requires Python 3.10 or later:

```sh
python3 companions/trellis_reference.py --output companions/results.json
```

Expected output:

```text
31 tests passed (9 positive, 22 negative).
No Lean compiler or kernel was run.
```

To rebuild the article with a standard TeX Live installation:

```sh
bash build.sh
```

Alternatively, run `latexmk -pdf -interaction=nonstopmode -halt-on-error
 trellis.tex`, or run `pdflatex` three times. The source uses common packages,
including Latin Modern, microtype, AMS mathematics, mathtools, stmaryrd,
booktabs, longtable, tabularx, listings, enumitem, fancyhdr, xurl, and hyperref.
There are no external bibliography files, figures, downloaded fonts, or network
services required by the build. Standard font packages must be installed in the
reader's TeX distribution; font files are not distributed in this archive.

`validation.json` and `SHA256SUMS` describe the delivered snapshot. Rebuilding
can change PDF metadata and hence its checksum; these files are not assertions
that every rebuild is byte-identical.

## Source attribution

`source_register.json` records exact repository revisions and what was directly
read. The bibliography links to pinned repository files where applicable.
Original Lean sources are not redistributed here. The mathematics is credited
to the inspected developments and their contributors, including the Imperial
College London provenance of the Frey package. The article does not claim
historical novelty for refinement types, behavioral specifications, or classical
mathematical arguments.
