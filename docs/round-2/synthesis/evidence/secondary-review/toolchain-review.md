# Secondary synthesis: toolchain and experiment audit

Audit date: 2026-09-06 UTC. Read-only source review of `docs/round-2/unified_report/`, with two new focused Lean runs in this evidence directory. The secondary source is not edited. No Lake invocation, dependency build/download, external-repository mutation, Git operation, or full benchmark rerun was performed. Parent owns synthesis and publication.

## Recommendation

Retain the secondary report's concrete theorem-supply inventory, exact native-evaluation axiom observation, small residual arithmetic checks, and historical cost observations. These make useful existing Lean baselines. Do not inherit its stronger claims that all proposed contracts already exist, that no round-2 report noticed `grobner`, that this tactic has established completeness, or that an unverified list checker establishes practical strict-mode cost for all realistic workloads. The experiments support a narrower and still useful next step: implement the missing denotation/reification bridge and measure the whole acceptance path against equally equipped Lean.

The most useful distinction is between (a) a theorem name resolving, (b) its premises matching the proposed method, (c) the checker accepting executable data, (d) a theorem connecting that data to the actual mathematical target, and (e) fresh execution under a declared proof policy. The supplied sweep mainly establishes (a); its arithmetic experiments establish particular instances of (c); the new target checks establish two small instances of (e) for existing Lean tactics.

## Source and execution provenance

Secondary TeX locators below are one-based lines of `docs/round-2/unified_report/unified_report.tex`. Its section 7 occupies lines 408–476; its experiment appendix is lines 723–731. Experiment paths below are relative to `docs/round-2/unified_report/experiments/lean/`.

The supplied README lines 3–8 attributes original runs to `lake env lean <file>`, Lean v4.32.0, Mathlib `81a5d257c8`, Windows 11/x86_64, 5 September 2026. I found four sources, `PolyCert.run1.log`, `PolyCert.run2.log`, `LinComb.log`, and `Supply.log`. There is no `Axioms.log` in that directory at audit time. I did not authenticate original timing execution or reconstruct its process environment. The new `lean/historical-evidence.json` hashes all inspected historical sources/logs, the installed Lean executable, and relevant implementation sources. It separates the version-reported core commit from the manifest-declared Mathlib revision. Source hashes preserve exactly what was inspected; they are not an independent source-to-binary or source-to-historical-log verification.

New runs used installed Lean 4.32.0, core commit `8c9756b28d64dab099da31a4c09229a9e6a2ef35`, existing cached imports under `C:/ProveIt`, `LEAN_NUM_THREADS=0`, and no output `.olean`. Both exited 0. `lean/receipt.json` and `lean/AxiomProbe.receipt.json` contain exact commands/version and source/log hashes. The former also records all declared package revisions, full import search path and the directly imported `.olean` hash. These are focused file checks with supplied caches, not a rebuild or a transitive artifact integrity audit.

## The theorem supply is useful but not the proposed contracts wholesale

Section 7.1, lines 411–436, overstates the inference from `#check`. `Supply.lean` is an intentionally mixed probe: the successful signature outputs coexist with errors for unknown `Real.sqrt_eq_iff'` (source 28), native evaluation of noncomputable `Polynomial.X` (57), and unsupported `polyrith` (61). `Supply.log` records the errors; this is not a clean whole-file compilation receipt. The successful `grobner` example at source 59 has now been isolated into a fresh exit-0 file.

Important signature restrictions in the supplied log:

| Need | Evidence and restriction |
|---|---|
| Local differentiation | `Supply.lean` 3–6; log 1–10. `HasDerivAt.congr_of_eventuallyEq` transfers an existing derivative using actual eventual equality at the point. Openness plus membership can establish a neighborhood; the named APIs do not automatically derive every domain guard or certify a CAS-produced expression. |
| Formal-series truncation/substitution | Source 8–19; log 11–30. `trunc` maps to semantic `Polynomial`; `coeff_trunc` has an index bound. `HasSubst` is an admissibility proposition. Resolving the names `HasSubst` and `subst` does not prove an arbitrary supplied substitution admissible or a residual-to-series transfer theorem. |
| Casts and reflection | Source 32–35; log 43–46. `Nat.cast_sub` needs `m ≤ n`. `Nat.cast_div` is into a `DivisionSemiring`, requires natural divisibility and nonzero **cast denominator in the target**. `Nat.cast_injective`/`inj` require `CharZero`. Nonzero naturals alone do not supply the target condition in positive characteristic. |
| Cancellation | Source 37–39; log 47–49. `IsUnit` cancellation works in the stated monoid context; cancellation by an arbitrary nonzero element requires the separate cancellation structure. This does not justify replacing units by nonzero coefficients in arbitrary rings. |
| Root isolation | Source 21–25 and 47–49; log 35–38 and 67–75. Polynomial roots and cardinality bounds carry domain assumptions; IVT, injectivity and mean-value theorems are mathematical ingredients. These probes do not implement a certificate schema, isolation algorithm or completeness checker. |
| Scalar transport | Source 51–53; log 76–81. `Rat.cast_injective` asks for a characteristic-zero division ring. A forward identity transport through the algebra map of a general rational algebra is a different contract and need not introduce these stronger assumptions. |

