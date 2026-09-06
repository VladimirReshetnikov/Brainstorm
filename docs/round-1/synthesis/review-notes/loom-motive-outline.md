# Independent analytic review: Loom, Motive, Outline

Reviewed 2026-09-05. This memo reads the complete substantive text and supporting README/source manifests of the three reports. Locators below refer to their committed TeX source, with section numbers counted from the source. These are design studies: none contains an implemented language, compiled translation of its proposed syntax, or a measured usability/compression result. I also inspected selected original repository objects through read-only `git show` at the reports' pinned revision; that is source corroboration, not Lean compilation. No original report or reference repository was modified.

## Overall assessment

These three proposals describe substantially the same architecture: retain Lean's logic and expressions; write mathematical choices as structured claims or plans; elaborate their consequences into scoped obligations; use bounded untrusted reconstruction; check the exact approved statement; save evidence separately from discovery. Their strongest distinctive contributions are concrete mathematical interfaces and failure examples, rather than three competing language foundations. The synthesis should merge their shared architecture once and preserve their examples and finer engineering distinctions as contributions to it.

Agreement across different examples makes a credible design hypothesis. It is not three empirical replications: all three reviewed the same ProveIt revision and heavily overlap in Leant documentation and proof-language precedents. Their repeated conditional soundness arguments say what acceptance must check; they do not establish compiler correctness, reconstruction feasibility, or cognitive benefit.

## Six-feature crosswalk

Paths abbreviated here: **L** = `docs/ideas/loom_proof_language/loom.tex`; **M** = `docs/ideas/motive_proof_language_article/motive.tex`; **O** = `docs/ideas/outline_proof_language/outline_proof_language.tex`.

| Common feature | Loom | Motive | Outline |
|---|---|---|---|
| Lean host and existing expression language | §§3.1, 12.1; lines 173–194, 812–816; labels `sec:design`, `sec:implementation` | §4.2, §10; lines 257–261, 637; labels `sec:contract`, `sec:implementation` | §§5.1, 15.1; lines 255–269, 905–907; labels `sec:surface`, `sec:implementation` |
| Claims/checkpoints as authoring unit | §§3.2–3.3; lines 198–208 | §4; lines 233–238; definition of proof-move contract | §4.1; lines 218–228; §5.1, 255–267 |
| Scoped obligations and method contracts | §§8.1–8.4; lines 550–615; `sec:semantics` | §§6.1–6.3; lines 423–469; `sec:semantics` | §7.1, §§10.1–10.2; lines 395–404, 617–658; `sec:plans`, `sec:semantics` |
| Statement/object fidelity before search | §3.4, §7.4; lines 212–216, 526–543 | §4.2, §9.2; lines 257–261, 608–612 | §4.2; lines 231–235; object distinctions §2.1, 144–148 |
| Frozen evidence and search-free replay | §10.1; lines 737–741; `sec:trust` | §9.5; lines 629–633; `sec:trust` | §§12.4–12.5; lines 779–798; `sec:trust` |
| Fair Lean baseline and shared-infrastructure cost | §§13.1–13.2; lines 845–855; `sec:evaluation` | §§11.1–11.3; lines 692–712; `sec:evaluation` | §§14.2–14.3; lines 860–888; `sec:evaluation` |

## Loom: best contributions and qualifications

**Distinctive center:** contracted local mathematical recipes, with especially careful treatment of dependent context identity, shared metavariables, and candidate/witness identity. Its three case studies are autonomous derivatives, Abel coefficients over a rational algebra, and Boolean-cube reindexing.

1. **Locality is explicit mathematics, not derivative syntax.** In §4 (`sec:derivative`, lines 223–295), differentiating an induction identity needs equality in a neighborhood, obtained from openness. The input derivative family is required only at values reached by the function; the proposal correctly refuses a hidden global smoothness assumption. The counterexample `f(t)=0`, `g(t)=t` at zero separates equality at a point from local equality. Ordinary and within-set derivatives get different contracts. This is a particularly strong first implementation target: a stable helper theorem can capture most of the filter bookkeeping, and a small surface adapter can show what it inferred. The report itself says syntax does not replace mathematical API design (285–287).

2. **Rational scalar transport preserves algebraic generality.** §5 (`sec:abel`, 302–383) gives the coefficient identity for a commutative rational algebra, explicitly including rings with zero divisors and the trivial ring. Rational inverses are taken in Q, then mapped to A; the argument never assumes A is a field or that its algebra map is injective. This is better than a generic cast-hiding proposal: typed normalization has a declared direction and a proof certificate. It also distinguishes index subtraction from ring subtraction and formal-series substitution from analytic convergence. §5.5 (387–401) correctly attributes further compression to an exponential-generating-function API.

