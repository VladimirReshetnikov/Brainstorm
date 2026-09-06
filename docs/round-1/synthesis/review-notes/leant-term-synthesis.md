# Current Leant automatic term synthesis: static review

Reviewed 2026-09-05 from `C:\Leant`, read-only. This is inspection of implementation, documentation, and test source. No Haskell build, unit/golden runner, live synthesis, Lean replay, SMT execution, or performance measurement was performed. Existing test transcripts and historical acceptance counts are evidence that the project records such checks, not fresh validation of this checkout.

## Exact source-state boundary

The root HEAD is `3a40904be8a410d832d9ab6900b3d3e7b425eccb`, matching Loom's source revision and newer than Motive/Outline's `c36adf114035fb2fba6c276b63944cc613b31668`. The working tree is **dirty**. At inspection:

- Modified: `README.md`, `leant.cabal`, `src/Leant/Synth/Verification.hs`, `src/Main.hs`, `test-unit/Spec.hs`, and the `lib/Djex` gitlink.
- Untracked: `docs/behavioral-synthesis.md`, `src/Leant/Synth/Behavioral.hs`, `test-church/behavior_probe.py`, `test-church/test_behavior_probe.py`, `test/synth-behavior.golden`, and `test/synth-behavior.txt`.
- Root HEAD pins Djex `45e35b29defde91e956f01b4bd69cd55c8779a0e`; the currently checked-out, clean Djex submodule is `63e7b2fa46d62c633e0b5a24a463e22b9e939df4`.

Therefore a claim about the current working implementation cannot be identified by root HEAD alone. In particular, the named Lean-proposition behavioral path below is uncommitted source, not functionality present in the root commit used by Loom. No `AGENTS.md` was found under this checkout. There is no root `lean-toolchain`; this review did not establish a runnable backend toolchain.

## What is implemented already

### 1. A structured translation and synthesis pipeline

`src/Leant/Synth/Fragment.hs:150–212` defines the structural fragment: arrows, products, sums, top/bottom, sort quantifiers, instance binders, exact contextual provider constraints, proper-type applications, and constructor descriptions of supported inductive families. It deliberately distinguishes Lean `Prod` from propositional `And`/sort-polymorphic products for later behavioral interpretation. Term-indexed/dependent applications remain opaque atoms (`186`); recursive families have explicit completeness and introduction-only qualifications (`198–211`). This is considerably richer than implication composition alone, while still far from a complete dependent proof-search representation.

The serializer operates on elaborated Lean expressions. Its resulting local structural problem is searched in the vendored Haskell Djex engine and rendered back to Lean. The exact backend candidate then faces a Lean check in the user's current environment. `Main.hs:1923–1925` states this producer/checker boundary; `Fragment.hs:1564–1570` and `Main.hs:3968–4003` implement its ordinary candidate program and response checks.

`Engine.hs:1119–1165` dispatches Djinn, Exference, or both, with independently prepared engine projections. `prepareSynthesis`, at `1173–1250`, distinguishes source goal from search goal, inserts constructor and caller premises under the appropriate quantifier prefix, and prepares both ordinary and typed-graph renderer closures from the same semantic origin. This is not a language model translating a whole informal proof: it is symbolic synthesis over an explicit translated problem.

The existing `test/synth-basic.txt`/`.golden` pair illustrates distributivity over sum/product, `fun f g x => f x (g x)`, polymorphic projections, constructive and classical cases, and several inhabitants of `Nat -> Nat`. These are recorded fixtures, not commands executed in this review. The broader fixture inventory includes rank-N, inductive families, correlated provider constraints, provider refutation fallback, and current-goal synthesis.

**Assessment.** This is a useful implementation base for connecting already-chosen mathematical facts. If a context supplies `A -> B`, `B -> C`, and `A`, it can assemble a `C`; if a derivative proposition is opaque, it can route that proposition through known implications but does not thereby discover the derivative theorem. A new proof language should supply domain-specific mathematical interfaces and exact local contexts, not expect structural synthesis to reconstruct arbitrary analysis internally.

