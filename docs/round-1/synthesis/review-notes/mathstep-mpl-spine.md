# Analytical review: MathStep, Mathematical Proof Layer, and Spine

This memo reviews the complete substantive TeX text, appendices, bibliographies, READMEs, and supplied source manifests of three reports. It distinguishes the reports' proposals and static source observations from this reviewer's evaluations. It does not verify the reports' external bibliographies, rerun Lean, or inspect the mathematical repositories independently. All line locators below refer to the supplied TeX files in this checkout. Section numbers were computed from the actual section hierarchy.

Report keys:

- **MS**: `docs/ideas/MathStep/MathStep.tex`, *MathStep: A Proof Language of Mathematical Steps*.
- **MPL**: `docs/ideas/mathematical_proof_language/article.tex`, *Mathematical Intent, Formal Evidence*, proposing a Mathematical Proof Layer.
- **SP**: `docs/ideas/Spine_Proof_Language/Spine_Proof_Language.tex`, *Spine: A Proof Language for Mathematical Intent*.

## Main judgment

These are substantially convergent designs, with different case-study portfolios and implementation priorities. They do not constitute three rival foundational languages. All recommend a conservative Lean extension whose durable units are explicit mathematical assertions or actions, completed by scoped proof-producing methods and search, with fixed meanings, inspectable obligations, and retained evidence. A unified report should describe that shared architecture once and spend its comparative attention on the useful refinements, unresolved engineering choices, and the empirical test still missing.

The agreement is proposal-level convergence, not corroborating evidence that the interface works. These reports share the same ProveIt revision, substantial Leant background, and in two cases the exact autonomous-derivative example. Their common conclusions therefore cannot be treated as independent measurements or a statistically independent vote. All three explicitly disclaim an implemented language compiler, executed proposed syntax, measured compression results, or a user study.

## Six-feature convergence crosswalk

| Common feature | MS: exact support | MPL: exact support | SP: exact support |
|---|---|---|---|
| Lean host and existing foundation/library | §3.2, `sec:concept`, lines 223–228; §18.1, `sec:implementation`, 1084–1089 | §16.1, `sec:implementation`, 914–918; §1, 90–92 | §1.1, `sec:thesis`, 112–115; §15.1, `sec:implementation`, 929–934 |
| Authored claims/checkpoints are persistent explanatory units | §3.3, 243–254; §10.2, `sec:ir`, 718–723 | §5.2, `sec:contracts`, 303–316; §5.5, 330–334; §15.1, `sec:experience`, 883–889 | §3.1, `sec:concept`, 247–252; §7.3, `sec:semantics`, 553–562; §10.6, 727–735 |
| Scoped obligations and checked method contracts | §§4.3–4.4, `sec:surface`, 284–311; §9.1, `sec:methods`, 642–659; §11.3, 772–800 | §§5.1–5.5, `sec:contracts`, 289–334; §§11.3–11.4, `sec:calculus`, 707–740; §16.5, 942–959 | §§7.2–7.6, `sec:semantics`, 538–609; §10.2, `sec:architecture`, 701–706 |
| Fix statement/object meaning before search; distinguish proof and data choices | §§4.2,4.5, 277–282,313–325; §§14.1,14.3, `sec:trust`, 954–977 | §§12.1–12.4, `sec:fidelity`, 751–777; §§2.2–2.3, 147–157 | §7.1, 531–536; §§9.1–9.3, `sec:ambiguity`, 647–668; §12.1, 792–797 |
| Freeze evidence and replay without rediscovery | §§15.1–15.4, `sec:freeze`, 988–1030 | §14.4, `sec:trust`, 872–878; §16.4, 936–940; §15.3, 897–903 | §§12.4–12.7, `sec:trust`, 813–855 |
| Fair ordinary-Lean baselines and charge for helper/method costs | §§19.1–19.4, `sec:evaluation`, 1133–1184; §18.4, 1126–1129 | §§17.1–17.4, `sec:evaluation`, 964–1018; §9 negative control, 610–629 | §§16.1–16.5, `sec:evaluation`, 965–1017; §5.5, 443–453; §4.3, 353–368 |

All three also converge on controlled syntax rather than unrestricted English as proof authority; context-sensitive notation; explicit theorem/instance identities; scope-sensitive witness choices; separation of search failure from negation; axiom allowlists and transitive dependency audits; exploratory versus publication status; ordinary Lean escape hatches; three levels of readable source, obligations, and formal evidence; and diagnostics stating missing mathematics.

## What each report contributes distinctly

### MathStep

