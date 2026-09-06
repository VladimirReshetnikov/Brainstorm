# FIBER: Refinement-Directed Mathematical Reasoning over Lean

Third-round proof-language proposal prepared for Vladimir Reshetnikov,
6 September 2026.

## Main files

- `fiber.pdf`: the complete 38-page article.
- `fiber.tex`: self-contained LaTeX source, with embedded bibliography.
- `sources.json`: pinned repository revisions, inspected paths, review scopes,
  and public background references. Original repository files are not bundled.
- `CoreEncoding.lean`: a small reference encoding in ordinary Lean, **not
  compiler-checked in the authoring environment**. It is not a FIBER compiler
  or a polynomial checker. In particular, `certificate_bridge` takes checker
  soundness and execution evidence as premises; it does not establish them.
- `tools/check_examples.py`: standard-library Python executable model and tests.
- `evidence/checks.json`: the actual finite-test receipt.
- `evidence/build.json`: PDF build and inspection record.
- `SHA256SUMS`: hashes of the delivered files other than this checksum list.

## Thesis

Extend source-level typing and elaboration with scoped, same-object
refinements and behavioral contracts. Compile to ordinary Lean dependent
types and proof terms, rather than add CAS reasoning to kernel conversion.
The article develops the typing rules, exact-quotient transport for Frey
curves under consistent weakened hypotheses, measure-indexed convergence
contracts, refinement-directed synthesis, and a mathematical soundness
argument for a sparse polynomial certificate checker.

## Evidence status

The two revised round-two syntheses and selected ProveIt, FLT, and Leant
sources were read. This is not an audit or rebuild of the whole repositories.
The Python companion completed **1,298 finite checks in 31 groups** with
Python 3.13.5. These tests exercise exact arithmetic and certificate examples;
they do not prove the Python implementation sound, verify the proposed
frontend, or constitute Lean kernel checking. General mathematical
arguments, reference encodings, executed tests, and proposed engineering
work are distinguished throughout the article.

## Run the finite checks

Requires Python 3.9 or newer; no third-party libraries.

```text
python tools/check_examples.py
```

The script writes `evidence/checks.json`. Its executable polynomial model
includes explicit dimensions, canonical integer coefficients, exact
certificate arity, and operational budgets. It is not a hardened network
certificate service. Resource refusal is not an algebraic refutation.

## Rebuild the PDF

Use a TeX installation with pdfLaTeX and the standard packages listed in the
preamble, including `newtx`, `microtype`, `mathtools`, `tcolorbox`, `listings`,
and `hyperref`. No images, font files, or separate bibliography databases
are needed.

On a POSIX shell, run `./build.sh`. On any supported shell, run this command
three times to settle the table of contents and cross-references:

```text
pdflatex -interaction=nonstopmode -halt-on-error fiber.tex
```

The PDF embeds its fonts, as normal for a LaTeX PDF; no standalone font
files are distributed.
