# Parallel round-four synthesis: concepts and integration review

Reviewed the entire 545-line `docs/round-4/unified_report/unified_report.tex`, its entire 80-line `appendix.tex`, all five included table fragments, the README, and the two new Lean sources statically. Compared the mathematical, architectural, implementation, and evaluation sections against our current `docs/round-4/synthesis/unified-report.tex`. No Lean, Python companion, PDF, or Git operation was performed for this review. The only written artifact is this memo.

The parallel report, **Nine Frontiers**, entered through main at `c92ef058979fcb8f6c11030ac9ed80c64186e0f8`. It is a **secondary synthesis of the same nine proposals**, not a tenth independently developed proposal. Its convergence counts, execution claims, and editorial recommendations must retain that status. Its copied historical logs are not this lane's fresh executions.

Snapshot hashes used for the comparison:

- Parallel main TeX: `92932d4a0144b67fe65a4d266f9195a3f733768dbe4adc28c6ad3295956e028e`.
- Parallel appendix TeX: `211fe44bc2ee197e23316c868c410d4a0e860e141db3c2a5f790d6051e0504ab`.
- Our main TeX before integration: `e0d9cc682edb6c822b3f760c4bb9a2b060b730b4e29149659ba243bcab231deb` (1,556 lines).

For concise but exact anchors below:

- **P** = `docs/round-4/unified_report/unified_report.tex`.
- **PA** = `docs/round-4/unified_report/appendix.tex`.
- **PM** = `docs/round-4/unified_report/matrix_rows.tex`.
- **O** = `docs/round-4/synthesis/unified-report.tex`, at the pre-integration hash above.
- **LI** = `docs/round-4/unified_report/experiments/lean/ListImage.lean`.
- **FR** = `docs/round-4/unified_report/experiments/lean/FreyRoutes.lean`.

Every locator of the form `P:484` therefore names a particular file and a nonblank one-based source line. Our locators will move after the root edits the report.

## Main judgment

Incorporate the concrete hand-instantiation specimen, a more explicit private proof transaction, and several sharper experimental questions. Most mathematical ideas highlighted by the peer already have self-contained treatments in our report: finite support semantics, two completeness flags, realizable frames, the rank bound, scope and transport, sharper Frey hypotheses, product-versus-logarithmic guards, weighted Fubini, inverse branches, CDF normalization, reopen, and matched Lean controls. Repeating those sections would add length without adding an argument.

The peer's strongest new contribution is a **specific implementation starting point**, not a replacement semantic architecture. Its prose frequently compresses genuinely different implementations into “nine engines of one specification.” Our existing distinctions between six antichain planners, Clover's typed first-proof grounding, Heather's behavioral model, and Rowan's diagnostic/semilinear system should remain intact.

## Recommended integrations, in priority order

### 1. Make the hand-instantiated routes a concrete acceptance specimen

**Peer:** P:386, P:484, P:502, P:505; FR:55, FR:68, FR:74, FR:81, FR:91, FR:98, FR:107. **Existing coverage:** O:1307–1310 and O:1472–1475 already require an actual mathematical registration, but do not point to this newly supplied artifact.

The valuable addition is that selected generic exports are now manually instantiated with actual arithmetic and cast theorems. This closes a real gap between an implication over anonymous propositions and a theorem about an integer numerator. It gives the next implementer a known target, explicit supplied rule terms, and two different sufficient routes. It does not implement theorem registration, goal extraction, premise inference, or source authoring.

Suggested integration after our first implementation gate:

> The parallel synthesis supplies a useful reference specimen: hand applications of Laurel, Bryony, and Sorrel's generic plans to actual Frey arithmetic. The next gate is to reproduce the appropriate theorem from a Lean goal: extract a bounded typed term pool, instantiate registered theorem constants after validating their types and argument roles, select a checked route, and reconstruct a proof at the original target. Compare the generated proof and retained residuals against the hand application; do not treat the existence of that hand application as an implemented registry.

