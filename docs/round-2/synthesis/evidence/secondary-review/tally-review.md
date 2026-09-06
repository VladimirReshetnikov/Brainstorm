# Audit of the secondary synthesis's tables

Reviewed source commit: `84af03f49f89a31b47ff3416ccdbc9180fd6b438`.

Scope: `docs/round-2/unified_report/{feature_matrix.csv,negative_suite.csv,question_tally.csv,tools/make_tables.py}` and the corresponding table/count claims in `unified_report.tex`. Original files were read-only. The generator was copied verbatim under `tables/tools/` and executed there with Python 3.14.4, `-B`, and `PYTHONDONTWRITEBYTECODE=1`. No Lean, Lake, or PDF command was run in this lane. The machine-readable receipt is `tables/receipt.json`; reproduction script is `tables/run_review.py`.

This is a full arithmetic/schema/provenance audit of the tables plus targeted source review of disputed interpretations. It is **not** a fresh independent recoding of all 522 feature cells or 198 possible report–question answers. Earlier complete readings and the existing 72-cell/241-reference convergence register provide the comparison context.

## Main findings

1. **40 unanimous rows out of 58, and 30 unanimous rows outside the ten-row inherited group, reproduce exactly.** They count manually authored editorial codes. They do not establish thirty historically new discoveries or independent confirmations.
2. **The nine source adversarial tables contain 182 rows, not 183.** The generator's 183 is the number of report–canonical-mutation incidences. The mapping is many-to-many. Every one of the 182 original table rows is referenced, so this is a unit/counting error rather than lost source coverage.
3. **The 51 canonical mutations, ten represented in at least seven suites, and seventeen represented in at least five suites all reproduce.** These are proposed mutation families, not 51 executed tests. There are **15 singleton families**, not the “four” stated in TeX line 577.
4. **`question_tally.csv` is a 22-row editorial summary, not a per-report tally from which modal answers or unanimity can be recomputed.** Its own variations go beyond the choice of first definition package.
5. **The fine taxonomy complements our broad convergence map.** Its partial marks mostly refine broad agreements; they do not refute our eight common commitments. It has several wording-sensitive cells and novelty claims that should not be carried forward without qualification.

## What the generator actually does

`tools/make_tables.py` lines 19–77 embed all 58 feature descriptions and nine-character mark strings. Lines 82–103 serialize these strings and count `Y`; the sole initial validation at line 79 checks string length. The code does not open the nine report sources, parse their sections, retrieve citations, compare with round one, compute inter-reviewer agreement, or infer a mark.

Lines 91–95 define “new” as every row whose group is not literally `Inherited foundation`. Thus “new” is an editorial partition label, not the result of a temporal source comparison. The original marks are openly described as the reviewer's readings in the module docstring (lines 4–9) and report table caption (TeX 229–234). That honesty should govern the stronger claims elsewhere.

Lines 108–182 similarly embed all 51 mutations and their per-report source row identifiers. Lines 186–198 serialize them and compute the number of participating reports with `len(prov)`. This is a manually constructed consolidation, not an automated deduplication algorithm. The source-row mapping is useful and auditable.

Lines 202–224 embed the 22 questions, modal prose answers, and variation prose. Lines 228–234 merely write them. There is no nine-report answer matrix, no response/abstention flag, no section locator, and no computation of a statistical mode. Fourteen variation cells contain the word `Unanimous`; that is stored prose, not a derived count.

The script prints the feature table body and the negative-suite rows represented in at least five reports. It does not rewrite the report, print the full 51-row appendix, or generate the question table's LaTeX. The report text is therefore manually synchronized. In this snapshot, our independent structural comparison found that all 58 printed feature mark/count rows and all 68 printed mutation ID/count rows (17 main-table plus 51 appendix) agree with the CSVs. That check does not prove semantic fidelity of every shortened table description.

All three reproduced CSVs have identical parsed rows and identical newline-normalized text. Their raw bytes differ because the imported CSVs and this Windows execution use different newline conventions. The receipt preserves both SHA256 values and labels this distinction explicitly. Hashes of all files under the original secondary package were identical before and after reproduction.

