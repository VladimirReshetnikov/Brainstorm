# Review of the merged round-4 peer report: evidence, suite and evaluation

Reviewed input: `c92ef058979fcb8f6c11030ac9ed80c64186e0f8`, under `docs/round-4/unified_report`. Read the README, complete table-generator source, all feature and question rows, all 52 negative families, the report's evidence/evaluation/Leant conclusions, companion/Lean run summaries, and selected directly relevant original tests. Only the inspected table generator was executed, in an isolated copy; no input, external repository, Git, Lean or PDF mutation occurred. This is a targeted evidence/evaluation review, not a fresh replay of the peer's Lean experiments.

## What is worth incorporating

The peer contributes a useful **indexed mutation catalogue**, an explicit proposal to compare independently implemented engines, a concrete reading exercise, and a sharper question about whether alternative supports actually change an author's next action. Its implementation order starts from a concrete mathematical use site and then connects registration, planning, checking and export. These are useful additions to our matched Lean experiment; they do not require adopting its stronger consensus claims.

The 52-family suite should be used as a traceability inventory. Attach each adopted family to an actual input, expected semantic status, a nearby admissible positive, checker/export target, and exact test identifier. Preserve distinctions among mathematical counterexamples, rejected promotions, conditional residuals, unsupported requests and diagnostic-only results. The peer already distinguishes prose/table/executed labels, which is useful; it needs a finer execution scope than one E token for a broad family.

## Generator reproduction and arithmetic

The generator was inspected before execution. `tools/make_tables.py` consists of hard-coded M/N/Q/LEAN/NEW/RUNS data and deterministic CSV/TeX emission. It does **not** parse the nine reports, inspect their source anchors, derive test outcomes from logs, or rerun any companion. The feature marks are defined at lines17–140, negative labels143–252, question answers254–337, compiler metadata339–368, and companion metadata370–384. The counting/emission routine begins at415.

An isolated `python -B tools/make_tables.py` run passed. All 11 generated CSV/TeX fragments match the supplied text after newline normalization. Input hashes remained unchanged and no bytecode was generated. Exact command, source/result hashes, output and independent CSV counts are in `docs/round-4/synthesis/evidence/parallel-evidence/table-receipt.json`.

The arithmetic reproduces:

| Editorial register | Reproduced count |
|---|---:|
| Feature rows | 101 |
| Rows with all nine Y marks | 62 |
| Such rows additionally coded “not stated in round 3” | 19 |
| Negative families | 52 |
| Families with no inherited family ID | 21 |
| Families marked E for at least one report | 21 |
| Families attributed to at least five reports | 36 |
| Question rows / explicit-all rows | 20 / 14 |

These are reproducible counts **of the editorial coding**. They do not establish semantic novelty, independent agreement or executed Lean coverage. Neither CSV nor generator provides a precise source locator for every cell, and some rows conjoin multiple claims. Our source-anchored matrix should remain the authority for our own reading rather than importing 62/19 as measured findings.

There are two direct internal discrepancies:

- The prose says six reports prove the affine-frame theorem (`unified_report.tex:99`, `:245`), but I2 has only **five** Y marks: Alder, Clover, Heather, Laurel and Rowan (`feature_matrix.csv:65`; `make_tables.py:92`). Fennel and Juniper are P. Resolve the theorem/coding criterion before repeating a count.
- The prose says the six non-unanimous question rows are T-questions (`unified_report.tex:301`). The CSV gives **T1, T2, T5, T9, T10 and Q9**. This is a factual tally-description error, not a failure of the generator.

The inherited/new column is not a reliable novelty measure merely because its sums reproduce. For example, broad unresolved-frontier and publication distinctions already appear in the previous synthesis (`docs/round-3/synthesis/unified-report.tex:509`, `:526`, `:1616`). The stronger *ordered residual calculus* may be new while a coarsely bundled statement about visible conditional status is inherited. Row definitions, granularity and explicit citations determine that distinction.

## Corrections to the peer's strongest conclusions

**Nine engines do not implement the same antichain specification.** The peer recognizes six antichain engines and three different companions at322, then says “nine implementations of the same specification” at383 and treats the antichain theorem as their common oracle at414,436,485,501. Its own G1/G2 rows exclude Clover, Heather and Rowan (`feature_matrix.csv:45–46`). Clover/Rowan primarily compute first-proof reachability; Heather is a restricted behavioral frontend with a small use-site resolver. Rowan's diagnostic leaves are not certified sufficient residuals. A cross-test disagreement can therefore be an intentional semantic difference, not a bug.

The useful revised experiment is: compare the six support engines on a normalized finite Horn interchange format, then compare the other engines on compatible **projections**, such as reachable facts or individually checked routes. Align the known facts K, authorized assumptions H/offers O, nullary evidence, methods, cycles, budgets and completeness flags. Compare completed support families modulo ordering; compare partial runs only for derivation soundness and honest incompleteness. Typed-grounding and behavioral engines require their own adapters and contracts. Do not claim their JSON certificates differ only trivially.