Be precise about the results: FR:83, FR:92, and FR:99 prove **three second-coefficient rational-cast identities** through two Laurel routes and one Bryony route. FR:109 proves a **conjunction of first- and second-numerator divisibilities**, not a fourth cast identity. FR:42 supplies the `p ≥ 2` first-numerator helper. Our independently checked sharpening already exists at O:1243–1249, so the sharper bound itself is not a new contribution of this peer integration.

Bryony's intermediate `NumeratorExact` is interpreted as the same divisibility proposition, with the bridge supplied by `id` at FR:98–105. Sorrel similarly receives an already proved first-numerator divisibility at FR:112–116. These are legitimate manual interpretations of opaque atoms; they do not establish that the original Python strings carry these meanings automatically.

### 2. State the proof service's transaction explicitly

**Peer:** PM:18 (B9), PA:26, P:324. **Primary source:** `docs/round-4/ideas/Rowan/Rowan.tex:584–608`. **Existing coverage:** O:251–271 fixes meaning; O:1114–1137 defines requests/results; O:1289–1295 and O:1338–1343 require final target preservation. These imply much of the discipline, but do not describe the producer's mutation boundary concretely.

Suggested short addition to the request section:

> Resolve the mathematical request before invoking its proof producer. Run the producer in private elaboration state, with the original target and context protected. It may create candidate-local holes, construct authorized witnesses, and call providers. On return, reconstruct the exact candidate in the original context and check it against the original target before committing a fact. Neither rollback nor a request hash replaces this final check; the implementation must also prevent assignments from escaping into protected state.

This is a proposed interface invariant and transaction design, not an established Lean metaprogramming implementation. Rowan explicitly allows candidate-private data metavariables when a fixed existential or refinement specification authorizes witness construction (`Rowan.tex:577–582`). Avoid equating “sealed” with “closed term” or with “no holes anywhere in the candidate.”

### 3. Turn coverage reuse into a nontrivial amortization experiment

**Peer:** P:431, P:437, P:504. **Existing coverage:** O:1362–1376 already proposes caching domain certificates and measuring their costs separately. The added value is a falsifiable workload, not the reuse idea itself.

Suggested addition to the domain-certificate paragraph or question 6:

> Choose a guarded input domain whose realizable-image coverage requires a substantial argument. Measure that proof's development and maintenance cost, then compare many candidate checks sharing the domain against direct Lean proofs of the same candidate laws. Report the reuse count at which the shared domain proof pays for itself, including the cost of rebuilding it after a guard changes.

A tiny frame does not imply a cheap coverage proof. Keep the possibility that direct candidate proofs win. Also keep the distinction between a **sound span overapproximation** sufficient for positive affine reasoning and an **exact image with realizers** that can support source-level negative decisions. Our O:1375–1376 already makes that asymmetry correctly.

### 4. Test whether alternatives change author actions

**Peer:** P:322 and P:509. **Existing coverage:** O:1345–1360 separates the formal frontier from the work menu; O:1428–1430 measures first-proof and full-inventory cost; O:1479–1481 asks which completeness claim is worth paying for.

Suggested measurable extension:

> Compare a first sufficient route with an interface that can reveal alternative sufficient routes. Record how often the additional route changes the author's next action, avoids a difficult premise, or shortens repair after an edit. Include the cost and latency of producing alternatives. A complete antichain should remain an available specification for a declared finite fragment even if the interactive service usually returns one checked route with an explicit incomplete-inventory status.

Do not import P:322's claim that nothing is lost by substituting a route engine for an antichain engine. One derivation preserves proof sufficiency; it does not preserve minimal-support enumeration or coverage. Rowan's unresolved-leaf diagnostic is weaker still and cannot be treated as a sufficient route merely because its printed shape resembles a frontier. The existing cycle-plus-leaf probe at O:1043–1047 is material evidence against that flattening.

### 5. Make strict sealing versus role classification an empirical fork

**Peer:** P:324, P:507. **Existing coverage:** O:264–271 already preserves the two positions accurately. The useful addition is the next test.

Suggested question:

> On concrete staged elaborations, which legitimate author requests are rejected by a seal that forbids unresolved metavariables in the target and local declaration types/values? Can a role-based policy accept those cases while demonstrably preventing all assignments to meaning-bearing dependencies?

