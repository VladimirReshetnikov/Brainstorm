# From Proof Obligations to Checkable Plans

[Read the PDF](unified-report.pdf) · [TeX source](unified-report.tex) ·
[Convergence index](convergence.json) · [Validation receipt](validation.json)

This 28-page, self-contained report critically synthesizes all nine round-4 packages:
Alder, Bryony, Clover, Fennel, Heather, Juniper, Laurel, Rowan, and Sorrel.
It incorporates the reconciled round-3 conclusions directly, evaluates the
actual prototypes, develops shared support and observation semantics, and
proposes ten concrete questions for the next implementation/evaluation round.

The current branch was fast-forwarded to fetched `main` at
`58ced1ce667b3ba1ed162a0c6280959536c8bc5f` before this work. The
[source register](source-register.json) binds all **159 input artifacts**
(**325 supplied PDF pages**, **20 supplied Lean sources**) and four secondary
round-3 source/PDF files to that immutable snapshot. Input PDFs were not rebuilt.
The nine input packages and `C:/ProveIt` and `C:/Leant` were treated as read-only.

## Findings worth carrying forward

- Six companions implement finite antichains of sufficient premises. Clover
  supplies concrete term grounding, Heather a behavioral list frontend, and
  Rowan diagnostic frontiers and semilinear observation domains. The shared
  design is correlated architectural agreement, not nine usability experiments.
- A diagnostic explanation, a checked conditional route, a complete minimal
  family, a compiled theorem, and completion of the author's request have
  different guarantees. The report supplies a common semantics for each.
- Realizable affine frames and semilinear images fit a common source-domain
  interface. Empty element types and correlated observations change which
  behavioral equalities are valid; an abstract failure also needs source
  realization and negative transfer before it refutes a candidate.
- Fresh probes expose Clover name-hygiene failures, Heather tactic sequencing,
  Sorrel's total-support versus residual-support route selection, Rowan's
  diagnostic cycle boundary, and stale positive files left by Fennel/Heather
  after later unsuccessful requests reuse output directories.
- Laurel's symbolic lost-premise repair, Juniper's independent coverage checker
  and sharper first-coefficient premise, Clover's grounding profile comparison,
  and the domain-specific analytical examples are retained as distinct gains.
- The pinned Leant review confirms exact candidate type-and-behavior acceptance.
  Some tactic-suggestion paths at that pin display replacement text without
  replaying the final spelling. The proposed integration keeps that remaining
  requirement explicit; later live Leant revisions were not audited.

## Exact validation boundaries

The three [reading memos](review-notes) cover all reports and companions.
The [convergence index](convergence.json) preserves each lane's native dimensions
and its qualified implementation classifications. Its 102 heterogeneous cells
and 325 anchor occurrences are an evidence inventory, not a voting score.

[Python validation](evidence/python-validation.json) checks **36 recorded
suite/demo invocations**, all with their expected exits: 34 zero exits and two
intentional Alder rejection exits. It binds all 159 original files, 43 copied
Python/grammar sources, 127 retained post-run artifacts, and the additional
adversarial receipts. The Fennel/Juniper common-fragment audit compares 128
profiles and 768 target frontiers. None of these finite checks is a proof of
the Python implementation or a human productivity measurement.

[Original Lean checks](evidence/lean/execution-receipt.json) attempted every
supplied source, byte-identically, under Lean 4.32.0:

- **19 of 20 files compile unchanged.** Heather's `even_reverse_length.lean`
  fails with “No goals to be solved” after simplification already closes its goal.
- Accepted declarations comprise **22 generic conditional implication theorems**
  and **14 concrete mathematical declarations**. The twentieth file's rejected
  concrete declaration is separate. Laurel's accepted cycle module has no theorem.
- Clover's seven core axiom queries report no axioms. Those queries are not an
  audit of all other original declarations.

[Separate Lean follow-ups](evidence/lean/followups/execution-receipt.json) record:

- Three Clover adversarial exports rejected by Lean after their Python plans pass.
- Sorrel's selection specimen accepted as a valid conditional theorem, despite
  choosing new work when another route is already available.
- Heather's single tactic sequencing repair accepted with the theorem unchanged.
- Four sharper Frey helper theorems, two examples, and four axiom queries accepted.
  The first coefficient uses `p >= 2`; the `p = 3` fixtures distinguish it from
  the fourth coefficient. The reported axioms are `propext`, `Quot.sound`, and
  `Classical.choice` for three of the four theorems. No Fermat equation or entire
  curve construction is involved.

Lean runs were serialized. Existing ProveIt Mathlib dependencies were used
read-only through explicit `LEAN_PATH`; no Lake/dependency build or external
cache/source write occurred. Compiler acceptance is under those existing
artifacts, not a fresh complete audit of their compilation. No full Leant or
ProveIt build, synthesis backend execution, verified frontend, or authoring
study is claimed.

The [Leant source register](evidence/leant-review/source-register.json) separates
the immutable `823259f7...` audit, exact full/partial/hash-only read scopes, and
timestamped metadata for the later mutable checkout. The report is not an audit
of that later revision.

## Reproduction

From this directory, with Python, pdfLaTeX, Poppler, Pillow, and pypdf available:

```powershell
python -B scripts/verify_sources.py
python -B scripts/verify_convergence.py
python -B scripts/verify_python_evidence.py
./build.ps1
python -B scripts/render_review.py
python -B scripts/verify_report.py
```

The default validators check retained evidence; they do not rerun the experiments.
The lane evidence folders contain the isolated reproduction/audit runners and
exact commands. `scripts/check_lean.py` reruns all 20 original attempts serially;
`scripts/check_followups.py` then reruns the six additional cases. Both require
the recorded toolchain/dependency layout or an explicitly adapted environment.
Original compiler failures are retained as findings, not silently fixed.

`build.ps1` performs three strict passes without shell escape and rejects final
reference, glyph, and overflow problems. All pages are rendered and visually
reviewed; [visual-review.json](evidence/visual-review.json) binds that review to
the final PDF. The retained [build receipt](evidence/build-receipt.json) and
[log](evidence/build.log) bind the final source/PDF pair. Intermediate `.build`
and `.qa` files are ignored.

`artifact-manifest.json` binds every delivered package artifact except itself
and the regenerable final validation summary. After deliberate changes, rebuild,
review the new PDF, refresh the corresponding receipts, and explicitly run
`python -B scripts/verify_report.py --seal`. Default verification refuses drift.
Copied upstream metadata remains historical; the root execution receipts are
the authority for the new checks.
