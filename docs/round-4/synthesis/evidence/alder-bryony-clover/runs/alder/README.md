# Alder

**Residual Types and Proof-Producing Mathematical Elaboration**  
Fourth-round proposal, prepared for Vladimir Reshetnikov, 6 September 2026.

## Read the proposal

`Alder.pdf` is the 39-page article. `Alder.tex` is its self-contained LaTeX
source, including the bibliography and the TikZ diagram. The main design
chapters develop property-aware and behavioral source types, typed residual
obligations, finite proof-producing inference, certified computation, and
integration with Lean and Leant. Appendix A answers the twenty next-round
questions from the two round-three syntheses.

## What is implemented

The Python companion is a deliberately restricted executable language,
**Alder-0**, over opaque propositions and explicitly supplied Horn rules.
It contains an authored-source parser, scoped proof state, an antichain
inference engine, a separate derivation checker, and a generator of ordinary
Lean theorem source. It does not parse arbitrary Lean expressions or implement
the richer mathematical notation proposed in the article.

Rules become explicit theorem parameters in the generated Lean files; they
are not asserted as axioms or treated as known mathematical truths. Every
`show` must be justified without residual assumptions. `explain` reports
alternative sufficient premise sets and generates explicitly conditional
theorems. It does not add those premises to the context. Local assumptions
are discarded on leaving a block.

`observations.py` supplies exact-arithmetic companions for a list-length
expression model, affine observation frames, and the algebraic formal-root
example. These executions do not replace the mathematical soundness and
coverage proofs needed for a Lean integration.

## Reproduce the executed tests

Requirements: Python **3.10 or newer**, standard library only. The retained
run used Python 3.13.5. Run from the package root:

```text
python companion/test_alder.py
```

The test script checks 4,096 seed/repair configurations over all 64 directed
unary rule graphs on three atoms without self-edges, plus a deterministic
conjunctive-rule family, independent derivation checking, parser/scope
rejections, and exact-arithmetic cases. Detailed counts with their distinct
units are in `evidence/test_results.json` and Section 16.4 of the article.
The script regenerates the two accepted example outputs and the test report.

Compile one small authored example explicitly:

```text
python companion/alder_core.py companion/examples/quotient.alder --lean companion/generated/Quotient.lean --events companion/generated/quotient.json
```

`scope_rejected.alder` and `unused_claim_rejected.alder` are expected failures.
A failed source compilation does not write the requested output files.
The parser has no mathematical integer-division rules: the quotient example
is an opaque propositional model of an obligation graph.

## Lean execution status

No Lean executable was available in the inspected environment. **The generated
Lean files were not compiled here.** They contain no `sorry` placeholders.
With an installed Lean toolchain, the additional checks are:

```text
lean companion/generated/Quotient.lean
lean companion/generated/Locality.lean
```

These files express the propositional derivations using explicit proposition,
rule, and hypothesis parameters. Acceptance of them would check that limited
translation, not establish a complete mathematical frontend or prove that
an arbitrary registry name denotes a correct mathematical law.

## Build the article

Install a TeX distribution providing pdfLaTeX, latexmk, Latin Modern,
microtype, AMS packages, mathtools, stmaryrd, booktabs, tabularx, longtable,
xcolor, listings, fancyhdr, titlesec, enumitem, needspace, etoolbox, PGF/TikZ,
xurl, hyperref, and bookmark. These are standard TeX Live/MiKTeX packages.

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error Alder.tex
```

On a POSIX shell, `./build.sh` runs the tests followed by this PDF build.
The LaTeX source has no external figure files or bibliography database.
No font files or third-party dependencies are bundled. PDF timestamps and
test runtimes can change on a rebuild; byte-identical output is not promised.

## Files and evidence

- `Alder.tex`, `Alder.pdf`: article source and rendered document.
- `companion/`: implementation, authored examples, and generated Lean/JSON.
- `evidence/test_results.json`: executed results and companion source hashes.
- `evidence/source_register.json`: exact repository revisions and Git blob
  identities of the sources read, plus the primary literature consulted.
- `evidence/validation.json`: document build and inspection record.
- `evidence/pdf_build.log`: final pdfLaTeX build log.
- `SHA256SUMS`: hashes of the delivered files other than the checksum file itself.

Repository sources were read through the GitHub connector. The source register
records their provenance; it is not a claim that upstream files are vendored
in this archive. Historical Lean checks described by the round-three reports
are attributed to those reports, not to this delivery. No authoring-time,
productivity, or human comprehension study is claimed.
