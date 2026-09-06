# From Properties to Proof Obligations

[Read the report](unified-report.pdf) · [TeX source](unified-report.tex) ·
[Convergence crosswalk](convergence.json) · [Validation receipt](validation.json)

This 31-page, self-contained report critically synthesizes all nine round-3 proposals:
Basalt, Fiber, Gneiss, Karst, Moraine, Obsidian, Schist, Tephra, and Trellis.
Neither earlier synthesis is required. The report explains the inherited
computational contracts directly, develops a common refinement and behavioral
model, compares the proposed inference and implementation choices, and gives
ten questions for the next iteration.

The current branch was fast-forwarded from `a18e3eb` to fetched `main` at
`58bb54219f494b29310ff77384732129411da887` before this synthesis. Original
proposal packages and earlier reports remain unchanged. External repositories
were treated as read-only. This package and the repository navigation are the
only intended changes.

## Main findings

- The reports converge on proof-producing elaboration over ordinary Lean,
  fixed mathematical objects, scoped evidence, behavioral contracts, and a
  comparison against equally equipped Lean. This is correlated architectural
  agreement, not nine independent productivity experiments.
- Their distinctive contributions include finite grounded property inference,
  exact quotient transport, prefix-local inverse arguments, observation
  realizability for negative synthesis, and analytical interfaces with precise
  hypotheses and conclusion strength.
- Moraine's tensor-family reconstruction omits the assumptions that each factor
  is finite and free as a module while requesting that conclusion for the
  representing algebra. The report restores those assumptions, gives a
  singleton rational-polynomial counterexample, and pins the original source.
- The fresh Leant review acknowledges exact candidate-bound assertion checks
  and joint output contracts already present at the inspected commit. Callback
  association, abstract evidence, and a replayable original-target proof remain
  different guarantees.
- The recommended first experiment combines a small property-use interface
  with existing mathematical lemmas, a narrowly completed behavioral bridge,
  and controlled authoring/repair evaluation. A successful library or editor
  extension is an explicitly acceptable result.

## What the evidence establishes

- **Source provenance:** [source-register.json](source-register.json) covers all
  83 tracked artifacts in the nine input packages (334 PDF pages), with exact
  Git blobs and separate checkout hashes. The two prior syntheses are classified
  separately. Input PDF page counts are metadata, not fresh source/PDF rebuilds.
- **Critical comparison:** three full reading memos and a final semantic review
  are in [review-notes](review-notes). The crosswalk has 90 editorial cells and
  248 source-anchor occurrences: 89 explicit, one partial, zero absent.
  Obsidian's behavioral-consequence treatment is partial under that compound
  criterion. Marks do not score novelty or implementation completeness.
- **Nine Python reproductions:** Basalt 24 methods; Fiber 1,298 checks in 31
  groups; Gneiss 32 methods; Karst eight groups; Moraine 32 named tests;
  Obsidian 608 probes; Schist 10 methods; Tephra 23 methods; Trellis 31 cases
  (nine acceptance, 22 rejection). These are different counting units. Their
  commands, source copies, hashes, output, and limits are retained in the three
  reading-lane directories under [evidence](evidence). Python 3.14.4 was used
  with bytecode disabled and isolated output paths.
- **Seven unchanged Lean specimens:** all accepted by Lean 4.32.0, commit
  `8c9756b28d64dab099da31a4c09229a9e6a2ef35`, using only bundled imports. The
  source files contain 49 named theorem declarations, plus definitions/examples.
  Queries cover 32 unique declarations: 27 with no axioms and five with only
  `propext`. The remaining 17 were compiled but not individually queried.
  [Lean evidence and reproduction](evidence/lean/README.md) state the exact scope.
- **Two additional Lean theorems:**
  [SynthesisChecks.lean](evidence/lean/SynthesisChecks.lean) proves abstract
  refutation from an admissible realized witness, and transfers local inverse
  reversal through adequate observations. Both were accepted and report no
  axioms. Their observation, admissibility, and local-reversal assumptions remain
  explicit; this does not formalize the finite-matrix theorem itself.
- **Fresh bounded Leant source review:** [the memo](review-notes/leant-update.md)
  and [source register](evidence/leant-review/source-register.json) use immutable
  commit `823259f7e3c6d24e990d3f48f78c4f1c4f88059e`, preserving concurrent
  checkout modifications. This is static evidence; Leant, its backends, and
  its solvers were not executed during this review.
- **This document:** three serial strict pdfLaTeX passes, source/PDF hash
  binding, reference/glyph/overflow checks, and rendered-page visual inspection.
  The exact reviewed page count and PDF identity are in the validation and
  visual-review receipts.

Schist's accepted source proves the complete narrow affine-normalization
example, including denotation, checker soundness, its original arithmetic target,
and a rejected corruption. Moraine's source proves a fixed list grammar's
structural length semantics and promotion of a supplied universal model law.
Neither result establishes a general CAS, the proposed elaborator, arbitrary
source reification, or a link to actual Leant candidate semantics. No measured
authoring, productivity, or maintenance improvement is claimed.

## Build, inspect, and validate

Requirements: PowerShell, pdfLaTeX with the source's standard packages, Poppler
(`pdftoppm`), and Python with `pypdf` and Pillow. The build used MiKTeX pdfTeX
1.40.29, Python 3.14.4, and pypdf 6.13.2.

From the repository root:

```powershell
& docs/round-3/synthesis/build.ps1
python -B docs/round-3/synthesis/scripts/verify_sources.py
python -B docs/round-3/synthesis/scripts/verify_convergence.py
python -B docs/round-3/synthesis/scripts/render_review.py
```

The build performs exactly three strict passes and copies the PDF only after
source-stability and log checks. Both TeX inputs are bound in
`.build/build-receipt.json`. Build intermediates and page images stay in ignored
`.build/` and `.qa/` directories. After rendering, inspect all pages and the
detailed views, then update the committed `evidence/pdf-build-receipt.json`,
`pdf-build-log.txt`, and `visual-review.json` to describe the actual review.
A visual receipt for an older PDF must not be reused.

```powershell
python -B docs/round-3/synthesis/scripts/verify_report.py
```

The verifier writes `validation.json` only after checking the current source,
PDF, provenance, crosswalk, execution receipts, and visual receipt. It does not
rerun Lean or Python companions, prove mathematical prose, or substitute for
visual inspection. The local `.gitattributes` preserves the exact artifact
bytes bound by the receipts, including original tool-output whitespace.

Lean reruns are optional and must be serial:

```powershell
python -B docs/round-3/synthesis/scripts/check_lean.py
python -B docs/round-3/synthesis/scripts/check_synthesis_lean.py
```

They require the recorded installed toolchain path, use `LEAN_NUM_THREADS=0`,
unset `LEAN_PATH`, and request no output `.olean`, Lake command, external
dependency build, or download. Read the Lean evidence guide before rerunning.
Companion rerun commands are in the individual lane READMEs and receipts.

`verify_convergence.py --write` deliberately regenerates the consolidated map
and its TeX table from the reading records. `verify_sources.py --create` is a
deliberate source-register creation operation, not a way to suppress a failed
identity check. Several source READMEs mention checksum manifests absent from
the import; the register covers the files actually tracked. The repository's
policy against package checksum-ledger files is preserved.