## Reproduced counts and their units

| Quantity | Reproduced value | What it counts |
|---|---:|---|
| Feature rows | 58 | Editorially selected commitments/example choices |
| Feature cells | 522 | 58 descriptions × nine report marks |
| Explicit / partial-or-implicit / absent cells | 451 / 37 / 34 | Literal Y/P/N marks |
| Unanimous feature rows | 40 | Nine literal Y marks |
| Feature rows with at least seven Y marks | 44 | Literal row count |
| Inherited group | 10 | The group explicitly named `Inherited foundation` |
| Other rows | 48 | Every other group, irrespective of actual historical novelty |
| Unanimous other rows | 30 | Nine Y marks outside the named inherited group |
| Other rows with at least seven Y marks | 34 | Same group partition |
| Canonical mutations | 51 | Editorial mutation families |
| Report–canonical-mutation incidences | 183 | Sum of the `suites` column |
| Expanded local-reference occurrences | 187 | Comma-separated source row identifiers, including reuse |
| Distinct source table rows referenced | 182 | Unique `(report, local row)` pairs |
| Source table rows actually present | 182 | Direct extraction of the nine original tables |
| Canonical families appearing in at least seven suites | 10 | Not universal suite coverage |
| Canonical families appearing in five or six suites | 7 | Adds to a 17-family frequency-selected core |
| Singleton canonical families | 15 | Families with exactly one nonempty report column |
| Question summary rows | 22 | Ten S questions and twelve B questions |

The original source-table counts are Locus 28, Accord 26, Cadence 14, Concord 11, Facet 16, Meridian 23, Noema 18, Prism 20, and Vantage 26. `tables/negative-source-locators.json` records every source row, its exact TeX line and path, and the canonical mutations to which it was mapped. Cadence, Concord, and Noema do not print `r1`, `r2`, etc.; these are the consolidator's ordinal identifiers for their unnumbered tables. The receipt checks those ordinals against their actual row boundaries.

Five source rows are each mapped to two canonical families:

- Cadence r1 → M7 and M39 (cancellation and parameter degeneracy).
- Facet T14 → M16 and M17 (scope and stale origin).
- Noema r11 → M16 and M17.
- Prism N14 → M16 and M17.
- Concord r10 → M17 and M21 (stale origin and displayed-edit mismatch).

Four report–family cells combine two different source rows: Facet T2/T3 in M30; Accord A4/A5, Prism N2/N3, and Vantage V1/V2 in M33. Hence 183 incidences expand to 187 row-reference occurrences, and reuse removes five duplicates to yield 182 distinct source rows. Both split and merge operations are reasonable; they make “183 original rows deduplicated to 51” an incorrect description.

Correct the source-row count at secondary TeX lines 103, 149, and 546. The 15 singleton IDs are M10, M20, M26, M28, M37, M40, M41, M42, M43, M44, M47, M48, M49, M50, M51. Line 577 says “four,” lists thirteen, and omits M49 (strict inequality multiplied by a merely nonnegative factor) and M50 (algebraic-number equality inferred from a shared polynomial).

## The novelty claim needs a historical crosswalk

The count itself is correct. The interpretation “thirty new commitments, not fixed in advance” at secondary TeX 93, 103, 158, 312, and 513 is not supported by the generation method and overstates the historical distinction. There is substantial new CAS development, but the non-inherited groups contain inherited rules, strengthened applications, and repeated worked examples alongside new material.

Concrete counterexamples are already in the two first-round syntheses:

