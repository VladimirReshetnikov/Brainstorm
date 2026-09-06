# Critical reading: Karst, Moraine, and Obsidian

These notes cover the complete TeX texts, all READMEs, source registers, build helpers, Python companions and captured evidence, and both standalone Lean companions under `docs/round-3/ideas/{karst,moraine,obsidian}` at Brainstorm commit `58bb54219f494b29310ff77384732129411da887`. The package contents were read as design proposals; their external repository claims were not treated as fresh builds. One external primary source was retrieved to resolve a substantive omission in Moraine. All 26 input files byte-matched the pin and remained unchanged during the reproduced Python runs. This lane performed no Lean/Lake invocation or Git mutation. The parent separately owns fresh Lean validation.

## Most valuable conclusions for the unified report

All three propose **proof-backed properties at ordinary elaboration sites while preserving an already chosen Lean term**. The major change from round two is where the interface participates: binding, application, composition, temporary bundle construction, and synthesis, rather than only the receipt from a computational service. None establishes that a new kernel feature or independent language is required. Their useful differences concern which semantic boundary should be implemented and measured first.

1. **Karst gives the strongest concrete warning about abstract negative evidence.** A function returning `[]` preserves length on every input of `List Empty`, because its only possible input is empty. An unconstrained natural-length abstraction admits length one and produces a spurious apparent counterexample. This is explicitly a future original-Lean bridge test, not an accusation that current Leant admits or mishandles this target. Replaying a counterexample in an abstract model is insufficient unless an input satisfying the original dependent telescope can realize it. See *A new bridge test: abstract counterexamples must be realizable*, `docs/round-3/ideas/karst/karst.tex:1556`–1592; the ordinary Lean statement is `examples/KarstCore.lean:96`–100.

2. **Moraine provides a tractable positive counterpart.** Its closed list DSL over `Nat` has an affine length model. Every natural length vector is realized by zero-filled lists. Consequently, coefficient equality proves a universal length law, and a mismatching constant or coefficient yields a realizable zero/basis-vector counterexample. This supplies the missing adequacy ingredient in Karst's example for a deliberately restricted domain. The criterion does not extend to arbitrary list functions merely because they pass the same finite observations. See *An executable slice: universal affine length contracts*, `moraine.tex:1439`–1585, especially the realization argument at 1511–1514.

3. **Obsidian makes vacuity a specification-testing concern.** A local arithmetic lemma proved only under a full Frey contradiction context can succeed for the wrong reason. Axiom auditing alone cannot identify that problem. Test arithmetic under the weaker, satisfiable interface `odd p ∧ 4 ≤ p ∧ a ≡ 3 mod 4 ∧ 2 ∣ b`, with `(a,b,p)=(3,2,5)` as a positive instance. Separately constrain a named arithmetic method's dependency support. This is neither a general consistency checker nor a justification for rejecting proofs by contradiction. See *Extract a weaker arithmetic interface*, `obsidian.tex:373`–402, and *A subtle test-design problem: vacuous local contexts*, 443–450.

4. **Moraine broadens behavior beyond scalar predicates.** The two inverse maps in coinduced invariants must satisfy well-definedness, linearity, and inverse laws about those exact maps. A representing family of algebra-hom equivalences must additionally be natural under postcomposition; independent objectwise bijections do not supply naturality. This tests multi-object and higher-order contracts beyond `continuous f` or list length. See `moraine.tex:751`–824 and 828–949. Its finite/free reconstruction needs the correction below.

5. **Obsidian supplies a strong analytic negative neighbor.** On `(0,1)`, let `f_n = n · 1_(0,1/n)` for `n≥1`, and `g_0=f_1`, `g_n=f_(n+1)-f_n` for `n≥1`. The series sums pointwise to zero, each term is integrable, and the sum of the integrals is one. Its integral norms satisfy `∫|g_n|=2/(n+1)` for `n≥1`, so absolute summability fails. Thus termwise integrability plus pointwise convergence cannot replace its `L1Series` contract. This is a genuine counterexample to a weaker rule, not merely a missing-premise mutation. See `obsidian.tex:478`–557.