3. **Finite transformations preserve the author's choice.** §6 (`sec:affine`, 408–495) retains the membership partition, inverse map, and generalization over the evaluation point; it reconstructs bijection and cardinality details. The algebraic expansion needs only a commutative ring and an additive commutative group, not the later analytic assumptions. A many-to-one map is rejected unless another theorem accounts for multiplicities (469–473). Generalizing the induction motive is a visible choice (477–479).

4. **Its obligation model addresses a real concurrency trap.** §8.3 (589–605) distinguishes the visible proof DAG from shared elaboration constraints. Two leaves sharing a witness metavariable are not independent merely because the UI draws separate boxes. It proposes transactional substitution or explicit closed interfaces, and checked context substitution for cache reuse. This is more detailed than the other two reports and should survive into the synthesis. §8.4 (609–615) also proposes checking incomplete plans as conditional skeletons with explicit obligation parameters, without manufacturing `sorry` declarations. A skeleton is a conditional derivation, not a completed theorem.

5. **Good separation of guarantees.** §8.6 (637–639) separates typing, statement fidelity, contract fidelity, and explanatory fidelity. §§9.3–9.4 (681–708) preserve Leant's callback-acceptance meaning and require work bounds beyond a success quota. §10.5 (767–774) gives the deliberately limited stability claim: resolved proof replay survives a well-formed extension preserving its actual dependencies, while source search may change under a new simp rule.

**Assessment.** Loom offers the strongest low-level specification among this trio, but the hard work remains: deciding which constraints are stable enough to close as independent obligations; representing exact environment dependencies without locking every harmless detail; implementing replay formats across Lean versions; and designing useful local normalizers. Its metatheoretic propositions are conditional design arguments. They should be presented as acceptance invariants, not as proof that implementing the architecture is routine.

**Next useful experiment.** Implement only local derivative transfer, with exact existing theorem headers and separate ordinary/within-set contracts. Compare (i) original Lean, (ii) the same helper theorem in idiomatic Lean, and (iii) the contracted interface. Add failures for point-only equality, missing neighborhood, changed evaluation point, and a shared-witness concurrency case.

## Motive: best contributions and qualifications

**Distinctive center:** preserve mathematical decisions while generating their consequences; scope-aware finite reindexing and order calculations; especially strong negative controls and accounting for already-good Lean.

1. **Concision can make an already-good proof worse.** §2.3 (180–195) and §5.5 (394–412) use normalization of a geometric Richardson polynomial as an intentional negative control. The existing mass-one proof is already a rewrite and `div_self hden`. The desired language must not force it into a paragraph or claim shortening. The condition is exactly that the normalizing value is nonzero; `q != 0` is unnecessarily strong in some cases, while `q != 1` is insufficient in arbitrary fields because another relevant power can equal one. This gives a useful evaluation control: a language may be worthwhile overall without winning on every proof.

2. **Automatically provable does not mean narratively dispensable.** The Lambert chain in §5.4 (360–392) keeps `w >= 0` in the visible argument because it explains multiplying an inequality to obtain the lower bound. §5.3 (351–357) separates nonnegative factors for weak inequality from positive factors for strict inequality. This corrects an easy but harmful interpretation of “automate routine work”: an author should be able to retain an illuminating fact even if no machine assistance is needed to prove it.

3. **Representation bridges should remain typed and directional.** Binomial inversion §5.1 (287–331) spells out the interval bijection and its inverse, natural subtraction bounds, natural-to-integer binomial transport, and the final zero case. §8.1 (551–555) warns that transporting an integer equality to a quotient ring cannot be reversed merely by hiding casts. Its finite-sum abstraction is deliberately not an infinite-rearrangement rule (§5.2, 334–336).

4. **Failed approximation is weaker than refutation.** §7.4 (518–537) has a sharp counterexample: treating Lean's `0=0` as an opaque atom yields no propositional proof from an empty context even though the original equality has reflexivity. Intuitionistic nonderivability of double-negation elimination is not a proof of its negation. `Checked`, `RefutedOriginal`, `FragmentUninhabited`, `Unsupported`, and `UnknownBudget` express different evidence. This is an especially good source example for the synthesis's Leant integration section.

5. **Method provenance is implementable; indispensability is not promised.** §9.4 (622–626) refuses to retain the explanation “by alternating row” when a solver actually used the target inversion theorem. Yet it also observes that merely finding a lemma name in a dead binding does not establish explanatory relevance. Enforced recipe provenance is therefore distinct from claiming a lemma was semantically indispensable.

