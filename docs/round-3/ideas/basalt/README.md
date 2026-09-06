# BASALT — Round-three proof-language proposal

**A Property- and Behavior-Aware Mathematical Language over Lean**
Prepared for Vladimir Reshetnikov, 6 September 2026.

## Main article

`basalt.pdf` is the 40-page article. `basalt.tex` is its self-contained LaTeX
source; the bibliography is embedded, and no external illustrations or font
files are required.

The proposal covers contextual refinements, dependent behavioral contracts,
relational contracts on diagrams, demand-driven evidence synthesis, certified
computation, Leant integration, and matched evaluation against ordinary Lean.
It contains worked cases from ProveIt and the FLT repository and a close
response to both round-two syntheses.

## Build

With a standard TeX Live installation and pdfLaTeX:

```sh
bash build.sh
```

The script runs three passes and rejects unresolved references, missing glyphs,
and overfull boxes. It creates ordinary LaTeX build intermediates in this folder.
The distributed PDF was also rendered and visually inspected.

## Executable finite demonstrations

With Python 3.10 or later, no third-party libraries:

```sh
python companions/certificate_demo.py
```

The companion implements exact sparse integer-polynomial certificate checking
and a small list-length abstract interpreter. The supplied `test_run.txt` and
`test_results.json` record the actual preparation run: 24 test methods passed.
Some methods contain multiple finite instances. This is NOT a formal proof of
the Python implementation or a test of a BASALT compiler.

## Illustrative Lean core

`companions/ContractCore.lean` illustrates proof-only encodings of refinement
weakening, intersection packaging, contract composition and consequence,
observation congruence, and precision-demand composition.

**It was not compiled in the preparation environment.** No Lean compiler was
available. It contains no `sorry` or added axiom, but this is not a claim of
kernel acceptance. The article's mathematical soundness arguments are written
proofs, not a completed machine-checked formalization.

## Provenance and validation

`sources.json` registers the observed repository revisions and inspected files;
Appendix C in the article gives the inspection scope. The original repositories
were read through the connector, not independently cloned or rebuilt.
`validation.json` separates document checks, executed finite tests, and
unperformed Lean compilation. `MANIFEST.sha256` hashes all supplied files except
the manifest itself.

No new language compiler, whole-repository proof audit, performance benchmark,
or usability experiment is claimed by this package.
