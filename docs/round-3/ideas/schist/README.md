# Schist: A Property-Aware Mathematical Language over Lean

Third-round proposal prepared for Vladimir Reshetnikov, 6 September 2026.

## Main deliverable

`schist.pdf` is the 32-page article. `schist.tex` is its self-contained LaTeX
source, including the bibliography. It needs no external figures or bibliography
file. The proposal distinguishes its inherited round-two architecture from the
additional refinement-typing, requirement-propagation, and behavioral interfaces.

## Files

- `schist.pdf` and `schist.tex`: the article.
- `SchistCore.lean`: unexecuted Lean reference source for refinement weakening,
  contracts, anchored observations, requirement-transformer composition, and a
  small affine-expression certificate checker with a written soundness proof
  and an original-target example. This is NOT an implemented frontend.
- `check_examples.py` and `checks.log`: ten executed finite exact-arithmetic
  sanity tests and their recorded output. They do NOT validate the Lean file,
  the proposed elaborator, or any general theorem.
- `source_manifest.json`: source paths, returned Git blob identities, web
  references, and the scope of inspection.
- `validation.json`: the preparation-time validation record and payload hashes.
- `latex-build.log`: the final successful LaTeX build console output.
- `build.sh`: rebuilds the PDF and reruns the Python checks.

## Build the article and finite tests

With a standard TeX Live installation containing pdfLaTeX, latexmk, Latin Modern,
microtype, amsmath, amssymb, mathtools, booktabs, tabularx, longtable, xcolor,
listings, enumitem, needspace, fancyhdr, titlesec, xurl, hyperref, and bookmark,
and Python 3.10 or later:

```sh
bash build.sh
```

Alternatively:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error schist.tex
python3 check_examples.py
```

A rebuild may change the PDF's timestamp and hash. `validation.json` records the
files supplied in this archive, not arbitrary subsequent builds.

## Lean status

Lean and Lake were not available on PATH in the preparation environment. The
Lean file was authored but not compiled. It contains no authored axioms, `sorry`
placeholders, or `native_decide` invocations; no claim is made that it elaborates
successfully or that its transitive axiom inventory is empty. It uses the Lean
standard distribution, not Mathlib. Check it in a recorded Lean 4 toolchain:

```sh
lean --version
lean SchistCore.lean > lean-check.log 2>&1
```

The file includes `#print axioms` commands for its principal declarations.
A successful future run and an inspected axiom inventory are separate evidence
from the Python test log included here.

## Scope and provenance

Both main round-two TeX syntheses were read closely. Their companion files and
all nine individual proposals were not independently re-audited. Selected current
ProveIt, FLT, and Leant source files and documentation were inspected as recorded
in `source_manifest.json`. No repository was modified, cloned, or rebuilt here.
The additional probability case is development material, not a held-out benchmark.

The article's orbital-comparison generalization and core-calculus preservation
statement have written mathematical arguments. They are not claimed as new
historical discoveries or mechanically verified metatheorems. No productivity
or performance improvement for the proposed language has been measured.
