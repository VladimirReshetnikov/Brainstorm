# Comparative review: Accord, Cadence, and Concord (round 2)

This memo covers all substantive TeX in the three reports, their full Python companions, README/build instructions, and source/validation registers. Source checkout: `f333ff6cefc8b1f5c9aae79613d10ef95a7ba928`. Citations below use each report's **printed section number and one-based TeX source lines**. The originals were read-only. No repository build or PDF build/review was performed for this memo. A later, separately authorized focused Lean check is documented in the final addendum; the report comparison and Python evidence remain distinct from it.

## Overall assessment

The shared advance is a shift from proof holes to **specified mathematical computations on stable objects**. An answer can be an exact identity, conditional theorem, witness, complete solution description, finite observation, or enclosure; a valid answer of one kind does not automatically satisfy another kind of request. The reports propose one checked interface for theorem application, certificate checking, and justified execution of verified algorithms. They also treat definitions as ordinary mathematical anchors equipped with proved computational observations.

These are three closely aligned design specifications, not three independent demonstrations that the architecture works. All three explicitly read the same two round-1 syntheses rather than independently rereading the nine originals, and selected the same three ProveIt modules at the same reported public revision. Their shared examples and recommendations therefore have strong common input ancestry. They also cite existing verified-computation work as precedent, rather than claiming historical novelty. Concord makes that qualification especially explicit: “new” is relative to the two syntheses (§1.2, 118–131).

The most useful separation for a unified report is:

| Report | Distinctive emphasis | Exact first implementation slice | What this slice discriminates |
|---|---|---|---|
| Accord | A certified worksheet of mathematical transactions; broad answer taxonomy and display guarantees | Annotated finite reindexing plus polynomial certificate, replayed with discovery disabled (§17.1, 1588–1600) | Whether a small existing-theorem/certificate path supplies exact target, guards, source links, failure explanation and replay without a large parser |
| Cadence | Relation-indexed transformations; parameter specialization, bounded coherence policy, numerical observations | A claim/relation record, theorem wrapper, and proved polynomial-combination checker; first user task is complete all-parameter solving of \(ax=b\) (§15.1, 1553–1570) | Whether guards, degeneracy, set-valued outputs, coverage and exact retained evidence survive an end-to-end interaction |
| Concord | Demand-directed contracted queries; finite evidence about arbitrary infinite objects | Abel finite-jet residual certificate, paired with reindexing, local derivative and positive-root tasks (§17.1, 960–977) | Whether query-directed finite representations actually avoid solving or materializing a stronger problem while preserving the original object |

These are competing prioritizations, not incompatible semantic cores. Combining all three initial slices into one “minimal” milestone would obscure the actual implementation choice and inflate the first experiment.

## Evidence and provenance

The reported source boundaries are consistent and carefully qualified:

- Accord §2.1, 181–198 and Appendix C, 1836–1869.
- Cadence §1.1, 164–192 and Appendix D, 1945–1966.
- Concord §2.1, 142–157 and Appendix C, 1096–1102.

All three report Brainstorm `494be9d5ab41a5ae219fc6f800e6aee3c93bce39`, ProveIt `24ce8bd743eaab64a91ce90725ea00f498d319d2`, and Leant `3a40904be8a410d832d9ab6900b3d3e7b425eccb`. They distinguish those public committed sources from the newer ProveIt checkout and dirty Leant files described by the syntheses. This memo verifies what their source registers state, not those remote revisions' present availability or runtime behavior.

Direct Leant readings differ: Accord's register lists README, Verification and Fragment, while its exact-edit concern is attributed to the syntheses; Cadence additionally reads Engine and Main; Concord reads Fragment and Main. Do not describe all three as fresh independent executions of the suggestion path.

Fresh companion execution used Python 3.14.4 at `C:\Users\vresh\AppData\Local\Python\pythoncore-3.14-64\python.exe`, with `PYTHONDONTWRITEBYTECODE=1` and `-B`. Each exited 0. All output is isolated under `docs/round-2/synthesis/evidence/accord-cadence-concord`.

