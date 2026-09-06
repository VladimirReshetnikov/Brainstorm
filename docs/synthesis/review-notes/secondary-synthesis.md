# Review of the secondary synthesis

Compared Claude's *Nine Blueprints for a Mathematician's Proof Language over Lean*
with our existing synthesis at `ef67548c92f8f6ddccdd8b3677bf4cb67e79e90d`.
The reviewed secondary source is at Brainstorm commit
`70020efd267f43131b8ef386ea40577a9e67b7cd`, branch
`claude/lean-language-improvements-report-2b93cb`, file
`docs/unified_report/unified_report.tex`. Its worktree was clean at capture.

This is another analysis of the same nine proposals, not an additional independent
proposal. The original six-feature, 54-cell convergence crosswalk is unchanged.
Three bounded independent review lanes checked conceptual additions, corpus-audit
methodology, and the current Mathlib `says` implementation. No reference repository
was modified and no Lean or Leant build was run for this amendment.

The source archives and individual file SHA-256 and Git blob identities are in
`secondary-source-register.json`. Sources were extracted with `git show` at the
immutable revisions, and compared to working files after newline normalization.
The secondary archive includes the original TeX, matrix, audit script, reported
JSON and text results, README, and build script. It preserves the claims as made;
archiving does not endorse every claim.

## Incorporated ideas and their limits

| Secondary source lines | Idea | Incorporation and qualification |
| --- | --- | --- |
| 583–598 | A method's contract is an annotated theorem type. | New §9.6 prototypes theorem-binder roles as the logical core of simple methods. Role selection, dependency policy, resources, explanation, and versioning remain additional contracts; normalizers and structural plans need richer interfaces. |
| 600–631 | Inventory existing Lean/Mathlib mechanisms; focus on the missing accounting. | New §9.7 makes this a concrete implementation hypothesis and sharpens the equally equipped Lean baseline. Existing proof terms already retain formal evidence; a durable mathematical explanation and a defined replay mode remain separate work. |
| 639–654 | Statement lint and deterministic mathematical back-rendering. | New §9.8 separates factual semantic notices from actual method obligations, and requires false-alarm evaluation. A missing explicit hypothesis need not be a defect; a printer cannot infer author intent. |
| 696–700 | Definitions and representation interfaces deserve more attention. | New §9.9 expands our existing definition-authoring question into a two-representation experiment with checked bridge lemmas and downstream cost accounting. Greater leverage is a hypothesis, not an established result. |
| 560, 491 | View composition and distinct dependency controls. | Add a three-view composition test with dependent guards and competing routes; distinguish local premises, library inventory, and transitive axiom policy. |
| 633–637, 656–658 | Instrument actual proof states and export ledger tasks. | New §10.1 proposes a bounded stratified pilot and contextual benchmark export, with settled or explicitly represented shared constraints and theorem/module-level holdouts. |

Questions Q1, Q5, Q6, Q7, and Q9 now ask for these concrete experiments. The work
plan includes bounded measurement before choosing a routine profile. It does not
require an expensive whole-corpus instrumented build before the first prototype.

## Why several stronger conclusions were not imported

- **Convergence is not a probability estimate.** Secondary line 704's claim that
  the outline has a low chance of being wrong is unsupported. Shared prompts,
  repositories, sources, and design traditions are correlated. Semantic and
  implementation specifications remain open alongside empirical questions.
- **A statement seal needs more than one recorded expression.** Lines 549 and
  610 simplify the lock to one elaboration and an `Expr`. Our retained contract
  also accounts for context, dependencies, resolved structures, and remaining
  constraints; it is not weakened by this amendment.
- **Theorem attributes do not collapse all method costs.** Line 596 understates
  metadata, interpretation, diagnostics, and policy maintenance. An undischarged
  premise is an open obligation, not a proof of invalidity.
- **Existing tactics do not establish cheap natural authoring.** The supply
  inventory identifies reusable infrastructure. It does not demonstrate that
  mathematical input selection, explanation, or repair is merely a recording task.
- **Definitions have not been shown to dominate costs.** CAST and INDEX counts
  do not identify the causal origin of the work or compare representation designs.
- **A lexical absence of `sorry` is not proof completeness.** Secondary line 313
  draws this inference without compiling or auditing dependency assumptions.
