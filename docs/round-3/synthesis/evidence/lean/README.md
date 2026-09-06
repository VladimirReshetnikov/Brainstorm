# Fresh Lean checks for the round-3 synthesis

All seven supplied standalone Lean files were copied byte-for-byte from the
pinned proposal packages and checked serially. The first compilation succeeded
for every original file without any source edit. The original comments saying
that their authors did not compile them remain unchanged and describe the
upstream preparation status; this directory records the later review.

The toolchain is Lean 4.32.0, commit
`8c9756b28d64dab099da31a4c09229a9e6a2ef35`, at the executable recorded in
[receipt.json](receipt.json). Imports are only bundled `Init`, `Std`, or `Lean`.
The runs unset `LEAN_PATH` and use `LEAN_NUM_THREADS=0`. No Lake command,
dependency build/download, or output `.olean` was requested. Durations include
imports and instrumentation and are not comparative benchmarks.

Each proposal directory contains the unmodified source copy, `original.log`,
and an `Audit.lean` copy differing only by appended `#print axioms` queries,
with `audit.log`. The receipt binds both source and log bytes. One initial
review-only Karst query used the wrong namespace; correcting `Karst` to
`KarstCore` resolved the harness error. The original file had already compiled
unchanged on the first run.

The seven inputs contain 49 named theorem declarations: Basalt 2, Fiber 3,
Gneiss 2, Karst 12, Moraine 16, Schist 8, and Tephra 6. Definitions and unnamed
examples are not included in that count. The logs query 32 unique declarations:
27 report no axioms, and five report only `propext`. Those five are Moraine's
`model_sound` and `promote_model_spec`, and Schist's `eval_nf`, `check_sound`,
and `original_target`. No stronger inventory claim is made for the 17 named
theorems not individually queried or for all proof-bearing definitions.

The most concrete newly validated artifacts are:

- **Schist:** denotation of affine natural-number expressions in one variable;
  soundness of its normal-form equality checker; reconstruction of the original
  target `3 * (x + 2) = 3 * x + 6`; rejection of a corrupted constant.
  This is not a multivariate checker or an arbitrary-source reifier.
- **Moraine:** structural length semantics for its fixed `List Nat` expression
  grammar, and promotion of a *supplied universal model theorem* to actual lists.
  Its affine coefficient normalizer and the Python/Leant connections are not
  proved by this file.
- **Karst:** `dropAllLengthOnEmpty` shows why an unrealizable positive abstract
  length cannot refute length preservation on `List Empty`.
- **Fiber:** `certificate_bridge` assumes checker soundness and execution;
  acceptance proves the implication using those premises, not the premises.

[SynthesisChecks.lean](SynthesisChecks.lean) adds two generic interface theorems.
`refute_via_realization` uses a particular admissible realized abstract witness
to refute a fixed candidate's universal specification.
`reverse_via_observations` transports a supplied local inverse-reversal law
through surjective, jointly separating observations with commuting operations.
It does not itself prove the finite-matrix reversal theorem.
Both declarations were accepted and report no axioms; their source/log hashes
and exact command are in [synthesis-receipt.json](synthesis-receipt.json).

From the repository root, with that toolchain installed, run these one at a time:

```powershell
python -B docs/round-3/synthesis/scripts/check_lean.py
python -B docs/round-3/synthesis/scripts/check_synthesis_lean.py
```

These scripts reproduce checks and update their local evidence. The document
verifier checks retained receipt consistency; it does not execute the Lean
compiler. Fresh Lean acceptance is not an implementation or verification of
the proposed source languages, rule inference, or end-to-end synthesis.