| Companion | Fresh result and counting unit | What was actually exercised | What remains untested |
|---|---|---|---|
| Accord `certificate_lab.py` | 25 **unittest methods**, 0 failures/errors | Sparse rational-polynomial combination identities and corruptions; exact signs/principal roots in \(\mathbb Q(\sqrt2)\); enumerated bijections; finite binomial/telescoping samples; subtraction/division/jet counterexamples | No parsing, Lean checker, symbolic bijection proof, general denesting engine, protocol replay, semantic seal or security boundary |
| Cadence `certificate_exhibits.py` | 267 **recorded Boolean checks** | 6 polynomial checks; 60 sampled linear-solution equivalences; 190 Abel coefficient comparisons (10 degrees at 19 parameter pairs, three dual-number pairs); 3 guards/nonfield/jet controls; 6 Lambert numerator/control checks; 2 bracket checks | No all-parameter solver proof, universal series theorem, real derivative proof, interval existence/uniqueness proof, host adapter or parser |
| Concord `checks.py` | 459 **recorded finite checks** | 441 binomial instances; 5 residual coefficient identities; 4 Abel coefficient identities as rational polynomials in symbolic \(a,x\); 7 negative arithmetic neighbors; 2 rational square comparisons | No formal residual theorem, complete solver, real root semantics, parser, replay protocol or Lean verification |

Accord's loops include 700 binomial-orthogonality instances, 216 binomial-product instances, 42 enumerated bijections, and 101 telescoping instances, but these are inside individual unittest methods. Its Appendix B specifies **26 prospective adversarial language tests** (1791–1834); those are not the 25 executed methods (§18, 1675–1703). Do not aggregate any report's count with another's as if it measured capability or coverage.

Cadence's 190 comparisons test numerical rational or dual-number parameter instances; Concord's four positive-degree comparisons are polynomial identities with symbolic parameters but only four degrees. Those are different strengths along different axes. Cadence's nilpotent control is valuable evidence against an accidentally field-only arithmetic implementation, but three dual-number pairs do not prove generality over every rational algebra. Concord's 441-entry binomial grid dominates its total. Accord's polynomial representation validates monomial arity and nonnegative integer exponents at construction, but its dataclass can also be constructed directly and its bijection checker accepts arbitrary Python callables: the file expressly disclaims a hostile-input boundary. Cadence calls the multiplier-list-length mismatch an “arity rejection”; it is not validation of a multivariate symbol context.

Source implementations and count locations:

- Accord: polynomial construction/checker Python 20–92; enumerated bijection 95–100; quadratic-field sign/branch checker 103–132; tests 148–216; result generation 219–232.
- Cadence: dual numbers 19–64; polynomial-combination checker 104–113; jets/exponential 116–150; sampled solver 153–161; rational bracket computation 164–191; counts and exhibits 194–278.
- Concord: sparse polynomial and jet arithmetic 18–72; records/counting 78–149; output boundary 151–160.

The original article status statements also explicitly deny implementation/formalization: Accord 79–83 and §18; Cadence 81–84 and §17, 1731–1743; Concord 83, §7.2, 491–493 and Appendix C, 1098–1100. All universal derivations discussed next are paper mathematics, sometimes applying cited existing theorems.

## Eight-commitment crosswalk

The machine-readable version is `../evidence/accord-cadence-concord/crosswalk.json`. Every cell below denotes an **explicit design commitment**, not implemented capability. V is most concrete on original-expression reification in Accord; Cadence and Concord state exact execution/refinement/adapter requirements but do not supply a full reifier. E includes measurable outcomes and qualitative stopping rules; Cadence and Concord explicitly defer numerical usability thresholds until a pilot.

