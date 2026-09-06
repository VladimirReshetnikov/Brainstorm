# Review of the parallel round-3 synthesis, Nine Refinements

The peer report is a **secondary synthesis**, introduced by main at `8ddc6abb07df3906949f8f1a55b88288987fabe5`. It is not a tenth independent proposal and should not enter the nine-report convergence denominator. This review read the complete `docs/round-3/unified_report/unified_report.tex` (597 lines) and its complete `appendix.tex` (158 lines), compared their semantic recommendations against our current synthesis, and inspected the relevant retained Lean sources/logs. No Lean execution, PDF build, Git mutation, or modification of either report was performed here. This memo is the only file written in this follow-up.

Paths and line numbers below refer to the reviewed checkout. The peer paths remain stable at the stated pin; our report's line numbers may move during incorporation.

## Overall assessment

The peer's strongest additive contribution is new evidence for the **already chosen non-vacuous exact-quotient workload**, together with specific questions about **rewriting anchored evidence**, **dependent indices/universes**, and **sharing reification infrastructure**. Its proposed completeness table is a useful organizational idea but is mathematically wrong as written in two important places. Retain the idea only after separating positive soundness, decision completeness, and counterexample realization.

Our synthesis already develops the common refinement calculus, structure/data distinction, dependent behavioral composition, bounded qualifier closure, requirement transformers, non-vacuous Frey example, realization asymmetry, prefix observations, and matched Lean baselines. Repeating the peer's catalogue would add length without adding an argument. Our existing separation of observations from constructions, and of theorem truth from statement and method fidelity, is more precise than the peer's repeated assertion that the calculus is finished.

## Additions worth making

### 1. Promote the exact-quotient example's evidence status, with exact scope

**Peer:** `docs/round-3/unified_report/unified_report.tex:446`–`:447` (§7.3), `:557` (first slice); `docs/round-3/unified_report/experiments/lean/FreyExact.lean:9`, `:16`, `:28`, `:37`, `:42`, `:47`.

**Existing coverage:** `docs/round-3/synthesis/unified-report.tex:576` (§7.1, written arithmetic proof), `:642` (non-vacuity), `:1180` (first property-aware use site).

The new source supplies a direct Lean implementation of the arithmetic spine our report already recommends: powers of even integers divisible by 16, odd powers preserving the mod-4 residue, the two numerator-divisibility lemmas, and the two integer-to-rational quotient casts. Its helper for the second numerator has weaker premises than the first: neither oddness nor `a ≡ 3 mod 4` is needed for `sixteen_dvd_a4`/`cast_a4` (`FreyExact.lean:37`, `:47`). This is a particularly good demonstration of **operation-specific requirements instead of demanding an entire Frey package everywhere**.

Recommended incorporation: add a short paragraph after our arithmetic proof identifying these retained declarations and their precise premises. If root performs a fresh focused run, label that separately from this peer's historical log. The file does not formalize the complete equality of bundled Weierstrass curves, an elaborator, or the author's compact syntax. No Fermat equation, primality, coprimality, or nonzeroness assumptions on the parameters appear in the arithmetic theorem interfaces. Nonzeroness of the *cast denominator* is still supplied to `Int.cast_div` (`:45`, `:49`).

The retained log queries four principal theorems; it is not an axiom audit of all six named declarations. See the count and axiom reconciliation below.

### 2. Add an explicit rewrite-and-replay requirement for the evidence index

**Peer:** `docs/round-3/unified_report/unified_report.tex:473` (§8.3 blind spots), `:578` (T3, “Does simp break the anchor?”).

**Existing coverage:** our report `:491`–`:508` explains scope, typed substitutions and invalidation; `:1138`–`:1155` reuses Lean's contexts and snapshots. It does not spell out simplifier-driven rewrites of an anchored expression.

This is a useful missing concrete case. Given `p : P(t)`, replacing a lookup key by the printed normal form of `t` is insufficient. When rewriting provides `h : t = u`, derive evidence for `P(u)` by equality elimination and retain the dependency on `h`. When simplification rewrites the *proposition* by `h : P(t) ↔ Q(u)`, the appropriate adapter is the checked implication to `Q(u)`; it need not be an equality between `t` and `u`. Definitional equality can be delegated to Lean's conversion check. These are different routes to matching a goal.