6. **Karst identifies useful nonregression controls.** ProveIt's no-finite-model corollary and the final Frey contradiction are already short mathematical arguments. Long attribute/instance preludes are configuration cost, not deep proof length. A new syntax should preserve those short proofs and separately measure whether project-owned structure/automation profiles reduce configuration duplication. See `karst.tex:284`–341, 795–817, 1111–1127, and 1202–1236.

## A substantive correction: finite index is not finite module

Moraine's *A representing algebra with natural behavior* begins with only “a finite family of commutative A-algebras H_i” and then asks for a representing `W` finite and free over `A` (`moraine.tex:884`–901). The source reconstruction does not state the necessary finite/free hypotheses on each `H_i`. The original pinned Lean theorem does:

```lean
[∀ i, Module.Finite A (H i)] [∀ i, Module.Free A (H i)]
```

These assumptions occur at **original source line 37**, with the conclusion and naturality law at 38–43, in [the pinned primary source](https://github.com/anthropics/fermats-last-theorem/blob/aa2d8b34692b16c70f699536de0d8e75b9a3e9ef/P2M/Sol/S_Algebra_exists_algHom_equiv_pi.lean#L34). A byte-preserving fetched copy and hash receipt are retained in `evidence/karst-moraine-obsidian/primary/`.

The corrected statement assumes a finite index type and commutative `A`-algebras `H_i`, **each finite and free as an A-module**. It constructs a commutative `A`-algebra `W`, finite and free as an `A`-module, and equivalences `Hom_A(W,T) ≃ ∏_i Hom_A(H_i,T)` natural in commutative `A`-algebra targets `T`. The tensor universal property itself does not need the finite/free assumptions; the additional module conclusion does.

The omission is mathematically material. Take a singleton index, `A=Q`, and `H=Q[X]`. A natural representing equivalence forces `W` to be isomorphic to `Q[X]`, by uniqueness of representing objects, whereas the monomials `1,X,X²,…` show that `Q[X]` is not finite dimensional over `Q`. A finite index set does not supply finite generation of its members. This is a defect in the report's self-contained exposition, not in the original Lean source. It should become a paired test for preserving data-bearing class hypotheses during natural-language compression.

The primary source was read, not compiled. Its retained Git blob is `bbcb8ea57e0ed64d0271cc36911f8d8b49771388`, SHA-256 `11e2e14c7e7c5d2163e9996f2237cfd2b64054d9d208899a7f972a8b4a074dc8`. Browser extraction removed blank lines; original file lines, not browser line labels, are used here.

## Shared core and consequential differences

The machine-readable `evidence/karst-moraine-obsidian/convergence.json` records the ten requested comparison dimensions, with explicit/partial/absent editorial judgments and line anchors. This is a reading crosswalk, not a novelty score or independent usability result. The shared brief and inherited syntheses correlate the reports.

| Dimension | Karst | Moraine | Obsidian |
|---|---|---|---|
| Core elaboration | Ordinary Lean terms; relative graph soundness | Ordinary Lean derivation rules; explicit primitive-refinement alternative analyzed | Ordinary Lean overlays; relational operation signatures |
| Anchor and scope | Scope closure includes proof and proposition plus dependent declaration types | Evidence rows refer to resolved expressions and persistent telescopes | Context embeddings, witness packaging, branch coverage |
| Structure choices | Named instance/automation profiles; nonzero/regular/unit separated | Bundled adapters with projection equations and inverse laws | Measure/topology/scalars part of frozen semantic context |
| Behavior | Explicit consequence variance and intermediate-witness composition | Same laws plus two-input relations and natural families | Contract application, dependent construction, relational composition; no dedicated full arrow-variance theorem |
| Bounded inference | Request-wide budgets, cycle refusal, no proof/resource noninterference promise | Finite cheap worklist over fixed anchors; expensive term generation separately budgeted | Bounded transitions and `fun_prop` reuse |
| Observations | Backward derivative-jet demand with explicit sufficient precision | Error budget for endpoint deletion, distinct from reindexing/norm equality | Point, neighborhood, almost everywhere, and finite-order relations distinguished |
| Leant | Candidate identity plus realizable original-target refutation | Current `--where` surface and exact affine proof path | Handoff correspondence separated from original contract; operational semantics qualified |
| First checker | Sparse integer multivariate ideal certificates | Closed affine list-length contracts | Sparse integer certificates beside exact-quotient interface |
| Fidelity | Every asserted node checked; chosen method distinct from broad search | `by`, `hint`, and `solve` make different explanatory commitments | Named analytic reason plus independent statement/renderer validation |
| Evaluation | Five nested arms explicitly isolate property engine and frontend | Four arms isolate library, refinement typing, and proof surface | Five treatments include a renderer-only control |

The reports do not disagree about soundness by kernel checking. They disagree productively about **what the smallest informative implementation should be**. Karst starts with a polynomial checker and finite-map property index (`karst.tex:1785`–1835). Moraine starts with a bundle adapter and affine length bridge (`moraine.tex:1849`–1862). Obsidian starts with independently satisfiable exact division, then `L1Series` (`obsidian.tex:846`–853). These are different experiments: arithmetic reflection, source-level property usability, and behavioral synthesis should not be conflated into one demonstration.

For the next iteration, the smallest complete semantic bridge is likely the affine length DSL: it has a finite grammar, executable normalization, a clean soundness proof, exact counterexample construction, and an explicit realizability argument. That judgment is an engineering recommendation, not a measured performance result. A separate small bundle adapter should test whether property inference improves actual authoring beyond equally equipped Lean. Multivariate certificates and analytic packages remain useful subsequent stress tests.

## Mathematical distinctions worth preserving verbatim in substance

**Preconditions do not restrict the implementation's carrier.** A total `f:A→B` with `∀x, P x → Q x (f x)` differs from `g:{x:A // P x}→B`. The second need not extend to `A→B`, especially when `B` is empty. Local flattening may turn the restricted input into `∀x, P x → B`, never discard its proof binder. Karst 1653–1669 and Moraine 587–629 explain this especially well.

**Facts may be weakened by a proof of implication; values must not be relabeled.** For behavior `Beh(P,Q,f)`, a requested interface `(P',Q')` is valid when `P'→P` and `P' x→Q x y→Q' x y`. Composition retains `y=f x` while proving the second guard. Karst 879–913; Moraine 542–585. There is no general strongest inferred refinement or universal ordering of all mathematical guarantees.

**Proof irrelevance does not erase data-bearing choices.** Two multiplication operations, topologies, measures, bases, inverse algorithms, or chosen roots can differ while their underlying carriers match. Subtype packing remains necessary at first-class dependent boundaries. See Karst 375–416 and Moraine 796–824.

**Properties of a proof body are not automatically exported contracts.** Obsidian notes that the normalization source preserves the exponent internally but exports only `Nonempty FreyPackage`. An interface exposing `P.p=p` is stronger and requires its own theorem (`obsidian.tex:452`–476). This complements Moraine's missing input assumptions: preserve both hypotheses and guarantees, rather than infer either from the implementation's apparent behavior.

**Distinct finite-sum transformations need distinct result relations.** Moraine proves a general deletion bound `|sum_S g - sum_T g| ≤ kR` when `T⊆S`, at most `k` terms are deleted, and those terms have norm at most nonnegative `R`. Bijective reindexing yields equality; phase manipulation may yield equality only of norms; endpoint deletion yields an error bound. The singleton-versus-empty sum separates the latter from equality. The `{-1,0}` to-natural collision separates a cast from bijective reindexing (`moraine.tex:1003`–1060).

**Native execution, discovery effects, and mathematical behavior are separate.** A nondeterministic external proof search does not make the proved theorem nondeterministic. Conversely, a final-output theorem for a lazy Haskell service does not prove it never forces an undefined tail. Operational claims need an evaluation/trace semantics and implementation correspondence. Karst 929–969; Obsidian 661–666.

## Reproduced companion evidence and limits

All code was inspected before execution. `python -B .../reproduce.py` copies only the necessary Python files into this lane's `runs` directories, runs them with bytecode disabled, captures stdout/stderr, compares parsed results or named unittest outcomes with the original artifacts, and checks all 26 input hashes before and after. `reproduction.json` retains Python/platform identity, commands, source/output hashes, exit codes, and run durations. The runs all exited zero. Timings are receipts, not performance comparisons.

| Report | Fresh result | What it establishes |
|---|---|---|
| Karst | Eight groups exactly match historical JSON: 3,414 finite endomaps (154 injective), 7 polynomial protocol cases, 720 operation samples, 364 sorting inputs, 1 empty-type illustration, 312 exact quotients, 5 jet neighbors, 11 synthetic scope/origin cases | The particular finite tests ran successfully. Group counts have different units and should not be summed into a language-validation score. |
| Moraine | All 32 named tests pass; names match historical log. Includes 25,600 concrete/model comparisons and 729 ordered affine-form pairs | Closed Python grammar and protocol tests, not the general elaborator or universal theorem formalization. |
| Obsidian | Entire 608-entry JSON matches historical output: 525 arithmetic instances, 32 symbolic identities, 41 negatives, 1 satisfiability neighbor, 9 protocol-model probes | Exact arithmetic and fixed schematic-rule behavior; no Lean reifier or foreign-source proof. |

Important limits visible in the code:

- Karst's fifth-order precision “neighbor” includes the literal assertion `4 < 4 + 1` (`evidence/companion.py:238`); it does not exercise a real precision planner. Its empty-type illustration supplies the singleton list of possible values by hand (202–209). These support paper explanations, not implemented inference.
- Karst's polynomial operations validate dimensions and integer coefficients before pairing exponent vectors (24–76). The arbitrary-ring soundness argument is a paper proof (`karst.tex:1276`–1348), not a proof of Python or a Lean execution bridge.
- Moraine's source and epoch checks reconstruct both bounded syntax trees before comparing exact expressions (`length_contracts.py:126`–148). This is good reference-model behavior, but the epoch is a user-visible string and the receipt is an ordinary dataclass, not Leant's generative authority boundary. Structural limits cover arity/depth/node count and natural bit sizes; the mathematical theorem is separately unbounded.
- Moraine's complete coefficient criterion applies only after the structural affine-shape proof and realization argument. An arbitrary function can match empty and singleton lengths and drop all longer inputs; finite basis tests alone would then mislead.
- Obsidian's polynomial constructors establish the intended invariant, but direct construction of the exposed dataclass or hostile Python objects is outside its explicitly stated support (`obsidian.tex:750`). Multiplication's `zip` is justified only by that invariant. Do not promote it to a hardened serialization boundary.
- All three synthetic scope models have fixed vocabularies or lexical-prefix scopes. They do not establish correct handling of arbitrary Lean dependent contexts.
- The claimed PDF build receipts were inspected as supplied historical records. This lane did not rebuild their PDFs or visually re-audit the input documents; content review used the complete TeX.

## Lean companions: precise static scope

Karst's `examples/KarstCore.lean` imports `Init`, defines views, a behavior predicate, injectivity/surjectivity predicates and `dropAll`, and contains **12 named theorem declarations**. Eleven `#print axioms` commands are supplied; `viewIntro` is not among those eleven. Its `dropAllLengthOnEmpty` provides a particularly useful original-type theorem. It does not encode the full finite induction, polynomial checker, reifier, or a Karst elaborator.

Moraine's `companion/Contracts.lean` imports `Std`, contains **16 named theorem declarations and one anonymous example**, and models weakening, relational composition, inverse pairs, local predicates, and a closed list-expression grammar. `LengthExpr.model_sound` (166–174) proves concrete list length equals its recursive arithmetic model. `promote_model_spec` (177–184) requires a separate universally quantified model theorem. The affine coefficient representation, normalizer, coefficient criterion, and source reifier are absent. Compiling this file cannot establish that the Python coefficient checker is a Lean-verified service.

Obsidian has no standalone `.lean` file. Its appendix (`obsidian.tex:946`–975) contains an illustrative `Observation` record and weakening/composition definitions. Extracting and compiling them is possible, but it remains a small logical interface, not a frontend. The parent has reported successful unchanged compilation of the Karst and Moraine originals in its separately owned validation lane; exact executable version, logs, and axiom inventories belong to that lane's receipts.

## Answers returned to the earlier questions

Karst explicitly answers the ten *Nine Workbenches* questions and additional synthesis choices at 1955–2016. Obsidian explicitly answers eleven principal boundaries at 911–934. Moraine's answers are distributed through its implementation and positioning sections, not a numbered response table.

| Question | Karst | Moraine | Obsidian |
|---|---|---|---|
| First sound checker | Integer sparse polynomial denotation, operations, arity, execution, target reification; Lean work pending (1969–1972) | Affine length normalizer and universal coefficient criterion; structural Lean half supplied (1439–1585) | Integer polynomial paper soundness; genuine reifier/execution needed (914, 668–750) |
| Existing tactics | `grobner` bounded provider/control, no assumed certificate export (1973–1975) | Reuse `fun_prop`, `grind`; providers get same goals (1621–1641) | Pin limits/structures/evidence; no complete negative oracle (916, 738–740) |
| New workspace state | Object/source roles, supports, observation links, receipts; Lean owns logic (1976–1978) | Source association with evidence rows and scoped contexts (695–717) | Source-evidence records, obligations, origins, migration (918) |
| Partial/total default | Imported Lean meaning preserved; restricted domains explicit (1979–1981) | Distinguish carrier, restricted function, and totalized operations (611–629, 1253–1269) | Preserve imports; visible lexical partial/convergence conventions for new documents (920) |
| Which package first | Polynomial checker plus finite-map index (1982–1985) | Bundle adapter and affine length in parallel (1849–1862) | Satisfiable exact coefficients then `L1Series` (922) |
| Acceleration | No threshold; balanced/sparse/multivariate/large-coefficient workloads needed (1986–1988) | No native speedup claim; actual dependency policy required (1304–1322) | Measure checker/workload after independent replay (924) |
| Upgrades | Destination revalidation and new axiom-policy receipt (1989–1990) | Semantic diff and context-compatible proof reuse (1687–1703) | Historical old evidence plus fresh checked receipt (926) |
| Delegation and Leant | Fixed construction spec permits new witness; other existing objects frozen; require realized refutations (1534–1607, 2005–2014) | Classify authorized data metavariables instead of freezing all metavariables indiscriminately (1114–1142) | Delegate routine proofs and explicitly specified data construction; require original behavioral theorem (928–930) |
| Visibility | Domain/branch/precision/completeness/trust conditions visible (2005–2014) | Declared and currently consumed properties shown; incidental inference not public API promise (1810–1822) | Every meaning/trust-changing condition visible (932) |
| Executable mutations and stopping | Paired prototype register, finite companion only; library/index/renderer legitimate stopping points (1899–2016) | Paired semantic tests; retain library if it accounts for nearly all benefit (1705–1784) | Paired real Lean boundaries next; keep frontend only if it beats matched services (934, 906–909) |

## Questions to carry into the next iteration

1. Can we finish the affine-length checker's Lean normalization, soundness, complete characterization, and exact-source reification before adding any new property vocabulary? Which unsupported features should remain explicit refusals?
2. What is the smallest typed adequacy interface that supports both sound positive conclusions and realizable negative witnesses? How does it change for empty element types, fixed-length vectors, and dependent multi-input telescopes?
3. Can the same property service be exposed first as ordinary Lean commands, so a separate experiment measures the new surface independently? Which existing `fun_prop`, `grind`, bundle, and tactic facilities remain the most competent baseline?
4. How are data-bearing and proposition-valued instance parameters classified and shown in a semantic diff? The omitted finite/free hypotheses provide a concrete acceptance test.
5. Which statements are public contract commitments and which are incidental facts inferred from one implementation? Should exponent preservation, naturality, and extra regularity require explicit export declarations?
6. How should a named method constrain its proof support without pretending that unused assumptions prove dispensability or that an axiom audit establishes satisfiability? Which concrete positive neighbors accompany contradiction-context development examples?
7. Can a bundle adapter preserve the identity of both maps and all structural parameters with enough predictable inference to improve the coinduced-invariants example? Measure adapter cost and reuse, not only the displayed proof length.
8. How should the interface distinguish a required premise from one sufficient route's stronger premise? A message saying “this method needs fixed-zero evidence” must not claim no restriction is possible by any other argument.
9. What evidence should a mathematical reader see when a proof is valid but the advertised method or a displayed intermediate claim is wrong? Can statement, method, and kernel truth be tested independently?
10. Which first stopping decision will be binding? A useful library, property index, or renderer can succeed even if a new frontend does not justify itself; the next deliverable should allow that result.
