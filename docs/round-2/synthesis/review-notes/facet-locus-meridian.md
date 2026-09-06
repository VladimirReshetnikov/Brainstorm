# Round-two review: Facet, Locus, Meridian

Reviewer: Codex subagent `read_loom_motive_outline`. Source checkout: Brainstorm `f333ff6cefc8b1f5c9aae79613d10ef95a7ba928`. All substantive TeX, abstracts, appendices, READMEs, source manifests, Python companions, build helpers, and supplied validation/result receipts were read. This memo owns no original report or reference-repository file. No Lean, Leant, or PDF build was run. Git use was read-only. Companion execution and source-integrity evidence are described below.

## Recommendation to the synthesis author

These three proposals share a substantive second-round shift: the retained mathematical object, its computational presentations, and the exact relation licensed by a result become part of the language interface. This is more than another spelling for claims and obligations, but it is still a design hypothesis rather than implemented infrastructure.

Use **Facet** for the clean distinction between exact presentations and observations, the lack of a required universal encoder, and the arbitrary-solution Abel example. Use **Locus** for the most developed mathematical algorithm contract: residual-to-jet transfer with a unit derivative, constructive recurrence versus Newton production, and backward precision demands. Use **Meridian** for complete solutions as predicates, preservation of partial-function domains, demand for only the certificate strength a consumer needs, and the generic symbolic Lambert derivative calculation valid on both real branches. These are emphases, not exclusive claims.

Their first implementation targets genuinely differ. Facet starts with a polynomial calculation plus a guarded expression bridge; Locus starts with a branch-selected formal-root jet; Meridian starts with domain-preserving rational simplification and complete solving. Do not erase this useful experimental choice by claiming agreement on one roadmap. I favor combining Locus's small certificate theorem with Meridian's domain/solution-set example as two independent first slices over a common result protocol. Facet supplies the representation vocabulary that should connect them. A parametric Lambert certificate should then test whether the interface generalizes beyond finite arithmetic.

## Source keys and evidence boundaries

All line numbers below are one-based source lines, not PDF pages. Section numbers were checked against source heading order; generated heading maps are retained in `../evidence/facet-locus-meridian/*-sections.json`.

| Key | Primary source | Report's evidence scope |
|---|---|---|
| F | `docs/round-2/ideas/facet/facet.tex` (2059 lines) | Both syntheses at Brainstorm `494be9d5ab41a5ae219fc6f800e6aee3c93bce39`; selected ProveIt files at `7c4e3f109405b9805b35d27ae96bf09c7ee5f3d5`; selected committed Leant at `3a40904be8a410d832d9ab6900b3d3e7b425eccb`; no new Lean implementation (§1.4, 221–228; §16.3, 1683–1696; App. E, 1939–1977). |
| L | `docs/round-2/ideas/Locus_Proof_Language_Proposal/locus.tex` (2219 lines) | Git blob identities for files retrieved from `main`; explicitly not commit identities or evidence of a consistent built installation (§1.4, 227–242; App. C, 2064–2128). |
| M | `docs/round-2/ideas/meridian/meridian.tex` (2324 lines) | Both syntheses at `494be9d5...`; ProveIt at `24ce8bd743eaab64a91ce90725ea00f498d319d2`; committed Leant at `3a40904b...`; current manuals not assumed compatible with pinned project (§2.4, 295–302; App. B, 2141–2184). |

Each explicitly uses the two syntheses rather than independently rereading all nine round-one reports. They inherit a heavily overlapping sample: all three discuss BinomialInversion and AutonomousIteratedDeriv; F adds AbelPolynomialSeries, L adds AlgebraicInverseGerm, M adds LambertWHigherDerivatives. Agreement is correlated design support, not independent validation or three separate discoveries of these examples.

The different ProveIt commit labels do not necessarily identify different source text. Their manifests agree on the BinomialInversion blob `c6b0fe63a4faf8708b71e9b93aa2ce7406464d84` and AutonomousIteratedDeriv blob `1422b87f31073fed898ff0c8a080ea0a798aef5e`. Read-only local Git corroboration found Locus's germ blob `b7bd59bf3f940f965e1936942d0ea6adfb4e03d6` at the stated comparison commit and Meridian's Lambert blob `cd42c43ed6c0bc407e23fe3afe351bdd659fe9b7` at its stated commit. Targeted source reads confirmed the germ's `IsUnit` interface and zero-constant root, and the Lambert polynomial recurrence and two branch theorems. This is static corroboration, not fresh compilation.

Leant review scope is substantially narrower than our round-one implementation audit. F reads Verification 1–225, Engine 1–165, Main 4700–4995; L reads the Verification module, Engine 1–180, synth-internals 1–190; M reads Verification 1–190, Engine 1–160, Main 4600–4760 and 4820–5110. Engine module comments and exports support architectural claims, not a complete inspection of candidate generation. All preserve the distinction between committed sources and the uncommitted behavioral extension described by round one. A read-only `git show` of committed Verification confirmed its explicit callback-only `Verified` documentation. L's suggestion discussion is attributed to the earlier synthesis, while F and M directly inspect portions of committed Main; do not cite all three as fresh suggestion-path audits.

## Eight-feature crosswalk

“Explicit” means the report endorses the whole feature as a proposed contract. It does not mean an implementation passed tests. Multiple ranges are supplied where the feature is a conjunction whose parts occur separately.

