# Fennel
## A Proof Language of Stable Objects and Explicit Requirements

Fourth-round proposal, 6 September 2026.

## Main deliverables

- `Fennel.pdf`: the complete 32-page article.
- `Fennel.tex`: self-contained LaTeX source with embedded bibliography.

The article develops property-implicit arguments, dependent behavioral contracts,
proof-carrying alternative-premise frontiers, exact-statement preservation,
consumer-specific locality, certified computation, and realization-aware Leant
integration. It reviews the two requested round-three syntheses and selected
Lean implementations at immutable repository pins.

## Companion experiment

`prototype/fennel.py` is an executed, deliberately small frontend for a finite
Horn-implication language. It contains a parser, a minimal-support planner, an
independent certificate checker, and an ordinary Lean source exporter.

**This is not a full Lean elaborator.** Its atoms are opaque propositions.
Its rules are explicit implication parameters in exported Lean, not silently
accepted mathematical theorems. Pending premises remain explicit parameters.
Generated `.lean` files were **not compiled in this runtime** because no Lean
executable was available. The Python checker is not the Lean kernel.

From this directory, with Python 3.10 or later:

```sh
python prototype/fennel.py prototype/quotients.fnl --out prototype/generated
python prototype/test_fennel.py
python prototype/stress_frontiers.py
```

The scripts use only the Python standard library and do not access the network.
The recorded run used Python 3.13.5.

The test suite passed 27 boundary tests, compared all assumption subsets in
2,000 generated Horn graphs (12,872 closure comparisons), and independently
checked 1,820 selected-target certificates. The stress example exhibits 1,024
minimal supports for ten independent alternative pairs and correctly marks a
capped run incomplete. These are finite implementation tests, not a proof of
the Python implementation or measurements of Lean authoring productivity.

## Files

`prototype/quotients.fnl` is an opaque-proposition skeleton inspired by the
operation-specific prerequisites of exact integer-to-rational quotient
transport. It is not a new formalization of the Frey arithmetic.

`prototype/generated/` contains four generated Lean theorems, their JSON
certificates, and a status summary. Every generated theorem labels its
uncompiled status and its remaining premises.

`evidence/` contains test logs, JSON results, an immutable source manifest,
and a PDF/build validation summary. No upstream source files or font files
are redistributed in this package.

## Rebuilding the article

With a TeX Live installation containing the packages named in the preamble:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error Fennel.tex
```

Alternatively run `pdflatex -interaction=nonstopmode -halt-on-error Fennel.tex`
three times. No BibTeX run is needed. Compilation does not use shell escape.

## Scope of claims

The article separately identifies written metatheorems, executed prototype
tests, historical Lean checks attributed to the earlier syntheses, and features
that remain designs. No controlled authoring or comprehension study was run.
The larger mathematical syntax illustrated in the article is not parsed by
the finite prototype.