6. **Evaluation charges the missing work.** §§11.2–11.4 (699–719) exclude target aliases/downstream theorem leakage, use family-level held-out splits, charge package construction plus sketch and repair work in consistent units, and measure readers' ability to diagnose missing hypotheses. A shorter displayed proof can hide a large custom adapter; the report explicitly rejects counting that as a proven benefit.

**Assessment.** Motive is exceptionally careful about not overclaiming improvements. Its main remaining uncertainty is whether stable aliases and mathematical interfaces improve the authoring experience enough beyond using the same helpers in Lean. Its staged plan puts the full frozen manifest and hardened replay bundle in stage four (§10.4), whereas exact headers and generated Lean proofs occur earlier; the synthesis should make a minimal exact-target/replay boundary foundational and defer its rich packaging, not defer correctness.

**Next useful experiment.** Pair a moderately long binomial-reindexing proof with the already-short Richardson normalization proof, and ask authors/readers to repair a missing upper bound, nonzero denominator, and strictness condition. Measure both successful compression and regressions.

## Outline: best contributions and qualifications

**Distinctive center:** theorem-shaped proof plans, especially symmetry/context transport, endpoint reasoning, and double counting; clear separation of proof refactoring from language design.

1. **Some gains come from a better argument.** §1.2 (136–139) explicitly separates library engineering, proof refactoring, automation, and language/interface changes. In §6.2 (315–342), the residual-to-root proof obtains both endpoint inequalities and applies the intermediate value theorem once, replacing the original residual-sign split. This is a mathematical reorganization that can be implemented directly in Lean. The language contribution is displaying the two slope applications and their obligations. The theorem retains continuity on D, differentiability only on its interior, positive lower slope, and containment of the whole residual interval.

2. **WLOG must transport the complete problem.** §7.2 (`sec:wlog`, 411–434) gives a useful abstract reduction over problem states u: representative coverage, preservation of H under a transformation sigma, and a return implication on C. It does not unnecessarily require sigma to be an involution. Swapping visually symmetric variables is insufficient when a hypothesis such as `x=0` is asymmetric. This is stronger than “assume the ordered case” as informal syntax and provides an excellent contract testcase.

3. **Plans, preferences, and restrictions are different source constructs.** §4.4 (243–251) distinguishes `by lower_slope` (required checked plan), `prefer lower_slope` (ranking hint), and `using only` (dependency scope with declared background). This should become part of the unified language interface. Loom and Motive have compatible method-fidelity policies, but Outline makes the user-facing distinction especially crisp. It is an elaboration mode distinction, not a disagreement about proof validity.

4. **The floor-sqrt example derives side conditions from a balance.** §9.2 (549–582) counts pairs `(j,k)` with `j^2 <= k` to obtain the natural-number balance T + Q = s(n+1), and proves 6Q = s(s+1)(2s+1). Natural subtraction and exact division then follow from those identities. §9.4 (604–612) extracts a general finite fiber-counting plan. This suggests a wider useful technique: seek structural identities that entail exactness side conditions instead of treating every cast condition as an unrelated arithmetic goal. It remains an uncompiled alternative proof and requires a reusable counting library, whose cost is acknowledged in 601.

5. **Noncommutativity is an important preserved boundary.** §8.1–8.3 (462–535) distinguishes Gaussian summation over a semiring from its commutative alternative and proves closure of the centralizer of x under products without assuming those factors commute with each other. The generalized induction motive is visible. This adds a useful kind of negative test not supplied by ordinary field-calculation examples.

6. **Total operations and authoring conventions need separate policies.** §12.3 (772–776) distinguishes well-typed division/derivatives from applicability of cancellation/calculus theorems and from a stricter notation convention that may generate domain obligations. This avoids either making every division expression partial or reading a derivative symbol as a hidden differentiability premise. It is an explicit policy choice for the next iteration.

**Assessment.** Outline's best material is its mathematical refactoring and semantic-plan API. Its cost model correctly makes target fidelity and policy adherence hard constraints, rather than weighted penalties (§14.1, 855). Its broad list of proposed plans still lacks evidence of reliable lowering, failure localization, and maintenance under changing dependent contexts. A first implementation should select one plan, not attempt all illustrated phrases.

**Next useful experiment.** Implement WLOG with a supplied state transformation and exact context transport, or finite-range reindexing with supplied maps. Require a valid neighboring example for every rejection, as Appendix C says at 1102; a system that rejects every nontrivial transformation is not a successful precise language.