| Feature | Facet | Locus | Meridian |
|---|---|---|---|
| **R — Result states exact relation/guarantee** | Explicit: §§4.2–4.3, 415–470; exact result versus observation, selected versus all roots. | Explicit: §§4.1, 4.4, 448–474 and 528–558; output family/specification and relation table. | Explicit: §§4.1–4.3, 444–544; properties form a partial order, complete solutions and canonicality separate. |
| **O — Fixed objects with certified representations/observations** | Explicit: §§4.1–4.2, 378–423; §5.6, 599–611. | Explicit: §§3.1, 5.1, 351–373 and 598–620; §5.4, 678–688. | Explicit: §§3.1, 7.1, 308–326 and 904–923; §11.5, 1586–1593. |
| **G — Scoped guards/composition without silent strengthening** | Explicit: §§5.2–5.4, 510–578. | Explicit: §§4.5, 5.3, 560–577 and 644–676; branch-local reuse §3.3, 395–411. | Explicit: §§6.2–6.4, 739–833; dependent route qualifiers §7.2, 926–952. |
| **V — Algorithm/checker versus actual execution and reification** | Explicit: §§6.1–6.3, 614–687. | Explicit: §§4.1–4.3, 463–526, and §4.6, 579–593. | Explicit: §§5.1–5.3, 568–662. |
| **D — Ordinary theorem/definition packages; separate operational policy** | Explicit: §5.1, 489–508, and §§12.1–12.3, 1319–1367. | Explicit: §5.1, 598–620; §12.7, 1670–1682; App. A.3, 1968–1988. | Explicit: §3.4, 398–417; §§7.1, 7.5, 904–923 and 1015–1034. |
| **L — Exact-target providers, exact displayed-edit replay, honest negatives** | Explicit: §§11.3–11.6, 1212–1316; non-derivability example 1257–1282. | Explicit: §§11.3–11.6, 1445–1537; historical suggestion observation attributed, not newly reproduced. | Explicit: §§11.2–11.5, 1492–1600. |
| **P — Retained evidence and publication/replay boundary** | Explicit: §§13.2–13.5, 1389–1463. | Explicit: §§12.2–12.6, 1572–1668. | Explicit: §§12.2–12.4, 1649–1727. |
| **E — Fair Lean baselines, negative neighbors, measurable stopping criteria** | Explicit: §14.3, 1501–1538; §§15.1–15.4, 1563–1649; App. D, 1885–1934. | Explicit: §13.3, 1741–1772; §§14.1–14.4, 1777–1853; App. B, 1990–2059. | Explicit: §§13.1–13.4, 1748–1800; §§14.1–14.4, 1819–1942. |

## Facet: distinctive contributions and assessment

### Exact presentation need not provide an encoder

F §4.1 (392–413) defines a data type `D`, a validity predicate, and `decode : {d // Valid d} → A`; representing a particular `a` adds `decode d = a`. No total encoder `A → D` is required. This avoids pretending that every arbitrary mathematical object has an available finite description. A function can remain opaque and participate through its laws; an algorithm returns `Unsupported` if it lacks an applicable presentation. This is a particularly useful specification for integration with noncomputable mathematical APIs.

F §4.2 (415–448) treats observations as a general relation `V : D → A → Prop`. A finite jet or interval need not identify a unique entire object. The F₂ counterexample in §4.1 (384–390)—`X²−X` induces the zero evaluation function without being the zero polynomial—shows why even complete observation of a finite function space need not reflect polynomial equality. This is stronger than merely saying finite samples cannot prove equality.

F §5.6 (599–611) turns observational replacement into an operational design: give consumers capability-bearing handles with explicit precision rather than rewrite arbitrary occurrences of the underlying object. A derivative consumer requests a particular jet; a full-function theorem requests the actual function. This supplies a tractable first implementation of round one's observation-relative idea. The remaining difficulty is enforcing all dependent consumers' declared interfaces and tracking changes in their requirements, not inventing one global notion of observational equivalence.

### Contract wrappers and conditional data preserve dependency order

F §5.1 (489–508) adopts theorem types as contracts but adds project-owned typed wrappers with named fields, rather than treating upstream binder names or positions as permanent semantic identities. Logical interface, algorithm, routine profile, and renderer get distinct versions. This is a sensible response to annotation fragility; it costs real maintenance and the report explicitly charges it.

F §5.2 (510–529) carefully distinguishes `Π h, Σ b, R` from `Σ b, Π h, R`: a computed value itself may depend on a guard or a witness introduced by that guard. This is the clearest of the three accounts of why “result plus a bag of pending conditions” is not a general dependent interface. F §5.3 (536–554) retains intermediate objects, instantiated bridges, ordered guards, and the final relation; relational composition is not automatically equality.

Its concrete cast route (§5.4, 556–578) uses `b ≤ a`, `d ∣ (a−b)`, and `d ≠ 0` to transport natural subtraction/exact division to rational arithmetic, normalize, and reflect a final equality back through an injective cast. At `(a,b)=(2,3)` subtraction fails; at `(3,0,2)` division exactness fails. A floor route is a different contract. These are sufficient guards for this chosen route, not a claim to characterize weakest applicability conditions of every library theorem.

### Worked mathematics worth retaining