| Commitment | Accord sections / TeX lines | Cadence sections / TeX lines | Concord sections / TeX lines |
|---|---|---|---|
| R: exact result relation/guarantee | §6.1 519–549; §6.2 551–574 | §2.3 286–301; §4.1 403–432 | §4.1 252–280; §4.4 311–318 |
| O: stable objects, certified observations | §§5.1–5.2 409–447; §5.5 500–515 | §5.1 507–543; §5.4 583–614 | §§6.1–6.2 393–413; §6.5 447–452 |
| G: scoped guards and nonstrengthening composition | §§8.1–8.3 775–839 | §§4.2–4.3 434–466; §7.3 846–872; §13.2 1436–1447 | §4.2 283–296; §6.3 415–429; §14.4 909–914 |
| V: algorithm/checker theorem versus execution/reification | §§7.1–7.2 612–666 | §§6.2–6.3 653–690; §12.2 1325–1341 | §§5.1–5.3 322–372 |
| D: ordinary theorem/definition packages, separate policy | §5.1 409–420; §14.1 1410–1426 | §5.1 507–529; §5.5 622–632; §4.4 468–491 | §4.3 298–309; §6.1 393–398; §14.3 887–907 |
| L: exact provider target, displayed-edit replay, honest negatives | §13.2 1319–1346; §§13.4–13.5 1373–1406 | §§12.2–12.4 1325–1395 | §12.1 800–805; §12.3 830–835; §§13.2–13.3 855–869 |
| P: retained evidence/replay publication boundary | §§14.3–14.4 1448–1482 | §§14.1–14.2 1491–1530 | §§15.1–15.3 918–935 |
| E: equally equipped baselines, negative neighbors, stopping | §17.1 1588–1600; §§17.3–17.5 1621–1673 | §§16.1–16.4 1611–1709 | §§17.1–17.5 960–1023 |

## Distinctive contributions worth retaining

### Accord: a worksheet with explicit result-display fidelity

Accord distinguishes Object, Assertion, Calculation, Scope and Plan nodes, with Presentation as a derived interface (§3.2, 286–317). That is more useful than merely renaming tactics: it distinguishes a claim whose proof is missing from a calculation whose output is missing and a choice whose intended data is not determined by its type (§4.2, 365–381).

It has the clearest three-way reason policy: `by method M` constrains the construction, `prefer M` is a soft strategy preference, and `by search` allows any proof within the stated search policy (§4.3, 383–394). Local-premise, global-library and axiom restrictions remain separate. This can resolve a real product tension: exploration benefits from opportunistic automation while a published named move makes a stronger explanatory promise.

The proposed fifth publication check is a valuable extension of the round-1 four-part boundary: **the rendered answer must preserve its certified exactness, conditions and completeness** (§14.3, 1448–1463). A checked enclosure displayed as equality, or root witnesses rendered as “all roots,” can mislead even when the underlying proof terms are individually valid. This is best understood as an explicit computational instance of document/statement fidelity, not a new foundational correctness theorem.

Accord gives a fully spelled-out guarded observation composition proposition (§8.2, 794–826). Existing \(V(a,r)\), producer evidence \(G(a,r)\to W(r,s)\), and a bridge
\(V(a,r)\land W(r,s)\land H(a,r,s)\to Z(o(a),q(s))\)
yield \((G\land H)\to Z(o(a),q(s))\). Its proof is elementary implication composition; the useful contribution is the interface discipline, especially that the consumer guard concerns the **actual retained** \(s\). The dependent generalization must use ordered telescopes, not a bag of guard strings.

Its shared-metavariable transaction discussion (§8.5, 858–869) is also concrete. Independently valid-looking subresults may commit incompatible assignments to the same chosen root/parameter. A source dependency DAG does not justify parallel mutation of host elaboration constraints. Cadence independently makes the same point (§13.1, 1430–1434); Concord's ordered dependencies are compatible but less explicit about shared metavariable scheduling.

Finally, Accord alone among these three supplies a general rational **two-square-root denesting certificate** (§12.2, 1219–1270), rather than only the standard \(\sqrt{3+2\sqrt2}\) example. Under
\(a,c,d\ge0\), \(d^2=a^2-b^2c\), set \(u=(a+d)/2\), \(v=(a-d)/2\). It proves
\(\sqrt{a+b\sqrt c}=\sqrt u+\sqrt v\) for \(b\ge0\), and
\(\sqrt u-\sqrt v\) for \(b<0\).
The proof correctly establishes \(a\ge d\), hence \(u\ge v\ge0\), and
\(2\sqrt u\sqrt v=|b|\sqrt c\); both candidates have the right square and nonnegative sign. The \(b=0\) case avoids division. Rational \(d\) gives unnested rational radicands; failure to find it establishes no global denesting impossibility. This is a reusable theorem-shaped certificate proposal, not an implemented denesting algorithm.

