# Analytic review: Contour, Mosaic, and Reason

This memo reviews the complete TeX sources and the relevant supplied supplements. Locators below refer to the source files as supplied in `docs/ideas`; section numbers are the printed report sections, and line ranges are one-based TeX source lines. No source report, ProveIt file, or Leant file was modified. No Lean build was run. These notes analyze the reports; they do not independently establish every claim the reports make about external projects.

## Source key and status

| Key | Source | What actually exists |
|---|---|---|
| C | `docs/ideas/contour-proof-language/contour.tex` | 38-page design study, illustrative EBNF (`grammar.ebnf`), pinned source manifest, paper proof of a dependent certificate-assembly theorem. No implemented compiler, Lean-compiled translation, or benchmark. Explicit at lines 88–99, 748–752, 1278; README confirms. |
| M | `docs/ideas/mosaic_proof_language/mosaic.tex` | 32-page design study, source manifest and PDF build helper. Conditional paper soundness argument; no implementation, Lean compilation, benchmark, or user study. Explicit at lines 82–94, 644–659, 812–815, 865–866. |
| R | `docs/ideas/reason_proof_language/reason.tex` | 32-page design study plus a Python simply typed lambda calculus checker with products, sequential claim assembly, replay, and bounded selection from a supplied candidate stream. No Reason parser, dependent checker, views, Lean extension, or implemented mathematical examples. Explicit at lines 87–89, 961–971. |

C and M pin ProveIt `24ce8bd743eaab64a91ce90725ea00f498d319d2` and Leant `c36adf114035fb2fba6c276b63944cc613b31668` (C Appendix C, `app:sources`, 1216–1278; M Appendix A, `app:sources`, 839–866). R honestly records that no immutable revision was established (2.1, 128–132; Appendix C, 1084–1127). Source pinning is stronger provenance, not stronger proof-language implementation evidence.

## Exact crosswalk for the six requested common features

| Feature | Contour | Mosaic | Reason |
|---|---|---|---|
| Lean host, existing kernel/library retained | §1, 110–115; §14.1, 1012–1018 | §1.2, 118–125; §11.1 (`sec:implementation`), 661–668 | §1, 98–102; §16.1 (`sec:implementation`), 880–884 |
| Assertions/claims/checkpoints organize the argument | §1.1, 117–121; §4.1 (`sec:language`), 261–284 | §§4.1–4.2 (`sec:layers`), 199–209; §5.1, 225–244; §1.2, 121–123 explicitly checks every checkpoint | §3.2 (`sec:language`), 183–192; §10.2, 629–635 |
| Typed scoped obligations and method contracts | §§9.3–9.4 (`sec:core`), 677–711; §11.1 (`sec:methods`), 839–845 | §9.1 (`sec:synthesis`, `eq:obligation`), 535–543; §9.6, 594–599; Appendix B, 894–906 | §3.4 (`sec:contracts`), 200–218; §10.1, 605–615; §§11.2–11.3, 696–708 |
| Formal statement/object fidelity before proof search | §9.1, 653–661; §9.2, 665–675 | §5.3, 259–270; §10.1, 605–616; §10.4, 654–657 | §10.1, 605–615; §11.1 (`sec:ambiguity`), 688–694 |
| Frozen evidence, locked replay, discovery separated from verification | §§13.2–13.4 (`sec:trust`), 976–1007 | §9.5, 587–592; §11.5, 713–718 | §13.3 (`sec:replay`), 795–810; §13.4, 812–816 |
| Fair Lean baseline and full/amortized adapter costs | §2.5, 230–234; §15.1 (`sec:evaluation`), 1068–1074 | §2.3, 145–148; §§13.2–13.3 (`sec:evaluation`), 790–806 | §4.4, 255–259; §6.2, 369–371; §17.1 (`sec:evaluation`), 919–925 |

These three reports explicitly support all six propositions. This is textual convergence among proposals, not measured validation, and does not make three statistically independent experiments. They share the motivating task, Lean/Leant architecture, corpus, and prior-art tradition.

## Strongest contributions worth preserving

### Contour