### 2. Two search modes with different evidence claims

`Engine.hs:259–266` distinguishes `SynthCandidates`, `SynthRefuted Bool`, and `SynthNoTerm`. Djinn invokes a validated session/request and bounded higher-rank search (`1299–1356`). Its `ProvedUninhabitable` handling (`1357–1372`) refuses a negative conclusion when family projection is incomplete, and marks refutation as sound only with no explicit Djinn budget plus complete fragment projection and no unsafe atoms. `fragmentProjectionComplete`, at `4255–4257`, checks depth/unsafe-atom conditions. `Fragment.hs:2194–2208` gives an explicit refusal for a lone opaque goal or unsupported type application, subject to later provider handling.

Exference is heuristic, with no negative evidence (`Engine.hs:1374–1376`). Its request sets step and queue limits and selected ranking (`1441–1452`), runs a typed query (`1462–1464`), and retains exact run authority with typed candidates. If necessary, it retries allowing unused variables, omitting optional multi-constructor elimination, or focusing the prelude inventory (`1514–1554`). Those are alternative bounded routes, not a complete search of Lean.

The negative result is not exported here as a Lean proof of a proposition's negation. It is a qualified search/translation conclusion. A proof-language adapter should preserve its qualification and use checked source-level counterexamples or negation proofs for stronger user-facing claims.

**Assessment.** The reports are correct to stress positive/negative asymmetry, but “all search is bounded” is too simple a description of current settings. `defaultSynthLimits` sets Djinn's choice budget to `Nothing` (`831–840`), while Exference and candidate windows have separate bounds; Main also supports wall-clock synthesis limits, including an explicit zero/indefinite setting. A new authoring layer should own an explicit complete resource policy rather than inherit defaults without examining them.

### 3. Candidate quality is more than printed length

The implementation has `balanced`, `compact`, `diverse`, and `legacy` profiles. `docs/candidate-quality.md:14–52` records defaults and costs: size, elimination structure, provider cost, and a repeated structural-family penalty. Bound-variable spelling does not determine cost; sharing is counted once. Diversity affects order and grants no equality or evidence transport.

The corresponding Engine code preserves Djex's structural ordering rather than overriding it with a frontend size sort (`1344–1356`). Exference observes a bounded candidate pool before rendering/deduplication and retains the spent work for render failures or duplicates (`1465–1483`). Renderer-only reconstructed provider type choices are marked `RouteUnobserved` and receive no exact typed origin from the original graph (`1491–1508`). The documentation is candid that finite-pool ranking can delay the first result, that a deadline can expire after a prefix was found, and that ranking does not imply global minimality (`candidate-quality.md:82–89`).

**Assessment.** This is directly relevant to human-scale proof language design: the shortest inhabitant is often a poor computation or an opaque proof. Leant already has an extensible ranking mechanism and structural diversity. It does not yet measure explanatory quality; scores are useful search heuristics, not evidence that a mathematician understands the resulting proof.

### 4. Exact candidate/evidence association survives the pipeline

`Engine.hs:269–294` retains an `ExferenceRunAuthority` containing preparation, name table, policy, session, and request beside an opaque typed candidate. `prepareSynthesis` builds a single origin (`1213–1227`) rather than a set of unrelated caches for source goal, providers, and renderers. `DetailedVerificationVariant` preserves the displayed spelling, renderer ordinal, route, and exact typed origin (`434–517`). Arbitrary textual wrapping discards authority because it denotes a new term (`525ff`); classical wrappers are therefore not eligible to borrow an unchanged graph's behavioral evidence.

The ordinary `Verified` wrapper explicitly denotes acceptance by its supplied callback (`Verification.hs:44–50` in the dirty file), not universal kernel/behavioral authority. `verifyDistinctCandidateGroupsBy` (`155–217`) keeps the first actually accepted exact case-sensitive spelling, retries rejected spellings, leaves fresh variants available, and transfers no receipt from a later equal-looking occurrence. It does not refill a caller's window; it relies on the caller to bound the input stream. The guard runs before forcing tails after the quota is met.

