# Rowan: Contract-Directed Mathematical Proofs

A fourth-round proposal for a concise mathematical proof language over Lean,
prepared for Vladimir Reshetnikov on 6 September 2026.

## Article

`Rowan.tex` is self-contained, including its bibliography. `Rowan.pdf` is the
compiled version. The article closely considers both round-three synthesis
reports and examines selected ProveIt, FLT, and Leant sources at recorded
revisions. It distinguishes inherited design decisions from Rowan's additions.

The central additions are immutable original-target requests, explicitly
bounded theorem instantiation, and admissibility-indexed behavioral checking.
The main mathematical result is an affine equality criterion on a supplied
finite union of linear sets, with constructive counterexample coordinates.
It includes exact-division, local differentiation, and naturality examples,
a certified CAS interface, and a staged analysis of Lean type-system changes.

## Build and run

Run these commands inside this directory:

```sh
python rowan_model.py
python test_rowan.py
latexmk -pdf -interaction=nonstopmode -halt-on-error Rowan.tex
```

The Python files require Python 3.11 or later and only the standard library.
They were executed with Python 3.13.5. The LaTeX uses ordinary TeX Live packages
and needs no external images, fonts, bibliography database, or network access.
No font files or upstream source archives are included.

## What executed

All 32 named tests passed. The generated finite cases include 12,675 list/model
comparisons, 4,374 affine pair/image checks, 24,057 finite affine sample
evaluations, 100 shuffled-rule trials, 139 Frey arithmetic cases, and two
explicit realized list counterexamples. These categories are not independent
formal theorems and should not be summed as an overall theorem count.

`demo_results.json`, `test_results.json`, and `test_log.txt` preserve the
executions. Running the tests rewrites `test_results.json`; its single-run
timing varies and is not a benchmark against Lean or Leant.

## Model boundary

`rowan_model.py` implements a parsed finite *symbolic* engine. The accepted
commands are `object name : Sort`, `assume name : Predicate(objects)`, and
`derive name : Predicate(objects)`. Object values are symbolic; numerical
Frey checks are a separate exact-integer computation. Registered Horn rules
are assumptions of this model, not Lean theorem certificates. Grounding and
derivation replay do not prove the mathematical truth of that registry.
The model rebuilds each request rather than caching cross-context evidence.

The list interpreter covers natural lists, empty lists, inputs, cons, append,
reverse, and mapping the successor function. The semilinear checker establishes
model equality on the image *supplied to it*. It does not automatically infer
that image, prove a source-to-model theorem, or supply a Lean proof. Its
counterexample is model-relative until an admissible source input is realized
and its behavior is checked. The two supplied concrete examples do that in
Python, not in Lean.

The richer Rowan syntax shown in the article is proposed syntax and is not
accepted by this miniature parser. No Rowan Lean elaborator or Leant plugin is
included. No Lean compiler was available in this session, and no upstream Lean
project or previous report experiment was rerun. The generic mathematical
arguments in the article are written proofs, not newly kernel-checked proofs.
The article's productivity study and kernel-extension experiment are proposed,
not completed. The user's requested language-design article is the primary
deliverable; the model is a bounded accompanying experiment.

## Provenance

`sources.json` records repository commits, inspected paths, available blob
identities, and external primary sources. The reported later Leant revision
`823259f7` could not be retrieved; direct source observations use the available
`3a40904be8a410d832d9ab6900b3d3e7b425eccb` revision. This is an availability
limitation rather than a claim that the prior report is wrong.

`SHA256SUMS.txt` covers the packaged files other than itself. Regenerate it
after changing files or rerunning tests if checksum validation is desired.