### Cadence: parameter specialization, usable defaults, and exact numerical observations

Cadence's strongest new test is complete solving of \(ax=b\) over the reals (§7.1, 800–824): singleton \(\{b/a\}\) if \(a\ne0\), all reals if \(a=b=0\), empty otherwise. Output must support a case description and infinite solution sets. The exact relation is membership iff the original equation (§7.2, 826–844). This immediately differentiates “a formula works generically” from a complete answer for all parameters.

Specializing a generic answer is itself a semantic operation (§7.3, 846–872). A conditional equivalence \(G(a)\to(P(a,x)\leftrightarrow Q(a,x))\) can specialize only with evidence of \(G(a_0)\); substituting a degenerate parameter cannot erase a denominator guard. The nearby example \(x^2=x\), divided by \(x\), retains the sound candidate \(1\) but loses \(0\) (§7.4, 874–883). This is stronger than merely warning that division by zero is bad: it asks the UI and certificate structure to preserve solution coverage.

Cadence offers a practical representation conflict policy (§5.4, 583–614): certify agreement at one observation of the same anchor, record accepted routes, choose a project canonical route for new automatic elaboration, and require explicit selection for incompatible alternatives. It does **not** claim equality of raw representations, universal observational equality or automatic dependent transport. §5.5, 616–632 pairs stable project-owned wrappers with separately versioned lexical policies. This addresses maintenance more directly than a general hope for coherent views.

Its precision calculus has a stronger sufficient composition bound than the basic common rule (§9.5, 1072–1129). With \(f\equiv_N\tilde f\), \(g\equiv_M\tilde g\), both inner constants zero, and \(g\) divisible by \(X^r\), it obtains
\(f(g)\equiv_{\min(rN,M)}\tilde f(\tilde g)\).
The two-error decomposition is sound: outer truncation contributes order \(rN\), inner perturbation contributes order \(M\). The zero-constant hypotheses make the coefficientwise infinite sums locally finite. It explicitly calls the bound sufficient, not optimal. Differentiation loses one degree; inversion preserves precision under a unit-constant hypothesis. These are paper interface laws, not companion-tested universal algorithms.

Cadence's numerical example keeps an already specified object fixed (§11, 1264–1304). For \(p(x)=x^3-x-1\), signs at 1 and \(3/2\), continuity and \(p'(x)\ge2\) establish a unique root **in that interval**. Twenty rational bisections produce
\(1389067/1048576 < r < 2778135/2097152\), width \(1/2097152\).
The separate residual bound \(|r-q|\le |p(q)|/2\) follows from the mean value theorem for \(q\) in the same interval. Refinement adds observations of the same root; it does not choose a new root or prove equality to a decimal. The Python code checks rational signs, containment and widths, while the existence/uniqueness and derivative arguments remain in the paper.

Its protocol distinguishes ProbeAccepted, EditReplayed, GoalProgress and DocumentSealed (§12.4, 1369–1395). It also gives a particularly sharp sufficient negative bridge: checked \(T\to F\) and \(F\to\mathrm{False}\) yield \(T\to\mathrm{False}\); a lossless-translation label is no substitute (§12.3, 1357–1360).

### Concord: finite residual evidence about an arbitrary fixed point

Concord's most technically discriminating proposal is demand-directed finite observation (§7, 454–533). A coefficient \(n\) requires precision at least \(n+1\); derivative precision \(N\) requires input \(N+1\). Cache keys include original series, algebra, variable, assumptions, precision and representation contract (§7.4, 525–528). Weaker demands can reuse stronger evidence through proved restriction; the reverse needs new evidence.

The finite implicit-series residual proposition (§7.3, 495–523) deserves prominent treatment in the synthesis. For \(\Psi(S)=z\exp(-aS)\), all relevant constant coefficients zero, and the **original arbitrary solution** \(T=\Psi(T)\), a polynomial \(P\) with
\(P-\Psi(P)\equiv_N0\)
satisfies \(P\equiv_NT\). The proof uses the precision-improving property
\(S\equiv_kT\Rightarrow\Psi(S)\equiv_{k+1}\Psi(T)\),
then induction from vacuous precision zero. The certificate may be discovered by any producer; checking a finite residual identifies it with the original fixed point to the exact requested precision. This avoids silently replacing the arbitrary solution by a canonical one.