- **Binomial inversion** (§7.1, 745–784): the integer kernel sum is δₙⱼ, with empty interval and diagonal cases handled, then integer scalar action transports the result to any additive commutative group. No multiplication or division of group elements occurs. The author chooses `k=j+i`; coverage is a required proof. Omitting the endpoint invalidates the advertised reindexing even if another library theorem proves the conclusion (§7.2, 807–817). Finite evaluation is not the general binomial identity (§7.3, 819–830).
- **Polynomial autonomous derivatives** (§8.1, 833–867): for an actual derivative equation `HasDerivAt W (p(W x)) x` on open `U`, set `P₀=X`, `Pₙ₊₁=p Pₙ′`; the generic analytic theorem gives `W⁽ⁿ⁾(x)=Pₙ(W(x))`. For `p=1+X²`, `P₄=16X+40X³+24X⁵` (§8.2, 869–907). This isolates verified finite polynomial production from the inductive analytic theorem. It preserves the source's more general range-local interface (§8.3, 909–925). Point equality `0=t` at zero remains an invalid derivative-transfer input; extra global smoothness would not repair it.
- **Abel series specified by a law** (§9, 936–1060): for a commutative Q-algebra and any `T=t exp_formal(-aT)`, derive `[tᵐ]exp_formal(xT)=(1/m!)x(x−ma)^(m−1)` for `m≥1`, constant coefficient one. Lagrange–Bürmann is the mathematical choice. `m` is canceled using the image of its rational inverse, not a field structure on the target or an injective algebra map (§9.2, 966–997). This admits zero divisors and does not require a nontrivial target ring. A finite recursive algorithm computes observations of the *arbitrary specified T* (§9.4, 1031–1052); it need not replace T by a canonical constructor. A unique-solution theorem can later justify that identification separately. The shifted coefficient rule splits `s≤n` from `n<s` (§9.3, 1016–1028); truncated natural subtraction cannot erase the second branch.
- **Branch and approximation examples** (§10, 1062–1163): distinguish equality in Q(X) from total real-function equality; denest `sqrt(5−2sqrt 6)=sqrt 3−sqrt 2` using a sign proof as well as squaring; identify a root of `x³−x−1` in `(1,3/2)` and convert the exact residual at `53/40` into the bound `0<53/40−α≤77/128000`. The latter combines exact arithmetic with a derivative lower bound and the mean value theorem; the script checks the arithmetic, not that analytic theorem.

### Negative evidence and execution

F §11.4 (1257–1282) is unusually precise: complete intuitionistic non-derivability of excluded middle cannot become a proof of its negation, because intuitionistic logic proves its double negation. A two-world Kripke countermodel illustrates non-derivability. The counterexample does not require lossy opaque abstraction. A complete derivability procedure and a mathematical decision procedure answer different questions. Keep `ReportedNonDerivability` separate from `CheckedNegation`; an abstraction log and a dependency record also have different meanings (§11.3, 1234–1255).

F §§6.1–6.3 (614–687) distinguish a verified producer, a verified certificate checker, and an unverified candidate later proved correct; all must establish reification and the link between concrete execution output and the logical computation. A genuine theorem `Spec(d,F(d))` does not certify forged native bytes. This is shared with L and M, not unique to F.

### First slice and evaluation

F §14.3 (1507–1529) starts with instrumented Lean, then one polynomial calculation and guarded real-expression bridge; finite reindexing/local calculus follow, then a series template, Leant, and root/numeric extensions. §14.5 (1554–1561) explicitly rejects another large toy checker in a different logic as the decisive next milestone.

F §15.1 (1565–1589) gives the finest nested baseline decomposition: original Lean L₀; shared lemmas/interfaces L₁; ledger/rendering L₂; definition and CAS services L₃; authored step language L₄. It explicitly acknowledges that a fully crossed ablation may be meaningless when an algorithm depends on its presentation package. This is a valuable correction to vague calls to “hold everything else fixed.” §15.4 (1640–1649) permits library-only, view-only, selective-wrapper, or selectively dispatched Leant outcomes.

## Locus: distinctive contributions and assessment

### Persistent workspace as a measured sharing hypothesis

L §3.1 (351–373) defines a workspace `(E,Γ,O,F,V,P)` but states only `(E,Γ)` determines typing. Registries organize use rather than create a second logic. §3.3 (395–411) proposes bounded guard closure and exact scoped reuse. A join of two case-local fact stores requires a case-elimination proof; taking their union is unsound. §3.5 (430–443) gives a concrete benefit hypothesis: share a polynomial representation and its bridge across derivative, residual, and root computations rather than reify repeatedly.

This is a genuinely testable hypothesis, but not yet a gain over an equally equipped Lean worker. The ablation must distinguish representation sharing from interface syntax. Whole-workspace cache keys are the conservative initial choice (§12.6, 1651–1668), followed later by smaller dependency-aware keys. This may overinvalidate, but offers a reasonable path to a correct first implementation. Exploration records should be collectible separately from accepted evidence (§13.1, 1687–1706), avoiding permanent retention of every failed search state.

### The formal-root residual contract is the strongest first experiment

L §8.1 (916–936) uses ProveIt's `dyadicGermTwo`, the unique zero-constant root of `F(z,Q)=z+4z²−4Q/9`. The finite observation convention is **modulo Qᴺ**, i.e. degrees `<N` (§8.2, 938–949). This differs by one from Facet's “through degree N” notation; the synthesis should standardize or always state the convention.

