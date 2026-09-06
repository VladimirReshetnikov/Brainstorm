# Read-only audit of current Leant tactic suggestions

This is a static source review performed for the synthesis task. No source in `C:\Leant` or its dependencies was changed, no Lean or Cabal build was launched, and no interactive proof/test suite was run. Findings below distinguish directly observed control flow from unexecuted triggering examples and proposed tests.

## Snapshot and scope

The current `C:\Leant` HEAD is `3a40904be8a410d832d9ab6900b3d3e7b425eccb`. The working tree is dirty, including `src/Main.hs`, `README.md`, `src/Leant/Synth/Verification.hs`, Cabal metadata and unit tests; therefore HEAD alone does not identify the inspected implementation. The inspected `Main.hs` has 269 changed lines in the Git diff summary (including additions and removals); these observations concern the current working-tree file, not a claim about committed HEAD or any earlier memory snapshot.

SHA-256 at inspection:

| File | SHA-256 |
|---|---|
| `C:\Leant\src\Main.hs` | `4A081070EF63AB43379528E9114802F3ACBEB5962E3FA980479DD31BA42DFA43` |
| `C:\Leant\src\Leant\Backend.hs` | `EFE32AD4130D226F283E397924DAD48BC6438CB586F2EEA27BF3F92C71DE8EFC` |
| `C:\Leant\README.md` | `355D6029EEABFA0791D6C67A82ECD2711671178038A4DBBE30C111BF11CB1D88` |
| `C:\Leant\test\prove-suggest.txt` | `26CC0811CE647ABE6AE0212D2D3DDC7FEEC95AA3F9AB742DA20E8699C46CB4F9` |
| `C:\Leant\test\prove-suggest.golden` | `2842EAE4230E1FC2957AF0EEDD5682F04AFD9A130A127382B626C3F8168E792A` |

The primary boundary reviewed is `Main.hs` 4833–5480: goal/result accessors, `parseTryThis`, `suggestTactic`, tactic application, `:auto`, and `:qed`. Supporting paths are backend request/death handling, current documentation, the suggestion golden fixture, and the test inventory.

I also read the installed LeanInteract interface and a locally cached REPL source tree at:

`C:\Users\vresh\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\lean_interact\cache\augustepoiroux\repl\repl_v1.3.18_lean-toolchain-v4.32.0\REPL`.

This establishes an available local protocol's meaning, not that every Leant invocation uses that backend binary. Leant permits backend overrides and discovers cached executables (`Backend.hs` 159–198).

## Findings and limits

### 1. High priority: the advertised suggestion can differ from the tactic actually checked

**Observed.** `probeOnce` submits the candidate tactic, wrapped in a 20,000-heartbeat option, to the original proof-state ID (`Main.hs` 5075–5087). On success, `probe` replaces the candidate text with `parseTryThis` output if present (5099). It uses the original response's remaining-goal count to annotate that replacement as closing (5100–5107), then caches/displays it (5172–5181). It does not rerun the exact selected replacement at that original proof state before assigning the annotation. For `exact?` chains, `renderChain` constructs `text <;> found` from a single reported `Try this` message (5161–5166), again without replaying the newly constructed displayed string.

The same substitution occurs during actual tactic application: `applyTactic` executes the supplied tactic, then stores `parseTryThis` output as its script entry while retaining the proof-state ID returned by the original tactic (5255–5280). `:script` may therefore represent a replacement text that has not produced the stored proof-state transition.

**Trigger/risk.** A suggestion-producing tactic can close or advance the probe yet print a replacement that parses differently, relies on a context name unavailable when replayed, contains layout-sensitive multiline code damaged by trimming, or simply has different behavior. `parseTryThis` trims each line and strips bracket markers (4861–4878); this is a presentation parser, not a semantic identity check. These are plausible triggers derived from the control flow, not reproduced failures in this review.

**Limits.** Ordinary trusted Lean tactics usually produce usable suggestions; this finding does not assert that all existing suggestions are wrong. It is an evidence-binding gap: a proof-state receipt for the generating tactic is being used as if it certified the displayed replacement. Suggestions themselves do not advance the authored proof stack. Furthermore, standalone `:qed` re-elaborates the entire assembled replacement script, so many bad replacements are caught before saving (finding 4).

**Recommendation.** Bind the success annotation and stored script entry to exact executable text replayed at the original state; preserve the originally applied tactic until replacement replay establishes the intended transition. For a chain, validate the final complete chain, not just the fragments from which it was assembled. Store the original and selected forms separately for provenance if useful.

### 2. High priority for completion claims: empty goals are not the same as a completed proof

