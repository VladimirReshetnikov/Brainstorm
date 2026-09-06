# Independent semantic review of the round-3 synthesis

Review scope: the complete `unified-report.tex` draft, sections 1–15, appendices, and bibliography, plus static review of `evidence/lean/SynthesisChecks.lean` and read-only checks of the retained validation receipts. This lane does not mutate the TeX, run Lean/build tools, or modify Git state. The successive-pass notes below preserve the reasoning behind corrections; the final-pass disposition records which changes were incorporated.

## Targeted corrections sent to the author

The distinct-contribution paragraphs in section 3 initially cite several shifted source section numbers. Correct mapping from the actual source TeX section order:

| Proposal | Initial citation | Relevant sections |
|---|---|---|
| Fiber | 8–9 | 9 exact quotients; 10 probability |
| Gneiss | 3, 9, 11 | 3 source diagnosis; 8 finite sections; 10 FLT interfaces |
| Karst | 9, 13 | 8 finite injection; 12 Leant/`List Empty` |
| Schist | 6, 10, 15 | 7 requirements; 9 orbital probability; 16 affine reference core |
| Tephra | 8–9, 14 | 7 observations; 8 prefix inverses; 13 realizability/parametricity |
| Trellis | 7, 13, 18 | Correct: closure, affine checker, evaluation |

Basalt's broad 10–15 citation and Moraine's 6,10 align with the claims they accompany. Section numbers apply before appendices; the source's appendix sections must be identified as letters when cited.

The introductory implementation recommendation should make clear that Schist's natural-number one-variable affine equality checker is a checked boundary seed/control. It cannot itself establish integer exact division, divisibility, or a cast into a field. The first exact-quotient interface must assemble ordinary exact-division and map lemmas, or add a separately justified checker. Reusing the acceptance architecture is not reusing the affine algebra's expressiveness.

## Mathematics and self-containedness through section 6

The mathematical claims checked so far are sound at their stated scope:

- Consequence and composition use the correct precondition implication direction and retain the actual intermediate value.
- Finite qualifier closure is relative to fixed ground rules, and the draft explicitly excludes rule generation, checking and proof-size costs from its bookkeeping bound. Grounded local expressions are correctly distinguished from numerical sampling.
- Sufficient requirement composition does not claim weakest preconditions. The draft already avoids Tephra's ambiguous suggestion of a unique weakest registered sufficient route.
- Construction is distinguished from adding a property to an unchanged object. Normalization may change the witness and must retain a relation to the original.
- Complete solutions require both soundness and coverage; enclosure collapse can establish equality; derivative transfer needs a local identity; all are accurately restated without relying on earlier reports.
- The source/translation/kernel distinction is substantive: checking an emitted term cannot establish that the frontend emitted the intended theorem.

The section 2 page counts for Schist 33, Tephra 39, and Trellis 37 were independently confirmed from the delivered PDFs with `pypdf`. Schist's older package validation record says 32, so the draft is right to use fresh PDF metadata and distinguish it from a source/PDF parity claim.

No correction is needed to the core logic in sections 1–6. The prose is self-contained at this stage; it defines the result, refinement, construction, and behavioral interfaces before depending on them. Remaining semantic examples and practical bridge/evidence details are expected in later sections rather than repeated here.

## Static review of the new Lean interface theorems

### `Round3Synthesis.refute_via_realization`

The statement correctly refutes the *fixed candidate's* universal contract over admissible inputs. It requires:

1. An actual source input `x` and `allowed x`.
2. Proof that `observeIn x = a` for the challenged abstract input.
3. A commuting theorem for the candidate and model on allowed inputs.
4. A preservation theorem saying a true source specification implies the abstract specification at the corresponding observations.
5. A proof that the abstract specification fails at `a, model a`.

The proof instantiates the purported source-wide contract at the same `x`, transports the observation via the commuting and realization equalities, and contradicts `bad`. No global surjectivity is needed, no inadmissible input is used, and no conclusion that *every candidate* fails follows. The assumptions are sufficient rather than minimal, which is appropriate for a reusable interface. The theorem does not supply an executable realizer, an abstract decision procedure, provider-law certification, or input-image completeness.

### `Round3Synthesis.reverse_via_observations`

The theorem correctly abstracts the finite-prefix proof pattern. It assumes jointly separating observations, individually surjective observations, commuting implementations for both endomorphisms, and a separate local reversal law. From `f(g x)=x`, surjectivity gives `fo i (go i y)=y` for *every* observed value `y`. The local law reverses that identity, and joint separation reflects equality back to the original object.

The `onto` premise is used and matters: without it the global one-sided identity only establishes the observed identity on the image of the observation, while `localReverse` expects it on the entire observation type. For prefix projections it is supplied by extension by zero; it is not a consequence of joint faithfulness. `localReverse` stands in for the separate finite-matrix theorem (or another directly finite endomorphism class). The Lean theorem does not prove that arbitrary observed endomorphisms have this property, and its source comment accurately says so. It also makes no finiteness or linearity claim by itself.

Both supplied proof terms match these mathematical arguments. This is static assessment only; root-owned execution receipts determine whether Lean accepts them and which axioms they use.

## Second review pass: worked examples, Leant, and checker evidence

