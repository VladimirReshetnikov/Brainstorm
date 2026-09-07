# Fresh bounded Leant source audit for round 4

Reviewed baseline: `823259f7e3c6d24e990d3f48f78c4f1c4f88059e`. All implementation bytes came from immutable Git objects under `C:/Leant`, or from previous retained copies freshly compared byte-for-byte with those objects. No live worktree source contents, builds, backend runs, synthesis requests, or tactic executions were used.

Evidence: `docs/round-4/synthesis/evidence/leant-review/source-register.json`, with fresh Git blob IDs, SHA-256 hashes, exact read ranges, copied-source parity, timestamped metadata and retained numbered Main/Fragment excerpts. Five small modules were reread fully; four additional previous source copies were hash-reverified only. Main and Fragment were inspected only in the registered ranges. The parent-pinned Djex gitlink and its source blob/excerpt hashes were also reverified; only its two registered ranges were reread.

## Report changes required

**Replace the current-checkout assertion.** The report's sentence saying a fresh status check still finds HEAD823259... and the previous dirty files is stale. A preliminary command during this audit returned HEAD `2d400ed8178119c922d644b509d504c097e944ba` and an empty status. The retained capture at `2026-09-06T23:08:12.205571+00:00` found the same newer HEAD with modified `README.md`, `docs/length-ranking.md`, and `docs/synth-internals.md`. The checkout is being edited concurrently. Recommended wording: “The implementation baseline reviewed here is the immutable commit823259… . A later live checkout was observed separately; its timestamped metadata is retained, and its contents are outside this audit.” Do not silently promote the new HEAD into the reviewed implementation baseline.

**State exact displayed-tactic replay as a requirement, not an existing guarantee of this pin.** The current draft's sentence about replaying exact displayed executable text can read as a statement of existing Leant behavior. At the reviewed pin the suggestion path probes a tactic, may replace it with parsed `Try this:` text, and then displays that replacement without another replay. Chained `exact?` has the same distinction. This is a concrete integration opportunity and should be identified explicitly. This audit supplies static path evidence, not a reproduced failing tactic example.

Suggested replacement paragraph:

> At the reviewed commit, tactic suggestions are probed against an existing proof-state identifier, and `Try this:` output may replace the displayed tactic. The final replacement spelling is not always replayed: the direct branch displays it after the original probe, while the `exact?` chain can splice a found term into new text. A stronger suggestion contract would replay that final executable text in the intended context and distinguish closing the focused goal from completing the entire proof. This is proposed additional work at this pin, not an already established guarantee.

The source path below shows why that qualification is necessary. Later live development may already have changed it; that was deliberately not inspected.

## Exact candidate type plus behavior acceptance is supported

`src/Main.hs:4104–4153` defines `synthVerifyBehavioral`. Its call at4121–4123 passes the exact `detailedVerificationVariantText` key to `verifyBehavioralCandidateGroupsBy`, with a type-check callback and a behavioral callback for the same candidate object. The type callback at4130–4142 renders the candidate into `candidateVerificationProgram`, rejects request/fatal/errors/sorries and a missing command environment, and accepts only a successful response. The assertion callback at4144–4153 embeds the same exact variant text into `behavioralDecisionProgram` and passes response success through `behavioralCheckedResponse`.

The generated candidate check in `src/Leant/Synth/Fragment.hs:1564–1570` is:

```lean
set_option autoImplicit true in noncomputable example : (goal) := (term)
```

`src/Leant/Synth/Verification.hs:223–283` supplies the acceptance order: only a successful type callback invokes behavioral assessment; only `BehavioralSatisfied` chooses the candidate and creates the returned acceptance receipt. Behavioral failure/inconclusiveness tries another candidate rather than consuming a success slot. Exact rendered keys suppress only already accepted spellings. This supports the report's wording that candidate verification **can** combine exact-spelling type acceptance with a supplied behavioral assertion; it should not imply every synthesis mode necessarily uses that path.

`src/Leant/Synth/Behavioral.hs:44–55` produces an `example` whose target contains a lexical `let` binding of the exact candidate to the supplied name, followed by the supplied proposition, and whose proof is `by decide`. Options at57–61 set `autoImplicit false` and a heartbeat bound. The claim checked is the supplied proposition, not an automatically invented universal function contract. If that proposition is universal and supported by executable decidability, acceptance is not merely finite testing. Conversely, a conjunction of examples remains just that conjunction.

`Behavioral.hs:74–90` separately attempts the negated proposition after unsuccessful positive decision. Failure to decide the positive assertion is not itself a counterexample. Only successful decision of its negation produces `BehavioralFalsified`; failed decisions or transport failures remain inconclusive. `Main.hs:2426–2433` rejects fatal/errors/sorries/missing environment. The request timeout path retires the backend rather than treating timeout as mathematical falsity (`Main.hs:2435–2469`). These are useful existing mechanisms to preserve, not propose as missing.