Recommended insertion near our `:504`: the index may use normalization to propose matches, but accepted reuse must typecheck the proof at the current target, with any equality/iff transport retained. A changed simplifier profile may change the proposed route and requires rechecking its retained dependencies; it does not license changing the mathematical anchor by a string rewrite.

A paired test is straightforward: first obtain a fact at `t`; rewrite a goal to `u`; accept the typed transport; then change the rewrite premise or selected structure and require invalidation or a new adapter. This exercises a real Lean editing workflow rather than another abstract identity slogan.

### 3. Make dependent indices, universes, and snapshot reconstruction explicit

**Peer:** `docs/round-3/unified_report/unified_report.tex:468`, `:473`; questions `:576`, `:583`.

**Existing coverage:** our `:426`–`:439` already includes translation of dependent contexts; `:1160`–`:1171` distinguishes meaning-bearing holes from authorized construction/proof holes. The peer therefore exposes an implementation obligation, not an entirely missing semantic idea.

Recommended addition: accepted evidence identities include the elaborated term's universe arguments and dependent indices. For a family `B : A → Type`, replacing `a` by an equal `a'` may require transporting data of type `B(a)` before a dependent proof can even be applied. At an incremental-elaboration boundary, preserve or reconstruct a well-typed telescope/substitution; do not assume an old free-variable identifier denotes the new declaration's binder. Persistent caches are candidates for reuse, not a second context.

Add one regression involving a dependent family and one involving an unresolved universe/data index. These should test the existing “freeze meaning” policy transactionally while continuing to allow proof-local metavariables and explicitly authorized witness construction.

Do not repeat the peer's absolute claim that none of the proposals addresses universes: Gneiss explicitly freezes universe assignments at `docs/round-3/ideas/gneiss/gneiss.tex:645` and includes them in request identity at `:1363`; Fiber lists universes and quantifier dependencies at `docs/round-3/ideas/fiber/fiber.tex:366`. Basalt already describes immutable request snapshots, transactional metavariables, and stale-result rejection at `docs/round-3/ideas/basalt/basalt.tex:1887`–`:1892`. What remains open is a checked implementation of these policies under Lean's actual editing behavior.

### 4. Replace the peer's completeness table with a capability table

**Peer:** `docs/round-3/unified_report/unified_report.tex:518`–`:536` (§9.2); T5 at `:580`.

**Existing coverage:** our `:974`–`:985` proves the affine criterion on paper and identifies the missing mechanization; `:987`–`:1026` separates positive transfer, witness realization, and correlated observations. Our mathematics should be retained.

The organizational idea is useful: attach an explicit theorem inventory to every abstraction used by a synthesis provider. The columns should distinguish:

1. **Positive transfer:** an accepted abstract result entails the requested concrete claim, with the interpreter/reification bridge explicit.
2. **Decision completeness:** every true concrete claim in the declared fragment can be certified/decided by this abstraction, under the actual admissible-input semantics.
3. **Negative transfer:** a true concrete claim implies the abstract property that the counterexample violates.
4. **Realization:** the particular abstract counterexample comes from an admissible concrete input; global surjectivity is a stronger optional theorem.
5. **Observation coverage:** if a family of observations determines an object, state its universal quantifier. A theorem about all prefixes is not a finite test result.

An implementation need not possess all five capabilities to be useful. In particular, an incomplete but sound checker can certify successful answers. If a column is missing, the adapter must refrain only from the corresponding promotion.

For `List Nat` and the fixed affine grammar, the written zero/basis-vector argument supplies decision completeness; the source grammar/evaluator/model-normalizer correspondence still needs to be connected to rendered candidates. For `List Empty`, coefficient-vector equality over unrestricted naturals is a sufficient positive check but is not complete for the concrete universal behavior. If the model is restricted to its actual input image `{0}`, a different criterion—equality of the constants—is complete. These distinctions yield a more reusable provider interface than a Boolean “complete” badge.

### 5. Add the quantifier distinction for pruning partial synthesis candidates

**Peer:** `docs/round-3/unified_report/unified_report.tex:397` (Fiber contribution), `:495` (N24); `docs/round-3/unified_report/appendix.tex:67`.

**Existing coverage:** our `:955`–`:959` permits contracts to constrain partial candidates but does not explicitly distinguish rejecting one completion from rejecting its whole sketch.

Recommended insertion in the Leant experiment section: a counterexample to one completed term justifies rejecting that term. Rejecting a sketch as impossible requires a sound abstraction excluding *every permitted completion*, or an explicit label that the pruning is heuristic. For a partial term `s[?h]`, `¬Spec(s[h₀])` is not `∀h, ¬Spec(s[h])`. This matters before behavioral checking has a final candidate identity and is a genuinely useful strengthening of our existing acceptance boundary.

This is separate from input realization: a real concrete counterexample to one completion still does not refute all completions.

### 6. Ask about shared reification without promising one universal reifier

**Peer:** `docs/round-3/unified_report/unified_report.tex:556` (affine rational inequalities with opaque real atoms), `:579` (T4).

**Existing coverage:** our `:1060`–`:1069` separates syntax/denotation, checker soundness, reification, execution, and original-target reconstruction. Our `:1184`–`:1185` correctly warns that Schist's natural-number checker is not an integer-division solver.

Useful question: after two concrete bridges exist, which parts of atom identity, term traversal, typed reconstruction, and proof assembly can they share? A reusable reification interface should return a typed expression plus a theorem linking its denotation to the original term, with a fixed atom valuation and coefficient interpretation. That pattern is broader than any one checker.

Do not collapse list-program semantics, natural-number affine equality, rational nonnegative linear combinations, and ring-polynomial identities into one untyped grammar. They use different operations and semantic laws; natural-number subtraction is a typical trap. Length extraction itself is an interpreter theorem, not merely ring-expression reification. An affine inequality checker over the reals needs ordered-algebra hypotheses and nonnegative multiplier evidence absent from Schist's equality checker.

Recommended treatment: one next-iteration question or a small extension to the checker gate, not a new mandatory framework preceding the authoring experiment. The peer's choice to start with a rational inequality reifier is defensible but does not demonstrate that it is the uniquely smallest or cheapest slice.

### 7. Separate a read-only renderer from new input syntax in evaluation

**Peer:** `docs/round-3/unified_report/unified_report.tex:570`; `docs/round-3/unified_report/appendix.tex:20` attributes a renderer-only arm to Obsidian.

**Existing coverage:** our `:1255` groups a narrative surface/document view into L4 and our `:1325` already specifies the semantic reading test.

A sentence can clarify that improved display and new input syntax are independently switchable treatments over the same checked record. A renderer-only outcome is worth measuring even if authoring remains ordinary Lean. Avoid turning this into a full factorial experiment unless the pilot can support it; the immediate point is not to attribute a display benefit to a parser that was never needed.

### 8. Retain paired non-vacuous fixtures and target-specific control lemmas

**Peer:** `docs/round-3/unified_report/unified_report.tex:567` proposes a positive-inhabitant column in every negative table; `:437`–`:444` supplies existing Mathlib control interfaces.

**Existing coverage:** our `:642`–`:668`, `:1290`–`:1323` already addresses non-vacuity and paired boundary tests.

A modest operational improvement is to record the positive fixture, its admitted premises, the mutated premise, and the expected kind of failure for each acceptance test. This makes the non-vacuity policy executable. It does not make constructive inhabitation of every abstract mathematical hypothesis a universal requirement for proving a theorem.

The supply log offers specific baseline types: exact cast transport needs nonzeroness of the denominator *in the destination division ring*; the derivative-Lipschitz adapter needs differentiability as well as a derivative bound. The generic `mul_eq_one_comm` interface uses `IsDedekindFiniteMonoid` (`Supply3.log:13`), while the matrix application still needs the instance for the actual matrix algebra. Preserve this distinction: finiteness of scalar one-sided inverses alone is not a proof of stable finiteness of every matrix algebra.

## Claims that should not be imported without correction

### A. “Finite evidence exactly when completeness” is too strong

At peer `unified_report.tex:519`, completeness is made necessary for a finite observation to prove a universal claim. It is not. A finite certificate accepted by a sound checker can establish a universal polynomial identity even if certificate discovery or the supported checker is incomplete. What is required for that successful result is its soundness/denotation/target bridge, not a decision procedure for every true statement in the domain.

The parallel “exactly when a realization theorem is available” wording also suppresses the negative transfer premise. Realizing an abstract input is insufficient if the abstract property does not follow from the concrete specification. Conversely a direct proof of the original negation needs no intermediate abstract realization theorem. Our `:998`–`:1004` already states the relevant implication correctly.

### B. The `List Empty` table cell is false under the table's own definition

Peer `:523` defines completeness as deciding the universal claim; `:530` calls unrestricted length coefficients over `List Empty` complete. Compare the constant-empty function with the identity. Their abstract affine models are `0` and `n`, with unequal coefficient vectors. Every actual input has length zero, so the two functions satisfy the same length behavior on every concrete input. An unrestricted coefficient-equality decision rejects a concrete universal law that is true.

The correction is either “positive sound but incomplete for the concrete domain” or an explicitly different model restricted to the realizable image `{0}`. It is not enough to leave “complete: yes, realizable: no” without distinguishing abstract and concrete universals. Our exact image formula at `:1006`–`:1017` already supplies the right explanation.

Peer `:532` also places “prefix agreement for all N” in a table titled finite evidence. Joint faithfulness may be correct, but the hypothesis is an infinite universally quantified family, not one finite observation. A finite proof of that universal theorem should not be confused with a finite observation of the object.

### C. Core encodings are not alpha-equivalent

Peer `:144`, `:184`, `:455`, `:589` describes the seven encodings as alpha-equivalent or the same file written seven times. Alpha-equivalence only renames bound variables. Choosing a subtype versus a record, representing a local anchored proposition versus a packaged value, or adding different higher-order interfaces is a substantive representation change. Table `:194`–`:204` itself lists different constructions and absent combinators.

Use “shared semantic pattern” or “closely related encodings with small adapters,” not a syntactic equivalence claim. A useful future coherence theorem could relate particular encodings; none is established by compiling them separately.

### D. The matrix qualifies claims that the prose calls unanimous

Peer `:260` marks Obsidian's variance treatment partial and `:263` does the same for the refined-domain/guarded-total distinction; `:145` says both appear in all nine. Row H3 at `:297` marks proof-linked provider laws explicit in four reports and partial in five, while rule 10 of “Ten unanimous rules” at `:340` includes the stronger requirement. These can be sound recommended policies without being nine equally explicit treatments.

The peer's 76 rows are a more granular editorial taxonomy, not a second sample of proposals or a numerical novelty estimate. Do not combine its 46 unanimous rows with our 89 explicit cells as if the units were comparable.

Its novelty prose also contradicts its own inheritance table: peer `:481` calls N11/N19/N25 new, but `appendix.tex:54`, `:62`, `:68` identifies inherited M18/M28/M33. The parenthetical assertion that the new families are failures “only a property-aware layer can fail” (`:481`) is false: ordinary Lean tactic adapters, replay systems, renderers, and libraries can mishandle several of them. Family ids organize examples; they do not prove novelty or necessity of a language layer.

### E. Do not turn a sufficient method premise into mathematical necessity

The peer's matrix rule F5 (`:282`) correctly says diagnostics should name a premise required by the selected method, not declare it necessary. Its negative suite sometimes violates that rule:

- `appendix.tex:82` says leastness needs an attainment witness. Attainment is sufficient, not necessary. On `(0,1)`, `f(x)=x²` has least Lipschitz constant 2, because secant slopes approach 2, although every secant slope is strictly below 2. The required missing item is a proof of leastness, which may use a limit rather than attainment.
- `appendix.tex:76` names an `L¹`-summability contract as *the* required response to interchange. A valid dominated-convergence or another appropriate interchange theorem is an alternative. Our `:1312` already leaves this open correctly.
- `appendix.tex:80` combines failure of a particular contraction route at `q=1` with a general orbital-comparison obstruction. Our orbital theorem requires orbit convergence and normalization; `q=1` is relevant only where it prevents those hypotheses, not as a universal ban on every comparison argument.
- `unified_report.tex:549` says semantic subtyping/equality reflection “makes timeout mean false.” An implementation could instead return unknown. The substantive concern is coupling conversion to open-ended proof search, together with decidability, predictability, and trust costs; the false/unknown mistake is not forced by the syntax of the extension.

### F. The prose overstates completion and predicts unmeasured implementation effort

Peer `:455` says nothing remains to design at the calculus level, while `:468`, `:473`, and T3/T4/T7/T8 list unresolved source-meaning, rewriting, dependent-index, and rule-generation issues. Agreement is enough to choose a prototype, not a proof that a full specification is complete. “Three hundred lines away” at `:470` and `:591`, and “smallest checker” at `:556`, have no measured derivation. Our exit gates should remain acceptance conditions rather than source-line or effort estimates.

The blind-spot paragraph at `:473` overstates absent mathematical domains as well: the corpus includes binomial inversion and finite-map arguments, so “no combinatorics” should not be repeated literally. It is reasonable to ask for substantially different transfer domains; it is not necessary to erase the examples already studied.

## Count and execution-evidence reconciliation

These are static reconciliations of retained inputs, not new compiler runs.

| Artifact | Peer prose | What the retained source/log establishes |
|---|---|---|
| Seven original cores | 48 theorems, 43 axiom-free, five `propext` (`unified_report.tex:411`, `:424`, `:429`) | There are **49 named theorem declarations**. Karst has 12; its log queries 11. `viewIntro` at `docs/round-3/ideas/karst/examples/KarstCore.lean:17` is omitted from the peer's queries. The peer has 48 distinct queried declarations, of which 43 have empty inventories and five only `propext`. These are two different counts. |
| Our original-core audit | 32 distinct queries | This remains correct: our independent audit queried a smaller selected set. Do not retroactively relabel it as the peer's 48-query audit. Both share the same seven source files. |
| Moraine complete affine criterion | Contribution paragraph says criterion and model soundness are both kernel-checked (`unified_report.tex:400`) | The source proves `LengthExpr.model_sound` at `docs/round-3/ideas/moraine/companion/Contracts.lean:166` and promotes a *supplied universal* model law at `:177`. It does not implement the coefficient normalizer or mechanize coefficient equality iff universal length equality. The peer itself correctly restricts the claim to the soundness half at `unified_report.tex:434`, `:559`. |
| `FreyExact.lean` | Four theorems and six examples (`unified_report.tex:447`, `appendix.tex:100`); 62 lines | **Six named theorems, seven examples, 67 lines**. Four principal theorems are queried; two helpers are not. Named declarations are at lines 9, 16, 28, 37, 42, 47; examples at 52, 53, 56–59, 61. Two examples compute the positive triple's coefficients, four show dropped-premise failures, one shows an inexact cast. |
| Frey axiom inventory | “standard axioms” for four principal results | `FreyExact.log:1`, `:3`, `:4` report `propext`, `Classical.choice`, `Quot.sound`. `:2` (`sixteen_dvd_a4`) reports only `propext`, `Quot.sound`. This does not show all named helpers were individually audited. |
| `Supply3.lean` | Supply probe verifies names and examples | Sixteen `#check`s and three positive examples precede **one deliberate negative tactic probe** at `Supply3.lean:27`. `Supply3.log:43` emits the experimental `mvcgen` warning and `:44` the expected synthesis error. The complete file is not a successful zero-error compilation. The peer discloses this in `appendix.tex:99`. |