The example
\(P=z-az^2+\frac32a^2z^3-\frac83a^3z^4\)
has residual zero through degree four. Transporting its precision through \(\exp(x\cdot)\) gives
\([z^4]\exp(xT)=x^4/24-ax^3/2+2a^2x^2-\frac83a^3x=x(x-4a)^3/24\)
(§10.4, 691–713). The companion checks these symbolic rational-polynomial identities, including a perturbed fourth coefficient that fails. The proof from residual to the arbitrary \(T\) is still unformalized. This is a good candidate for the next formal implementation because it exposes a clean discovery/checking asymmetry and meaningful precision failure without analytic convergence.

Concord has the most explicit treatment of **nonderivability versus negation** (§13, 844–869). Complete intuitionistic proof search may find no uniform derivation of \(P\lor\neg P\), but intuitionistic logic proves its double negation, so that outcome is not a proof of its negation. A classically enabled Lean context can prove excluded middle outright. This is a semantic issue even for a correct complete search procedure, beyond buggy metadata or lossy translation. Its second example—failure to inhabit \(\forall A:\mathrm{Type},A\) does not make every individual \(A\) empty—also guards quantifier movement.

Concord's three-view test is particularly concrete (§6.4, 431–445): natural expression → integer expression → rational expression → polynomial normal form. Moving truncated subtraction needs \(n\le m\); moving an intended exact natural quotient can need \(d>0\) and \(d\mid u\); reflection back needs an actual injectivity theorem. A quotient homomorphism can preserve equality without reflecting it (§6.2, 413): \(0\) and \(2\) coincide modulo 2. This makes it harder to mistake “certified representation” for unrestricted equality elimination.

Concord also contributes useful limits: radical equality certificates do not certify shortest/minimal denesting (§11.1, 748); complete root solving may enlarge a candidate set and later filter it, so intermediate arrows need not be biconditionals (§11.2, 773); and a local antiderivative of \(1/x^2\) cannot justify a finite improper integral across zero (§11.4, 788–796). The stated integral convention must distinguish totalized host operators from ordinary integrability/improper-integral claims.

## Shared worked mathematics and corrections

### Binomial inversion

All three preserve the key domain distinction: calculate the integer kernel
\[
K(n,j)=\sum_{k=j}^{n}(-1)^{n-k}\binom nk\binom kj=\mathbf1_{n=j},
\]
then use integer scalar action on an arbitrary additive commutative group. No multiplication or division in the target group is required. Reindex \(k=j+i\), \(0\le i\le n-j\), use the binomial product identity and the alternating row; treat \(n<j\) as the empty interval and the zero exponent separately. Locations: Accord §9.1, 888–929; Cadence §§8.1–8.3, 886–954; Concord §§8.1–8.3, 537–589.

The named reindexing must check membership, injectivity, coverage and summand correspondence. Dropping the inclusive endpoint invalidates the advertised operation even if another proof establishes the final equality (Accord §§9.3–9.4, 963–987; Cadence §8.2, 923–935; Concord §8.2, 576–578). These are tests of method conformance and useful explanation, beyond theorem truth.

**Correction before quoting the displayed transform laws:** Cadence §8.3, 937–948 and Concord §8.3, 580–587 omit explicit quantification over the sequence relation. Their displays must be read uniformly, not as a fixed-\(n\) iff/implication. A fixed-\(n\) reading is false: for \(n=1\), take \(a_0=1,a_1=0,b_0=0,b_1=1\) in \(\mathbb Z\). Then \(b_1=a_0+a_1\), but \(a_1\ne-b_0+b_1\). State \((\forall n,\ b_n=\sum_{k\le n}\binom nk\cdot a_k)\) before concluding the inverse for all \(n\), or require the forward equations at every \(k\le n\). Cadence's claimed iff requires uniform quantification on both sides. This is a scope defect in the prose display, not a refutation of the intended standard theorem. Accord's subsequent substitution of the formula for every \(b_k\) makes the uniform dependency clear (§9.1, 920–929).

