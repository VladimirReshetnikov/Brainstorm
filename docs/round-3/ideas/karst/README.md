# Karst
## Scoped Refinements and Behavioral Contracts for Mathematical Proof

A third-round proof-language proposal prepared for Vladimir Reshetnikov,
6 September 2026.

The 40-page article proposes an identity-preserving refinement layer over Lean:
proved mathematical properties become usable during elaboration while the
underlying object remains fixed. Behavioral contracts, scoped obligations,
explicit structure choices, and relation-specific computational observations
elaborate to ordinary Lean propositions and proofs. The initial design does not
change Lean's kernel or its definitional equality.

## Contents

- `karst.pdf`: the rendered article.
- `karst.tex`: self-contained LaTeX source, including bibliography and diagram.
- `build.sh`: PDF build helper.
- `source-register.json`: inspected repository revisions, selected Git blob
  identities, reading scope, and primary documentation references.
- `examples/KarstCore.lean`: ordinary-Lean model of selected refinement and
  behavioral rules. **Not compiled in this session.**
- `evidence/companion.py`: executable, standard-library Python reference checks.
- `evidence/results.json`: recorded finite-check results.
- `evidence/run.log`: stdout from the executed companion.
- `evidence/document-validation.json`: document build and inspection receipt.
- `SHA256SUMS`: integrity hashes of the other packaged files.

## Evidence and limitations

This is a design article, not an implemented language. Its mathematical
arguments are paper proofs, not claims of machine-checked formalization.
The Python companion was executed successfully. It checks finite endomaps,
polynomial operations and malformed certificates, sample sorting behavior,
exact Frey-coefficient quotients, formal-jet arithmetic, and a synthetic
scope/origin model. These are finite checks, not proofs of universal semantics
or compiler correctness. The different check-group counts have different
units and are intentionally not combined into a headline total.

No Lean executable was available in the working environment. Consequently the
included Lean model is uncompiled, and its `#print axioms` commands request a
future audit rather than record an audit already performed. It is not a parser,
elaborator, or verified polynomial checker. No cited repository was built or
independently verified in full. There are no measured productivity or performance
claims for Karst.

Both round-two synthesis reports were reviewed at the pinned Brainstorm
revision. The nine underlying proposals are discussed through those syntheses;
this package does not claim an independent audit of their entire source trees.
New development examples use ProveIt's finite-type argument and the Frey-package
interfaces and final proof assembly in the FLT repository. Development examples
are not held-out evaluation tasks.

## Reproduce the finite checks

From this directory, using Python 3 with its standard library:

```sh
python3 evidence/companion.py > evidence/run.log
```

This rewrites `evidence/results.json`. Random samples use seed `20260906`;
other cases are deterministic or exhaustive over their documented finite ranges.
The code raises an assertion or validation error when a required check fails.

## Build the article

Install a normal LaTeX distribution with pdfLaTeX, latexmk, and the packages
listed in the source preamble, then run:

```sh
./build.sh
```

Alternatively:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error karst.tex
```

The bibliography is embedded and the figure uses TikZ. The build requires no
network requests once the LaTeX packages are installed. PDF bytes may differ
between TeX distributions or builds; the packaged hash identifies this specific
rendering, not a promise of byte-for-byte reproducibility elsewhere.

## Check the Lean model separately

Using a deliberately selected, pinned Lean 4 installation:

```sh
lean examples/KarstCore.lean > evidence/lean-check.log 2>&1
```

Inspect the exit status and the complete log, including the axiom inventories.
This command has **not** been run here. Checking this small model would still not
verify the proposed Karst frontend, the polynomial checker, or the source
repositories.

## Source and redistribution scope

The article supplies commit-pinned repository links and primary-source
bibliography entries. The source register explains which files and sections
were inspected. No repository snapshot, third-party report, or font file is
redistributed in this archive.