Record both rejected legitimate cases and nearby wrong-target mutations. Do not adopt the peer's unproved claim that role classification is inevitably “the eventual design.” A strict seal may remain adequate for the chosen interface. An authorized witness inside a fixed existential request is not a counterexample to strict sealing, as Rowan's construction explanation already makes clear.

### 6. Mechanize coverage independently, with a real certificate contract

**Peer:** P:438, P:485, P:503; Juniper is credited explicitly. **Existing coverage:** O:397–411 already states the coverage-checker conditions; O:1479–1485 discusses inference costs and grounding.

The incremental recommendation is a named deliverable: implement a Lean finite-profile certificate datatype and checker, prove its conditional soundness/coverage theorem, and feed it translated certificates from a shared fragment of the existing planners. Bind the original target, proposition/root interpretation, known and offered assumptions, allowed rules, and method policy. Keep independent derivation replay distinct from checking complete support coverage.

Do not promise “a few dozen” or “a hundred” lines, as P:438/P:503 do. The mathematical core may be small while representation, parsing, semantic registration, coverage enumeration, and target bridges dominate. An untrusted JSON decoder must produce values that are checked under the fixed request; importing JSON does not discharge that bridge.

Our report already records a successful bounded Fennel/Juniper differential experiment at O:1179–1188. The peer's blanket “nobody ran two engines against each other” at P:436 describes its nine-input review and should not overwrite this newer evidence. Extend the existing common-fragment experiment instead of presenting it as wholly unperformed.

### 7. Optional mathematical addition: formal polynomials versus polynomial functions

**Peer:** P:340, PM:40 (E6), PA:26. **Primary source:** `docs/round-4/ideas/Rowan/Rowan.tex:1416–1422`. **Existing coverage:** O:873–879 discusses ideal-membership certificates but does not state this example.

A concise self-contained addition would be:

> Over the field with two elements, the formal polynomial `X² − X` is nonzero, yet its value is zero at both field elements. Formal coefficient inequality therefore does not by itself refute equality of the induced functions on a fixed domain. A checker for functional equality needs the appropriate observation-domain theorem, just as the list-length checker does.

Explicitly identify this as a **higher-degree extension** of the admissibility lesson. It is not a counterexample to the affine-frame theorem, whose hypothesis class excludes the quadratic polynomial.

### 8. Optional evaluation refinement: a reading pilot before a surface implementation

**Peer:** P:488, P:508. **Existing coverage:** O:1407–1422 defines matched L0–L4 arms and a renderer control; O:1499–1501 asks about semantic comprehension.

The genuinely actionable addition is a small blinded reading pilot over compact statements and expanded checked statements before implementing more syntax. Ask participants to identify hypotheses, domains, and the distinction between conditional/incomplete/unsupported/refuted outputs. Include new zero-factor, mass-normalization, and discontinuous-branch cases. This is a comprehension pilot, not evidence of authoring productivity, parser acceptance, or a completed L3/L4 comparison.

### 9. Coordinate next-round artifacts without a novelty vote

**Peer:** P:497 proposes distinct deliverables. This can improve the next iteration: assign a Lean registry, a coverage checker, a domain theorem, a reading pilot, and cross-implementation adapters to separate bounded lanes, all sharing frozen interfaces and positive/negative fixtures.

Do not import P:510's stopping rule based on adding a “unanimous row.” Agreement is neither novelty nor utility, and a lone counterexample can invalidate a shared design. Keep our existing predeclared empirical interpretations at O:1452–1464. A useful campaign can also stop a bad design on a precise mathematical finding even when no new compiler artifact is needed.

## Scope of the peer's two new Lean files

This is a **static assessment**, for the root's fresh compiler/axiom audit to confirm separately.

### ListImage