### Autonomous differentiation and Lambert polynomials

All three retain an induction identity on an open \(U\), use it as eventual equality near a chosen \(x\in U\), then apply the chain rule at values actually reached by \(W\). Equality at one point does not suffice (\(0\) and \(t\) at zero). The hypotheses must say that the actual derivatives exist with the given values; merely an equation involving Lean's totalized derivative operator can be weaker. Accord §10.1, 991–1011 and Cadence §10.1, 1152–1165 are explicit about “has derivative”; Concord §9.1, 593–602 refers back to the source theorem's derivative hypotheses. Preserve that explicit form when synthesizing.

Cadence §10.3, 1201–1249 and Concord §9.2, 617–644 both derive
\[
P_{n+1}(w)=(1+w)P_n'(w)-(nw+3n-1)P_n(w)
\]
from \(H_n=e^{-nw}P_n/(1+w)^{2n-1}\), \(n\ge1,w\ne-1\), multiplied after differentiation by \(e^{-w}/(1+w)\). Their product/quotient calculation is correct; the bracket combines \(n(1+w)+(2n-1)=nw+3n-1\). \(G_0(w)=w\) is a separate base case, avoiding natural-number underflow at \(2n-1\). Cadence's first four polynomials and Python numerator transitions agree. The finite polynomial calculations are not formal verification of the real local derivative theorem.

### Abel series and rational algebra generality