The `#eval (Polynomial.X : Polynomial ℤ).natDegree` failure supports a specific native-execution limitation, not the assertion that `Polynomial`/`Finsupp` “do not compute at all” (TeX 595) or that Lean lacks executable polynomial representations. `Mathlib/Algebra/Polynomial/Basic.lean` 66 starts a noncomputable section; 74–76 defines the semantic representation; 480–481 defines `X` using `monomial`. Existing reflective tactics already use computational representations. The proposed contribution should be a suitable reusable interface, evidence bridge and accounting policy, not rediscovery of computation itself.

## `grobner`: existing bounded core tactic, already noticed

TeX 414, 432 and 616 should not be incorporated literally. Five original report main texts name `grobner`: Cadence 727 (section 6.4), Concord 389 (section 5.6), Noema 398, Prism 425 and Vantage 1046. These passages mainly use it to discuss the retired `polyrith` service and provider-independent replay. Actual execution at the local pin is a useful addition; awareness is not new.

Installed Lean's `Init/Grind/Tactics.lean` 351–357 describes `grobner` as a thin wrapper around `grind` enabling the Gröbner solver. `Lean/Elab/Tactic/Grind/Main.lean` 475–478 routes it through `evalGrindCore`. `Init/Grind/Config.lean` 118–126 gives default `ringSteps := 100000` and `ringMaxDegree := 1024`; 247–271 defines the disabled-solver configuration, and 304–308 enables the ring solver for `GrobnerConfig`. `RingM.lean` 15–22 checks the limits; `EqCnstr.lean` 529–551 stops full simplification/search when limits intervene. The latter's 522–524 also distinguishes available cancellation evidence. These are bounded tactic implementation facts, not a proof of completeness over a published input/failure contract.