**“Finished” overstates the architecture's status.** The peer says the frontier calculus is finished and mechanization would be formalization rather than design (`unified_report.tex:414`). The finite ground theorem is well specified, but its intended composition with dependent telescopes, authorized premises, selected method evidence, bounded grounding, residual projection, route selection and Lean export still contains design decisions. Our Rowan diagnostic and Sorrel route-selection/partial-label probes demonstrate why a correct finite theorem does not settle the combined interface.

**“No report claimed more than it had” is too strong.** At420 the peer makes that blanket conclusion. Sorrel's literal partial-subset statement is mathematically overstrong (`docs/round-4/ideas/Sorrel/sorrel.tex:845`), and the table/prose collapses some finite proxies into broader execution labels. Preserve individual authors' generally careful evidence distinctions without endorsing an unrestricted absence-of-overclaim assertion.

**“All nine export generic Lean” is false.** The one-paragraph summary99 says that. Rowan ships no Lean source, Clover has a concrete endomorphism core and applications, and Heather exports concrete list targets. The peer's own appendix describes these differences. Similarly, compiling a theorem-free cycle module is file acceptance rather than a theorem count, and a generic conditional export is not a checked arithmetic registration.

## Refine the negative-suite semantics and execution labels

1. **S11: changing a guard does not necessarily invalidate positive soundness or lower dimension.** The required response says “recompute the frame” (`negative_suite.csv:12`), and the prose459 says a guard lowers dimension and test count. Even lengths and nonempty lists still have one-dimensional affine span. An old sound overapproximation may continue to cover a stronger guard; what may fail is the realizability of its old test points or exact decision completeness. Distinguish positive soundness, coverage, completeness and negative witness realization in the expected status.

2. **S16/S17/G10: state whether the seed is known, offered or absent.** An available seed can yield a closed proof. A merely authorized offered seed yields a conditional route. No seed yields no closed derivation, but Rowan may return a nonempty diagnostic fallback. Thus “both frontiers empty” and “a seeded cycle yields only a conditional route” are not universal outputs (`negative_suite.csv:17–18`; `feature_matrix.csv:54`). After deleting a known seed, a conditional route exists only if it remains authorized as an offer or the repair operation explicitly reopens it.

3. **S26's Sorrel E token is not evidence for the exact named operation.** That family asks to remove a used *versus an unused* premise from a retained derivation (`negative_suite.csv:27`). Sorrel tests availability closing, exact leaf support and seed deletion (`sorrel_model.py:286–320`), but does not perform Laurel's paired used/unused proof-abstraction transformation. Its G12 matrix mark is only P. Laurel's `reopen_known` and its tests139/148 are direct execution of the named operation. Keep Sorrel's related tests, but label the narrower property actually tested.

4. **S27's Rowan E token is an analogy, not policy-after-antichain execution.** Rowan has no support minimizer. Its tests at `test_rowan.py:84–92` restrict support/rules; they do not test a permitted route erased by support minimization. Sorrel's filter-before-saturation test addresses alternative routes (`sorrel_model.py:328–331`), but its base supports `{P,S}` and `{Q,S}` are incomparable. It does not catch the specific bug where a forbidden smaller support dominates an allowed larger support before filtering. Split “restricted rule search,” “prefiltering alternatives,” and “policy-sensitive dominance” rather than counting all three as the same executed guarantee. The strict-subset and same-support/different-method pairs below are still useful additions.

5. **E/T/P measures different kinds of support, not a strength ladder.** S20 combines forged support, target alteration, premise order and corrupt nodes; an E for one mutation need not cover all four. S25 combines context/snapshot/rule changes, while many companions check symbolic context IDs rather than real Lean context transport. S48 often tests atom identity, not a mathematical target relation. Use claim-level test IDs and distinguish model execution from exact Lean elaboration tests.

The run summaries likewise need their original/retry context. The peer's original Lean summary records Clover's importing example failing before an appropriate local core artifact is supplied, plus Heather's actual tactic-template failure; the table records Clover's successful retry with its module dependency. That is a legitimate recovery when described, not 19 first-attempt successes. Heather's locale-dependent demo failure also has a separately successful UTF-8 run. Logs and retries support these qualified statements; a table-generator run does not independently reverify them. `README.md:30–36` describes a ProveIt-specific compiler invocation and module path arrangement; treat it as that run's environment, not a general Lean rule requiring writes inside ProveIt.

## Concrete paired tests worth adding