All three keep an arbitrary commutative \(\mathbb Q\)-algebra \(A\), arbitrary \(T=tE_{-a}(T)\), and explicit algebra map \(\iota\). The equation forces zero constant coefficient. Lagrange–Bürmann plus \(E_x'=xE_x\) and exponential products yields
\[
[t^N]E_x(T)=\iota(1/N!)\,x(x-Na)^{N-1},\quad N\ge1,
\]
with constant coefficient 1 separately. The crucial cancellation uses \(\iota(1/N)\iota(N)=1_A\): the image of a rational unit is a unit even without an injective algebra map, a field structure or nontriviality of \(A\). Locations: Accord §§11.1–11.3, 1075–1154; Cadence §§9.1–9.3, 957–1048; Concord §§10.1–10.3, 653–689.

Their derivations appear mathematically sound at the stated paper level. They explicitly rely on the correct formal inversion theorem and its substitution/unit hypotheses, not numerical checks. The coefficient engine computes in a small decidable algebra and transports identities forward into \(A\); it does not embed all of \(A\) into a field. Finite jets cannot establish equality of full series: \(F\) and \(F+t^N\) agree below \(N\) over a nontrivial coefficient ring. Formal precision gives no analytic remainder estimate without convergence/quantitative hypotheses.

Accord additionally derives the binomial-type identity through \(E_x(T)E_y(T)=E_{x+y}(T)\) (§11.4, 1156–1173). Cadence explicitly proposes comparing sequence-first and formal-series-first EGF definition packages with bridge costs charged (§9.4, 1056–1070). Concord makes the finite residual route the primary implementation experiment, while maintaining its difference from the universal coefficient proof.

### Certificate soundness, completeness and the negative neighbors

All three distinguish a polynomial combination certificate \(p=\sum q_ip_i\) from a complete solver or ideal-membership decision procedure. It yields \(p=0\) under the original hypotheses \(p_i=0\), not a conclusion about all solutions or failed-search impossibility (Accord §7.3, 668–689; Cadence §6.4, 697–731; Concord §5.3, 358–372).

Cadence and Concord explicitly reject \(p^k=0\Rightarrow p=0\) in arbitrary rings with nilpotents (Cadence 697–724; Concord 370 and 1004). Accord's radical certificate checks sign separately from square equality (its tests 07–10); Cadence and Concord use the same principle. Complete root lists additionally need coverage; exact root representations need identity through a unique isolating specification; enclosures need containment of the same original object.

These examples should be selected to test different failure modes, rather than repeating all three reports' near-identical catalogues. Particularly discriminating additions are parameter degeneracy, nonzero nilpotents, precision loss under differentiation, backwards equality transport through a noninjective map, stale provider origins, and false unused assertions.

## Answers to the first-round questions

Cadence is the most directly usable decision register. Appendix A (1764–1815) supplies **ten distinct S1–S10 rows**, each with a proposed default and a test that could change it. Appendix B (1817–1877) supplies **twelve U1–U12 rows**. These are proposed answers, not twenty-two settled empirical questions.

Concord Appendix B (1071–1093) covers the same ten A and twelve B question identifiers in **twelve grouped rows**. Do not say it has twenty-two separate answer rows. It combines related issues and points to experiments: wrapper stability, alternative proofs under named methods, meaning-bearing edits, provider replay, measured routine yield, view composition, retained evidence, definition templates, document-only value, data alternatives, conflicting packs, and stopping.

Accord has no explicit all-questions crosswalk. Its answers are distributed, so only claim substantive coverage, not an audited twenty-two-row completion. Useful mappings are:

| Round-1 theme | Accord answer and exact location |
|---|---|
| Smallest useful step; contract role identity | Ordinary local wrapper plus maintained input roles; separate theorem and policy versions (§14.1, 1410–1426) |
| Whether a reason constrains a proof | Hard `by method`, soft `prefer`, explicit `by search` (§4.3, 383–394) |
| Automatic choices; meaningful semantic review | Preserve object identity, distinguish construction from proof (§4.2, 365–381; §13.2, 1348–1351); effect discipline (§15.3, 1528–1539) |
| Verified suggestion | Exact displayed edit replay, root proof completeness and operation-wide resource limits (§13.4, 1373–1393) |
| Adapter cost and routine yield | Same-assets three-way comparison and cost \(L+\sum(A_i+R_i)\) (§§17.3–17.4, 1621–1659) |
| Composable views | Observation-specific coherence and ordered guards (§5.5, 500–515; §8.2, 794–826) |
| Replay unit and repair | Retained exact evidence, source, contracts and explicit environment identity (§14.4, 1465–1482; §15.3, 1528–1539) |
| Definitions | Ordinary definitions with selected observation interfaces (§§5.1–5.3, 409–480) |
| Visibility/notices | Choices visible and consequences expandable (§3.3, 319–334; §15.1, 1501–1512); exact result display guarantee (§14.3, 1448–1459) |
| Provider outcome and data alternatives | Exact mathematical negative evidence (§13.5, 1395–1406); property-bearing chosen data (§13.3, 1353–1371) |
| Pack ownership/conflicts | Explicit profile composition, no new-import reinterpretation (§15.4, 1541–1553) |
| When to stop | Keep useful library/renderer if syntax supplies no measured benefit (§17.5, 1661–1673) |

For Cadence's decisions, particularly useful tighter citations are S1–S4 1775–1790; S6–S10 1794–1812; U3–U7 1835–1854; U9–U12 1859–1874. Concord's full grouped table is sufficiently short to cite 1080–1091.

## Tensions, limitations and next-iteration questions

1. **Choose the first falsifiable artifact.** Accord's finite reindexing/certificate path minimizes mathematical novelty and can isolate the frontend boundary. Cadence's \(ax=b\) path stresses complete-answer semantics but also needs case/set presentation. Concord's residual-jet path best tests computation about a noncomputable or arbitrary object but requires a reusable formal precision/residual theorem. Which uncertainty is actually blocking investment? A common infrastructure spike can support one primary slice and two held-out tests; declaring all primary avoids this decision.

2. **Measure the incremental value of demand tracking.** Concord's coefficient demand and cache policy are concrete, but a naïve implementation may still elaborate or expand the full object (§15.4, 946–948). Cadence's improved composition bound could save work but makes inference and diagnostics more complicated. Compare explicit fixed precision, demand propagation with basic min rules, and valuation-aware rules on actual checking cost. A stronger bound is not automatically a better first implementation.

3. **Define the publication artifact precisely.** All three preserve evidence and distinguish discovery-free checking from computation-free checking. Concord explicitly offers certificate replay and stricter term-only replay (§15.1, 918–923). Cadence recommends exact evidence plus readable source and computational certificate (§14.2, 1519–1530). Decide what is portable, which trusted check route validates a concrete execution, and whether two profiles are necessary initially. Proof-text freezing alone is insufficient.

4. **Make the answer relation authoritative without creating a second type system.** A tag such as “complete,” “conditional,” or “precision 10” must refer to an actual dependent proposition and checked output, as all three intend. Establish a small interoperable relation vocabulary while leaving ordinary theorems expressible directly. Measure the cost of annotations and relation adapters; avoid wrapping every lemma in a heavy custom protocol.

5. **Choose a bounded policy for automatic representations.** Cadence selects a canonical route for new nodes; Concord defaults to retained objects and a closed observation interface for automatic replacement; Accord offers a relational contract and explicit profile composition. These are compatible at a high level but leave different implementation burdens. Test an added observation and a newly imported route, not just two routes that already agree at one coefficient.

6. **Separate explanatory promises by mode.** Accord's hard/soft/open reason policy is a concrete solution; Concord permits keeping strict method conformance as a publication option if it impedes exploration (§17.5, 1021). Measure whether users understand “valid checkpoint reached by another method” versus “the advertised move validated.” The document renderer must not hide this distinction behind a single green state.

7. **Test complete answers without relying on generic division.** Cadence's \(ax=b\) and Concord's \(x^2=a\) jointly suggest a compact parameter-specialization suite: singleton, empty, infinite, branch-selected witness, complete finite roots. Include the \(x^2=x\) lost-root mutation and a specialized guard failure. The task should ask the reader what was proved, not merely whether the output looks plausible.

8. **Specify negative evidence at the object logic.** Concord's excluded-middle argument shows that a flawless search procedure can still answer a different question. Before adapting Leant negative statuses, decide whether the product ever promises a checked host negation, only fragment-relative exhaustive search, or a checked counterexample relation. Do not use completeness/abstraction flags as an informal substitute for a bridge theorem.

9. **Use the mathematical scope defects as adversarial tests.** The missing uniform quantifiers in the two binomial displays are especially relevant to the design goal: natural mathematical notation encourages readers to infer a sequence-level convention, while a formal interface must retain the exact dependency. Ask whether the semantic display makes the required family of hypotheses clear without forcing raw binder dumps.

10. **Do not infer usability from companion counts or source-audit percentages.** All three correctly reject that inference. A useful next experiment must include authoring, reading and repair, equally equipped Lean, charged package costs, held-out families, and an already compact Lean control. Readers should identify the guard, generality, chosen object and precise result guarantee. A library and renderer remain legitimate outcomes if authored syntax supplies no benefit.

The reports support a common research direction with several well-chosen mathematical stress tests. They do not yet decide the engineering economics, certify the proposed boundary, or establish that mathematicians prefer authoring through the proposed surface. The next synthesis should preserve both the convergence in requirements and the differing implementation bets.

## Follow-up: focused Lean evidence authorized after the source review

The user subsequently allowed a bounded Lean experiment. `../evidence/lean/FocusedChecks.lean` was checked with the existing Lean 4.32.0 executable and cached mathlib at `81a5d257c8e410db227a6665ed08f64fea08e997`, without invoking Lake, rebuilding dependencies, downloading packages or editing ProveIt/Leant. The final invocation exited 0; exact command, environment, hashes and timing are in `../evidence/lean/receipt.json`, with a reproducing `check.ps1` and explanatory README.

Source lines 19–31 prove failure of the unguarded totalized real-division identity at \(x=1\), its universally quantified negation, and the guarded identity for \(x\ne1\). Lines 44–69 prove a fixed-\(n=1\) binomial counterexample with \(a_k=0\) for all \(k\), \(b_0=1\), and all other \(b_k=0\), including negations of the pointwise implication and iff. This is an alternative to the paper counterexample given above. All eight named theorem audits list only `propext`, `Classical.choice`, and `Quot.sound`.

This adds focused kernel-accepted mathematical evidence for two semantic distinctions. It does not implement any report's language, relation registry, certificate checker, provider protocol, or publication boundary, and it is not an aggregate build or independent recheck of the imported dependency closure.
