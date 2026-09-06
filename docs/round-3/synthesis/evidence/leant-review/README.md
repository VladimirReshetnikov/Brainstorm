# Immutable Leant review evidence

This folder supports `../../review-notes/leant-update.md`. It records a static read, not a build or runtime test. Sources were obtained with `git show` at Leant `823259f7e3c6d24e990d3f48f78c4f1c4f88059e`; the mutable `C:/Leant` worktree was not a source of code bytes and was not modified.

- `source-register.json`: complete nine-file read scope, original Git blob IDs and SHA-256 hashes, immutable permalinks, command inventory, and the independently captured live status snapshot.
- `source/`: byte-for-byte immutable source copies for six requested modules and three direct implementation dependencies.
- `djex-register.json` and `djex-length-excerpts.txt`: the two bounded line ranges reviewed in the imported product-contract implementation, pinned through Leant's submodule gitlink. The register hashes the complete source blob and retained excerpt separately; only the excerpt was read.
- `capture.py`, `capture-djex.py`, `annotate-scope.py`: read-only source capture and editorial metadata helpers. They invoke Git read operations or edit this evidence folder only. Run with `python -B` from the Brainstorm root using the commands recorded in the register. Re-running capture preserves the original timestamped status snapshot rather than pretending it is a fresh live snapshot.

The historical Djex foundation report mentioned in the register was consulted for navigation only. Its date-specific integration status is not current implementation evidence. No Haskell, Lean, Lake, SMT, synthesis, or tactic-suggestion execution was performed in this review.
