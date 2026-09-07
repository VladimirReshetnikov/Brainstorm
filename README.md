# Brainstorm: mathematical proof-language design

The independent proposals explore ways to express mathematics more concisely
and naturally while retaining rigorous verification.

The latest [unified report: From Proof Obligations to Checkable Plans](docs/round-4/synthesis/unified-report.pdf)
is a self-contained critical synthesis of the nine [round-4 reports](docs/round-4/ideas):
Alder, Bryony, Clover, Fennel, Heather, Juniper, Laurel, Rowan, and Sorrel.
It compares conditional proof plans, six finite support-antichain engines,
concrete grounding, realizable behavioral observations, and Leant integration.
Fresh reproduction and adversarial review distinguish valid plans, faithful
exports, complete requests, and measured authoring benefits.

The [TeX source](docs/round-4/synthesis/unified-report.tex),
[convergence index](docs/round-4/synthesis/convergence.json),
[source register](docs/round-4/synthesis/source-register.json), and
[build and evidence guide](docs/round-4/synthesis/README.md) accompany the PDF.
All 36 documented Python invocations meet expected exits. Nineteen of twenty
supplied Lean files compile unchanged; the original failure, separately checked
repair, sharper Frey lemmas, and additional export failures are retained.

The revision incorporates the parallel [Nine Frontiers](docs/round-4/unified_report/unified_report.pdf)
synthesis at `c92ef05`, including its manual arithmetic route instantiations and
concrete list-image lemmas. It qualifies the peer's convergence and test counts,
corrects domain-certificate reuse under stronger guards, and makes the next
registry, coverage, and authoring experiments more concrete. The additional
sources, compiler checks, table reproduction, and review decisions have their
own [provenance and evidence](docs/round-4/synthesis/evidence/parallel-review).

The previous [unified report: From Properties to Proof Obligations](docs/round-3/synthesis/unified-report.pdf)
is a self-contained synthesis of the nine [round-3 proposals](docs/round-3/ideas):
Basalt, Fiber, Gneiss, Karst, Moraine, Obsidian, Schist, Tephra, and Trellis.
It evaluates scoped refinements, behavioral contracts, predictable inference,
certified observations, Leant integration, and the implementation experiments
needed to justify a new authoring layer. The review reproduces all nine Python
companions and compiles all seven supplied Lean specimens unchanged, with
precise limits on what each artifact establishes.

The [TeX source](docs/round-3/synthesis/unified-report.tex),
[90-cell convergence crosswalk](docs/round-3/synthesis/convergence.json),
[source register](docs/round-3/synthesis/source-register.json), and
[build and evidence notes](docs/round-3/synthesis/README.md) accompany the PDF.

The revision incorporates the parallel [Nine Refinements](docs/round-3/unified_report/unified_report.pdf)
review, reproduces its Frey arithmetic proofs, and adds checked abstraction
counterexamples, editing/replay requirements, and a broader evaluation plan.

The previous [unified report: Mathematical Objects, Certified Computation](docs/round-2/synthesis/unified-report.pdf)
synthesizes the nine [round-2 proposals](docs/round-2/ideas):
Accord, Cadence, Concord, Facet, Locus, Meridian, Noema, Prism, and Vantage.
It evaluates their shared architecture, mathematical contracts, distinctive
contributions, implementation limits, and questions for the next iteration.
It includes reproduced Python companions and focused Lean checks, with precise
boundaries between design proposals, finite computations, and kernel evidence.

The [TeX source](docs/round-2/synthesis/unified-report.tex),
[72-cell convergence crosswalk](docs/round-2/synthesis/convergence.json),
[source register](docs/round-2/synthesis/source-register.json), and
[build and evidence notes](docs/round-2/synthesis/README.md) accompany the PDF.

The report also evaluates the additional round-2 synthesis,
[Nine Workbenches](docs/round-2/unified_report/unified_report.pdf), incorporating
its useful toolchain experiments and test catalogue with explicit qualifications
about benchmark scope, novelty counts, and the hypotheses of implication rules.

Round 1 remains available:

- [Original nine proposals](docs/round-1/ideas): Contour, Loom, MathStep,
  Mathematical Intent / MPL, Mosaic, Motive, Outline, Reason, and Spine.
- [Codex synthesis](docs/round-1/synthesis/unified-report.pdf), including the
  original Leant term-synthesis and tactic-suggestion source review.
- [Claude synthesis](docs/round-1/unified_report/unified_report.pdf), including
  the additional Leant study and discussion questions.

The round-4, round-3, and round-2 reports each explain their relevant earlier concepts
directly; the earlier syntheses are optional background reading.
