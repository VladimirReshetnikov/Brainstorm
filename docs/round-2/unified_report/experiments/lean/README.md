# Lean experiments behind the round-2 unified report

All files were run with `lake env lean <file>` from the ProveIt checkout
(toolchain `leanprover/lean4:v4.32.0`, Mathlib package revision `81a5d257c8`,
Windows 11, x86_64), on 5 September 2026. The `.log` files are the verbatim
compiler output (paths shortened). Nothing here is a verified checker: the
polynomial code is unproved, and the experiments measure cost and axiom
inventories, not soundness.

| File | Question it answers |
|---|---|
| `Axioms.lean` | Which axiom does `native_decide` introduce on this toolchain? (a per-invocation axiom, not `Lean.ofReduceBool`) |
| `PolyCert.lean` | How does kernel checking of an ideal-membership certificate (`decide`) scale with degree, versus `native_decide`? Also checks the Catalan residual-jet certificate and the derivative precision loss. Two runs: `PolyCert.run1.log`, `PolyCert.run2.log`. |
| `LinComb.lean` | Cost of the proof-producing route (`linear_combination`, i.e. `ring`) on the same identity family. |
| `Supply.lean` | Do the consensus CAS contracts already exist in the pinned Mathlib? Also probes `Polynomial` computability, `grobner`, and `polyrith`. |

Reproduce with, for example:

    cd C:\ProveIt
    lake env lean path\to\PolyCert.lean
