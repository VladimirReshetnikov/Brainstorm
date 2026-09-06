# Close review: Basalt, Fiber, and Gneiss

Reviewed against main `58bb54219f494b29310ff77384732129411da887` on 2026-09-06. All three TeX sources were read in full, including appendices and references, together with all Python/Lean companions, READMEs, build scripts, source registers, and recorded evidence. Inputs were read-only. Source locators below are repository-relative and one-based. Section names are included where useful because TeX line counts are not page counts.

## Main assessment

All three proposals make substantially the same foundational recommendation: keep ordinary Lean as the logical target, add a local index of proved properties about selected terms, and let expected contracts guide bounded elaboration. They explicitly acknowledge that subtypes and dependent records already express the mathematics. Their research claim is better retrieval, composition, explanation, and maintenance of that evidence. This is a convergence of design positions, not evidence that the proposed layer outperforms idiomatic Lean.

The most useful differences are mathematical workloads and prototype order:

| Report | Distinct contribution worth retaining | Suggested first experiment |
|---|---|---|
| Basalt | Relations on entire diagrams; ideal-preserving maps and completion towers; concrete realization of abstract counterexamples | A refinement-aware ideal-map composition and a CDF boundary calculation, alongside the certified algebra path |
| Fiber | Backward constraints on incomplete synthesis candidates; non-vacuous Frey exact-quotient benchmark; measure-indexed quantitative reasoning | Same-carrier enrichment and exact quotients first; compare refinement elaboration separately from a new surface |
| Gneiss | Prefix causality makes infinite sequence operators safely accessible through finite square sections; property flow through selected FLT witnesses | Small property library, coefficient checker, then finite/local observations, before surface syntax |

The supplied executables move beyond architectural prose, but none implements a frontend or supplies its actual polynomial denotation/soundness/reification proof in Lean. Their written mathematical arguments are useful specifications. Passing the Python models is a different evidence category.

## Basalt: claims and evaluation

1. **Same-object enrichment versus packaging.** The local object stays `x : A`; evidence `P x` joins a scoped retrieval index. Only API boundaries require a subtype/record. This avoids repeated rebindings and nested subtype projections. Structure selection is separately data-bearing: continuity under one topology does not authorize changing the topology. See `docs/round-3/ideas/basalt/basalt.tex:436` (Local refinements versus exported values), `:462` (Properties are not structure selection), and `:494` (Contexts and judgments).

2. **Diagram properties cannot be reduced to adjective lists.** Exactness belongs to a pair of composable arrows, and transport needs commuting squares relating the actual maps. Independent endpoint injectivity/surjectivity is insufficient even if composition is zero. The explicit counterexample over a nonzero field is `k -> k^3 -> k`, with `a |-> (a,0,0)` and `(x,y,z) |-> z`: image dimension one, middle kernel dimension two. Tensoring multiplication by two on the integers with `Z/2Z` separately shows why flatness is needed. The source's final theorem is already short, so the possible gain is reusable prerequisite assembly, not hiding invention of the ladder helper. See `basalt.tex:738`, `:1154`, `:1162`, `:1197`, `:1232`, and `:1249`.

3. **Ideal preservation gives a concrete reusable behavioral interface.** `IdealHom((R,I),(S,J))` retains an algebra map `f` with `f(I) subset J`. Composition derives preservation; preservation of ideal powers supplies quotient maps; naturality makes their family a tower morphism; all quotient observations determine the completed map. An arbitrary finite prefix does not prove the completion functor law. Objectwise bijections require compatibility, and inverses obtained from propositional bijectivity may be noncomputable. The failed identity-induced map `Z/(2) -> Z/(3)` is an excellent nearby negative: representatives zero and two agree in the source but not the target. See `basalt.tex:1029`, `:1055`, `:1077`, `:1122`, and `:1139`.

