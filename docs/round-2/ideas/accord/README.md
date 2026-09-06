# Accord: a certified worksheet language

Second-round proof-language design prepared for Vladimir Reshetnikov, 5 September 2026 (Pacific time).

## Start here

Read `accord.pdf` (37 pages). `accord.tex` is the complete self-contained LaTeX source, including the bibliography and architecture diagram. No external image assets or bibliography database are required.

The proposal extends the two Brainstorm syntheses with first-class computational result contracts, observation-specific representation interfaces, guarded calculation, and a combined proof-assistant/CAS architecture. Worked examples cover binomial inversion, autonomous higher derivatives, Abel generating functions, and branch-safe radical denesting.

## Contents

- `accord.pdf` — rendered article.
- `accord.tex` — complete LaTeX source.
- `certificate_lab.py` — small exact-arithmetic executable companion.
- `test-results.json` — results from 25 executed unit tests.
- `source-register.json` — inspected source paths, reported repository revisions, and Git blob identities.
- `build.sh` — article rebuild and companion-test commands.
- `BUILD_REPORT.json` — compilation and artifact-check observations.
- `SHA256SUMS` — checksums of the eight primary deliverable files.

## Rebuild

Requirements: a TeX distribution containing pdfLaTeX, Latin Modern, PGF/TikZ, listings, microtype, hyperref, xurl, and the usual mathematical/table packages. `latexmk` is preferred; the script falls back to three pdfLaTeX passes. The Python companion requires Python 3.10 or newer and uses only the standard library.

```sh
sh build.sh
```

To run only the companion:

```sh
python3 certificate_lab.py --report test-results.json
```

## Evidence boundaries

Accord is a design, not an implemented Lean extension. The syntax examples, protocol, and compiler architecture are proposals. The mathematical derivations are paper proofs. The Python companion is **not formally verified**, does not parse or check Lean, and is not a security boundary. Passing its 25 tests does not prove universal correctness of its arithmetic code or the proposed language.

The broader 26-case adversarial suite in Appendix B is a specification for a future Lean implementation; it is not claimed as an executed implementation test suite. The companion illustrates only a subset with exact finite calculations and explicit counterexamples.

Repository observations are from static source inspection. Neither ProveIt nor Leant was built or tested during preparation of this article. The syntheses' corpus audit and historical test receipts were not rerun. Claims about modified Leant working-tree features and tactic-suggestion details are explicitly attributed to those reports, not presented as fresh runtime findings.

Git blob identities in the source register were reported by the repository connector. They are not local SHA-256 hashes or full checkout attestations. External sources are linked in the article, not redistributed. Moving Lean/Mathlib documentation URLs are not pinned toolchains for an implementation.
