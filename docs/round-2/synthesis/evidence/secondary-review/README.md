# Review of the additional round-2 synthesis

The input is `docs/round-2/unified_report/` at Git commit
`84af03f49f89a31b47ff3416ccdbc9180fd6b438`. The current branch incorporated that
commit by a clean fast-forward from `d9387e521a559d6a18cedd58cae1dcebad7d7cff`.
The original secondary report, its tables, experiments, and logs are unchanged.

- [Source register](source-register.json): exact Git blobs and separate checkout
  hashes for all 17 imported artifacts; checked by
  [verify_secondary.py](../../scripts/verify_secondary.py).
- [Design review](design-review.md): useful additions, inherited ideas,
  mathematical corrections, and evaluation implications.
- [Tally review](tally-review.md): reproduction of the three tables and audit of
  counting units, coverage, editorial judgments, and novelty claims.
- [Toolchain review](toolchain-review.md): source-based assessment of existing
  tactics, polynomial representations, trust, and the limits of the supplied
  performance evidence.
- [Fresh Lean probes](lean/README.md): six accepted declarations, axiom output,
  source/log hashes, exact toolchain, and reproduction instructions.
- [Table reproduction receipt](tables/receipt.json) and
  [source locators](tables/negative-source-locators.json): isolated generation,
  parsed-row equality, and all 182 original negative-suite rows.

## Incorporation decisions

The report adopts the finer convergence analysis with its editorial status
visible, the combined negative-test backlog with its original subcases preserved,
the comparison against existing Lean workspace mechanisms, explicit current-tactic
controls, and a checker-soundness-first implementation milestone. It also adds
tests of actual CAS-generated obligations to the proposed Leant evaluation and
distinguishes a development example from a genuinely unseen holdout.

Three implication rules require mathematical repair: a complete solution set
needs soundness as well as coverage; an open neighborhood helps only when the
identity holds throughout it; and collapsed interval bounds can prove equality.
These become explicit examples and proposed tests in the revised report.

The historical polynomial timings remain attributed observations, not fresh
measurements. The supplied checker lacks a proved interpretation and soundness
bridge to the original mathematical target, and its fixed short factor does not
benchmark general dense polynomial multiplication. Fresh focused Lean checks
establish the availability of the selected tactics and the observed axiom
difference; they do not establish CAS performance or generic checker soundness.

Table generation reproduces the author's manual coding. It does not establish
independent empirical consensus, validate every feature classification, or prove
that features outside the inherited-feature group are new. The secondary
synthesis remains separate from the nine input proposals in every source count.
