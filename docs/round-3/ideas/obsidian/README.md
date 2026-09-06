# Obsidian — Round-three proof-language proposal

**Property-Aware Types and Lawful Mathematical Reasoning over Lean**  
Prepared for Vladimir Reshetnikov, 6 September 2026.

## Contents

- `obsidian.pdf`: the article.
- `obsidian.tex`: self-contained LaTeX source with embedded bibliography and diagram.
- `experiments/checks.py`: executable exact-arithmetic and scoped-protocol design probes; Python standard library only.
- `experiments/results.json`: captured results of all 608 checks.
- `source_register.json`: inspected source paths, available blob identifiers, reported repository heads, and scope of review.
- `build.sh`: reruns the probes and builds the article with three pdflatex passes.
- `SHA256SUMS.txt`: checksums for the other delivered files.

## Central proposal

Use a property-aware authoring and elaboration discipline over ordinary Lean: local proof-backed refinements for unchanged objects; theorem-backed relational signatures for lawful use of observations; and explicit preservation contracts for constructions that change witnesses. The worked cases include exact integral Frey coefficients, normalization of counterexamples, the Mellin transform of the logarithmic Bose kernel, and local iterated differentiation.

## Rebuild

Run `sh build.sh`, or run `pdflatex obsidian.tex` three times. The TeX source requires standard TeX Live packages including lmodern, microtype, AMS mathematics, stmaryrd, listings, tcolorbox, TikZ, hyperref, and xurl. No external images, bibliography database, or custom font files are needed.

To rerun only the experiments:

```sh
python3 experiments/checks.py > experiments/results.json
```

## Evidence and limitations

Both requested round-two main TeX reports were read in full. Selected source files and current Leant boundaries were inspected. The source register states exactly which files or sections were read. The first synthesis's separate generated crosswalk table was not retrieved, and no independent full reading of the nine individual proposals is claimed.

All 608 shipped Python probes passed. They are not Lean kernel proofs. They consist of 525 arithmetic instances, 32 symbolic coefficient identities, 41 negative arithmetic/format neighbors, one explicit positive satisfiability check, and nine scoped protocol-model probes. The mathematical soundness arguments in the article are paper proofs for the stated models, not a machine-checked verification of the Python implementation.

No Lean compiler was available in the execution environment. Neither mathematical repository was built or globally audited, and the proposed language, its Lean reifier, and its Lean checker are not implemented in this package. The illustrative Lean core is explicitly uncompiled. The PDF was compiled and rendered for visual inspection.

The package contains no third-party repository checkout or font files.