The concrete residual theorem (§8.3, 951–976) says: if Δ is the specified exact zero-constant root, J also has constant zero, and `F(J)∈(Qᴺ)`, then `J−Δ∈(Qᴺ)`. The factorization

`F(J)−F(Δ)=(J−Δ)(1+4(J+Δ))`

works because the second factor has unit constant coefficient one. Thus the finite checker needs only the chosen branch and low residual coefficients; existence of Δ is a separate input theorem. This is useful mathematical compression of the acceptance boundary, not merely a protocol sketch.

The general theorem (§8.4, 983–1012) takes `F∈R[[Q]][Y]`, an exact root Δ with constant d, another J with the same constant, and a unit constant-term derivative `F̄′(d)`. A divided-difference polynomial U satisfies `F(J)−F(Δ)=(J−Δ)U`, with `U(0)=F̄′(d)`. Hence U is a unit and residual congruence reflects to root congruence. **An arbitrary commutative ring, including zero divisors, suffices.** Nonzero is not enough for this contract. Unit derivative is sufficient, not claimed necessary for every possible root-identification method.

The producer recurrence (§8.5, 1014–1045) is `a₁=4/9`, `aₙ=−4 Σᵢ₌₁ⁿ⁻¹ aᵢaₙ₋ᵢ`. It yields

`Δ ≡₆ (4/9)Q − (64/81)Q² + (2048/729)Q³ − (81920/6561)Q⁴ + (3670016/59049)Q⁵`.

The paper explains how the same coefficient recursion defines an infinite constructive series and how uniqueness identifies it with the preexisting noncomputable root. Its Catalan coefficient formula (§8.6, 1047–1080) is an independent mathematical derivation, not required to accept each finite jet. The formal binomial square root proof uses characteristic zero over Q; do not silently carry that particular derivation to the general-ring theorem.

Newton doubling (§8.7, 1082–1105) chooses `h=−F(J)/F′(J)` and uses `F(J+h)=F(J)+F′(J)h+h²H` to double residual order. No division by two is needed. Truncated inverse/products still need their own correctness proofs. The paper recommends retaining the residual checker even for a verified producer, allowing producer replacement under a stable meaning contract. **The supplied Python program implements the triangular recurrence and residual check, not Newton iteration or the general-ring theorem.**

### Precision as an exact effect

L §8.8 (1107–1138) provides usable transfer laws: differentiation consumes one additional coefficient, unit inversion preserves a given congruence order, and valuation bounds sharpen multiplication. In particular, if errors are in Qᴺ and Qᴹ and the other factors have valuations b and a, output error lies in `Q^min(N+b,M+a)`. This can guide backward precision demands. It also introduces a compiler challenge: consumer precision changes require correctly invalidating old dependencies, and a valuation lower bound must remain attached to every saving. Zero-constant substitution is a sufficient initial interface, with nilpotent alternatives left explicit.

The wrong root `−1/4−Δ` has a vanishing residual but fails the required constant coefficient (§8.9, 1140–1145). This negative neighbor is stronger than corrupting an arbitrary coefficient: every equation check can succeed while object identity fails. The real formula `(sqrt(1+64q/9)−1)/8` needs a separate analytic realization near zero and a separate numerical remainder theorem (1147–1161).

### Additional mathematics and interface details

- Binomial inversion and the source's already-short final wrapper remain negative controls (§6, 747–831); changing a finite sum to an infinite one requires a different contract even for a bijection.
- Local autonomous differentiation preserves range-local hypotheses (§7, 836–910); arbitrary Gₙ need no symbolic CAS. The CAS becomes useful only for supported concrete polynomial/rational families.
- Denesting uses `sqrt(5+2sqrt 6)=sqrt 2+sqrt 3` (§9.1–9.2, 1166–1226). The companion adds exact rational radical bounds and a sufficient sign test, unlike Facet's algebra-only radical checks. A defining polynomial need not be minimal for root isolation; minimality needs additional evidence. Complex roots cannot inherit real positivity, and principal square-root multiplication fails at the negative-real example.
- Root brackets for `x³−x−1` use a rational endpoint checker, independent of the bisection history (§9.3, 1228–1265). Monotonicity is proved by a polynomial difference on `[1,∞)`, so the checker need not require its upper endpoint to be at most two. Width `2^-48` gives midpoint error `2^-49`.
- Conditional equality saturation is explicitly optional (§10.4, 1363–1381): an equality edge proved under `x≠1` cannot merge unconditional global classes. Prefer deterministic normalization and a few explicit routes first.
- Optimizer ordering (§10.5, 1383–1393) first preserves meaning/objects, then avoids substantive obligations, then considers check cost and display. This is a useful proposed policy, not a claim of global optimality; there may be legitimate user tradeoffs between a simpler guard and a much more expensive check.
- The negative interface distinguishes `Γ ⊢ ¬T` from negation of the closed telescope `¬(ΠΓ,T)` (§11.4, 1484–1495). This subtle point deserves inclusion in a common protocol: a “negate goal” command must select which proposition it actually means.
- L §12.4 (1613–1628) grants automatic representation replacement under an actual uniqueness theorem, while retaining construction costs and explanatory interests. This is compatible with Facet's fixed-object presentation changes and Meridian's conservative data policy, not an unconditional license to switch witnesses of a weak specification.