**Observed.** `probeOnce` accepts a response if there is no fatal field, no error diagnostic, and a `proofState` (5083–5087). `respGoals` returns an empty list for absent or malformed `goals` (4836–4839). The suggestion and chain logic classify closure by reduced goal count (5106, 5140, 5151); `applyTactic` accepts the same broad successful-response shape (5260–5280). `formatGoals` prints “All goals accomplished” solely on an empty list (4844–4846), and `:qed` gates only on the locally stored goals being empty (5416–5425). The file does not read `proofStatus`.

**Protocol evidence.** The cached REPL's `REPL/Main.lean` 249–298 distinguishes an empty tactic goal list from a complete proof: it checks the root assignment and expected type, rejects remaining expression metavariables, submits the term to the kernel, checks `hasSorry`, and only then returns `Completed`. Empty visible goals can instead yield `Incomplete: contains metavariable(s)`, `Incomplete: contains sorry`, an `Error: ...`, or `Not verified: more than one initial goal`. These statuses are placed in a separate `proofStatus` field (300–323), rather than necessarily producing an error diagnostic. `REPL/JSON.lean` 240–256 serializes that field alongside goals and proofState.

**Trigger/risk.** A tactic that removes visible goals while leaving a sorry, a root metavariable or a term rejected at the proof-status validation stage can receive the same completion presentation as a checked term. The comment-text safeguard for `-- Remaining subgoals:` (5101–5105) recognizes one rendering convention and does not cover the authoritative status variants. Malformed response data can also resemble empty goals in the current decoder.

**Essential qualification: current-goal versus whole-proof closure.** A response with ordinary open goals can still legitimately certify progress on the focused goal. The golden fixture explicitly uses “closes the goal” for `omega` taking a conjunction proof from two goals to one (`test/prove-suggest.golden` 52–64). Therefore requiring whole-proof `Completed` for every useful local suggestion would be incorrect. The installed Python interface also documents `proof_status` as the status of the **whole proof** (`lean_interact/interface.py` 619–630). A correction should retain local-progress/current-goal annotations and reserve “whole proof complete” for the appropriate stronger evidence. Root-level `Error` or incomplete-with-no-goals must not be silently promoted to that stronger status.

**Recommendation.** Parse response shapes strictly; capability-negotiate status support; retain separate states for transition accepted, current goal closed, whole proof completed, draft admitted, incomplete, and backend status unknown. Check exact replacement replay as in finding 1. Where older protocols lack proof status, report that limitation or perform an explicit final validation rather than treating absence as success.

### 3. Medium priority: speculative suggestions share the session process and timeout fate

**Observed.** Probes call `runTactic st ps` against the live backend (5079, 758–764), with a heartbeat limit. They do not submit an isolated worker request. The original proof-state snapshot is reused and the authored stack is not advanced by a suggestion. Cached REPL `Snapshots.lean` 150–160 shows tactic evaluation producing a new snapshot, which supports that intended logical-state separation.

However, `Backend.request` waits using the session request timeout (`Backend.hs` 616–635). On `RequestTimeout`, `runPayloadAfterBackend` calls `backendDied` (Main.hs 779–786). That kills the backend, prints/preserves the existing script, leaves prove mode, clears backend-local sorry handles, and invalidates derived environments (707–716; 5187–5196). The current README explicitly documents this behavior (334–336).

**Trigger/risk.** A probe whose external execution, uninterruptible or non-heartbeat work, memory consumption, or crash crosses the process boundary can interrupt the user's proof session even though it was only advisory. Heartbeats control ordinary Lean work; they are not a process-isolation or universal wall-clock mechanism. Snapshot restoration does not reverse arbitrary host I/O or process-global effects.

**Limits.** The implementation already handles backend death conservatively: it does not continue using stale proof-state IDs. A heartbeat exhaustion is intended to be a normal tactic error and preserve the session. No backend failure, external side effect, or loss of script was reproduced here. This is an architectural exposure, not a finding that immutable proof snapshots mutate unexpectedly.

**Recommendation.** Use a separately owned advisory worker where viable, or explicitly document the shared-fate tradeoff. Give advisory work its own wall-clock and memory budgets. Preserve the current emergency-exit and stale-ID protection regardless of isolation strategy. Backend stdin write/flush currently occurs before the timed response wait (Backend.hs 619–625), so a claimed complete request timeout should also specify whether transmission is bounded.

### 4. Draft admission is intentional, but “saved theorem” must not be confused with a sealed proof

**Observed.** Prove mode deliberately starts from an `example ... := by sorry` hole (Main.hs 5207–5218) or resumes a reported sorry (5226–5232). `cmdQed` warns when the script text contains the substring `sorry` but continues (5430–5432). For a standalone statement, it builds a theorem declaration and submits the whole assembled script through `runCurrentCmd` (5439–5454). If errors are reported it stays in prove mode; otherwise it records the environment and prints `saved: theorem ...` (5463–5475). A data-valued target can fall back to `def` (5444–5461). For a resumed sorry, `:qed` prints the replacement block and leaves; it does not save/recheck the original enclosing declaration (5433–5438).

