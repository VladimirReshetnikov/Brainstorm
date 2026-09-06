# Juniper
## Property-Directed Mathematics with Explicit Obligation Frontiers

Fourth-round proof-language proposal prepared for Vladimir Reshetnikov.
September 6, 2026.

## Read the article

`Juniper.pdf` is the compiled, 37-page article. `Juniper.tex` is its
self-contained LaTeX source, including its bibliography and diagram. No external
figure files, bibliography database, or font files are needed.

Juniper proposes a property-aware authoring discipline over ordinary Lean,
initially without changing the kernel. Its specific increment is a semantics of
unfinished steps as residual proof telescopes, together with a finite antichain
algorithm that exposes alternative sufficient sets of additional premises.
Conditional routes never become unconditional facts. The article gives paper
proofs of soundness, termination, relative completeness, schedule independence,
and a separately checkable completeness certificate.

Worked examples cover autonomous differentiation, exact Frey quotients, analytic
inverse derivatives and differential polynomials, quotient descent, and
proof-linked behavioral synthesis. The two round-three syntheses are reviewed
together, with an explicit distinction between inherited architecture and this
proposal's contribution. See `source-manifest.json` for inspected source paths,
immutable revisions, and the limits of the review.

## What is implemented, and what is not

The Python companion implements only the **finite ground propositional** slice:
a small parser, an antichain solver, independent derivation/coverage validation,
and a generic Lean implication exporter. Atom names are opaque identifiers.
`Open` does not invoke a topological prover, and `Positive` does not invoke an
arithmetic prover. Rules are supplied assumptions in this reference language.

The richer mathematical syntax in the article, Lean theorem registration,
mathematical reification, property-aware Lean elaboration, editor integration,
and a verified CAS are **proposals**, not implemented features of this archive.
No full ProveIt, FLT, or Leant build and no human productivity study was run.

`companion/Generated.lean` contains generic implication proofs, parameterized by
propositions and rule hypotheses. It has no `sorry` or `axiom` declarations, but
it was **not compiled**: no Lean or Lake executable was available in the working
environment. Python validation is not a substitute for Lean kernel acceptance.
Compilation of this file would check only the generic implication assembly, not
a mathematical interpretation of the source atom names.

## Rebuild the PDF

A normal TeX Live installation with pdfLaTeX and the packages named in the
preamble is required. No shell escape or network access is needed.

```sh
./build.sh
```

The script uses `latexmk` when available, otherwise three pdfLaTeX passes.

## Run the executable companions

The scripts use the Python standard library only and require Python 3.10 or
newer. The recorded runs used Python 3.13.5.

```sh
cd companion
python test_frontier.py
python inverse_polynomials.py
python juniper_frontier.py example.jnp \
  --json example-result.json --lean Generated.lean
```

The two experiment scripts regenerate their JSON reports in the current working
directory. Run them from `companion` as shown. To retain fresh console logs:

```sh
python test_frontier.py > test-run.log 2>&1
python inverse_polynomials.py > inverse-run.log 2>&1
```

The supplied example has two conditional routes for `QuotientReady`:
`{Open, Positive}` and `{DirectGerm, Positive}`. The seedless self-dependent
`NeverNeeded` goal has no route in the supplied finite profile. This means
non-derivability in that profile, not that its proposition is false.

A bounded attempt can be demonstrated with:

```sh
python juniper_frontier.py example.jnp --max-attempts 2
```

`--max-attempts` bounds attempted rule/support combinations. It is not a wall
clock deadline or a complete memory limit. On interruption, found routes remain
valid, but full coverage and global minimality are not asserted. The unlimited
algorithm can have exponentially many minimal supports, even for small input
rule sets.

## Recorded results

- 32 unit tests passed, with zero errors or failures.
- 400 generated profiles, each with seven atoms, four offered premises, and
  twelve rules, matched an independent exhaustive subset/closure oracle on
  2,800 goal frontiers. This covers 6,400 offer-set assignments.
- All 400 reversed-rule schedules produced the same frontiers.
- 189 admissible Frey arithmetic fixtures satisfied both divisibility claims.
  Boundary fixtures separately exercise the removed premises.
- The inverse-polynomial companion generated orders one through six, compared
  the first four against separately written expected expressions, and performed
  38 degree/weighted-degree checks across nineteen monomials.

These are finite tests of the reference implementation, not a formal proof of
its source code. The article's all-input algorithmic and mathematical guarantees
are paper theorems. Timing values in the JSON are isolated illustrative runs,
not a performance comparison with Lean or a productivity measurement.

## Archive contents

- `Juniper.tex`, `Juniper.pdf`: article source and compiled article.
- `README.md`, `build.sh`: scope, limitations, and reproduction commands.
- `source-manifest.json`: source revisions and review scope.
- `SHA256SUMS`: byte-integrity hashes for the other delivered files.
- `companion/juniper_frontier.py`: parser, solver, validator, Lean exporter.
- `companion/test_frontier.py`: unit tests and reproducible finite experiments.
- `companion/inverse_polynomials.py`: exact differential-polynomial recurrence.
- `companion/example.jnp`, `example-result.json`, `Generated.lean`: example.
- `companion/test-results.json`, `test-run.log`: recorded frontier checks.
- `companion/inverse-results.json`, `inverse-run.log`: recorded polynomial checks.

The upstream repositories retain their own licenses and attributions. Their
source files are not copied into this archive. Juniper is a proposal inspired by
and explicitly citing those materials, not a claim of authorship of them.