### First slice and evaluation

L §13.3 (1741–1772) starts with the actual dyadic residual-to-jet lemma and exact rational polynomial arithmetic in Lean, accepting external J through a small `compute` node. Domain cancellation and finite/local methods follow; then constructive coefficient production, backward precision, comparison with Newton, a Leant adapter, and frontend study. This is narrower mathematically than a general CAS, yet exercises branch identity, precision, and an arbitrary-order theorem.

L §14 (1777–1853) separates original Lean, refactored Lean with identical methods/CAS, and the workspace frontend; it then explicitly ablates representation sharing, guard reuse, explanations, and notation. This is less finely nested than Facet's five arms but compatible. Quantitative thresholds follow a pilot, not invented savings percentages. Its 28 integration regressions are proposed; the 24 Python methods are a different suite (§15.1, 1858–1880; App. B, 1990–2059).

## Meridian: distinctive contributions and assessment

### Complete solutions and certificate strength

M §4.1 (444–489) treats result properties as a partial order under proved implications, not a universal trust ladder. Factor multiplication does not imply irreducibility; root membership does not imply completeness; complete solution sets do not imply a finite enumeration or canonical order. M §4.2 (497–529) makes solution predicates primary: `ax=0` over R gives all R when a=0 and {0} otherwise, so a finite-list-only interface cannot express every complete answer. Sets deliberately forget multiplicity; factor multisets need a different contract.

M §4.3 (532–544) distinguishes determinism from canonicality. Variable and term orders, coefficient normalization, algebraic extension, and equality notion are parameters of a canonicality claim. Stronger guarantees can cost more and need not help a downstream proof. Its later demand-directed certification proposal (§16, 2009–2016) is therefore more than a UI preference: ask for the weakest adequate proved property, and attach stronger properties to the same retained object when needed.

### Partial-function equivalence and complete solving

M §6.2 (739–772) models a partial expression as a domain predicate D and `v : Πx,D x→A`. Exact partial equivalence includes **domain equivalence and equality of values**. Equality on a selected set is weaker. This distinction can be lost even when every local algebraic equality is correct.

Guarded equivalences compose by conjunction at the same ambient argument (§6.3, 775–792); under substitution σ the guard becomes `G∘σ` and the domain becomes `D∘σ` (794–810). Dependent or transformed arguments require actual instantiated guards rather than string union. The simple common-denotation composition in §7.2 (926–952) is deliberately the initial fragment, not a purported universal solution for dependent views. All three reports ultimately require dependent transport; Meridian is most explicit about postponing its full generality.

For the partial quotient `(x²−1)/(x−1)`, the complete zero set is {-1}; for the totalized real expression it is {-1,1} (§6.6, 860–884). This is an excellent statement-fidelity test because the difference is in the requested object, not an unsound ring tactic. Clearing denominators produces candidates that must be filtered through the original domain. Exact domain-preserving normalization returns `(x≠1, x+1)`; extending to every real is a different object (§6.2).

M §6.4 (813–833) states a critical qualification for diagnostics: generated guards may be sufficient without being weakest. Failure of a chosen guard does not prove the target false. §6.5 (836–856) requires branch coverage but not necessarily disjointness. Overlap is harmless for branches each certified to represent the same original object; more general relations may require additional compatibility. A symbolic case object is not automatically an executable function without decidable tests or a selection algorithm.

### Injectivity does not reflect arbitrary properties

M §7.4 (987–1012) supplies a valuable counterexample beyond generic cast warnings: Z→Q is injective, but `X∈(2X)` in Q[X] and not in Z[X]. The witness `1/2` lives in the enlarged coefficient domain. Thus injectivity reflects equality of mapped elements, not arbitrary existential properties over enlarged witnesses. This should appear prominently in the synthesis's transport section; it prevents an overly broad “injective view” capability. The ordinary nonunit counterexample in Z/6 accompanies it.

M §7.3 (955–984) compares a natural-subtraction route through Z,Q,R requiring `b≤a` with an alternative real `max(a−b,0)` route. Both preserve the original natural value but expose different expressions/guards. Adding the second route must not rewrite old meaning by search success. This is a concrete answer to round one's competing-view question rather than merely a demand for future coherence.

### The generic Lambert calculation is the hardest language test

M §8 (1037–1245) preserves the source decomposition rather than changing the proof. It introduces an executable integer polynomial family

`P₀=1; Pₙ₊₁=(1+w)Pₙ′−((n+1)w+3n+2)Pₙ`,

then maps coefficients into the semantic real-polynomial family. The first values are `1`, `−w−2`, `2w²+8w+9`, `−6w³−36w²−79w−64` (§8.2, 1054–1089). It also proves degree n and leading coefficient `(-1)^n n!` over Z; those statements must not be transported unchanged to arbitrary positive characteristic.

Set `Hₙ(w)=exp(-(n+1)w) Pₙ(w)/(1+w)^(2n+1)` and `φ(w)=exp(-w)/(1+w)`. The generic quotient/product-rule schema gives

`Hₙ′(w)=exp(-(n+1)w) Pₙ₊₁(w)/(1+w)^(2n+2)` and `Hₙ′φ=Hₙ₊₁`.