The `mvcgen` caveat is worth incorporating into our current `unified-report.tex:1116`–`:1121`: the tactic is present at the pinned toolchain, but the retained probe explicitly marks it experimental. Keep its role as a baseline/control and do not infer a successful effectful-contract example from the deliberately invalid `example : True := by mvcgen`.

The supply log's deprecation (`Supply3.log:10`, `:40`) supports replacing the old `Matrix.mul_eq_one_comm` spelling with `mul_eq_one_comm`. The shown type at `:13` is a general Dedekind-finite-monoid interface. This is useful library evidence, not a completed proof of the full prefix-local inverse theorem or a guarantee that every desired coefficient ring provides the required matrix instance.

## Concise incorporation plan

1. Cite the peer as a secondary synthesis at `8ddc6ab`; keep the nine-report corpus and original input pin separate.
2. Add its Frey theorem evidence to our existing exact-quotient case, with weaker per-operation premises and corrected theorem/example/axiom counts.
3. Add one paragraph and paired acceptance test for evidence reuse after `simp`, including dependent index/universe and snapshot requirements.
4. Add one paragraph distinguishing refuting a completed candidate from rejecting a whole synthesis sketch.
5. Optionally add a compact **capability** table for positive transfer, completeness, negative transfer, realization, and observation coverage. Do not copy the peer's List Empty cell or its “exactly when” slogan.
6. Add a next-iteration question on reusable typed reification infrastructure and clarify the renderer-only control. Avoid expanding the first implementation into a general checker framework.
7. Preserve our stronger caveats: no alpha-equivalence claim, no settled-specification claim, no necessity claim from a sufficient premise, no conflation of a deliberately failing supply probe with successful compilation, and no novel-design score from the peer's editorial tallies.