4. **The CDF example demonstrates useful diagnosis beyond algebra.** For a reflection-invariant probability measure under `r_a(t)=a-t`, the calculation gives `F(a-x)=1-mu((-infinity,x))`. Atomlessness at `x` changes this to `1-F(x)`. The exact general correction is `F(a-x)=1-F(x)+mu({x})`. For the Dirac measure at zero with `a=x=0`, unconditional symmetry would say `1=0`. This supports a frontend that can retain a weaker useful conclusion while explaining the missing boundary property. The derivative-density example separately needs an everywhere finite derivative; an almost-everywhere derivative is insufficient (Dirac's CDF has derivative zero away from its jump). See `basalt.tex:916`, `:928`, `:967`, and `:985`.

5. **A semantic bridge for Leant's abstraction.** Basalt takes existing typed origins and finite-spine handoff seriously, then identifies the missing theorem chain: exact provider function laws; a denotation for supported candidate syntax; a proved abstract interpreter; an equality to the actual inserted Lean expression. Its small grammar has variables, empty list, reverse, and append, with output length a nonnegative integer linear combination of input lengths. This universal formula has an elementary structural proof, but only finite Python examples are executed. See `basalt.tex:1303`, `:1326`, and `:1351`.

6. **Negative abstract evidence needs realizability.** For a fixed element type `A`, possible list lengths are `{0}` when `A` is empty and all naturals when it is inhabited. A length-one arithmetic countermodel cannot refute a claim about `List Empty`. Positive proofs over an overapproximation remain sound, but converting a violating abstract assignment into a concrete counterexample needs actual inputs of the original types. This asymmetry deserves a prominent place in the unified synthesis. A refuted candidate still does not refute existence of some successful candidate. See `basalt.tex:1385` and `:1425`.

7. **Observational precision has a compositional law.** If `f` requires input agreement at `d_f(n)` for output agreement at `n`, then `g after f` has sufficient demand `d_f(d_g(n))`. This connects jets, quotient levels, and other domain-specific observations without a universal strength ordering. The transformer need not be minimal. See `basalt.tex:1619` and `:1649`.

8. **Three correctness boundaries.** Kernel truth, fidelity to the selected statement, and fidelity to the advertised method/edit are distinct. All displayed assertions must be checked, including unused ones. Method fidelity means a structured derivation applies the claimed contract; it does not recover a unique proof history from a proposition. See `basalt.tex:1768`, `:1780`, and `:1794`.

Basalt's sparse multivariate checker has the right universal paper contract: exact integer coefficient combination implies the denoted relation in every commutative ring, without injection of coefficient casts or a domain assumption. It explicitly separates execution evidence and reification. It does not formalize its actual normalization algorithm in Lean. Its Python implementation validates canonical exponent dimensions/ordering/integer types but has no global resource limits; do not describe it as a hostile-input service. See `basalt.tex:1448`–`:1609` and `companions/certificate_demo.py:22`–`:122`.

## Fiber: claims and evaluation

1. **Limited same-carrier coherence removes unnecessary policy.** Two refinement paths preserving the original carrier and ending in the same subtype are equal by subtype extensionality/proof irrelevance. Therefore not every difference in proof routing is a semantic conflict. This does not identify different embeddings, bases, structures, or witness values. See `docs/round-3/ideas/fiber/fiber.tex:216` (Refinement weakening), especially the Same-carrier coherence proposition immediately following it.

2. **The Frey transport benchmark must be inhabited.** A full Fermat counterexample package is inconsistent in the completed development, so global search could derive arbitrary coefficient claims by contradiction. Fiber extracts the consistent hypotheses `a congruent 3 mod4`, `b even`, and odd `p >= 4`. The concrete instance `(3,2,5)` satisfies them. They prove `4 divides b^p-1-a^p` and `16 divides -a^p b^p` without Fermat's equation, coprimality, or nonzero `a,b,c`. This is both API generalization and evaluation control. See `fiber.tex:448`, `:463`, and `:958`.

3. **Exact division separates three operations.** `ExactQuotient(n,d)={q:Int | d*q=n}` makes sense even for `d=0`; the constructor intentionally requires `d != 0` and `d divides n` so that the selected quotient is unique. Any ring homomorphism preserves its balance equation. Turning that into division by the image of `d` additionally requires a unit in the destination. An integer nonzero fact alone is insufficient. Define the rational model by base change, then characterize its rational coefficients; for existing code supply compatibility with the original separate definition. See `fiber.tex:474` and `:500`.

4. **Measure, parameter, and uniformity indices matter.** A dominated-convergence contract needs the same measure for measurable integrands, a common integrable majorant, and convergence. The phase `exp(i*t*x)` has norm one, so a probability measure supplies a constant majorant. This does not require independence of the coordinate variables. For countably many `n`, separate conull sets can be intersected; uncountably many real parameters cannot be silently treated the same way. A self-contained negative example for the unified report: under Lebesgue measure on `[0,1]`, for each `t` the assertion `x != t` holds almost everywhere in `x`, but no `x` satisfies it for every `t`. See `fiber.tex:424`, `:535`, and `:555`.

5. **Quantitative contracts compose, not just exact identities.** For bounded coordinates, `X_n=sum_{j<n} omega_j/2^(j+1)` and `X` its infinite sum satisfy `0 <= X-X_n <= 2^-n`. Centering by `delta_n=2^(-n-1)` gives `|X_n+delta_n-X| <= delta_n`. The Lipschitz estimate on complex phases and probability mass one yield characteristic-function error at most `min(2, |t|*delta_n)`, hence uniform convergence on bounded frequency intervals. This is not automatically uniform CDF convergence. The paper proof is valid under the stated hypotheses; the Python companion checks only finite endpoint/midpoint instances of the coupling inequality, not complex integration or infinite sums. See `fiber.tex:574` and `:599`, and `tools/check_examples.py:232`.

6. **Contracts can constrain holes before enumeration finishes.** In a sketch `append(h(xs), xs)`, demanding output length equal to input length forces `length(h(xs))=0`. This offers useful synthesis pruning before a concrete candidate exists. But failure of one sufficient decomposition does not refute the candidate, and a counterexample to one completion does not eliminate every possible completion. Fiber explicitly permits heuristic pruning in an incomplete search, reserving stronger absence claims for proved exclusions or an adequate complete fragment. This avoids requiring a proof for every scheduling heuristic while keeping result soundness exact. See `fiber.tex:337`, `:651`, and `:662`.

7. **Behavioral specifications have their own precision.** Length and sortedness alone permit a sorted list of zeros; set equality forgets multiplicity. Sortedness plus permutation specifies sorting under a linear order and entails idempotence. Key-based sorting needs an additional stability clause because equal keys can correspond to distinct records. See `fiber.tex:635`.

8. **Five evaluation conditions improve causal attribution.** Fiber separates existing Lean (L0), shared libraries (L1), shared providers (L2), refinement elaboration within Lean (L3), and the additional surface/document view (F). Basalt and Gneiss use four conditions that combine more of the final layer. The fifth arm is worthwhile: an effective elaborator need not imply that a standalone source syntax helps. No additive independence assumption is made. See `fiber.tex:940` and `:1009`.

Fiber's finite model has explicit arity, degree, term-count, coefficient-size, and multiplication-work limits. It evaluates examples not only over integers but also modulo four and dual numbers, useful controls against accidental field assumptions. These still do not establish universal implementation soundness. The input-size limits are not a fully hardened parser: raw coefficients may combine before the final bit-size check, and not every raw processing cost is bounded. The article expressly disclaims a hardened service. Several negative-example checks are arithmetic stand-ins (`0 != 2`, for example), not execution of the corresponding frontend rejection. See `fiber.tex:1079`, `tools/check_examples.py:31`, `:55`, `:139`, and `:236`.

## Gneiss: claims and evaluation

1. **Prefix causality licenses finite presentation.** For `R^N`, agreement of inputs below `N` must imply agreement of outputs below `N`. Define the finite action by projecting after applying the operator to a zero-extended vector. Causality gives `pi_N T = T_N pi_N`; linearity gives a finite square matrix. For causal linear `S,T` over a commutative ring, `S T = id` implies `S_N T_N = I` for every `N`. Finite square matrices over a commutative ring are directly finite, hence `T_N S_N=I`. Choosing `N=k+1` proves each coordinate of `T S=id`. This is a useful theorem-backed representation capability, not an unrestricted equivalence of infinite and finite objects. See `docs/round-3/ideas/gneiss/gneiss.tex:873` and `:897`.

2. **The counterexample isolates the behavioral prerequisite.** The right shift `S` and left shift `D` satisfy `D S=id`, while `S D` zeroes the first coordinate. Both are linear, but `D` is not prefix causal. Thus an automatic finite-section method must request the causality/presentation contract, not only linearity. The paper proof is mathematically sound; the companion checks selected binomial matrices and one shift observation, not the universal theorem. See `gneiss.tex:925`, `:936`, and `contract_model.py:225`.

3. **Properties belong to chosen FLT witnesses.** A selected positive squarefree level provides nonzeroness and exclusion of prime squares/cubes. A switch curve `W'`, by contrast, is new data with a specified trace-congruence relation to `W`; it is not equality of the curves. The order `W'`, then its level `N`, then transfer at that `N` must remain dependent. This helps separate useful automatic proof propagation from unauthorized witness replacement. See `gneiss.tex:1046` and `:1073`.

4. **Three hole kinds sharpen language design.** Proof holes have fixed propositions; delegated object holes permit values satisfying frozen relations; unresolved meanings include structures/domains/branches and must be settled before proof search. Unresolved guards are typed continuations, never facts inserted into an accepted index. These are clear engineering requirements for a refinement service. See `gneiss.tex:462` and `:569`.

5. **Existing executable-program verification is an implementation neighbor.** Gneiss explicitly points to Lean's `mvcgen` and adequacy-based monadic extension path, instead of proposing another imperative verification logic. That point is an attributed source recommendation; this lane did not inspect or execute `mvcgen` itself. Mathematical observation and provider timeout remain separate from semantics of the program being verified. See `gneiss.tex:743` and `:1829`.

6. **A narrower checker is a real prototype choice.** Gneiss specifies dense univariate coefficient sequences, trimming zeros and checking ideal combinations. Basalt/Fiber start with sparse multivariate integer polynomials. Both approaches can have sound denotation into arbitrary commutative rings, but the workload coverage and implementation cost differ. Do not count the dense checker as completed multivariate support. Gneiss explicitly defers the atom vector and symbolic-index issues. See `gneiss.tex:1155`, `:1181`, and `:1224`.

7. **The Python acceptance model is deliberately relative.** It recognizes a closed small rule vocabulary, compares exact advertised conclusions, and allows only backward dependencies. Its initial assumptions are trusted, anchors are strings/tuples, and abstract rule soundness is assumed in the metatheorem. This tests assembly discipline, not truth of arbitrary premises or authenticity of Lean terms. See `gneiss.tex:1634`, `:1657`, and `contract_model.py:33`–`:77`.

One finite-test weakness should survive synthesis: `test_frey_missing_oddness` uses `(a,b,p)=(3,2,2)`, which also violates the lower bound `p>=4`. It shows a bad case but does not isolate oddness. Fiber's `(3,2,4)` does isolate oddness and is the preferred negative neighbor. See `gneiss/contract_model.py:222` and `fiber/fiber.tex:533`.

## Shared conclusions, real differences, and limits

The ten requested dimensions are encoded in `../evidence/basalt-fiber-gneiss/convergence.json`, with three reports by ten dimensions and one to three exact anchors per cell. All thirty cells are explicit in these three reports. This broad agreement should not swamp the differences above, and should not be sold as independent empirical confirmation: all proposals respond to the same revised syntheses, source repositories, and task framing.

The most consequential remaining choices are not logical disagreements:

- **First workload:** Basalt wants algebraic map/diagram relationships; Fiber exact quotient transport and synthesis constraints; Gneiss finite observation and witness-property flow. These can become separately owned experiments using one shared acceptance protocol.
- **Checker representation:** Dense univariate minimizes the first proof; sparse multivariate addresses a wider intended CAS workload. The choice should be justified by the first sealed evaluation family, not by a broad consensus cell.
- **When to add synthesis constraints:** Fiber emphasizes backward constraints earlier than the other two, but still starts with accepted candidates plus universal proofs before a generalized engine redesign. Basalt supplies the most concrete restricted abstract-interpretation theorem.
- **Surface versus elaborator:** Fiber's fifth evaluation condition can tell whether an elaboration extension succeeds while the extra syntax fails. A common four-arm comparison cannot isolate those two effects as cleanly.
- **Proof fidelity versus explanation:** All require the selected method contract and checked intermediate assertions. None proves a minimal, indispensable, or unique explanation; Fiber says this especially clearly at `fiber.tex:843`.

All three warn against counting old revised reports as untouched independent votes; against interpreting test counts as theorem counts; against granting mathematical authority to provider status; and against calling already inspected development files held-out material. All acknowledge that the prior iteration's complete Lean checker gate remains open.

README integrity inventories name `MANIFEST.sha256` or `SHA256SUMS`, but those checksum files are absent from these three imported source packages. The new reproduction receipt therefore records the actual 29-file input inventory and fresh SHA-256 values; it does not claim to have validated unavailable author manifests. This is an artifact inventory issue, not a mathematical defect.

## Answers to the previous iteration's questions

Source answer blocks: `basalt.tex:2094`–`:2130` (sixteen question families), `fiber.tex:1014`–`:1036` (seven grouped responses), and `gneiss.tex:1783`–`:1815` (explicit R1–R10 plus first-synthesis topics).

| Previous question family | Basalt | Fiber | Gneiss |
|---|---|---|---|
| R1: first checker/denotation | Direct denotation of sparse multivariate integer data; normalization, convolution, equality reflection and original-target bridge | Same broad checker; exact-quotient frontend and non-vacuous Frey transport in parallel | Dense coefficient-list implementation first; prove arithmetic denotation and reification |
| R2: existing bounded tactics | Pinned proof-producing controls; no negative-membership inference | Same, with actual workload/tactic comparisons | Explicit bounded `grobner` contract, no assumed certificate-export API |
| R3: workspace state | Derived index into actual Lean terms/proofs, plus roles/evidence | Contexts/snapshots remain primary; contract and hole constraints are added | Only request/dependency/display/replay metadata that enables a new operation |
| R4: partiality | Preserve total imported operations; explicitly selected partial packages | Same; partial extension is a new object with a bridge | Same; total and partial equation solution sets differ |
| R5: first packages | Ideal maps/quotient observations, then CDF and diagram transport | Same-carrier properties/exact quotients, then measure/locality interfaces | Local properties/algebra, then locality and finite sections |
| R6: execution threshold | Trust permission first, performance choice second; no universal threshold | Measure actual checker, representations and execution routes | No numerical threshold before actual workload measurements |
| R7: upgrade policy | Fresh destination receipts, actual transitive dependencies | Same, with meaningful statement/structure comparison | Same; historical axiom-name blacklist is insufficient |
| R8: Leant | Provider-law proofs, candidate denotation, concrete counterexample realization | Candidate plus behavior proof, then restricted backwards constraints | Measure implication composition, witness assembly and relation transfer separately from lookup |
| R9: mutation suite | Positive/negative pairs and explicit weaker alternatives; only finite subset executed | 24-row focused backlog, finite neighbors labeled; no full frontend pass claim | 20-row focused backlog, model/integration categories distinguished |
| R10: next campaign | A few concrete library/elaboration gates, no speculative schedule | Lean package/constraints before another broad grammar | A few implementations with different experimental goals instead of another set of architectural renamings |

All three also answer the first synthesis's delegation/display/reuse questions: a frozen relational specification authorizes selecting a witness; meaning-bearing conditions should be visible; actual entailment and context correspondence authorize evidence reuse. Proofs of the same proposition often coexist, whereas conflicting witnesses/maps/structures require semantic reconciliation.

## Questions to carry into the next iteration

1. Which first workflow can exhibit a real benefit of expected-property elaboration over an equally equipped Lean tactic interface: exact quotient, ideal map, finite section, or measure-indexed calculation?
2. What is the minimal mathematical semantics of the property registry: immutable proof handles plus role annotations, and which existing Lean APIs provide everything else?
3. Can one restricted Leant grammar produce a Lean-checked denotation and universal behavior theorem, and concrete refutations with realizable inputs, before generalized prefix pruning is attempted?
4. Which classes of heuristic pruning may remain operationally incomplete, and what extra theorem is needed when the tool advertises exhaustive sketch elimination?
5. Should the first polynomial checker be dense univariate or sparse multivariate, and which actual consumer makes that complexity worthwhile?
6. Can the same demand-transfer interface usefully serve derivative jets, quotient towers, finite sections, and numerical Lipschitz bounds without becoming a cumbersome universal abstraction?
7. How should the default display communicate telescope order, measure identity, common conull sets, and changed structure data while keeping a mathematician's conceptual steps readable?
8. Will the experiment separate the effect of refinement elaboration from the effect of a new source syntax, as Fiber's five-arm design permits?
9. What controls prevent a mathematically valid shortcut through inconsistent hypotheses from contaminating a method-specific benchmark?
10. Which proof-routing differences can be erased by same-carrier coherence, and which selected witnesses/representation maps must survive as explicit data choices?

## Fresh execution and Lean handoff

`../evidence/basalt-fiber-gneiss/reproduce.py` was inspected and run with Python 3.14.4. It copied only the three companion programs into isolated retained output directories and invoked each with `-B`. All exited zero: Basalt 24 test methods, Fiber 1,298 finite checks in 31 groups, Gneiss 32 test methods. These counts have different denominators and must not be summed into an efficacy score. Before/after SHA-256 inventories confirm that all 29 source-package files were unchanged. Commands, timings, code-copy hashes, stdout/stderr hashes, and generated receipts are retained in `reproduction.json`.

All three Lean companions are short core-only files suitable for serial compilation by the root agent; this lane did not invoke Lean or Lake. Static review found ordinary constructions, no claimed frontend, and no actual polynomial checker. Basalt includes weakening/intersection, dependent composition/consequence, observation adequacy, and sufficient-demand composition. Fiber includes the analogous core and a generic `certificate_bridge` that explicitly **assumes** checker soundness and execution. Gneiss includes extrinsic property/contract structures, a conditional result, respectfulness, and complete-solution equivalence. Successful compilation would validate exactly those declarations; it would not close the missing checker or the paper's larger mathematical examples.

### Independent audit after the root's Lean runs

The root subsequently compiled all seven supplied Lean source files unchanged under Lean 4.32.0, commit `8c9756b28d64dab099da31a4c09229a9e6a2ef35`. I independently read the root-owned sources, logs, and receipts and verified their SHA-256 bindings without launching Lean. The reproduction script and resulting read-only audit are `../evidence/basalt-fiber-gneiss/audit_lean_evidence.py` and `lean-evidence-review.json`.

| Proposal | Named `theorem` declarations in original | Unique declarations with axiom output |
|---|---:|---:|
| Basalt | 2 | 2 |
| Fiber | 3 | 3 |
| Gneiss | 2 | 2 |
| Karst | 12 | 11 |
| Moraine | 16 | 3 |
| Schist | 8 | 8 |
| Tephra | 6 | 3 |
| Total | 49 | 32 |

This count excludes named definitions, structures, generated declarations, and unnamed examples, although the whole files compiled. The axiom output has duplicate queries in some logs; unique declaration names are the proper denominator. Of the 32 queried declarations, 27 report no axioms. Five report only `propext`: Moraine's `LengthExpr.model_sound` and `LengthExpr.promote_model_spec`, and Schist's `AffineCertificate.eval_nf`, `check_sound`, and `original_target`. The remaining 17 named theorem declarations compiled but were not individually queried by these receipts. Do not say all 49 are axiom-free or that a sample audit was a whole-environment audit.

Schist's successful source is a substantive exception to a blanket claim that none of the reports supplies a checked reflective example. Its one-variable affine-natural syntax includes literals, a variable, addition, and scaling by a literal natural. It proves the actual slope/intercept normalization denotation; equality of those normal forms implies universal evaluation equality; `original_target` proves `3*(x+2)=3*x+6` via `check_sound` and a kernel-checkable `decide`; `corrupted_rejected` checks the `+7` alteration. See `docs/round-3/synthesis/evidence/lean/schist/SchistCore.lean:98`, `:111`, `:125`, and `:128`. This closes a narrow complete loop, with definitional reconstruction of a manually encoded target. It is not an arbitrary Lean-expression reifier, multivariate/ring polynomial checker, or frontend.

Moraine's compiled denotation theorem is also more than a generic contract wrapper. Its grammar over `List Nat` includes inputs, empty list, cons, append, reverse, and map-successor. `model_sound` proves exact structural length semantics for every grammar expression and actual list environment. `promote_model_spec` then transfers an independently supplied universal arithmetic model theorem to every concrete list input. See `docs/round-3/synthesis/evidence/lean/moraine/Contracts.lean:137`, `:166`, and `:177`. What remains missing is proved coefficient-vector normalization/decision, a bridge to the Python algorithm, and correspondence with actual Leant candidate syntax/provider laws. The theorem does not accept a finite sample or raw solver status as its universal premise.

The root's two new generic synthesis implications also have hash-bound exit-zero receipts and report no axioms. `refute_via_realization` makes concrete admissibility, realization and behavioral-preservation premises explicit. `reverse_via_observations` requires onto/separating observations, commuting maps, and a local inverse-reversal theorem. The latter does not itself prove direct finiteness of matrix algebras or instantiate Gneiss's sequence theorem; that larger mathematical argument remains a paper proof unless separately formalized.