1. **Method repertoire across algebra, local analysis, binder traversal, and structural induction.** Its four source files are `AlgebraicInverseGermAnalytic.lean`, `AutonomousIteratedDeriv.lean`, `AliasQBinomialBridge.lean`, and `NaturalDeduction/Calculus.lean` (§2.1, 165–177; Appendix C `app:sourcemap`, 1295–1307). This broadens the shared discussion beyond one calculus or coefficient domain.
2. **Constructor-preserving induction completion.** The proposal `rebuild the same constructor from induction hypotheses` handles the ten routine branches of `Derives.mapAxioms` after the exceptional axiom-map branch. It insists on all eleven cases, exact contextual indices, and invalidation when a constructor is added (§8.1–8.3, `sec:structural`, 598–631). This is a sharply bounded and falsifiable structural-synthesis target. It also separates object-language classical axioms from classical reasoning in the metatheory (§8.4, 633–638).
3. **Congruence traversal under binders as reusable infrastructure.** The dyadic finite-cosine substitution introduces a local summand and membership proof, derives its bounds, instantiates a theorem, transports real equality into complex equality, and applies sum congruence. The general interface is typed traversal plus local side-condition synthesis, with named/structural expression selectors instead of occurrence numbers (§7.3–7.4, `sec:dyadic`, 562–594).
4. **A useful counterexample to naive branch selection.** For `R(q)=(sqrt(1+64q/9)-1)/8`, the alternative positive-square-root uniqueness proof preserves the original implication but differs from the source's factorization argument. It notices that the source's `q≥0` hypothesis is redundant for this alternative uniqueness proof without silently changing the theorem (§5.3, `sec:root`, 372–400). This is a good example of treating theorem strengthening as a separate result.
5. **A practical nuance about early statement fixing.** It explicitly acknowledges that dependent elaboration may require constructing a witness before every local expression is resolved. The rule is to prohibit proof-success-driven reinterpretation and to expose dependencies and the final resolved proposition (§4.2, 277–282). The unified architecture should retain this nuance rather than prohibit ordinary bidirectional elaboration.
6. **Separate positive-proof and negative-search cache keys.** Exact positive evidence can survive irrelevant library extensions; a failed bounded search depends additionally on provider inventory, policies, and budget (§15.3, 1016–1023). A search receipt is never negative mathematical evidence by virtue of being cached.

MS's implementation order is explicit: assertions/replay; guarded real algebra and elementary differentiation; Leant adapter; local differentiation and binder operations; structured induction; evaluation (§18.2, 1108–1119). It does not require rewriting Djex first (§18.3, 1121–1124).

### Mathematical Proof Layer

1. **Most concrete formal-series method kernel in this trio.** It proposes a restricted coefficient compiler based on linearity, derivative coefficients, rational scalars, and the support-aware shifted-EGF identity

   `n! [z^n] ((z^s/s!) EGF(a)) = choose(n,s) a_(n-s)`.

   Its proof splits `s≤n` from `n<s`; in the second case support and the binomial coefficient both vanish (§8.4, `sec:stirling`, 571–589; equation `eq:shifted-egf`). This supports a reusable implementation rather than a bespoke keyword for Stirling numbers.
2. **Preservation of algebraic generality as an acceptance test.** The Abel example is over an arbitrary commutative rational algebra, not a field. Fractions are rational scalar actions. The proof uses homomorphism preservation of rational identities, not injectivity or an added nontriviality premise; it even covers a degenerate coefficient algebra (§6.1–6.4, `sec:abel`, 339–420). The theorem applies to any solution of the substitution equation, not only the canonical `abelSeries`. Its constant coefficient must be handled separately to obtain the full series identity (§6.5, 422–438).
3. **Direction-sensitive representation transport.** `work in B via f` needs equality reflection, usually injectivity, for an equality target; implication preservation and order reflection have different contracts (§4.4, 257–263). In the Stirling proof the natural-to-rational map reflects equality; there is no ring map from rationals back to naturals (§8.5, 591–597).
4. **Explicit synthesis effect categories.** Requests are proof-only, data-producing, or statement-resolving, with different exposure and acceptance policies (§12.4, 771–777; protocol field at 792). This is a useful semantic design rather than merely a UX distinction.
5. **An especially honest compact-Lean control.** The weighted scaling proof is already four lines of `funext`, `fin_cases`, simplification and `field_simp`. MPL says a weighted-homogeneity method could add explanatory reuse across a family of maps, but its setup cost may make ordinary Lean preferable for a single example (§9, `sec:scaling`, 599–629). This resists attributing all long expressions to a language failure.

