# Bryony

**Contract-Indexed Mathematical Reasoning with Proof-Carrying Requirements**

A round-four proof-language proposal prepared for Vladimir Reshetnikov,
6 September 2026. Read `Bryony.pdf`; its self-contained source is `Bryony.tex`.

## The central idea

An exact demanded proposition has a family of sufficient prospective-premise
sets, each carrying a conditional proof recipe. The sets are minimized by
inclusion within a fixed candidate, context, and rule policy. An unproved
premise remains a requirement; it is never silently installed as a fact.

The article gives finite soundness, termination and relative-completeness
proofs; bounded grounding and context-replay protocols; Frey, Fubini and tensor
examples; Leant integration; and elaborator-level versus native refinements.
It includes a crosswalk answering both round-three synthesis question sets.

## Build the article

Use a standard TeX Live installation containing the packages named in the
preamble (including tcolorbox, stmaryrd, xurl, listings and Latin Modern):

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error Bryony.tex
```

There is no external bibliography database, figure dependency, or bundled font
file. With no latexmk, run pdflatex three times using the same flags.

## Run the finite reference model

Python 3.9 or later; standard library only:

```sh
python prototype/test_bryony.py
python prototype/bryony.py prototype/frey4.bry --output evidence/frey4
```

Tests update `evidence/results.json` and print their results. To preserve an
additional text log when rerunning:

```sh
python prototype/test_bryony.py > evidence/test-rerun.log 2>&1
```

The prepared run passed 23 test methods, including 400 finite rule systems,
3,873 exhaustive premise-subset closures, 2,800 atom-support comparisons and
1,835 independently replayed generated certificates. It also checks 288
positive Frey triples and four one-premise mutations by exact arithmetic.
These counts have different units and must not be added as a theorem count.
The exact Python version and run timing are retained in the JSON receipt.

## Exact scope

The implemented parser recognizes a tiny propositional DSL, not the proposed
mathematical language. Its atoms are names, not reified Lean propositions.
Rules are model assumptions. The implementation computes minimal sufficient
supports, builds proof trees and independently checks their structure. It
checks full source snapshots, not just hashes, at its model replay boundary.

The generated `evidence/frey4/Requirements.lean` contains ordinary generic
propositional proof terms with all proposition and rule assumptions explicit.
**This file was not compiled in the preparation environment.** With a selected
Lean toolchain, the next check is:

```sh
lean evidence/frey4/Requirements.lean
```

Even a successful compilation would certify those abstract implications, not
the mathematical meaning of the atom names. A real Lean adapter still needs
checked theorem registration, source correspondence, dependent-context handling,
and retained proofs of the exact candidate specification.

The metatheory in the article is a written proof, not a new Lean mechanization.
No author-productivity results or real-file Lean index costs are claimed.
The solver uses immutable trees and first-proof retention, not cost-optimal
proof search. It is a reference model, not a hardened service for untrusted
large or deeply nested inputs.

## Provenance

`sources.json` records source pins and review scopes. The two Brainstorm
syntheses were examined at bf333390. Selected ProveIt and Fermat files were
read at 24ce8bd7 and aa2d8b34. The accessible Leant branch resolved to
3a40904b. The later 823259f7 reference cited by the syntheses was not resolvable
through the public GitHub contents endpoint, so those reports' later local
claims are kept distinct from the source freshly read here.

The upstream repositories were not modified. Their full source trees and
articles are not redistributed in this archive.

`SHA256SUMS.txt` records the delivered files (excluding itself). The supplied
PDF was rendered and visually inspected; `evidence/pdf-review.json` records the
layout check, not a mathematical correctness certificate.