Only `w≠−1` is needed, not `w>−1` (§8.3, 1092–1126). The latter would silently exclude the lower real branch. The author-selected recurrence is used symbolically for arbitrary n and polynomial P; checking finitely many output coefficient arrays does not implement that derivative compiler.

The generic autonomous theorem then proves `W⁽ⁿ⁺¹⁾=Hₙ∘W` on open U under actual derivative assertions and `W(x)≠−1` (§8.4, 1129–1165). The principal branch has domain `(-e^-1,∞)` and the lower branch `(-e^-1,0)`; the same algebra feeds two distinct analytic instantiations (§8.5, 1168–1180). Neither endpoint is added by simplification. The obligation/provider table (§8.6, 1210–1228) cleanly separates polynomial denotation, generic differential rule, pole guard, numerator/exponential cleanup, locality, and branch instantiation.

The three nearby failures are meaningful: change `3n+2` to `3n+1`; remove the non-pole premise; replace neighborhood equality by point equality (§8.7, 1240–1245). The symbolic recurrence mutation is preferable to testing only obvious arithmetic corruptions. This case should be the later gate demonstrating that the design handles parameterized mathematical algorithms rather than only concrete calculations.

### Other useful details and first slice

- The Catalan equation `C=1+XC²` over Z has a fully specified recursive infinite solution, while its six-coefficient polynomial has residual coefficient −132 in degree six (§10.1, 1341–1392). This provides a straightforward finite/full boundary contrast to Locus's more elaborate branch-selected root.
- Denesting, `sqrt(x²)=|x|`, exact rational bounds for sqrt 2, antiderivatives on disconnected domains, antidifference endpoints, recurrence initial conditions, and the quantifier dependence of asymptotic bounds extend the result vocabulary (§10.2–10.4, 1395–1464). None is delivered as a general solver.
- M §5.4 (665–682) identifies prior verified polynomial work and says contemporary `polyrith` documentation marks the external service defunct. Treat this as a lead to verify against an actual toolchain/backend before reuse, not a direct execution finding of this memo. Cross-foundation verified code is not a drop-in Lean proof.
- Four suggestion statuses separate probe acceptance, exact displayed edit replay, requested result evidence, and document sealing (§11.4, 1543–1575). Missing status fields are protocol errors. This preserves the round-one static-review findings without treating a decrease in goals as completion.
- Three retained evidence forms distinguish mathematical record, certificate data/checker theorem, and host proof evidence (§12.3, 1675–1696). Search-free replay may perform substantial deterministic computation. Imported `.olean` filenames and hashes do not independently establish proof checking (§12.4, 1714–1727).
- First slice: partial-expression rational normalization plus complete solving; second: the generic Lambert derivative certificate; third: measured Leant adapter and exact suggestion replay; fourth: views, binomial transforms, jets (§13, 1748–1800). This gives analysis a relatively early role, but full symbolic solving is a broader initial requirement than Locus's residual checker.
- Evaluation names **contract surprise** (reader overestimates result strength) and **guard surprise** (author mispredicts valid specializations), §14.2, 1866–1871. These operationalize comprehension better than stylistic preference alone. The measures still need carefully designed tasks and explicit scoring; their names do not make them validated instruments.

## Response to the round-one questions

F has explicit answers to all ten primary-synthesis questions (App. B, 1791–1834) and all twelve secondary questions (App. C, 1836–1883). M consolidates both into sixteen decision rows (§15, 1945–2002). L answers them through the body rather than a numbered reply appendix. The following is a usable comparative map.

| Round-one issue | Shared resolution and remaining distinction |
|---|---|
| Smallest useful method / annotations | Ordinary theorem-backed wrapper plus ledger for deductions; computational theory needs denotation, algorithm/checker, and result relation. F §5.1; L §§1.3,12.7; M §3.4. Roles are not inferred from `Prop` alone. |
| Must reasons constrain proofs? | All three require the advertised method when wording names it, and offer explicit open search. L also spells out `prefer`. F 350–357; L 311–326; M 413–417. No claim of logical indispensability. |
| Automatic edits and choices | Proof-only evidence changes are easier to automate; retain accepted data and branches. F allows certified presentation changes of the same object; L develops uniqueness as a sufficient permission; M keeps arbitrary observational replacement out of the first implementation. |
| Exact suggestions and negatives | All keep origin, target, display replay, root/document completion, and mathematical negative evidence separate; L adds contextual-negation versus closed-telescope-negation. See L-feature crosswalk. |
| Competing views | Retained intermediate objects, instantiated guards, bounded discovery, pinned route, explicit choice or observation-appropriate coherence. M begins with equality in a common semantic space; F/L articulate a more general relational target from the start. |
| Definition authoring | Small proved packages/templates, not an unrestricted English parser. F prefers an arbitrary-solution series interface; L a uniquely specified formal root with constructive refinement; M partial expressions and executable polynomials. |
| Statement inspection | Deterministic notices expose resolved conventions; notices do not create proof obligations or recover intent. Dismissal tied to meaning/version; changing a resolved operation invalidates it. F 1402–1415; L 1572–1592; M 329–346,1977–1979. |
| Replay and upgrades | Old evidence remains tied to its pinned environment; upgrade is migration with renewed semantic comparison and checking. Scripts, certificates, and resolved terms have different replay costs/guarantees. |
| Adapter cost and authoring alternatives | Give ordinary Lean every helper/algorithm, measure construction and maintenance, compare source and document views, permit a library/view-only result. F five arms; L three treatments plus ablations; M four arms plus CAS ablation. |
| Ownership and competing packages | Project-owned semantic interfaces, lexical selection, separate logical and operational versions; import order must not choose mathematical meaning. F 1351–1367; L 1670–1682; M 1015–1034. |
| Explanatory fidelity | Reader must recover why hypotheses, branches, and representations matter; collapse mechanics contextually. F 365–375; L 328–340; M 190–208. M proposes explicit guarantee-overestimation measurements. |
| Discarded candidates and product stopping rule | Accepted value/specification belongs in publication, alternatives can remain optional/private exploration. A new syntax is contingent on evidence of additional authoring/reading value. |