MPL prioritizes a formal-series pack and a local-calculus pack after the small core, with weighted scaling later (§16.1–16.2, 914–926). Its outline puts structural synthesis/theorem instantiation before domain methods in the default search schedule (§13.2, 799–805), unlike MS's selected-method-first emphasis. Both explicitly classify the schedule as policy rather than semantics.

### Spine

1. **Every asserted source node must be certified, even if unused by the final proof.** This closes an important distinction between certification of the final theorem and certification of the displayed proof document (§7.3, 553–562; §7.6, 595–607; rejection test at 1010). A false intermediate assertion cannot survive merely because automation bypassed it. Other reports also require checked local assertions, but Spine states the unused-node requirement particularly clearly.
2. **Proof/data/structural/presentation holes.** Structural instances such as topologies, algebra structures, measures or norms can change meaning; proposition-valued instances such as `IsProbabilityMeasure μ` supply evidence of already-fixed objects and can be routed automatically when unambiguous (§§9.1–9.3, 647–668; §2.4, 205–208). This refines MPL's three-way effect taxonomy by explicitly separating rendering from semantics.
3. **Shared-metavariable coordination for parallel search.** Obligations for `P(x)` and `Q(x)` cannot be separately marked successful using incompatible `x`s. Spine proposes grouping by shared metavariables, immutable search snapshots, explicit candidate substitutions, and compatibility checks (§10.4, 715–718). This is more precise than simply saying that individual tactic branches should be isolated.
4. **Two proof plans kept separate.** The prefix convolution proof can preserve double induction and Pascal, or replace the inner induction with triangular finite-sum interchange and a hockey-stick lemma. Spine treats the latter as a different proof plan whose helper costs must be charged (§4.1–4.4, 297–373). The bounded-domain method keeps the endpoint apart from the residual range, preventing use of `m≤n` at `m=n+1`.
5. **Iteration and limits as compositional methods.** The characteristic-function proof exposes the difference function, orbit, step inequality, geometric decay, continuity, and limit-order reasoning. It preserves `q=0` and negative `q`; it does not require `|a(t)|<1` because contraction is in the argument, nor introduce moment assumptions (§5.1–5.4, `sec:contraction`, 377–441). The broader theorem “vanishing along a contracting orbit” is explicitly charged to the shared ordinary-Lean library (§5.5, 443–453).
6. **Typed observation paths.** In `Polynomial (PowerSeries R)`, `[z^k]` and `[Q^0]` are different operations, not ambiguous instances of “coefficient”; their composition follows a typed path through the nested object (§6.1, 457–464; §8.3, 627–632). The surviving-support method uses this distinction and parity guards (§6.2, 466–496).
7. **General rings and formal versus analytic meaning.** The formal implicit-root theorem needs a unit linear coefficient, not merely a nonzero one. Over integers, `2S(Q)-Q=0` has no solution because its degree-one coefficient would satisfy `2s₁=1` (§2.6, 222–225; §6.3, 498–520). A formal root does not by itself converge or supply an executable coefficient algorithm (§6.4, 522–527).
8. **Benchmark leakage control.** Exclude the target declaration and downstream declarations leaking its proof, audit dependencies, compare identical-model ordinary Lean, and report proof-plan categories separately (§16.1, 965–970). This is a valuable refinement of the common fair-baseline requirement.

Spine prioritizes finite sums, then iteration/limits, then coefficient views, then Leant integration (§15, 927–961). It allows generated explicit Lean declarations as an initial replay format instead of inventing a binary certificate format (§12.5, 836–841; §15.1, 929–934).

## Negative examples worth carrying into the unified report