| Secondary feature called non-inherited | Earlier explicit material | Appropriate classification |
|---|---|---|
| E1: search failure is not original-target negation; adequacy needs a theorem | `docs/round-1/synthesis/unified-report.tex` 310–315, 572–584 | Inherited boundary, sharpened in round two by excluded-middle and directional-adequacy arguments |
| E3: exact displayed edit replay and goal-count/completion distinction | Same file 938–956 | Inherited explicit requirement |
| E4: native Lean owner plus narrow Haskell service | `docs/round-1/unified_report/unified_report.tex` 493 | Inherited architecture, elaborated further for CAS |
| E5: whole-request budget, disposable workers, stale/cancelled replies | `docs/round-1/synthesis/unified-report.tex` 958–971 | Inherited explicit operational requirement |
| E7: type inhabitation is not behavioral specification; finite evidence proves only itself | Same file 305–308, 854–879 | Inherited explicit distinction |
| D3: preservation is not reflection | `docs/round-1/unified_report/unified_report.tex` 875 explicitly credits the distinction to the first-round MathematicalLanguage report | Inherited semantic distinction with stronger new counterexamples |
| F2: autonomous derivatives with range-local hypotheses | `docs/round-1/synthesis/unified-report.tex` 703–725 | Reused mathematical control with richer symbolic-computation treatment |

E6 (transactional shared metavariables), although not unanimous in the secondary matrix, is another example of the grouping issue: first-round Codex lines 566–570 and Claude line 517 already identify it. The secondary's own round-one account at 170–172 and its question table show how much negative evidence, replay, and definition architecture is inherited.

The particularly strong sentence at secondary 312 saying the earlier syntheses did not specify preservation/reflection is contradicted by the earlier explicit credit at line 875. The claims that every item in the ten-rule list is absent from both syntheses (317) and that the thirty-row unanimity fixes “one sensible interface” (513) also need weakening. A shared exact-target acceptance condition leaves major choices about representations, algorithms, certificate formats, execution trust, dependent guard APIs, defaults, and first slice.

A more defensible formulation is: **“Thirty rows outside our ten-item foundation group receive nine explicit marks. They mix new CAS-specific contracts with inherited principles applied more concretely; a historical novelty count has not been established.”** An improved register would separately label inherited, refined, and newly introduced claims and cite earlier support for each classification. It should not simply relabel all fifty-eight rows as new or old on the basis of their group name.

## Comparison with our 72-cell/241-reference broad convergence map

Our matrix has eight deliberately broad commitments across nine proposals. It records source support and qualifications, not 72 independently discovered ideas or implemented capabilities. The secondary has 58 finer descriptions and example choices across nine proposals. The two denominators are different. Forty of fifty-eight unanimous rows therefore does not contradict eight of eight broad architectural agreements.

| Our commitment | Main secondary refinements | What the detail adds |
|---|---|---|
| R: exact result relation | B1–B8; parts of C6, D10, D13 | Coverage versus witness correctness; factor multiplication versus irreducibility; mathematical kind versus validation status |
| O: fixed objects and certified observations | D1–D3, D5–D7, D9–D13 | Exact presentations, lossy observations, property-specific transport, precision, selected operational packages |
| G: scoped guards and composition | A3, B4, D4, D6–D7; E6 | Dependent telescope, sufficient guard, unit conditions, exact retained intermediate objects, transaction constraints |
| V: execution and reification boundary | C1–C6, C8, C10 | Verified algorithm/checker/proof-producing lanes, native trust accounting, exact opaque atoms, certificate-resource limits |
| D: ordinary packages plus policy | A4–A5, D8–D9, D14 | Definition-template choices, method-constrained reasons, avoiding CAS in definitional equality |
| L: exact providers and honest outcomes | E1–E8 | Haskell adapter, displayed edit, transactional state, behavioral evidence, composition benchmarks |
| P: retained publication evidence | A6, C7, C9; E3 | Every formal assertion checked, search-free versus computation-free replay, external-service independence |
| E: fair evaluation | A7–A9, C9–C10, E8; worked examples F1–F8 | Shared infrastructure, explicit costs, checking size/latency, domain-specific examples and first-slice choices |

The F rows mainly measure example selection or inspected corpus material. They should not be aggregated uncritically with architectural commitments as votes for a language interface. D9's EGF package, D12's residual bridge, and D13's partial semantics are genuine choices of emphasis. A report need not adopt all three as its first implementation task to support the broad O/R/D commitments.

Several useful fine distinctions were already present in our prose but lacked their own matrix row: separate irreducibility guarantees, exact partial-function definedness, dependent witness scope, and explicit certificate cost. The secondary's finer taxonomy is a good index for an implementation backlog and test catalog. It does not require replacing our broad matrix with a score or ranking.