`PostVerification.hs:55–80` gives each batch generative rank-2 occurrence handles; `sealPostVerificationBatch` (`117–142`) admits only a bounded exact permutation of those handles and rejects count/index/duplication mismatches. This is a concrete implementation of the reports' warning that ordering, caching, and display must not detach evidence from its owner.

**Assessment.** This is one of Leant's strongest reusable pieces. It protects producer/checker metadata identity using both typed abstraction and runtime checks. It is still not a mathematical proof artifact: Haskell nominal roles, private constructors, exact strings, and fingerprints prevent classes of accidental association errors, but they do not replace checking the selected term in its exact intended Lean context.

### 5. Existing Length behavior is a narrow, opt-in model

`docs/length-ranking.md:15–87` describes the implemented Length dialect: finite list-spine lengths, scalar and binary-product domains, canonical linear-integer queries, and independently replayed counterexamples. Ranking preserves all candidates by default; explicit filter authority can reject only a replayed counterexample. Raw `sat`, `unsat`, or `unknown`, unsupported preparation, and finite positive samples do not gain rejection authority.

The control flow is visible in `Length/Selection/Generic.hs:3–13`, `74–84`, and `227ff`: only the domain's replayed negative receipt belongs in a rejection; operational or association failure preserves the original batch. The implementation separates scalar and pair receipt types. `Length/Integration.hs:199–231` creates command-local contexts, and its selection projections distinguish rank results from filter survivors. The documentation says the progressive same-run cursor can consume at most two ordered batches under the current policy, not repeatedly refill a survivor quota. Persistent banks, general CEGIS, typed-prefix pruning, more behavioral domains, and Lean-checked specification artifacts remain proposed (`length-ranking.md:66–87`).

**Assessment.** This is useful behavioral filtering of well-typed programs under a restricted semantic model. It is not a general theorem prover for a witness specification. In mathematical proof authoring it could help find a bad computational witness, but a universal theorem about the actual Lean function still needs the appropriate checked bridge and provider assumptions.

### 6. New uncommitted host-proposition behavioral checks

The dirty working tree adds a separate named syntax, for example:

```lean
:synth choose : ∀ A : Type, A → A → A where choose Nat 11 29 = 29
```

`src/Leant/Synth/Behavioral.hs:22–60` first parses the complete goal and predicate as terms, checks the predicate under a binder of the exact requested type, sets `autoImplicit false`, and emits a local example binding the exact candidate followed by `by decide`. The supplied query name is lexical and does not replace a session declaration. At `72–89`, `decideBehavioralBy` reports satisfied after a successful positive proof, falsified only after a successful proof of the negation, and inconclusive if neither succeeds or transport fails.

`Main.hs:2337–2393` performs cold synthesis-environment setup before capturing the command deadline, does syntax/preflight checks, then threads one active behavioral request through synthesis. `2407–2448` uses owned backend request timeouts, a five-second per-request cap limited by the remaining command deadline, and backend retirement after a timeout. The generated Lean programs use 200,000 heartbeats. `Main.hs:4015–4049` checks exact type first, then the assertion. `Verification.hs:223–278` consumes a success slot only after both checks succeed; a later rendering of the same admitted candidate can still pass, and predicate failures remain distinct from type errors.

**What it establishes.** A proof of the supplied proposition about the selected candidate, relative to existing declarations and assumptions. The example above establishes that one application returns 29; it does not establish universally that the second argument is returned. A conjunction of finite tests proves that conjunction. Arbitrary infinite universal specifications often have no executable `Decidable` instance and can remain inconclusive. This is a broader input language than the Length DSL but a much narrower proof method than general specification synthesis.

**Current status.** There is source and focused test coverage for parsing, lexical capture, positive/negative/inconclusive classification, tail laziness, deduplication, and receipt ownership (`test-unit/Spec.hs:2597–2733`). Some checks are source-shape assertions and mocked callback tests rather than live backend checks. `docs/behavioral-synthesis.md:150–156` explicitly states that live six-operation synthesis acceptance is pending and that earlier rank-N/quality receipts do not establish this new feature's acceptance. This review did not run any of those tests. The new path should appear in the unified report as an uncommitted implemented mechanism awaiting its stated integration validation, not as a feature already verified by the original reports.