| Family | Positive fixture | Mutation and exact expected outcome |
|---|---|---|
| Guarded image (S11) | Free lengths, plus a proved sound cover | Restrict to even or nonempty lengths: do not infer dimension reduction. Old nonrealizing tests cannot directly refute source inputs. Restrict to length100: accept `n=100` with the singleton image instead of using an unrestricted refutation. |
| Cycle statuses (S16/S17) | Known A and rules A→B, B→A give an established result | Reclassify A as offered: conditional. Remove its offer: no closed derivation. Add an unresolved cyclic conjunct plus a leaf: the diagnostic leaf list is not a sufficient repair. |
| Coverage certificate (S21) | Two certified incomparable supports and valid closure coverage | Delete one support but leave `complete=true`: reject the coverage claim. Each surviving route may still pass sufficiency checking. |
| Route-preserving repair (S26) | Proof of G actually uses A and ignores B | Remove B: preserve the closed route. Remove A: abstract A as a residual and recheck the new proof. Compare with a fresh search that may choose another route. |
| Policy dominance (S27) | An allowed proof uses `{A,B}` and a forbidden shortcut uses `{A}` | Minimize without policy, then filter: detect loss of the allowed proof. With policy-indexed labels or prefiltering, recover the allowed route. Add two methods with identical support. |
| Zero-factor formula (S38) | Product derivative identity, and logarithmic form under nonzero factors | At n=1,a=1, the product is `1-a`: its derivative exists and is −1, while the logarithmic route's nonzero guard fails. Preserve the derivative target. |
| Measure normalization/atoms (S40/S41) | Cauchy formula for a Dirac point mass with actual total mass | Use twice that mass: reject replacing M by1. A Dirac measure remains a positive fixture, so adding atomlessness is a needless strengthening. Also test a=b and distinguish the outer dt endpoint-null argument. |
| Rank stopping (S51) | A proved coverage family for all admissible observations | Let o(0)=o(1)=0 and o(2)=1. Sampling0,1 stabilizes lifted rank but misses the affine law failure `o(x)=0` at2. A rank plateau cannot certify coverage. |
| Equality versus inequality (S52) | Exact affine equality transported by a witnessed span | `1-n≥0` at n=0,1 fails at2. Reject the equality-frame proof as an inequality certificate; require a suitable domain/order argument. |

The peer's inverse-derivative, quotient-descent and strict/non-strict weighted-subgraph neighbors are also useful later mathematical fixtures (S36/S37/S39), but the first quotient/endomorphism implementation need not implement all52 families. Activate families according to supported feature, retaining an explicit unsupported status for other requests.

## Useful changes to our experiment plan

- Adopt the peer's question **“How often would a second route change the author's action?”** (`unified_report.tex:509`) as a route-versus-alternatives ablation. Measure time to first accepted proof, time to choose a repair, chosen method, and whether the second route reduces author effort. Keep helper libraries, provider calls and mathematical tasks identical.
- Use a small balanced reading pilot drawn from the proposed twenty statements (`:488`, `:508`), but do not treat twenty as a justified sample size. Include true compact statements, unjustified strengthenings, conditional drafts, correct weaker results and unsupported methods. Ask readers to recover target, domain, quantifiers, selected structures, result strength and open premises before revealing the expansion. Counterbalance presentation; use the pilot to set the main study and thresholds.
- Add a common interchange/cross-engine test as described above, with independently checked adapters. This would be new executable evidence; the current peer report only proposes it.
- Preserve our pilot-informed stopping rules, held-out tasks after interface freeze and full registration/repair costs. The peer's proposed campaign stop condition based on absence of a new unanimous row (`:510`) is an editorial incentive, not an engineering criterion: row splitting can manufacture novelty, while finding a bug or disproving a promised gain can be valuable without adding a row. Evaluate progress against concrete delivered contracts and empirical uncertainty instead.

## Leant: keep the pinned source findings, not the peer's mutable status claim

The peer's `unified_report.tex:406`, `:445` and bibliography529 say823259… is HEAD, three commits ahead and “never pushed,” and treat connector lookup failure as evidence of a private revision. Those are historical/local observations or inferences, not durable properties of a Git object. Our fresh bounded audit already observed newer HEAD2d400… and recorded changing documentation status separately. It directly reverified the immutable823259… source bytes and preserved them/excerpts; its reproducibility does not depend solely on a live GitHub URL. Failure of one connector lookup establishes an access limitation, not by itself publication history.

Retain our verified substantive findings: exact candidate type plus supplied behavior acceptance (`Main.hs:4121–4153`, `Behavioral.hs:44–55`, `Verification.hs:223–283`), the deliberately limited callback receipt, assumed provider laws and structurally sealed joint Length contracts, and the additional source-denotation obligation. The peer adds no fresh exact-tactic-path verification. Our pinned audit showed direct and chained `Try this:` replacement text can be displayed without replay of the final spelling (`Main.hs:5197–5211`, `:5240–5270`); exact displayed-text replay remains a proposed stronger requirement at that pin. Do not overwrite these source-level conclusions with the peer's more general provenance paragraph.
