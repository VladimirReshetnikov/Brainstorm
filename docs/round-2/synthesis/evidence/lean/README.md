# Focused Lean checks for the round-2 synthesis

The final invocation of `FocusedChecks.lean` **exited 0** using Lean 4.32.0 (commit `8c9756b28d64dab099da31a4c09229a9e6a2ef35`) and the existing mathlib cache at revision `81a5d257c8e410db227a6665ed08f64fea08e997`. The cached mathlib checkout HEAD matched the ProveIt manifest revision. The final run took 55.18 seconds with `LAKE_JOBS=1` and `LEAN_NUM_THREADS=0`.

These are focused ordinary Lean theorem checks, not an implementation or validation of any proposed language, parser, CAS checker, provider adapter, semantic seal, or replay protocol. No Lake command, repository build, dependency rebuild or download was requested. The dependency source repositories were read-only. The imported cached artifacts were used as supplied; this is not a full transitive integrity audit or independent recheck of all mathlib.

## Checked mathematical claims

| Source lines | Declaration(s) | Meaning |
|---|---|---|
| 19–21 | `cancellation_at_one_fails` | At real \(x=1\), totalized \((x^2-1)/(x-1)\) equals 0, whereas \(x+1=2\). |
| 23–26 | `guarded_cancellation` | The identity holds for every real \(x\ne1\); uses `div_eq_iff` with its nonzero denominator premise, followed by polynomial normalization. |
| 28–31 | `unguarded_cancellation_is_false` | The unguarded universally quantified identity is false. |
| 44–55 | `one_forward_row_holds`, `inverse_row_value`, `corresponding_inverse_row_fails` | With \(a_k=0\) and \(b_k=1\) only at \(k=0\), the forward binomial equation at \(n=1\) holds, but the proposed inverse row is \(-1\ne a_1=0\). |
| 57–69 | `pointwise_binomial_implication_is_false`, `pointwise_binomial_iff_is_false` | Quantifying only sequences around a single forward row does not validate the displayed pointwise implication or iff. The intended inversion theorem requires the family of lower forward equations. |

All eight declarations' `#print axioms` outputs list only `propext`, `Classical.choice`, and `Quot.sound`; the log is retained. There are no `sorry` proofs, newly declared axioms, or `native_decide` uses. Ordinary Lean elaboration/kernel acceptance is the evidence here; a separate `leanchecker` recheck was not run.

The source defect concerns the missing family scope in Cadence §8.3 (TeX 937–948) and Concord §8.3 (580–587), not the standard uniformly quantified binomial-inversion theorem. Integer-valued sequences already refute the pointwise reading, so no field-specific assumption is involved.

The cancellation theorem uses the current pinned mathlib declaration:
[Mathlib.Algebra.GroupWithZero.Units.Basic, div_eq_iff, line 346](https://github.com/leanprover-community/mathlib4/blob/81a5d257c8e410db227a6665ed08f64fea08e997/Mathlib/Algebra/GroupWithZero/Units/Basic.lean#L346).
The theorem explicitly requires a nonzero denominator.

## Reproduction and receipt

From the Brainstorm repository root:

```powershell
& docs/round-2/synthesis/evidence/lean/check.ps1
```

The script locates the already installed pinned executable under the current Windows user profile, checks for active Lean/Lake processes, uses the existing dependency library directories in `C:/ProveIt/.lake/packages`, and invokes Lean directly on the experiment source. Missing toolchains or direct cached imports cause it to stop; it does not install or rebuild them.

`receipt.json` records the exact executable, source argument, environment search path, version, declared dependency revisions, exit code, timestamps, duration, source/log hashes, and hashes of the five direct imported `.olean` files. `FocusedChecks.log` contains the axiom audits. No `.olean` output for this experiment was requested.

An earlier clean invocation produced the same eight axiom audit lines, but its wrapper did not retain an explicit process-exit receipt. A subsequent reproduction attempt was deferred by the active-process guard. The final captured invocation supplies the documented exit-0 evidence; no overlapping Lean invocation was started by this lane.