## Limits a new proof language still needs to solve

1. **Exact statement approval is not the current REPL's public contract.** Ordinary `candidateVerificationProgram` is `set_option autoImplicit true in noncomputable example : (goal) := (term)` (`Fragment.hs:1564–1570`). This helps permissive interactive synthesis with implicit type variables. It is not a frozen Lean expression/telescope protocol that a mathematical document should use unchanged. Unknown binder/instance/notation choices need to be settled before approved-theorem search.
2. **Ordinary acceptance is relative to the current environment.** Main's routine verifier rejects transport errors, fatal responses, diagnostics, and `sorry` occurrences; the inspected path does not itself independently compute an allowlisted transitive axiom inventory or compare a protected external target. A theorem depending on existing extra axioms is a different evidence question from a candidate containing no new `sorry`.
3. **Result identity is not archived evidence.** Candidate provenance and callback receipts are unusually careful, but this pipeline does not itself export the reports' full statement lock, scoped source-to-proof graph, protected replay artifact, and persisted specification proof. New behavioral decisions currently retain statuses/observations, not a standalone saved proof of the predicate.
4. **Mathematical semantics remain opaque outside supported structure.** Arithmetic, locality, measure-theoretic regularity, index bijections, and selected proof-plan explanations must come from checked domain libraries or other reconstruction providers. More search over the wrong abstraction does not replace those libraries.
5. **Provider selection and budget design are part of semantics-aware usability.** Too little inventory loses easy compositions; too much competes for search resources. Several existing fallback lanes address this. A proof-language contract should report providers, actual reason/method used, and whether a failure is representation refusal, exhausted search, or a missing mathematical premise.

## Recommended bridge to the unified proposal

Reuse Leant as a candidate service behind closed, explicit local obligations. Preserve its exact candidate-owner association, result taxonomy, ranking controls, and provider metadata. Require the new frontend to check returned text/expressions against a separately fixed Lean target and telescope, retain a proof artifact, and audit the selected policy. Add proof-plan provenance above the existing term origin rather than pretending that structural origin already records the author's mathematical reason.

For a first experiment, give Leant three already-selected facts and a scoped target; compare direct Lean composition, Leant synthesis, and the new claim syntax. Then repeat under reordered hypotheses, same-printed-name/different-scope variables, changed provider inventory, and an opaque but reflexive arithmetic target. For computational witnesses, separately compare the new exact finite predicate path and a proved universal specification; do not mix their success rates.

## Fingerprints of mutable reviewed inputs

SHA-256 fingerprints captured after the source review. These identify read files; they are not proof or execution receipts.

| Path under `C:\Leant` | SHA-256 |
|---|---|
| `src/Leant/Synth/Engine.hs` | `43b34d8c4d6d9e7ea1a292289d2336f6f67db6babbb96d2bbdb1931a5d930ff0` |
| `src/Leant/Synth/Fragment.hs` | `9c550fc6095dafacee2e025bcbc75940c404d649a42d5fd8f308df651b56ac30` |
| `src/Leant/Synth/Verification.hs` | `4045c4cb2560704694d87bc7f20f378f0503ebda77daa492b068bd46e596bc88` |
| `src/Leant/Synth/Behavioral.hs` | `df5117bf817b765aa7bd8517e8f9f09b23b0d747d31a897f5d90c848f8b34da6` |
| `src/Main.hs` | `4a081070ef63ab43379528e9114802f3acbeb5962e3fa980479dd31ba42dfa43` |
| `docs/behavioral-synthesis.md` | `2ce7127e04e422b5155fe8c2610a38a943ed3feaf275379b29b4f959ea34cf81` |
| `test-unit/Spec.hs` | `0a54e244ff96aad655690745ffa91b564e8eeb83f6f3cc28fe7f4fc2bcbf8824` |