- **Some exclusivity claims are too strong.** For example, secondary line 573's
  claim that no report discusses universe constraints conflicts with Loom's
  discussion at lines 563–565 and 589 onward. Secondary line 481 assigns Loom
  distinct `obtain` and `choose` forms although its keyword list and grammar use
  `choose` (Loom lines 62 and 922); the semantic distinctions are discussed at
  526–543. We retain nonexclusive profiles and the primary-source crosswalk.
- **Uncalibrated migration percentages are not acceptance criteria.** Halving
  bridge density or lifting half the corpus (secondary 713–714) would reward
  counting conventions before their relation to user effort is established.

## Mathlib `says`: exact source boundary

The inspected Mathlib revision is
`81a5d257c8e410db227a6665ed08f64fea08e997`, matching ProveIt's manifest. The
checkout and selected files were clean. Source and supplied tests are archived
with their license; the tests were read, not executed.

In `Mathlib/Tactic/Says.lean`, lines 90–108:

- Normal `X says Y` executes **Y only** at 107–108, skipping discovery X.
- With verification enabled, or with `CI` present unless disabled by the
  corresponding option, it executes **X only**, captures its first suggested
  tactic, strips source positions, pretty-prints, and compares the suggestion
  against Y (95–106). That branch does not independently execute Y.
- `X says` runs X and offers source containing the resulting suggestion.

Suggestion capture at 52–75 uses structured `TryThis` information and parses text
when needed. Correspondence means agreement of the rendered suggestion syntax,
not equality of proof terms or independent same-state replay of both scripts.
Y can still contain automation; no sealed environment, axiom allowlist, or
proof-term artifact follows from `says` alone. This is a useful narrower contract,
and supports the existing Leant recommendation to replay exact displayed edits.

The supplied `MathlibTest/Tactic/Says/Basic.lean` tests illustrate normal-mode
noncorrespondence (45–49), mismatch detection (51–62), absent suggestions (78–88),
and CI behavior (90–105). This source inspection is not a runtime test receipt.

## Corpus audit: what its numbers mean

The archived JSON reports 1,004 files, 12,322 detected theorem/lemma declarations,
and 90,637 classified entries. The class counts sum to that total. The seven
families labeled reconstructible sum to 29,303 (32.3%); ASSERT is 28,727 (31.7%).
ANALYSIS is 6,524 (7.2%) versus 38/1,329 (2.9%) in the recorded sample. Our report
attributes these as lexical classifications, not a measurement of removable work.

The audit-review lane independently reran the script's `summarize` function on
the full FabiusFunction subtree, bypassing its output-writing `main` and disabling
bytecode writes. All 17 serialized summary fields reproduced at ProveIt commit
`7c4e3f109405b9805b35d27ae96bf09c7ee5f3d5`; the subtree was clean. This was a
read-only Python classification run, not Lean compilation. The 23-file comparison
sample was not rerun: neither the JSON nor the documented command preserves its
exact input paths. The placeholder in the appendix is insufficient to reconstruct
that sample without making additional choices. The marker table, including the
repository-wide heartbeat counts, is also not produced by the shipped script.

The script recognizes selected first keywords on source lines inside heuristically
detected proof bodies. It does not count all tactic executions. Inline theorem
bodies such as `:= by omega`, nested tactic sequences, and continuation lines can
be missed. Names used in a proof can trigger category changes without changing
its reasoning: renaming a hypothesis to contain `Continuous` or `cast_` can change
an `exact` entry from STRUCT to ANALYSIS or CAST. These properties preclude calling
the reconstructible share a rigorous lower bound, a constant cost, or measured
author effort. ASSERT counts also do not measure assertion-subproof coverage.

The per-file prose overstates its own artifact: secondary line 303 gives a
10–71% range, whereas the archived low-density list includes
`TransseriesDifferentialClosure` at 1.5%. Its top-density list begins with
ThueMorseBlockProducts, PerronRootEnclosure, BellShiftEGF, and RieszSharpness;
it does not support the statement that the eight highest are all EGF, umbral,
and Stirling-number files. These secondary claims are not repeated in our report.

The constructive use is to choose a broader sample, calibrate labels against real
goals and human judgments, and measure fixed-budget adapter success with all
author inputs and library work accounted for. Corpus classification does not
replace Lean checking, proof coverage, usability studies, or a causal comparison
between representations.