### Wording-sensitive feature marks

**C7 conflates a semantic policy with a particular historical citation.** The row says “Accepted evidence must not depend on a remote service surviving (the polyrith lesson)” and marks Locus, Accord, and Facet N (`make_tables.py` 44). Secondary TeX 314 explains this as whether they consulted current Mathlib documentation. None of those three names `polyrith`, but all three explicitly retain proof terms/certificates to replay without rediscovery: Locus §12.3, 1630–1643; Accord §14.4, 1465–1476; Facet §13.5, 1445–1457. These support our P cell. A missing `polyrith` citation is not missing evidence-retention architecture. Split the feature into **retained service-independent evidence** and **explicit discussion of the `polyrith` shutdown**, or rename C7 so its N genuinely means what was counted.

**D2's Meridian P is debatable under the row's own wording.** Meridian §4.1, 467–487 distinguishes exact expression claims, finite coefficient observations, enclosures and their forbidden promotions; §7.1, 904–923 distinguishes semantic objects, representations, and finite projections. It does not give Facet's same explicit exact-presentation/observation pair of abstract type schemas. A P can therefore mean “less formal taxonomy,” but should not mean that Meridian fails to distinguish exact information from a finite observation. Document the coding threshold. Our O agreement is not contradicted.

**C2, C10, D10–D13 describe stronger conjunctions than the broad matrix.** Reusing proof-producing `ring` does not necessarily mean explicitly designating a third lane. Discussing costs does not necessarily put certificate degree bounds into a protocol field. Finite observations do not imply an implemented or even fully specified demand planner. Their P/N marks can usefully expose these levels of specificity if that criterion is stated.

**B4's “guards are never promoted to hypotheses” should mean “never silently added to the original theorem.”** A visible branch can assume a guard, and a conditional theorem can bind it. Facet §5.2, 510–529 explicitly represents premise-dependent results. Literal prohibition of guarded hypotheses would rule out the architecture the reports endorse. This wording should be tightened before using the row as an executable conformance criterion.

No corrected total of unanimous feature rows is claimed here: doing so would require a consistent recoding rule for all 522 cells, not just changing a few disputed marks.

## The negative catalog is valuable, but canonicalization must preserve exact tests

The strongest part of the data package is its complete, explicit source-row mapping. It makes rare cases easy to preserve: wrong formal-root branch (M10), witness-quantifier exchange (M47), integer ideal membership after extending scalars (M41), guard circularity (M43), positive-versus-nonnegative scaling (M49), and selected algebraic-root identity (M50). These should survive regardless of popularity.

However, the canonical rows are sometimes umbrellas rather than interchangeable executable tests:

- **M6 merges inversion, cancellation, and elimination of a power.** Facet T6 (1898–1909, specifically 1908–1909) tries to invert 2 in Z using nonzeroness. The canonical description says cancellation/nonunits or power certificates in rings with zero divisors, with “unit or regularity evidence” as the expected response. Z has no zero divisors; 2 is regular and cancellable but not invertible in Z. A checker accepting regularity for an inverse request would be wrong. Keep separate request kinds and source subcases under this family. Locus T06 (2014–2015) and Concord r8 (1004) also concern materially different algebraic premises.
- **M38 merges approximation-to-equality and interval-to-sign promotions.** Meridian C3 (1895–1896) supplies a tiny floating residual for an exact identity. Concord r9 (1005) supplies a zero-containing interval for a sign request. They share the need to respect the guarantee, but neither is a test of every clause of the canonical row. Retain separate payloads and expected exact propositions.
- **M8 rewrites Meridian's actual counterexample.** Meridian D2 (1885–1886) uses a partial-function solution certificate for the totalized equation. That is sharper than merely forgetting a domain during normalization: the solution set changes. Preserve the convention and target predicate in the executable test.
- **M27 contains different strengths of negative failure.** Facet T12 (1920–1922) is complete intuitionistic nonderivability of excluded middle, not merely budget exhaustion. Retain that semantic counterexample separately from timeout and malformed-status tests; otherwise the most informative new refinement disappears under a general failure-status label.
- **M34 folds different certificate invariants together.** Polynomial coefficients, recurrence parameters, and Sturm remainder/endpoints have different soundness theorems and parser contracts. One generic corrupt-byte test cannot stand in for all of them.