## Genuine differences and unresolved choices

- **No foundational split:** all three recommend a Lean extension, local reconstruction, a native escape hatch, and later richer discourse. It would misrepresent them to assign “contracts” only to Loom, “readability” only to Motive, or “plans” only to Outline.
- **Evidence-first sequencing:** Loom §12.1 makes statement/evidence boundaries the first engineering target. Motive §10.4 adds its full sealing package later, although its first stage already uses exact headers and exports Lean proofs. This is a difference in staging emphasis, not permission to admit unchecked theorems.
- **Anaphora across edits:** Loom §7.3 (520) wants accepted referents to become stable IDs so insertion cannot silently redirect them. Outline §5.3 (289–291) gives lexical last-assertion rules and displays changed referents in a semantic diff. These suggest a real default choice: retain a previously accepted referent until explicit rebinding, or re-elaborate lexically and require review of a detected semantic change. The reports do not settle how pretty source is rewritten after either action.
- **Concurrency:** Loom's shared-constraint warning should qualify generic claims that a proof DAG can be solved in parallel. Independence requires a checked interface or coordinated metavariable state, not only absence of visible edges.
- **Proof versus explanation:** all distinguish kernel validity from plan fidelity and reader understanding. The next design must specify whether changing a method-specific explanation is an automatic source repair, an author choice, or a mode-dependent operation.
- **Representation-normalization policy:** all retain exact coercions internally; Outline explicitly permits stricter notation-domain conventions. A next-round question should ask what the default displays and when new domain obligations are generated, rather than ask whether all casts can be omitted.

## Additional synthesis suggestions

These suggestions extend the reports rather than claim an existing implementation.

1. Treat acceptance as a tuple of independently inspectable results: exact-statement comparison, proof check, axiom/dependency policy, method conformance, replay receipt. Keep comprehension evidence outside that tuple. This makes failures specific and avoids both a misleading universal badge and a long linear status ladder for incomparable facts.
2. Give every recipe a paired evaluation contract: its intended reusable theorem/interface, at least one positive example at weak hypotheses, a nearby invalid plan, a resource budget, and an idiomatic-Lean baseline using the same helper. This tests usefulness and precision together.
3. Use proof refactoring to generate a side-condition basis. Outline's balance identity and Loom's rational-unit transport show that several small conditions can be consequences of one structural certificate. Discovering that certificate may matter more than speeding up independent arithmetic leaves.
4. Treat statement stability as semantic review proportional to the change. A fully resolved unchanged Lean header need not demand repeated modal confirmation; a changed binder, branch, representation, or assumption should be surfaced. All three call for approval/fidelity, but a product needs an ergonomic review protocol to avoid turning correctness into constant interruptions.

## Read-only source corroboration

The following were inspected from local Git object stores, not rebuilt:

- ProveIt `24ce8bd743eaab64a91ce90725ea00f498d319d2`, `AutonomousIteratedDeriv.lean`: complete module confirms range-only `hGd`, eventual equality obtained using `hs.mem_nhds`, and the separate globally differentiable wrapper.
- Same revision, `MeanValueBracket.lean`: complete module confirms the residual theorem's interval containment and sign split, the two slope application APIs, the nonnegative lower-slope hypothesis for its upper absolute-value theorem, and shorter inverse corollaries. Outline's endpoint reorganization is an alternative to this source, not an already-compiled source change.
- Same revision, `GeometricRichardson.lean`: inspected source confirms the normalized mass-one theorem uses only `hden` at the field stage and is a two-line proof; the degree theorem separately requires a nonzero base.
- Same revision, `AbelPolynomialSeries.lean`: section assumptions at source lines 75ff are `[CommRing A] [Algebra Q A]`; `coeff_exp_subst_of_abel_eq` starts at 113 and constructs `hcancel`/`hfactorial` at 128/132.
- Same revision, `QPascalSummation.lean`: full 94-line module confirms first summation `[Semiring R]` at 43, second `[CommSemiring R]` at 58, and generalized induction at 76 with instances at k and k+1 at 86.
- Leant `3a40904be8a410d832d9ab6900b3d3e7b425eccb`, `src/Leant/Synth/Verification.hs`, lines 41–55: `Verified` explicitly records supplied-callback acceptance and disclaims kernel proof/solver/behavioral authority.

The reports cite external literature and moving Lean documentation. This memo has not independently audited those bibliographies; the parent synthesis should verify any external technical claims it chooses to adopt. Motive's README names a `SHA256SUMS.txt` that is absent from the delivered directory; that is a minor packaging discrepancy, not evidence about the language proposal.