1. **A typed mathematical move owns its side conditions.** Its reindexing example retains the author-selected map `k=j+i` and certifies interval membership, inverse identities, multiplicity, and summand agreement (§6.2, 480–495). Its logarithm/division ledger retains positivity and branch-domain obligations (§5.3, 403–425). This is more concrete than natural-language aliases for `rw` or `simp`.
2. **Dependent obligation assembly is stated carefully.** The placeholder telescope may contain proof or witness data, later obligations may depend on earlier placeholders, and the frozen exported target must contain none (§9.5, `thm:assembly`, 713–752). This is a paper theorem conditional on well-typed, scope-correct lowering and dependent substitution, not a mechanized compiler theorem.
3. **Shared unknowns require transactional solving.** Solving `exists x, P x and Q x` cannot independently choose inconsistent witnesses. Coupled metavariables define components; failed alternatives must restore metavariable and local-instance state (§9.6, 754–758). This is a genuinely useful engineering requirement often missing from generic obligation-DAG diagrams.
4. **Foundational and mathematical dependency policies are distinct.** Author-visible theorem interfaces cannot sensibly be equated with the full transitive implementation closure (§9.3, 683–687). For source `by reindex`, its method certificate should actually be rooted in the reindexing theorem rather than an unrelated closed-form proof (§11.1, 839–845; Appendix B, 1210–1214).
5. **It preserves weak algebraic hypotheses.** Binomial inversion only needs an additive commutative group; formal-series uniqueness uses a commutative ring; a later coefficient cancellation needs a unit, not merely a nonzero natural numeral (§§6.4, 7.1, 7.3; 505–513, 520–540, 581–591). Adding a field hypothesis to make automation easier weakens the author's theorem.
6. **Explicit anti-leakage benchmark design.** Remove the target theorem and its downstream closure, including aliases, helper dependencies, simplifier channels, and old caches (§15.2, 1076–1082). Three-way comparisons also hold the mathematical API constant and measure first-use/amortized costs (§15.1, 1070–1074).
7. **Replay has a precise limited stability claim.** Preserve the complete kernel-relevant dependency closure and rules, and the same certificate checks; this does not imply that fresh search is stable when the library grows (§13.4, 990–1007). Normal source export may rerun tactics and therefore is weaker than retained elaborated evidence (§13.2, 976–982).

### Mosaic

1. **Every authored checkpoint is part of document correctness.** A final theorem proof cannot bypass a false intermediate assertion. A true unused assertion can still be checked and marked unused (§1.2, 121–123; §10.2, 619–624; §12.2, 741–746). This distinguishes verification of a document from verification of its final theorem.
2. **Premise annotations have different formal strengths.** `using p,r` prioritizes facts; `from only p,r` restricts local premises to a dependency-closed telescope; `library only` separately restricts global search (§5.2, 246–257). Proving sufficiency does not certify indispensability or the author's mental process.
3. **Two explanation profiles are explicitly permitted.** In the checkpoint profile all intermediate assertions check but the final proof need not follow the advertised method. In the method-constrained profile a command must instantiate its transformation interface (§9.6, 594–599). The latter can reject a valid alternative proof; this is an exposed tradeoff, not a logical defect.
4. **The analysis example exposes uniform induction and integral orientation.** The Fabius bound needs an induction hypothesis uniform in `x` to use it at `2*t`; the `integrate` ledger includes integrability, interval orientation, pointwise/AE comparison mode, domain constraints, and nonzero coefficient denominators (§6, `sec:flatness`, especially 315–338 and 369–394). It proposes a general analytic interface separately from the repository adapter, preventing unproved assumptions from being disguised as library facts.
5. **The symmetry contract transports the whole problem.** Coverage plus transport suffices; a group action is optional infrastructure (§7.2, 424–443). A symmetry of one subexpression is inadequate when other hypotheses break symmetry.
6. **The floor-square-root case cleanly separates proof strategy and encoding.** Double counting is explicitly a proposed alternative to the repository's successor-step proof (§8.1, 453–463). The finite representation itself is an obligation (§8.3, 498–514); transport back from rationals additionally needs exact division, subtraction bounds, and embedding injectivity (§8.4, 516–531).
7. **It distinguishes callback acceptance from proof evidence.** Leant's opaque `Verified` wrapper records a supplied callback's acceptance; the name does not make it a kernel certificate (§2.5, 162–167; §11.2, 670–675). The same warning applies to Mosaic's own proposed `SerializedCheckedDeclaration` field (§11.3, 677–702).

### Reason