Read the appended draft through the end of "Certified computation: what is now actually checked."

The exact-quotient helper is satisfiable under the stated parameter assumptions. All three single-premise mutations work: `(3,2,4)` makes the first numerator -66, `(3,3,5)` makes it -1, and `(3,2,3)` makes the second numerator -216, which is not divisible by 16. The transport theorem separates source balance, homomorphic transport, and target inversion correctly. Its isolated context avoids the vacuity of deriving helper facts from an already available contradiction.

The finite-prefix proof, its two different shift/halving negatives, and its separation from the generic checked observation theorem are correct. The draft does not misattribute the finite-matrix theorem itself to `SynthesisChecks.lean`. The orbital argument and its bounded-product strengthening are valid, with no unnecessary cancellation or continuity assumption. The distribution-function atom correction, concentration-spike failure of dominated interchange, and derivative-attainment direction for least Lipschitz constants are also correct. The singleton `Q[X]` tensor counterexample establishes the claimed omission in the reconstructed premise, conditional on the exact source comparison retained by the other review lane.

The list-length account correctly distinguishes the interpreter theorem, the supplied universal model law, the Python affine coefficient normalizer, and the still-missing arbitrary-candidate correspondence. Zero plus basis-vector testing is complete for equality of the stated natural-coefficient affine expressions, because evaluating at zero identifies constants and natural addition cancellation identifies each coefficient at the basis vectors. It is not a generic finite-testing argument, and the draft says so.

Three targeted edits were sent:

1. The Fiber citation in the exact-quotient worked example should use section 9, not section 8.
2. In the negative-evidence paragraph, replace plain "global surjectivity" with **surjectivity of the observation restricted to admissible inputs**. An abstract witness realized only at a disallowed source input cannot refute the guarded source specification. The Lean theorem already has the correct stronger requirement `allowed x` for its particular witness.
3. Specify real-valued measurable random variables/probability laws in the probability applications, including real `t` and nonnegative epsilon for the coupling bound, or restate the intended more general ambient-space hypotheses. Specializing characteristic-function uniqueness to laws on the real line is a concise way to make this example self-contained without inheriting the earlier source's complete-space assumptions silently.

The main strong idea still worth incorporating in the final fidelity section is Trellis section 16.2's three distinct dependency notions: public-interface premise, premise supplied to this application, and actual retained proof dependencies. None alone proves mathematical indispensability. A required named method needs an actual derivation node, not a decorative occurrence of a theorem constant.

## Final pass: implementation, evaluation, questions, and evidence

The full report now incorporates the source-section corrections, Schist checker scope qualification, admissible-realization wording, explicit real probability hypotheses, definition of `F_0`, and Trellis's three dependency notions. These changes were verified in the revised source. The implementation gates preserve the source-to-model and model-to-original-target obligations rather than treating a successful checker as a complete frontend. The staged evaluation separates mathematical libraries, additional automation, property elaboration, and narrative presentation. The ten discussion questions identify concrete choices and falsifying experiments and are understandable without earlier reports.

Two last edits were sent and then independently verified in the revised source:

1. The common-services paragraph originally granted solvers and Leant providers to L1–L4, which conflicted with L2 being the added-services treatment. It now grants mathematical packages and theorem registrations to L1–L4, added search/certificate services to L2–L4, and ordinary existing Lean automation to the baseline where applicable.
2. The bibliography's Lean axioms URL had an extra `The-Type-System/` component; a fresh web request returned 404. It now uses the verified official address `https://lean-lang.org/doc/reference/latest/Axioms/`.

Read-only independent counts agree with the report:

- The seven source files contain 49 named theorem declarations: Basalt 2, Fiber 3, Gneiss 2, Karst 12, Moraine 16, Schist 8, Tephra 6.
- Deduplicating the original and additional audit log declarations gives 32 individually queried declarations: 27 report no axioms and five report only `propext`. The five are Moraine's `LengthExpr.model_sound` and `LengthExpr.promote_model_spec`, and Schist's `AffineCertificate.eval_nf`, `AffineCertificate.check_sound`, and `AffineCertificate.original_target`.
- The two separate `Round3Synthesis` interface theorem logs each report no axioms. They are correctly reported separately from the original 49-theorem inventory.
- All nine Python figures agree with retained receipts: Basalt 24 test methods; Fiber 1,298 checks in 31 groups; Gneiss 32 test methods; Karst eight groups; Moraine 32 named tests; Obsidian 608 probes; Schist 10 test methods; Tephra 23 test methods; Trellis 31 cases (nine acceptance, 22 rejection).
- Moraine's nested loops independently account for its more detailed figures: 400 generated expressions times 4 cubed length vectors gives 25,600 interpreter comparisons; 3 cubed affine forms paired with each other gives 729 ordered form pairs. These are finite regression instances within two named tests, not additional theorem declarations.

No unresolved mathematical or semantic blocker was found in the final source. The relevant limitations remain explicit: the audit does not prove the frontend's statement fidelity, establish general checker soundness beyond the checked fragments, prove arbitrary provider correspondence, or demonstrate improved authoring productivity. This review is not a PDF layout or source/PDF parity check, and it relies on the root-owned execution logs for Lean compilation rather than rerunning Lean.