Primary pinned core sources: [tactic documentation](https://github.com/leanprover/lean4/blob/8c9756b28d64dab099da31a4c09229a9e6a2ef35/src/Init/Grind/Tactics.lean#L351-L357), [configuration](https://github.com/leanprover/lean4/blob/8c9756b28d64dab099da31a4c09229a9e6a2ef35/src/Init/Grind/Config.lean#L118-L126). Local inspected source hashes are in the register.

Mathlib's `Tactic/Polyrith.lean` 15–22 explicitly describes the discontinued Sage service and distinguishes `grobner` from a `Try this: linear_combination ...` suggestion. Lines 55–60 implement the failure. `Tactic/LinearCombination.lean` 15–31 explains weighted combinations followed by normalization. The successful original-target proofs in `lean/TargetChecks.lean` establish that both available tactics prove `x²-y²=0` from `x-y=0` over `ℚ`. “Without a certificate” should mean no user-supplied external certificate; the tactic still constructs proof evidence. It does not establish provider discovery, displayed-edit replay, reusable explicit ideal-membership certificates, or language implementation.

## What the list checker actually certifies

`PolyCert.lean` 4–17 defines addition, scaling, multiplication and a Boolean zero test for lists of integers. Theorems 29–38 state `check ... = true`. No theorem defines and proves a polynomial denotation, proves checker soundness, or transports these successes to an original Lean polynomial goal. The report admits this limitation at TeX 473 and 731; preserve it whenever quoting the measurements.

Two useful implementation cautions arise from source inspection:

- `List.zipWith pmul qs fs` at source 17 silently truncates unequal lists. This need not itself make a suitably specified denotational checker unsound: omitted multipliers can denote zero and unused extra ones can be ignored. It does mean the prototype does not enforce request-bound arity. A strict certificate protocol must reject mismatches or explicitly specify their mathematical and operational meaning.
- `xn1 n` at source 19 represents `X^n-1` only for positive `n`: at zero it still produces `[-1,1]`. The tested family starts at 10, so the actual positive cases are unaffected. A generalized interface needs the precondition or corrected zero case.

`geomBad` is defined at source 23 and is never referenced by a theorem or evaluation. Neither historical PolyCert log contains a corrupted-certificate rejection. TeX 471 and appendix line 727 therefore claim negative execution not supported by the shipped source/log pair. Add a real negative fixture in a future experiment; do not count the unused definition as one.

## Historical timing: narrow workload and partial phase accounting

The defensible historical degree-1280 observation is the sum of the reported tactic and kernel-typechecking entries: run 1 gives 530 ms + 477 ms = 1.007 s; run 2 gives 1.61 s + 1.05 s = 2.66 s (`PolyCert.run1.log` and `.run2.log`, lines 168 and 183). These are archived profiler measurements of `check=true`, not freshly reproduced end-to-end acceptance latency. Whole-file reported wall times are 9.479 s and 11.303 s (649), including many theorem declarations. Profiler phase sums need not equal elapsed wall time.

The multiplication workload is especially favorable: `pmul (geom n) [-1,1]` has one factor of fixed length two. In source 9–11 each recursive step scales this fixed-size factor and adds at its short head, returning the remaining tail. Thus the generic schoolbook multiplication's two-factor quadratic intuition does not justify TeX 471's claimed quadratic scaling for this family. Degree alone leaves coefficient bit size, density, arity and factor balance unspecified. The measurements do not establish negligible cost for all nine reports' examples or all small-thousands-degree problems.

The native entries near 1.02–1.04 s / 2.67–2.71 s are labeled kernel `type checking` in the logs (for example 200 and 360), while nearby compilation/interpretation subphases are milliseconds (201–206 and 361–366). Those labels do not justify attributing a universal fixed one-second cost to compilation. The experiment gives observed profile entries, not a controlled causal decomposition or an established crossover point.

`LinComb.lean` tests degrees 10, 20, 40, 80, 160 and 320. There is no 640 or 1280 case. Table 7.3 labels its degree-320 result in the 640 row, so retain the explicit `n=320` annotation if using that number. `LinComb.log` records 2.01 s for `ring` and 1.65 s for kernel checking at 320, but also other elaboration/sharing/lint stages. The file's elapsed time is 64.660 s. The report's selected phases omit import and other work. Its input also includes an expanded expression for a multiplier and proves an actual equation from a hypothesis, whereas PolyCert checks preconstructed coefficient lists. This is informative exploration of different routes, not a matched backend benchmark.

Useful future tests, also recorded in the JSON register: balanced dense factors; sparse multivariate expressions; large rational coefficients; target reification and denotation transfer; soundness-theorem application; proof-term size and memory; same-source strict/native policies; controlled fresh-process timing and separately reported import costs; true corrupted/arity/context-mismatch cases.

## Residual and native-policy observations

`PolyCert.lean` 44–47 checks a finite Catalan list: the residual vanishes below degree 6 and has coefficient -132 at degree 6. Source 49–50 checks that the finite-list derivatives of `X^5` and zero differ below degree 5. These are soundly scoped finite arithmetic claims. They do not prove a theorem connecting an arbitrary exact solution in `R[[X]]` to its jet, the general unit/power-series residual lemma, or preservation of arbitrary-order observations. No Abel instance appears in that source, so TeX 585's “Catalan and Abel instances checked” should not be inherited. The estimate that the missing machinery is a hundred lines (TeX 476, 583) is a proposal, not measured implementation effort.

Section 7.2's native-policy lesson is confirmed. Core `Lean/Meta/Native.lean` 31–37 specifies compilation/evaluation of a closed Boolean, 65–73 checks the native Boolean result, and 75–87 creates an axiom asserting its truth. `Lean/Elab/Tactic/Decide.lean` 57–65 supplies the `decide` expression to that path. [Pinned implementation](https://github.com/leanprover/lean4/blob/8c9756b28d64dab099da31a4c09229a9e6a2ef35/src/Lean/Meta/Native.lean#L31-L87).

Fresh results make the environment boundary explicit:

| Fresh source | Theorem | Printed axiom inventory |
|---|---|---|
| `TargetChecks.lean`, Mathlib tactic import | `grobnerRat`, `linearCombinationRat` | `propext`, `Classical.choice`, `Quot.sound` |
| Same file | `pureDecide` | `propext` |
| Same file | `nativeDecide` | `propext`, generated per-invocation native axiom |
| `AxiomProbe.lean`, no imports | `pureDecide` | none |
| Same no-import file | `nativeDecide` | generated per-invocation native axiom |

Do not promise that every `decide` proof is literally axiom-free: the imported environment changes this particular inventory. The useful policy distinction here is additional computation axioms versus the admitted ordinary logical axioms, with the actual transitive inventory recorded. The no-import probe separately reproduces the exact shape of the secondary report's example. Neither probe establishes correctness of an external CAS or of the proposed checker denotation.

## Suggested incorporation

Use the secondary report to make the next experiment concrete: existing Lean already supplies many underlying theorems and proof-producing polynomial tactics, while this prototype shows that a small closed coefficient-list test can be checked strictly at modest historical cost. The unresolved work is binding executable representations to the same mathematical target, proving the certificate checker/transport theorems, preserving guards and publication policy, and measuring the full process. The strict/native distinction should remain an explicit evidence policy; the recorded timings are one workload rather than a general backend recommendation.