- LI:10–19 proves `(∃ xs : List α, xs.length = n) ↔ n = 0 ∨ Nonempty α`. This is a useful exact image statement. `Nonempty α` is a proposition and does not impose an `Inhabited` instance.
- LI:23–28 proves a sufficient one-point affine equality criterion on `List Empty` from equality of constants. It does not state the converse in that theorem.
- LI:32–35 proves an integer-coefficient affine law for **all natural numbers** from agreement at zero and one. Despite the comment, this theorem has no element type, list parameter, inhabitance premise, or source-realization statement. Combine it with `length_image` to obtain the intended realizable list interpretation.
- LI:40–51 proves an iff criterion for the diagonal observation of a `List Nat` and its reversal.
- LI:55, LI:57, and LI:59 are three examples: an independent-length witness, a reflexive list expression, and failure of a corresponding independent-input universal equality.

There are **four named theorems and three examples**, not four independently formalized list-domain frame theorems. There is no even-length frame, no proof for arbitrary numbers of independent lists, no general frame datatype/checker, and no interpreter/denotation induction for Heather's grammar. P:251's reference to “all four” checks, P:403's “four frames,” and the README:22 phrasing need this qualification. The image characterization is itself valuable without inflating its role.

### FreyRoutes

- FR:16, FR:23, FR:30, FR:42, FR:49: five arithmetic helper theorems.
- FR:56, FR:62, FR:69, FR:75: four generic route theorems.
- FR:83, FR:92, FR:99: three actual cast-identity applications.
- FR:109: one actual conjunction of divisibilities.
- FR:119–126: seven concrete examples, including `(3,2,3)` as positive for the sharper first numerator and negative for the second.
- FR:128–132: five explicit axiom queries; these query selected declarations, not all thirteen named theorems individually.

The introductory comment FR:3–10 and P:409 overgeneralize the nine exporters and call all applications coefficient identities. Preserve the useful actual statements and the manual status. The arithmetic theorem remains parameterized by stated mathematical hypotheses; “unconditional” here can only mean that no opaque rule propositions remain, not that all hypotheses disappeared.

## Material claims not to carry across unchanged

| Peer source | Problem | Correct boundary for incorporation |
|---|---|---|
| P:99, P:179, P:364, P:383, P:514 | “All nine” compute the same proof frontiers and export generic Lean. Rowan has no Lean source; Clover/Heather include concrete mathematics; Rowan's diagnostics do not have antichain sufficiency. | Keep our nine implementation classifications and declared overlapping fragments. |
| P:144, P:348, P:425 | Fourteen of twenty files are called generic implications. | The source inventory is **twelve nonempty generic-export files plus one empty cycle module**, two Clover concrete files, and five Heather concrete files, totaling twenty. Our existing per-package accepted-declaration table O:1216–1233 is more precise. |
| P:163 | Tensor representing algebra is finite/free “only if every factor is.” | The cited construction uses finite/free factors as sufficient hypotheses. No necessity direction has been established. In general tensor products can collapse, e.g. tensoring with a zero algebra; do not silently reverse the implication. |
| P:249 versus P:337 | Affine-hull dimension `r` is identified with the number of required test points. | A full `r`-dimensional affine hypothesis class needs `r+1` affinely independent evaluations in the worst case; lifted-span rank is `r+1`. Our O:629–637 states the needed qualification. |
| P:251, P:403, P:459 and frame table P:470/P:473 | The prose suggests all displayed domain cases were checked by ListImage, while the table labels even/empty-admissible cases “no.” | Describe the exact four named statements above; a table criterion may be proved on paper without this file proving it. |
| P:283; PM:44 (F1) | “Nothing” from unfinished work can enter the index before every residual is discharged. | It cannot enter as a proof of the original unconditional target. A proved conditional theorem or already proved component may be indexed with its exact type and status. P:183 itself gives the more accurate restriction. |
| P:290; PM:60 (G10) | A seeded cycle yields “only” a conditional route. | A prospective seed produces a conditional route; a seed already proved in the current context can yield a closed result relative to that context. Seedless cycles cannot produce evidence. |
| P:322 | First-route replacement loses nothing from the antichain specification. | It loses alternative and coverage information while retaining sufficiency only when the returned route has an actual continuation/proof. |
| P:326 | Scalar-domain differences matter “only” when the observation codomain has torsion. | Distinguish the observation lattice, the scalar domain used for coverage, and the target additive group of the affine map. Integer-span and rational-span hypotheses differ; division is safe only with the relevant torsion-freeness/vector-space justification. Our O:658–663 is safer. |
| P:406, P:445, bibliography P:529 | Local branch/tracking status is promoted to “never pushed” and “private revision.” | State the inspected immutable local source and limitations of the peer's remote lookup. Being ahead of one tracking branch does not prove a commit exists nowhere remotely. Our newer Leant receipt and static findings must not be replaced by a historical live-HEAD claim. |
| P:414, P:423 | The calculus is “finished,” proofs interchangeable, remaining work merely formalization. | The fixed finite theorem is mature. Different root identities, policies, result kinds, certificate formats, dependent grounding, and source bridges remain design and engineering choices. |
| P:420 | No report claimed more than it had. | Our Sorrel partial-family and route-selection findings and other reproduced interface failures warrant the more granular assessments already present. Do not replace them with a blanket endorsement. |
| P:425 | Generic implications “prove nothing,” their compilation confirms exporters, and recompilation should cease. | They prove generic implications and check these finite emitted files. They do not connect opaque atom names to mathematics or prove arbitrary exporter correctness. Changed emitters and exact emitted artifacts still require validation. |
| P:427 versus PA:5/PA:26 | No shipped parser accepts any proposed source surface. | Rich proposed notation remains unimplemented, but Clover, Alder, Rowan, and others do have actual small parsers. Cite supported grammar separately from illustrations. |
| P:436, P:501 | All formats differ trivially and every cross-engine disagreement is a bug. | Differential checking needs explicit common semantics and adapters. Native policy, named roots, offered-goal treatment, and diagnostic/result kinds can intentionally differ. Our Fennel/Juniper comparison already makes the restriction concrete. |
| P:459 | A guard lowers observation dimension and the number of counterexamples. | A guard can lower dimension, preserve it, shift an affine base, or make the domain empty. Even lengths and positive lengths retain one-dimensional affine span. The theorem bounds distinguishing tests, not the cardinality of all possible counterexamples. |
| P:456, P:259, PM:53/PM:59 | Consensus and executed-mutation marks suggest uniform semantics or common test coverage. | Treat the 101-row and 52-family tables as editorial navigation. Do not add their cells as independent votes, novelty measurements, or a shared executed suite. A broad mutation name does not establish the same observation in every engine. |