## Companion inspection and fresh execution

Fresh execution used Python **3.14.4**, `-B`, and `PYTHONDONTWRITEBYTECODE=1`. A review harness runs scripts using absolute source paths with its working directory and every output path under `docs/round-2/synthesis/evidence/facet-locus-meridian/`. All three source directories were SHA-256 inventoried before and after execution; all original files remained unchanged. Mathematical output fields agree with the shipped receipts. Interpreter/version evidence is freshly recorded, not inferred from the old receipt. The review did not execute any build helper because those would create products in the original report directories and run prohibited PDF builds.

| Companion | Fresh outcome | What the code actually does and does not test |
|---|---|---|
| F `math_checks.py` | 1100 checks, exit 0 | 725 finite binomial kernels; 20 Z/6 inversion values; five autonomous polynomials; five initial and 325 Abel exponential coefficient checks; domain/F₂/precision counterexamples; three radical-algebra checks; five cubic residual arithmetic checks. Uses only integers/Fraction. No sign checker for the denesting identity, analytic enclosure proof, generic algorithm theorem, parser, or provider protocol. |
| L `certificate_demo.py` | 24 unittest methods, zero failures/errors, exit 0 | Jets at precisions 1–24, coefficient formula through degree 24, 702 binomial instances, wrong-branch/corrupt/precision mutations, finite radical algebra and sufficient interval sign checks, cubic brackets. Producer and checker use different mathematical procedures but share ordinary Python arithmetic helpers; this is not implementation-independent formal verification. No Newton producer, general-ring unit-derivative theorem, Lean bridge, or integration matrix execution. |
| M `check_examples.py` | 27/27 checks, exit 0 | Concrete domain-retaining rational example; first Lambert polynomials; one linear identity in symbolic n and five finite derivative-numerator instances; one mutation; Catalan residual; exact sqrt 2 bound arithmetic; coefficient-domain and natural arithmetic counterexamples. No generic derivative compiler or complete solution-set algorithm. |

Important code locators:

- F: `check` at 20–23 fails directly on a false check; polynomial multiplication/differentiation at 33–42; formal exponential recurrence at 45–53; Abel producer at 56–61; binomial and torsion checks 64–77; Abel sample checks 90–102; jet example 117–121; radical algebra 123–150; cubic arithmetic 153–161. The full program is only 175 lines and is an exposition checker, not a language prototype.
- L: `synthesize_dyadic_jet` 74–83 and `check_dyadic_jet` 91–104; checker validates positive integer precision, tuple/Fraction coefficients, normalized representation, size, branch constant, and low residual. The size restriction is a serialization/canonical-representative restriction, stronger than the paper's residual theorem which allows any polynomial J with the required congruence. It does not invalidate the mathematical theorem; it should be stated if this exact checker interface is reused. `valid_radical_bounds` 131–139, `biquad_enclosure` 142–149, `check_principal_radical` 152–158; positivity is sufficient and deliberately incomplete. `bisect_cubic` 174–182 versus `check_cubic_bracket` 185–188; the checker checks endpoint rational inequalities, relying on the paper for continuity/monotonicity. Tests 202–250 exercise positive, corrupt, precision, wrong-root and serialization cases; 259–275 exercise radical mutations; 303–312 exercise root brackets.
- M: `RestrictedRational` 58–71 stores a finite exclusion set and rejects it before denominator evaluation. It is not an implementation of the full dependent-domain model or domain equivalence checker. Simplification at 93–94 is hand-constructed for the chosen example, not a discovered rational normalizer. `lambert_next` 52–56 computes the recurrence. Checks 115–128 validate an algebraic coefficient identity and finite numerator instances, not differentiation of exponentials/quotients or all-n analytic correctness. Catalan residual 130–137 and rational bounds 139–148 are exact arithmetic.

The counts are **not comparable coverage metrics**: F counts individual finite assertions, L reports test methods containing parameterized loops, M reports named checks. The 16/28/23 proposed language-integration tests are separate from all these executed counts.

Reproduction: run `python -B docs/round-2/synthesis/evidence/facet-locus-meridian/review_runner.py`. The harness creates per-report JSON results, stdout/stderr, section maps, and `review-receipt.json`, with source hashes and before/after identity checks. It runs no Lean, Leant, PDF tool, or Git mutation.

## Contradictions, qualifications, and gaps to preserve

