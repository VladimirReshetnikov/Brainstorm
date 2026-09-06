# Prism: A Proof Language with Certified Mathematical Computation

A second-iteration design study prepared for Vladimir Reshetnikov, dated
5 September 2026 (Pacific time).

## Contents

- `prism.tex`: self-contained LaTeX article, including bibliography.
- `prism.pdf`: rendered article.
- `experiments/exact_experiments.py`: deterministic, standard-library-only Python
  exact-arithmetic experiments.
- `experiments/certificates.json`: generated polynomial and rational-interval data.
- `experiments/results.json`: executed experiment receipt and limitations.
- `evidence/source-register.json`: commit-pinned inspected source register.
- `evidence/validation.json`: document build and inspection record.

## Build the article

Run in this directory with a standard TeX Live installation:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error prism.tex
```

Alternatively, run `pdflatex prism.tex` until references stabilize (normally
three passes). There are no external images, bibliography databases, font
files, shell-escape commands, or network dependencies.

## Reproduce the arithmetic experiments

Python 3.9 or later is sufficient. No packages need to be installed.

```sh
python experiments/exact_experiments.py
```

The script regenerates `certificates.json` and `results.json` in its own
folder. To use another directory:

```sh
python experiments/exact_experiments.py --out reproduced
```

Do not use Python's `-O` flag; the script explicitly refuses optimized mode
because its tests use assertions. It uses exact integers, rational numbers,
and dual numbers over the rationals. Its pseudo-random inputs use a fixed seed.

## Evidence status

Prism is a proposed language and architecture, not an implemented compiler.
All Prism listings are illustrative design syntax. The article includes paper
proofs and static inspection of the specified repository snapshots, not a new
Lean-checked formalization. No Lean or Leant build was executed in this study.

The Python program passed 2,475 reported finite checks, including expected
rejection of malformed candidates and exact counterexamples. It is not a
formally verified checker; finite tests do not establish the article's universal
mathematical theorems. No authoring-speed, comprehension, or performance benefit
of the proposed system has been measured.

The source register distinguishes direct inspection from matters discussed only
in the two supplied synthesis reports. The package does not redistribute the
original repositories or claim to reproduce their unpublished working trees.
