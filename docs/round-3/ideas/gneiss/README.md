# GNEISS — third-round proof-language proposal

**Property- and Behavior-Aware Mathematical Elaboration over Lean**  
Prepared for Vladimir Reshetnikov, 6 September 2026.

## Read the article

`gneiss.pdf` is the compiled article. `gneiss.tex` is its complete source,
including the diagram, mathematical arguments, code displays, and bibliography.
No external image assets or bibliography database are needed.

The proposal adds contextual property views and compositional behavioral
contracts to mathematical elaboration while retaining ordinary Lean terms and
proof checking. It compares a conservative frontend with genuine kernel
extensions, reviews both round-two syntheses, and develops examples from
ProveIt, the FLT repository, and Leant. The proposal does not claim to invent
refinement types or the existing round-two acceptance discipline.

## What is and is not verified

- **Performed for this article:** PDF compilation, visual inspection of the
  rendered pages, and the Python reference model's 32 passing test methods.
- **Mathematical arguments:** the restricted elaboration preservation argument,
  contract composition, finite-section inversion, local differentiation,
  Frey coefficient integrality, and coefficient-list checker soundness are
  paper proofs in the article, not newly kernel-checked Lean proofs.
- **Uncompiled specimen:** `GneissCore.lean` encodes a small portion of the
  proposed contracts in ordinary Lean. No Lean executable was available in the
  preparation environment. This file is not a compiler receipt or proof of
  frontend correctness. Compile it and inspect its actual axiom reports before
  treating it as a kernel-checked artifact.
- **Not implemented or measured:** the complete GNEISS frontend, an end-to-end
  Lean polynomial checker and reifier, a new Lean kernel, and author-productivity
  or maintenance improvements.
- **Source-reported only:** the cited repositories' own Lean builds and previous
  experiments were read, not rerun here. They are not this article's validation.

The Python program is a restricted contract-assembly and exact finite-arithmetic
model, not a Lean proof checker. Its input assumptions are treated as authorized;
its anchors are stand-in identifiers; it does not validate hostile serialized
inputs or prove the truth of supplied assumptions. Passing its tests is not
universal behavioral verification or evidence that the full inherited negative
suite passes in an integrated language.

## Rebuild the PDF

Use a TeX distribution with pdfLaTeX, latexmk, and the packages named in the
preamble (including newtx, TikZ, tcolorbox, hyperref, and needspace).

```sh
sh build.sh
```

Alternatively:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error gneiss.tex
```

The build script rejects unresolved references/citations, missing characters,
and overfull boxes. Rebuilding can change PDF timestamps and file hashes.
No font files are included in this archive.

## Rerun the reference tests

Python 3.10 or later, standard library only:

```sh
python3 contract_model.py > tests.log 2>&1
```

This command writes a fresh `test_results.json` next to the program and exits
nonzero on failure. The delivered `tests.log` and result record belong to the
preparation run, not to a future local run.

## Assess the Lean specimen separately

Select and record a Lean toolchain, then run:

```sh
lean --version
lean GneissCore.lean
```

The specimen includes two `#print axioms` commands. Compilation and those
reports must actually succeed before assigning a stronger validation status.

## Provenance and integrity

`sources.json` lists the exact repository commits, selected file blob identities,
reading scope, and external primary references. `validation.json` records the
scope of the build and test checks. `SHA256SUMS` contains delivery hashes for
all files except itself. On systems with GNU coreutils:

```sh
sha256sum -c SHA256SUMS
```

The archive contains no copied repository, original source-report PDFs, or
installed fonts, and it makes no changes to the referenced repositories.