1. **It offers new mathematical organization, not merely syntax.** The folded function factors through `abs`, making evenness a consequence of an explicit invariant (§5, `prop:fold`, 261–305). The factorial example preserves both a short existing induction and an alternative parity partition, without claiming the new route must be cheaper (§6, 307–371).
2. **Finite partition is represented by an equivalence.** The affine-difference formula uses a powerset decomposition `P([n+1]) ≃ P([n]) ⊔ P([n])`, carrying domain, inverse, aggregation, and cardinality/sign laws (§7.2, 413–421). `generalizing z` remains visible because the induction hypothesis is used at two new arguments (§7.3, 423–440).
3. **Local analytic information belongs in formal syntax.** `near z` denotes neighborhood equality, needed before differentiating an identity; point equality alone is insufficient (§8.3, 507–527). The derivative statement asserts actual derivative existence, not merely an equation involving a totalized derivative operator (§8.1, 450–458). The proof avoids division by parameters `a,b`, correctly retaining zero cases (§8.2, 468–505).
4. **Representation friction can sometimes be avoided mathematically.** Its square-root double count derives the natural-number balance `|D|+Q=s(n+1)` and division-free `6Q=s(s+1)(2s+1)` before introducing natural quotient and subtraction (§§9.1–9.3, 543–599). This is a useful alternative to Mosaic's rational-transport presentation: certified transport should not become the default response when a better invariant avoids it.
5. **Worker/session identity and durable evidence are explicitly different.** Requests carry worker generation and exact context/target identity; stale replies cannot be accepted by matching printed text; opaque process capabilities are not serializable proof certificates (§12.6, 771–775). It acknowledges Leant's existing native rewrite study as a precursor, not delivered functionality or a new invention (§2.3, 154; §15.3, 866–870; Appendix C, 1114–1119).
6. **Different kinds of failure remain distinct.** A checked negation, checked counterexample, fragment diagnostic, rejection, unsupported result, cancellation, and budget exhaustion are separate outcomes (§12.4, 746–763). Even complete propositional search failing to prove arbitrary `P` does not establish `not P`; the distinction is stronger than just “timeout is inconclusive.”
7. **The executable companion substantiates one narrow interface.** It checks each claim before adding its name and closes the resulting telescope by lambda application; final checking happens again (`toy_checker.py` 267–288). Replay compares origin and rechecks the stored term, even though certificate constructors are public (186–212). Candidate selection has distinct success/pool-end/budget states and does not even obtain an iterator at budget zero (215–257). It selects among supplied candidates; it is not a term-synthesis implementation.

## Fresh companion verification

