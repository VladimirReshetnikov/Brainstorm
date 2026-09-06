# Parallel synthesis: source review and focused reproduction

The branch fast-forwarded from `856b619` to fetched `main` at
`8ddc6abb07df3906949f8f1a55b88288987fabe5` before this incorporation.
[source-register.json](source-register.json) binds all 28 artifacts in
`docs/round-3/unified_report` to that immutable Git state and their checkout
bytes. *Nine Refinements* is a secondary synthesis of the same nine proposals,
not a tenth independent contribution. Its original package is unchanged.

The [critical review](../../review-notes/parallel-synthesis-review.md) records
useful additions and corrections with source anchors. The original 83-file
proposal register and historical execution receipts remain intact.

## What was executed

The [execution receipt](execution-receipt.json) records three serial Lean runs:

- [FreyExact.lean](FreyExact.lean) is an unchanged copy of the peer's file:
  six named theorems and seven examples. Four interface theorems have printed
  axiom inventories. `sixteen_dvd_a4` uses `propext` and `Quot.sound`; the other
  three queried theorems also use `Classical.choice`. The two helpers compile
  but are not individually queried. The file proves divisibility and rational
  coefficient casts, not a complete curve-model correspondence or elaborator.
- [SupplyChecked.lean](SupplyChecked.lean) adapts the peer's `Supply3.lean`:
  replace the deprecated matrix lemma with `mul_eq_one_comm`, remove its final
  deliberate misuse of `mvcgen`, and add a checked admissible Frey tuple. The
  four positive examples check continuity, derivative equality from local
  equality, finite-matrix reversal, and the conjunction of the arithmetic
  premises. The original `Supply3` log correctly remains an expected negative
  probe, with an experimental warning and an error. No working effectful
  `mvcgen` workflow or concrete analytic interchange is demonstrated here.
- [AdequacyChecks.lean](AdequacyChecks.lean) is new. Three small theorems show
  that the affine models `0` and `n` agree at every input of `List Empty`, while
  their coefficients differ; raw coefficient equality is therefore incomplete
  for that source domain. All three printed inventories are empty. This is not
  a Lean formalization of the general affine completeness theorem or a Leant
  semantic adapter.

Frey and the positive supply probe import existing Mathlib artifacts from the
read-only `C:/ProveIt` dependency directories. The receipt records Lean 4.32.0,
the Mathlib revision `81a5d257c8e410db227a6665ed08f64fea08e997`, all dependency
revisions, their tracked-source status, the project manifest hash, and the
explicit `LEAN_PATH`. This does not assert a fresh rebuild or audit of every
imported library artifact. `AdequacyChecks` uses bundled Lean only, although it
is run in the same environment. No Lake invocation, external repository write,
download, native-evaluation axiom, or output `.olean` is requested.

## Reproduction and validation

After ensuring there is no competing Lean build, run from the repository root:

```powershell
python -B docs/round-3/synthesis/scripts/check_parallel_review.py
```

This intentionally replaces the three local execution logs and the receipt.
It requires the recorded Windows paths, installed Lean toolchain, clean pinned
dependency sources, and existing library artifacts. Runs are serial with a
15-minute bound per file; elapsed times include import and process costs and
are not a performance benchmark.

For read-only consistency validation, with no experiment or build rerun:

```powershell
python -B docs/round-3/synthesis/scripts/verify_parallel_review.py
```

The validator binds the peer artifacts, verifies the source-copy/adaptation
distinction, checks successful retained executions and their hashes, and
reconciles source declarations with axiom-query inventories. It also checks
the arithmetic of the peer's CSV metadata without certifying its editorial
scoring: 48 negative families have 142 report-family incidences, not 142 distinct
source rows or executed tests. The peer's 48-theorem headline omits Karst's
unqueried `viewIntro`; there are 49 named declarations in the seven original
cores. Their prior 32-query audit in our package remains a separate receipt.
