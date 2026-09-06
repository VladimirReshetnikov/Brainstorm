# Laurel

## Mathematical Interfaces and Proof-Producing Residual Types

Fourth-round proof-language proposal, prepared for Vladimir Reshetnikov on
6 September 2026.

**Read `Laurel.pdf` for the article.** `Laurel.tex` is its self-contained,
editable LaTeX source. The PDF contains 35 physical pages, including the cover,
contents, appendices, and references.

Laurel proposes a mathematical authoring layer over Lean in which a fixed
object's proved properties form its usable interface. Its principal increment
is **proof-producing residualization**: an unfinished step returns a conditional
proof with explicit remaining requirements, rather than merely failing or
silently changing the theorem. The article develops alternative residual
contracts, a finite exact inference algorithm, repair after a lost hypothesis,
behavioral synthesis over realizable observations, and a staged comparison of
elaborator-level refinements with possible kernel extensions.

## What is included

- `Laurel.pdf` and `Laurel.tex`: the article and its source.
- `sources.json`: repository revisions, source locators, and the scope of
  the source inspection. The bibliography is also embedded in the article.
- `prototype/laurel_core.py`: an executable finite symbolic residual engine,
  an independent derivation checker, a narrow lost-premise repair operation,
  a small input parser, and an ordinary-Lean proof-skeleton exporter.
- `prototype/test_core.py`: boundary tests, exhaustive small-profile tests
  against a separate closure oracle, randomized tests, and finite arithmetic
  and observation fixtures.
- `prototype/bench_frontier.py`: an output-width experiment illustrating
  exponentially many incomparable residual supports.
- `prototype/examples/`: four small symbolic input files.
- `prototype/generated/`: their JSON results and uncompiled Lean exports.
- `evidence/`: retained execution results and PDF validation metadata.
- `MANIFEST.sha256`: checksums of all other files in this package.

## Evidence boundaries

The Python companion was executed. Its final retained run passed 19 boundary
unit-test methods and compared 98,304 target frontiers across 32,768 exhaustive
three-atom profiles with an independently implemented closure oracle. It also
compared 3,000 target frontiers across 500 seeded six-atom profiles and checked
budgeted runs. Exact counts, environment, and elapsed time are recorded in
`evidence/test_results.json`. The output-width experiment is a small local
measurement, not a performance claim about a Lean frontend.

The engine operates on **declared symbolic atoms and ground Horn rules**. A
rule's mathematical name is not evidence that the rule is true. The independent
checker validates a derivation relative to the declared profile; it does not
fetch or verify mathematical theorems from Lean. The JSON status
`established_in_profile` means exactly that: established relative to the
profile's declared facts and rules.

**No Lean executable was available in the working environment. None of the
exported `.lean` files was compiled here.** They quantify over arbitrary
propositions and explicit implication hypotheses. Even a successful future
compilation of those files would check only these conditional skeletons, not
the mathematical interpretation of their atom names.

The complete mathematical frontend, dependent theorem-registry integration,
Leant adapter, and editor interface are design proposals. The metatheory and
mathematical generalizations in the article have written proofs, not a new
machine-checked formalization. No human authoring study, productivity gain,
whole-repository build, or new kernel soundness result is claimed.

Both round-three synthesis main texts were read closely. Representative source
files from ProveIt, the Fermat repository, and Leant were inspected. This is not
an independent audit of every individual round-three proposal or of either
large Lean development. The reports' historical compilation results remain
attributed to those reports. In particular, the newer Leant snapshot discussed
by the syntheses is distinguished from the remote `main` revision observed in
this inspection.

## Reproduce the Python tests

Requirements: Python 3.10 or newer; standard library only. The retained run used
Python 3.13.5. From the extracted `Laurel` directory:

```sh
cd prototype
python test_core.py
python bench_frontier.py
```

These scripts write their result summaries under `../evidence/`. Rerunning them
will update elapsed-time and environment fields and therefore change the
packaged checksums. Preserve the original evidence files before rerunning when
comparing with the retained run.

Run one symbolic example and export its result:

```sh
python laurel_core.py examples/frey_a4.laurel \
  --json generated/frey_a4.json \
  --lean generated/frey_a4.lean
```

Demonstrate a bounded, inconclusive search:

```sh
python laurel_core.py examples/quotient.laurel --budget 0
```

The budget counts candidate premise combinations. An interrupted run can
retain sound conditional derivations, but does not claim complete or globally
minimal frontiers. `no_route_in_profile` means no route in this selected finite
fragment, not that the mathematical target is false.

### Symbolic input format

```text
context Demo
atoms A B C
known A
offer B
rule combine: A B -> C
show C
```

Here `B` is an authorized residual requirement. The result for `C` is
conditional on `B`; the engine does not turn that condition into a known fact.
Atom and rule names are ASCII identifiers. Comments begin with `#`. Rules are
finite ground implications, not arbitrary Lean syntax. New data witnesses,
quantifier instantiation, semantic equality, and mathematical name resolution
are outside this parser.

## Rebuild the article

A TeX installation with the packages named in `Laurel.tex` is required, including
`newtxtext`, `newtxmath`, `tcolorbox`, and `latexmk`.

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error Laurel.tex
```

Alternatively, run `pdflatex Laurel.tex` enough times to settle all references
and the contents. The article has an embedded bibliography, no external figures,
and no dependency on repository downloads or execution of the companion.

To verify the original extracted package before making changes, use:

```sh
sha256sum -c MANIFEST.sha256
```

The companion performs no network access and makes no changes to user accounts
or external repositories. Generated files and evidence are local to this
archive directory.