`printResponse` treats only error/fatal diagnostics as failure and surfaces sorries separately (835–861). It suppresses warnings beginning “declaration uses” (849–851). No transitive axiom allowlist is applied by this `:qed` path. Textual substring checking cannot reliably detect aliases, macros expanding to admissions, imported admitted lemmas, or all unapproved axioms; it also flags comments or names containing that substring.

**Interpretation.** Allowing a draft declaration with a sorry is normal Lean exploration semantics and is explicitly accommodated by the implementation. This is not evidence that Lean's kernel accepted a theorem without its declared axiom dependency. The issue is status granularity relative to documentation saying `:qed` saves a “finished proof”/“real theorem” (README 134–136, 330–333). An admitted theorem is a real environment declaration but not a sealed proof under the reports' stronger acceptance policy.

**Recommendation.** Preserve a deliberate draft-save operation, visibly classify admitted/conditional declarations, and add a separate sealed finish that rechecks exact statement identity and the transitive axiom policy. Do not describe all saved declarations as independently checked completed proofs. A source-only resumed-sorry result should remain clearly labeled as replacement text awaiting incorporation and checking.

## Python parity and current tests

There is **no current tracked Python Leant REPL or suggestion implementation** in this checkout. `git ls-files '*py' '*prove*' '*suggest*'` lists corpus/quality scripts, suggestion transcripts, and related reporting artifacts; root directory inventory contains the Haskell application and launcher, not a `leant.py`. Current untracked Python files concern behavioral corpus probes. Thus there is no applicable two-language Leant suggestion parity claim to verify here; a historical Python implementation would need an explicitly identified revision/path.

The installed **LeanInteract Python API**, a separate dependency, exposes `ProofStepResponse.proof_status` with whole-proof semantics (`interface.py` 619–630). Its generic `lean_code_is_valid` method accepts an explicit `allow_sorry` option, defaulting to true (581–600). This demonstrates a useful separation of syntactic acceptance and admission policy, not that its consumers automatically enforce strict proof completion.

`test/prove-suggest.txt` and `.golden` cover ordinary introduction, conjunction goals, `:suggest` cache display, undo, exact-term suggestions, existential decomposition, and induction plus `simp_all`/`omega`. They include a two-to-one goal transition, making the local-goal meaning concrete. The runner `test/run-tests.sh` executes scripted inputs against the actual REPL and compares filtered output. These files are useful positive-path regression tests, but no fresh run occurred in this review.

The current `test-unit/Spec.hs` has backend lifecycle/isolation and synthesis verification tests, including fake sorry responses, but searches for `proofStatus`, `Try this:`, and suggestion-policy code found no direct tests for this suggestion path. The Cabal test suite's module list includes backend and synthesis modules, not the executable's `Main.hs` suggestion functions (`leant.cabal` 122 onward). This is a bounded source-inspection observation, not proof that no external test ever covers a case.

## Recommended tests before stronger claims

1. **Exact displayed-text replay:** a tactic advances/closes but emits an invalid or differently scoped `Try this` replacement. Do not annotate or record that replacement as checked. Include multiline indentation, multiple alternatives, bracketed markers, and the composed `exact?` chain.
2. **Whole-proof status matrix:** zero visible goals with `Completed`, `Incomplete: contains sorry`, `Incomplete: contains metavariable(s)`, root `Error`, unverified multiple-root status, missing status, and malformed goals. Ensure distinct outcomes and capability handling.
3. **Legitimate partial progress:** two goals → one with `Incomplete: open goals remain`; preserve a current-goal-closure annotation while withholding whole-proof completion. Include shared-metavariable goals to test the proposed stronger transition contract.
4. **Script/state association:** apply a question-mark tactic, inspect `:script`, undo/reapply, and replay the entire stored script. Assert that each recorded replacement corresponds to the originally applied transition or is separately marked unreplayed.
5. **Draft versus sealed finish:** literal sorry, macro-expanded sorry, an admitted helper, an approved classical dependency, an unapproved axiom, and harmless `sorry` text in a comment/name. Draft save should retain status; sealed save should enforce the actual dependency policy.
6. **Timeout and worker fate:** normal heartbeat exhaustion, backend wall-clock timeout, crash, and cancellation during a probe. Verify printed script recovery, cleared proof-state/sorry IDs, no later stale submission, and—if isolation is added—continued health of the user's backend.
7. **Resumed-hole versus standalone finish:** distinguish printed replacement source from a replayed and saved whole declaration; never infer the enclosing theorem's completion from one resumed hole.

These findings support the reports' proposals for exact candidate identity, typed result statuses, isolation, and sealed evidence. They do not show a kernel soundness defect and should not be used to dismiss Leant's separate synthesis verification machinery. The directly supported conclusion is narrower: current tactic-suggestion and prove-mode UX has weaker evidence boundaries than the unified language architecture proposes.