The CSV's expected behaviors are prose, and it carries no executable input, positive partner, domain, theorem identifier, exact expected result, source scope, or replay receipt. Source row IDs are the beginning of a test register, not an implemented suite. The source reports do ask for positive neighbors; the consolidator candidly notes at TeX 577 that they are not stored in the CSV. Pair them explicitly before saying a prototype “passes the 51-mutation suite.”

The frequency-based 17-family core is a reasonable starting list, but the justification at secondary 546—“because nine designers agreed that a system which accepts any of them is wrong”—overstates what a threshold of five suites establishes. All nine may share a broader rule while only five tables include a particular instance. Frequency is neither a risk score nor a proof that low-frequency tests can wait. Several singletons protect trust or statement integrity as directly as the popular rows.

## The question answers are broadly compatible, with meaningful variations

The 22 modal summaries are a useful discussion agenda. The source references in our per-lane memos support broad agreement about exact statements, ordinary theorem wrappers, meaning-sensitive notices, retained evidence, and a fair Lean comparison. But the stronger summary that variation is **only** the first definition package (secondary TeX 103) is contradicted by its own table:

- S1 varies the taxonomy of requests and implementation families (345).
- S3 explicitly identifies Prism's delegation-by-specification rule (347). That affects whether constructing a new witness satisfying an already fixed request can proceed automatically.
- S4 varies status organization and receipt models (348).
- S5 records Facet's five nested comparison arms (349).
- S6 distinguishes anchor-relative and observation-relative coherence (350), with real choices about which route is pinned and how much transport is automatic.
- S8 distinguishes replay levels and retained evidence forms (352).
- S10 records representation views and contract-/guard-surprise measures (354).

These variations need not be logical disagreements; many are compatible refinements or different defaults. “Broadly compatible answers, with differing mechanisms and defaults” is justified more readily than “essentially the same answer from every report that addresses them.” The latter needs per-report answer records and explicit denominators, especially when two reports answer in the body rather than in numbered tables.

For subsequent use, retain each row's concise synthesis but add per-report source ranges, a response state (explicit/partial/not addressed), the chosen default, and the concrete experiment proposed to resolve it. Compute modal labels only after choosing an equivalence criterion for answers. Do not count taxonomy differences as philosophical opposition or flatten consequential defaults into unanimity.

## Recommendations for incorporating this review

1. Keep the 58-feature taxonomy as a finer index, and describe its marks as one reviewer's proposal coding. Keep our 72-cell source-located broad convergence as the architecture crosswalk.
2. Correct **183 source rows → 182 source rows / 183 report–family incidences**, and **four singletons → fifteen**. Preserve the many-to-many map rather than forcing a one-to-one deduplication narrative.
3. Replace the unsupported “30 genuinely new” interpretation with an inherited/refined/new crosswalk. In particular, credit the first round for exact-edit replay, negative-evidence boundaries, service architecture, behavioral specifications, and preservation/reflection.
4. Split policy support from mention of a particular tool in C7, and state the explicit/partial criterion for combined feature rows.
5. Adopt the complete source-mapped mutation catalog as an implementation backlog. Add typed requests, precise domains, positive partners, exact expected failures, and retained evidence before treating it as an executable suite.
6. Preserve the rare mathematical controls, especially inverse-versus-cancellation, guard dependency, root identity, and original-target nonderivability. Rank by semantic risk and checker coverage in addition to report frequency.
7. Treat the question tally as a compatible-answer synopsis with meaningful remaining defaults. The data do not establish a unique sensible interface, and they do not yet establish unanimity on an executable protocol.

The companion `tables/receipt.json` and `tables/negative-source-locators.json` provide reproducible evidence for the counting and coverage corrections. Interpretation claims in this memo remain source-based judgments with the cited line ranges; they are not promoted to mechanically verified facts by the JSON receipt.