## The `Verified` receipt has a deliberately limited meaning

`src/Leant/Synth/Verification.hs:44–58` explicitly documents `Verified` as an opaque callback-acceptance receipt. It is not behavioral evidence, a solver certificate or a kernel proof. Its nominal role and exact-candidate projection prevent ordinary use from coercing it into a receipt for another candidate. The report's qualification is accurate.

The distinction survives even when this particular callback has invoked Lean: the Haskell receipt stores the candidate and acceptance outcome, not a retained Lean proof object of the supplied assertion. A later consumer wanting portable logical evidence must retain/replay the stronger authority separately. This is the relevant target for the synthesis proposal's proof-linked acceptance artifacts.

## The exact displayed-tactic path is weaker than exact-candidate checking

`src/Main.hs:774–776` sends a tactic and proof-state identifier to the backend. `suggestTactic` at5145–5162 uses the current proof stack and caches suggestions by that state. `probeOnce` at5179–5191 adds a heartbeat option and accepts a response with no fatal error, no error diagnostic and a proof-state identifier. It does not independently replay every eventual displayed spelling.

- **Direct branch:** at5197–5204 the original tactic is probed and `text` becomes parsed `Try this:` output if present. At5208–5211 a textual remaining-subgoals marker is excluded and a reduced goal count causes the replacement text to be displayed as closing the goal. There is no second `probeOnce ps text` between extraction and display.
- **Chained branch:** at5240 the code probes `text ++ " <;> " ++ fin`. If `fin` is `exact?`, `renderChain` at5265–5270 parses a single one-line suggestion and returns `text ++ " <;> " ++ found`. That newly assembled final spelling is displayed at5246 without another probe. Its construction restrictions reduce risk but are not replay of the exact result.
- **Completion scope:** acceptance uses `length (respGoals v) < nGoals`, not an empty goal list. The UI says “closes the goal,” which is naturally the focused goal; it must not be summarized as having completed all goals in the user's proof. Progress suggestions are intentionally also retained and displayed when no closer is found.

This is a static observation about the branches, not a claim that a false theorem was accepted by Lean. It is closely related to the round-4 exporter lesson: the term/tactic that was checked and the final executable text shown to the user can differ.

## Length interfaces are richer than independent output tags

The report's positive claim about existing source-spine identity, argument roles, provider transfer expressions and joint-output contracts is supported, with the following boundaries.

- `src/Leant/Synth/Length/Contract.hs:29–49` supplies exact source names and explicitly assumed provider laws. Roles and transfer expressions are not inferred from a provider's name or Lean implementation. `:63–99` defines scalar and canonical binary-product contract carriers as passive assertions.
- `Length/Handoff.hs:158–223` takes an opaque verified candidate, recovers retained typed provenance, rejects retargeted fragments/premises/changed search goals, checks direct rendering, resolves exact family/provider bindings and seals the candidate-specific problem. `:227–312` handles the canonical binary-product result and configured component spines. `:408–452` resolves provider laws against retained schemes; these remain assumed or constraint-conditional summaries. `:454–510` reconstructs the exact rendering and checks its text and ordinal against the accepted variant.
- The Djex parent gitlink is `22da13fd69ce54dd1e47db9faba28eb2869629d1`. At that pin, `synthesis/internal/Language/Haskell/Synthesis/Internal/Semantic/Length.hs:354–385` permits input variables and two distinct result-component variables in a shared postcondition, while forbidding result references in preconditions. `:1344–1449` checks target shape, roles, observed inputs and result components and normalizes the shared formulas. Thus it can represent relational conditions involving both outputs; it is not merely two unrelated scalar summaries.
- `Length/Adapter.hs:1–15` explicitly bounds the claim: this is a structural association with the exact model and assumed provider laws, not a Lean source-level proof or candidate-pruning permission by itself. The report appropriately proposes an additional retained source-denotation theorem and admissible-domain bridge.

Keep the existing report wording “does not, by itself, prove an abstract transfer law about the candidate's Lean implementation.” Avoid saying that an exact identity, sealer or passive provider law already proves the mathematics of that implementation.

## Scope and suggested citations

The report can cite pinned `src/Main.hs` at4121 and5197 for the two acceptance paths, alongside its existing `Verification.hs` citation. The register includes full immutable blob identities and preserved numbered excerpts so these claims do not depend on the mutable default branch or on copying Main's entire large source file.

No Haskell compilation, Leant server execution, solver call, tactic replay or kernel check was performed in this audit. It verifies source-level control flow and evidence boundaries at the pinned commit; it neither validates the backend protocol implementation nor assigns behavior to the newer current checkout.
