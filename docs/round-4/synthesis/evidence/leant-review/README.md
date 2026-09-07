# Fresh pinned Leant source review

Baseline: `823259f7e3c6d24e990d3f48f78c4f1c4f88059e`.

`capture.py` reads immutable Git objects under `C:/Leant`, byte-reverifies all nine source copies retained by the previous round, verifies the parent-pinned Djex gitlink and source/excerpt hashes, captures Main excerpts, and records independently timestamped live HEAD/status metadata. It never reads live worktree source contents or writes outside this evidence directory.

`finalize-register.py` captures narrow direct acceptance helpers from Main and Fragment, then records the exact static read scopes. `source-register.json` distinguishes full fresh reads, selected fresh ranges and hash-only revalidation. Five small modules were reread fully; four previous modules were reverified only. Large source blobs are represented by hashes and numbered excerpts rather than duplicated in full.

The linked review memo is `../../review-notes/leant-baseline.md`. Its material new finding is that pinned candidate type/behavior acceptance checks the same exact candidate text, while the tactic-suggestion path can display transformed `Try this:` text without replaying that final spelling. Exact displayed-text replay is therefore a proposed stronger boundary at this pin.

Scope: static read-only source review. No builds, backend/service runs, tactic execution, external source edits, or Git mutations. Live metadata changed during the review; only the timestamped register describes its recorded observation. The newer checkout's implementation is outside scope.