## Appendix assessment and attribution

The report cards at PA:5–29 are useful routing summaries and largely align with our profiles. They explicitly identify Clover's concrete rules and Rowan's absence of Lean, which helps correct several main-text generalizations. The source map at PA:60–80 is useful as an attributed map of what each author said they read, not independent confirmation of every historical source inspection.

The negative-suite appendix distinguishes executed, tabulated, and prose cases at PA:32. Preserve that distinction if borrowing a family. Our existing selected paired mutations already cover most of the useful families; no need to reproduce fifty-two rows merely to claim coverage. New mathematical neighbors can be selected for a root-owned kernel task, but this conceptual review does not claim they have been compiled.

PA:58 explicitly reports cold starts and concurrent Mathlib work. Its elapsed times must not become comparative engine performance figures. PA:49–56 describes retained logs and scratch copies, while our source-hash receipts and fresh serial runs provide a different evidence boundary. Keep the peer records as secondary historical evidence and name any new reproduction separately.

## Concise incorporation package

The best change is approximately five short prose additions plus strengthened questions, not another broad section:

1. Add a secondary-synthesis provenance paragraph and the two new Lean specimens with exact statement-level scope.
2. Add the private resolve/discharge/check-and-commit boundary to the existing request contract.
3. Name the manual Frey application as the reference for the Lean-goal-to-registry gate.
4. Add the nontrivial coverage amortization and alternative-route utility experiments to the already existing cache/work-menu sections.
5. Optionally add the finite-field polynomial-function example to certified computation.
6. Refine next questions to request strict-seal counterexamples, a mechanically checked coverage certificate, a common-fragment differential adapter, and the actual Lean-to-planner direction.

Retain our self-contained mathematics, implementation distinctions, existing fresh reproductions, explicit negative probes, and matched stopping rules. The peer supplies a useful starting artifact and sharper priorities; it does not establish a new shared semantic theorem or justify erasing meaningful disagreements.