On this review run, under Python **3.14.4**, the command below completed with exit code **0** and **32 tests passed in 0.003 seconds**:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s supplement -p 'test_*.py' -v
```

Working directory: `docs/ideas/reason_proof_language`. No test files or supplied test transcript were changed, and bytecode writing was disabled. The suite exercises the toy's tested type/scope rules, exact-origin mismatch rejection, forged-wrapper rechecking, bounded candidate consumption, and sequential claim assembly (`test_toy_checker.py` 14–177). This does **not** establish dependent scoping, Lean checking, semantic statement fidelity, mathematical method correctness, or full implementation soundness. `Query.generation` is explicitly an opaque label, not an environment digest (`toy_checker.py` 186–192), so the toy does not demonstrate durable cross-session replay. A candidate count and recursive operation fuel are also not a sandbox or a general wall-clock resource guarantee; the candidate iterator is explicitly trusted caller code (230–236).

## Adversarial cases to use in the synthesis

| Tempting human move | Concrete failure | Report anchors |
|---|---|---|
| Cancel a nonzero factor in a ring | In Z/6Z, `2*0=2*3` but `0≠3`; require unit/cancellation evidence | C §7.3, 581–591 |
| Reuse a non-strict estimate as a strict one | Lambert lower bound at zero; multiplication by `w` needs strict positivity | C §5.3, 425; §11.5, 885–891 |
| Differentiate equality at a point | `p(x)=x`, `q(x)=0` agree at zero, derivatives differ | R §8.3, 523–525 |
| Transfer smoothness through a folded normal form | Smoothness of `f` does not alone yield differentiability across `abs` at zero | R §5.3, 301–305 |
| Insert an index during sum reindexing | `T -> T∪{n}` is not injective without `n∉T` | R §7.4, 442–444; C §15.5, 1110 |
| Read natural operations as field operations | Cast `(0-1)` or `(1/2)` unconditionally | M §8.4, 516–529; R §4.2, 230–238 |
| Generalize a positive-domain proof by symmetry | `x≥0 ⇒ x=abs x` does not imply `x=abs x` for `x=-1` | M §7.3, 445–448 |
| Finish a theorem despite a false unused checkpoint | Final target may be trivial; authored document still invalid | M §12.2, 741–746 |
| Solve independent-looking existential conjuncts | They may share one witness; incompatible assignments cannot be merged | C §9.6, 754–758 |
| Treat a restricted search miss as refutation | Failure to derive arbitrary `P` is not evidence of `not P` | R §12.4, 759–763; M §9.4, 572–585 |

## Convergences, tensions, and recommendations for the unified analysis

**The convergence is stronger on architecture than on syntax.** All three choose a Lean-hosted, small declarative shell; exact mathematical expressions; an obligation/certificate boundary; proof-producing domain methods; explicit representation laws; bounded, replaceable search; and progressive disclosure. Their core command inventories differ mainly in spelling (`have`/`claim`, `show`/`conclude`). A synthesis should recommend one shared semantic interface before spending the next iteration on naming a new language.

**The central contest is not Lean versus a new foundation.** All three say that some source proofs are already good and that a new mathematical API may produce equivalent gains in idiomatic Lean (C §2.5; M §§2.3, 7.1; R §§2.2, 5.3, 6). Preserve this as a falsifiable possibility. None establishes that Lean's foundations cause the observed friction.

**Preservation of method is an explicit selectable strength.** C centers typed mathematical moves and rooted schema certificates, allowing explicit broad-search/Lean escape annotations. M names checkpoint and method-constrained profiles; R distinguishes permissive `by auto` from a constrained annotation (§11.2, 696–702). This is largely a policy spectrum, not an irreconcilable disagreement. The unified report should ask which annotation and default profile the next prototype will implement, and what its UI promises when a valid alternative proof is found.

**Replay formats remain open.** C most clearly distinguishes ordinary Lean source from retained elaborated evidence; R explicitly permits several encodings with stated contracts (C §13.2; R §13.3). “No model query” is weaker than “no theorem search,” and a deterministic tactic script may still search internally or change with a simplifier. A concrete next iteration should define named replay grades and test each grade independently, rather than use one undifferentiated “reproducible” claim.

**Choose whether to avoid or automate a representation change.** M and R independently give a floor-square-root double count, while R's additive balance keeps the proof in naturals longer. C's Pascal proof similarly prefers an additive identity before subtraction (§8, 615–621). This suggests an additional synthesis principle: a certified view is one option; preserving an algebraically better invariant may remove the need for a view altogether. Compare both costs on the same theorem rather than rewarding every inserted adapter as a feature.

**First domain scope differs materially.** C deliberately postpones broad analytic moves (§11.6, 893–899) and recommends ordered-field/finite-sum vertical slices before Leant. M proposes interval comparison and power-integral adapters as early tests (§11.1, 663–668). R chooses fold, finite-index equivalence, and exact-number transport for its first view milestone (§16.2, 894–895), with neighborhood analysis later in realistic use. A sensible unified roadmap starts with one finite or ordered-field slice and one deliberately harder dependent/local-analytic slice to avoid both universal ambition and an arithmetic-only success story.

**The target-lock rule needs a precise engineering formulation.** The three reports allow deterministic ordinary inference but prohibit choosing meaning by proof convenience. In a dependently typed host, some elaboration decisions themselves require proof obligations. The implementation should distinguish semantic choices that must be committed from proof fields that merely certify an already committed object, and allow provisional objects during drafting without presenting them as locked. This is a synthesis question, not an observed flaw in a delivered compiler.

**The paper metatheorems are assurance designs, not empirical accomplishments.** With final exact-type checking as a hypothesis, their logical conclusion follows by familiar typing/substitution principles. Their value is identifying where contexts, dependent witnesses, scopes, and acyclicity must be preserved. They do not establish that natural text was elaborated as intended, that an executable elaborator satisfies its specification, or that proof explanations are useful. Count the toy as tested software only at its actual narrow scope.

## Questions for the next iteration

1. Is the first accepted artifact a checked theorem, a document whose every checkpoint checks, or a document whose advertised methods are also certified? Which profile is the default, and how can the author loosen it visibly?
2. What exactly is frozen before reconstruction in the presence of dependent object construction, typeclass selection, and proof-bearing refinements? What counts as a semantic change rather than a new proof of the same object?
3. Can one small shared obligation protocol serve ordinary Lean tactics, a domain-schema library, and Leant without reducing exact contexts to pretty-printed strings? How will shared metavariables be owned and rolled back?
4. Which two transformations will establish generality: one accessible finite/ordered-field case and one dependent/local-analytic case? What deliberately false variants must fail with mathematical diagnostics?
5. What does `using` mean: a hint, a sufficient restricted context, or a claimed essential reason? The third cannot be equated with syntactic dependency. Should the syntax expose only the first two?
6. What is the minimum replay artifact and trust profile? Can the full vertical slice be checked with the search worker unavailable, and are intermediate claims still independently accounted for after proof-term normalization?
7. How will the benchmark charge adapters and prevent target/downstream/cache leakage? Will it publish refactored-Lean and plain-declarative baselines using exactly the same mathematical interfaces?
8. Can a prototype extract a reusable schema or a better additive invariant from existing Lean, then validate its explanation, without treating shorter source as the only objective? The paired square-root and parity examples offer concrete tests.