| Proposed transformation or mutation | Concrete obstacle | Locators |
|---|---|---|
| Differentiate equality only at one point | `f(t)=t` and `g(t)=0` agree at zero, derivatives differ | MS §6.4, 504–516; MPL §7.4, 494–498 |
| Drop a root branch condition | At `q=0`, `z=0` and `z=-1/4` solve the quadratic; only zero is the selected root | MS §5.3, 396–400 |
| Treat natural subtraction as ring subtraction | `N=1,k=2` invalidates the dyadic cast identity; `n=0,m=1` invalidates `(n+1)-m=(n-m)+1` | MS §7.2, 556–560; SP §2.2, 177; §4.2, 341–351 |
| Apply shifted-EGF factorial quotient without support | `n<s` requires zero support, not division by a fabricated factorial index | MPL §§8.2–8.5, 532–597 |
| Infer `m/2>0` from `m≠0` | Natural division at `m=1` is zero; evenness must remain in scope | SP §6.2, 466–473 |
| Weaken unit to nonzero over a commutative ring | `2S-Q=0` has no integral formal-series solution | SP §2.6, 222–225 |
| Weaken `|q|<1` to `|q|≤1` for orbit decay | Generic geometric-decay method no longer applies at the boundary | SP §13.2, 875–879; §16.4, 1001 |
| Replace arbitrary solution by canonical one, rational algebra by field, or local differentiability by global | Valid proof may establish a different, less general theorem | MPL §12.1, 751–755; MS §6.1, 441–453 |
| Move a witness outside its dependencies | Changes quantifier order or creates an escaping variable | MS §4.5, 313–325; SP §9.2, 654–663 |
| Treat empty/exhausted search as negation | Non-discovery and fragment-relative nonderivability do not produce a Lean proof of `¬P` | MS §12.3, 838–854; MPL §13.3, 807–819; SP §11.7, 785–788 |
| Accept only final theorem while printing unchecked intermediate claims | A valid final proof can bypass a false displayed assertion | SP §7.3, 562; §16.4, 1010 |

Not all failures in this table refute the enclosing theorem. Some refute one local rewrite; some merely show a method's current premises are insufficient; some detect a changed specification. This distinction belongs in both the report and the proposed diagnostic interface.

## Tensions and unresolved choices: mostly compatible refinements

**No substantive foundational contradiction was found in these three reports.** Differences in names (`have` versus `fact`), method schedule, and first domain pack are implementation alternatives, not different notions of truth. Their conditional soundness arguments all reduce completion to ordinary dependent substitution or checked constructor application in a fixed Lean environment (MS §11, MPL §11, SP §7).

- **Statement freezing versus dependent elaboration.** A slogan requiring every metavariable to be fixed globally before any proof work is too rigid for dependent constructions. MS explicitly qualifies it, and Spine permits bidirectional elaboration within a step (§10.1, 699). A common rule should be: freeze the header's mathematical meaning; preserve each node's declared contextual dependencies; prohibit silent reinterpretation on search success; finalize and display any statement-resolving choices. The granularity of that boundary remains to be implemented.
- **Replay format.** MS's proof capsule and Spine's frozen package emphasize terms or reconstruction certificates; MPL also permits deterministic generated proof code. Spine explicitly allows this as an initial format while acknowledging re-elaboration. The unified report should state levels of replay evidence: deterministic search-free source replay, retained native terms, and independently checkable export are related but not identical promises.
- **Dependency restrictions versus explanations.** All recognize that `using only` can enforce a conservative permitted-dependency policy, while mere syntactic occurrence cannot prove semantic necessity or pedagogy. Spine's unused-node rule ensures truth of every assertion; it does not ensure that every asserted reason explains the result. An optimizer can preserve authored checkpoints and method plans, but stronger claims about explanatory faithfulness need human evaluation.
- **Automatic context closure versus predictability.** Propagating bounds and proposition-valued instances is useful. Unrestricted fact closure, rewriting, or global retrieval can explode search, change explanations, and hide structure choices. Versioned profiles and bounded search are a common response, but the appropriate default budget and profile vocabulary have not been tested.
- **Concision versus burden of reviewing semantic choices.** Rich expanded headers can contain exactly the casts, instances, and notation details the language seeks to hide. The research problem is selective disclosure of material changes, not simply displaying everything. MPL's “semantic choices” panel and Spine's effect taxonomy offer a starting point, not measured UX success.
- **Language versus library investment.** The reports themselves provide strong reasons that much of the gain may be reusable library interfaces. The unified report should recommend a shared IR and method API, with optional surfaces, rather than spending the next iteration merging three grammars or choosing a new language name before measuring value.

## Reviewer additions and discriminating next-iteration experiments

These are this reviewer's synthesis recommendations, not reported results.