1. **No substantive contradiction was found in the worked algebraic/analytic derivations read here.** The polynomial recurrences, residual argument, guarded composition, and stated counterexamples are coherent under their explicit hypotheses. This is mathematical review plus finite execution, not a kernel certificate. Unimplemented theorem interfaces and claims about actual future elaboration remain unverified.
2. **Precision conventions differ.** F's J_N includes degrees ≤N (581–597, 1031–1052); L's N-jet and M's order N mean modulo Qᴺ/Xᴺ, degrees <N (L 938–949, M 1341–1354). Mixing these would create exactly the off-by-one error their tests are designed to prevent. A common protocol must encode the meaning rather than merely an integer named `precision`.
3. **Program annotations do not supply proof.** “Verified producer” in L §8.5 and “verified algorithm” throughout are specified mathematical obligations, not delivered Lean functions. L's exact checker is more substantive than F/M's checks but remains unverified Python. The general formal-root theorem and Newton doubling are paper arguments.
4. **A computational relation can be exact without being equality.** An enclosure or finite-jet relation can have exact evidence. Avoid a dichotomy in which “approximate result” suggests uncertain correctness; the approximation is in what is asserted, not necessarily its proof status.
5. **The reports do not solve route planning or universal dependent transport.** F describes contract-directed planning as open (1660–1666); L says its composition theorem does not solve route selection (674–676); M explicitly narrows the initial semantic space (944–947). Their common route records are a specification worth implementing, not evidence that composition scales.
6. **Negative outcomes have more than one failure source.** A failed sufficient guard, an incomplete solver, a certified non-derivability result, a false specification, and a serialization rejection are distinct. The final synthesis should not reduce all negative neighbors to “reject false theorem.” Several examples invalidate only a method or an overly strong result label.
7. **Uniqueness and equality do not make all operational changes invisible.** Equal semantic roots may have different computational costs or displayed constructions. L explicitly notes this (1623–1628); retain the separate notion of mathematical plan or meaningful construction provenance when adopting uniqueness-based replacement.
8. **Source-level and current-library assertions need their stated scope.** L's file blobs do not establish a consistent repository toolchain. F/M's limited Engine reads are not an independent full engine audit. Moving-manual claims about native computation, `cbv`, or deprecated external `polyrith` should be checked for the eventual target environment before becoming implementation commitments.
9. **Minor imported-package discrepancy:** all three READMEs list a checksum manifest absent from the actual imported directory: F/M `SHA256SUMS`, L `SHA256SUMS.txt`. This does not invalidate their mathematics or rerun results. Our fresh evidence supplies SHA-256 identities; do not claim the advertised original checksum file was verified. No original files were edited to fix this.
10. **The broad paradigm still needs a discriminating experiment.** An ordinary Lean package can expose the same object registries, checked representations, reusable guards, and computational contracts. Their existence is not by itself a new-language benefit. The papers correctly permit a library/view-only outcome; preserve it as a real stopping choice rather than ceremonial caution.

## Suggested next-round questions and experiments

1. **Choose two first slices under one protocol.** Implement L's dyadic residual checker and M's partial/total rational zero-set distinction through ordinary Lean before requiring new authored syntax. Fix the semantic object, output relation, context, checker, and replay format. Compare actual source input and failure localization through both frontends.
2. **Make the relation vocabulary precise.** Can one result carry independent proofs of exact value, domain equivalence, coverage, multiplicity, canonicality, finite precision, and enclosure? Which implications are library theorems rather than type coercions? Include the same roots with incomplete coverage and the same function values on unequal domains.
3. **Adopt a universal precision convention at the wire boundary.** Prefer explicit `coefficients_below N`/ideal membership, retaining surface “through degree N” as a translated notation. Check differentiation and substitution against emitted precision demands, including valuation-sensitive multiplication and newly increased precision after an edit.
4. **Test when sharing actually pays.** Reify one polynomial used in derivative, residual, evaluation, and root tasks. Compare exact-target Lean with and without shared representations and guard closure. Record serialization, elaboration, memory retention, invalidation, and checking costs separately from frontend input.
5. **Verify the residual theorem at its stated algebraic generality.** Prove the unit-derivative version over commutative rings, then instantiate Q and a ring with zero divisors. Add a merely nonzero nonunit negative neighbor. Keep root existence separate from finite checking. Compare triangular and Newton production under the same checker and output relation.
6. **Demand a genuinely parametric second gate.** Produce the Lambert quotient/product derivative certificate for symbolic n and arbitrary polynomial P, then both branch instantiations with the source's non-pole/range-local hypotheses. Fixed-n finite checks cannot substitute for this gate.
7. **Clarify admissible representation replacement.** Compare a unique-root specification, a weak “some root” specification, an exact presentation, and an observational jet handle. For each, state which edits preserve the accepted object, which preserve only registered observations, and which require explicit plan/object review.
8. **Extend view capabilities beyond injectivity.** Use M's ideal-membership Z→Q example to require property-specific witness transport; include equality preservation, equality reflection, solution coverage, and coefficient-domain witnesses as separate interfaces.
9. **Prototype author/reader diagnostics.** Distinguish a semantic notice, an unproved sufficient guard, a certified impossible guard, an unsupported representation, and an invalid method. Measure M's guarantee/guard overestimation tasks; a refusal-only system does not pass.
10. **Use current Leant behind a receipt-preserving adapter only after the boundary works.** Evaluate structural assembly against direct application and existing Lean search on the same premises. Test exact displayed-edit replay and contextual negation explicitly. Failure to find structural inhabitants must never be promoted to a negative mathematical theorem by metadata alone.