1. **Same-backend factorial experiment.** Hold formal theorem, helper library, automation budget, and model access fixed. Compare ordinary Lean, Lean plus methods and structured diagnostics, and the new authored-step layer. Add a display-only condition if feasible. On matched held-out tasks, record author edits, time to success, adapter count, diagnostic success, certificate size, replay memory and latency. This separates gains due to mathematics, automation, diagnostics, and syntax. Stop claiming a language benefit if only the helper-library condition wins.
2. **One common dependency problem, three surfaces.** Implement a tiny contextual-obligation IR for `have/fact`, `suffices`, `calc`, and `choose`; expose it via ordinary Lean syntax and a thin declarative surface. Test witness-dependent obligations, the same witness shared by two goals, and an unused false assertion. This tests the common architecture before domain conveniences can mask scope mistakes.
3. **Rejection-pair corpus before broad showcases.** Pair each valid example with the smallest invalid local mutation: pointwise/local derivative equality; natural-subtraction interior/endpoint; coefficient support; nonzero/unit; formal/analytic root. Have reviewers classify the failure as false local claim, unsupported method, stronger theorem, scope error, or inconclusive search. Measure whether the tool diagnoses the right category and source node, not just whether export fails.
4. **Two different-domain methods, held-out transfers.** A small sum-congruence/guard-propagation method and a locality/derivative-congruence method exercise binder scopes in unrelated mathematics. Develop each on one report example and evaluate on unrelated statements. Then add the shifted-EGF method as the next genuinely specialized pack. Include constructor rebuilding as a bounded Leant comparison lane rather than making the whole prototype depend on external synthesis.
5. **Preserve generality tests.** In the Abel pilot use a general rational algebra rather than assuming a field, include a trivial algebra instantiation, and keep arbitrary `T`. In the contraction pilot include `q=0` and negative `q`. In the derivative pilot retain range-local assumptions. A method whose convenience depends on strengthening hypotheses fails the same-theorem condition even if the resulting script is shorter.
6. **Replay and repair perturbations.** Disable synthesis after freezing. Rename bound variables, alter comments, reorder irrelevant declarations, change provider ranking, and add an irrelevant theorem. Then change an actually used definition, structural instance, or branch hypothesis. Record false invalidations and missed invalidations separately. A safe initial implementation may over-invalidate; do not confuse that with proof failure or claim fine-grained stability until measured.
7. **Method-boundary ablation.** Compare one broad “analysis” method with the composition locality → derivative congruence → chain rule. On broken and unfamiliar examples, determine whether smaller contracts improve diagnosis and reuse enough to offset more authored checkpoints. This directly tests the claimed mathematical-step granularity rather than assuming it is self-evident.
8. **Reason-versus-result experiment.** Give the system a proof outline with a true but unused checkpoint, a false unused checkpoint, a cited method that was bypassed, and an alternative direct proof. Require a certificate for all asserted claims; show exact dependence; have readers assess explanatory relevance. This separates enforceable document correctness from the harder human notion of a faithful explanation.

Suggested questions for the next discussion:

- What is the smallest user task on which a shared obligation ledger demonstrably improves ordinary Lean supplied with the same method lemmas?
- Which changes count as statement-resolving effects, and how can the interface expose them without asking the author to inspect every inferred argument?
- Which proof steps should authors be able to protect as explanatory checkpoints, and what exact restriction does such protection impose on fallback search?
- Is explicit generated Lean adequate for the first frozen artifact, and which acceptance guarantees remain deferred until an independent evidence export exists?
- Should the initial domain choice optimize ease of implementation (guarded algebra), broad reuse (bounded sums/locality), or the largest observed adapter burden (formal coefficients)? What measurement will resolve that priority?
- When should a successful generated derivation become an ordinary reusable lemma, and who reviews its generality and applicability conditions?
- What upper bounds on tail latency, generated proof size, and manual method configuration would make the interface unacceptable even if source tokens fall?
- Can method authors supply a standard package of theorem contract, positive examples, rejected examples, explanation schema, and domain-generalization tests?

## Evidence status and source provenance

MS's explicit limitations: lines 104–112, 802–807, 1158, README “Scope”; source manifest pins ProveIt `24ce8bd743eaab64a91ce90725ea00f498d319d2` and Leant `c36adf114035fb2fba6c276b63944cc613b31668`.

MPL's explicit limitations: lines 77, 94–102, 740, 980, 1131–1144, README “Scope and status”; source manifest pins the same ProveIt revision, later Leant README/BehavioralSelection `3a40904be8a410d832d9ab6900b3d3e7b425eccb`, and earlier detailed internals `c36adf114035fb2fba6c276b63944cc613b31668`.

Spine's explicit limitations: lines 91, 117–120, 607–609, 987, 1096–1131, README “Scope”; it pins the same ProveIt revision and Leant `3a40904be8a410d832d9ab6900b3d3e7b425eccb`. Its exact inspected repository line ranges are at 1111–1116 and 1124.

Their existing PDFs and reported document validation are evidence of presentation artifacts, not evidence of an implemented language, kernel replay of the new notation, compiler verification, or measured improvement. The mathematical reconstructions and conditional soundness arguments are expository. The parent synthesis should preserve those boundaries and attribute unverified repository observations to the reports unless independently spot-checked.
