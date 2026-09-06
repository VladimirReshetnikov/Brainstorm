# Facet
## Mathematical Objects with Certified Computational Presentations

A second-round proof-language proposal prepared for Vladimir Reshetnikov,
5 September 2026 (Pacific time).

The 37-page article proposes a Lean-hosted proof/CAS workspace in which stable
mathematical objects have explicitly certified computational presentations.
It builds on both Brainstorm syntheses, examines three ProveIt developments
and selected committed Leant implementation boundaries, and specifies a
verified-CAS architecture, worked examples, integration protocol, evaluation
plan, responses to all 22 next-round questions, and 16 proposed acceptance tests.

## Files

- `facet.pdf`: compiled, visually inspected article (37 pages).
- `facet.tex`: self-contained LaTeX source with embedded bibliography.
- `source-manifest.json`: inspected source revisions, paths, blob identities,
  reading scope, and primary external references.
- `math_checks.py`: supplementary finite exact-arithmetic consistency checks.
- `math-check-results.json`: recorded results (1,100 checks passed).
- `build.sh`: optional build helper for a standard TeX installation.
- `validation.json`: document-production and supplementary-check receipt.
- `SHA256SUMS`: checksums for the other files in this directory.

## Rebuild the article

Install a normal TeX distribution providing pdfLaTeX, latexmk, Latin Modern,
and the standard packages named in the source. No external figures,
bibliography database, font files, or shell-escape commands are needed.

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error facet.tex
```

Alternatively, run `sh build.sh`. The helper places build products in `build/`.
The shipped PDF was built with pdfLaTeX. Different TeX versions may produce
slightly different line breaks or PDF bytes.

## Run the supplementary checks

Python 3.10 or later is sufficient; no third-party Python packages are needed.

```sh
python3 math_checks.py > math-check-results.json
```

The script uses exact Python integers and `fractions.Fraction`. It prints JSON
to standard output; the command above saves it as `math-check-results.json`.
Its checks cover finite binomial
kernels and inversion, the displayed polynomial recurrence, finite Abel-series
coefficients, and selected domain, precision, radical-algebra, and rational
residual calculations.

## Evidence and limits

This is a research proposal, not a delivered implementation of Facet. Proposed
syntax, interfaces, certified algorithms, provider adapters, and acceptance
tests are specifications. No new Lean code was compiled, and no Leant build or
regression suite was run for this article. Source inspections are static.
Both synthesis reports were read closely; the article does not claim a new
independent full reading of all nine original proposals.

The supplementary Python checks are finite consistency checks for the
exposition. They are not kernel-checked proofs, do not establish universally
quantified identities, and do not verify a proof-language implementation.
The radical checks verify algebra rather than principal-branch inequalities;
the root-enclosure checks verify rational arithmetic rather than a
machine-checked analytic theorem. Mathematical arguments and proposed formal
interfaces are presented in the article.

The ProveIt revision is the comparison snapshot used by the syntheses, not a
claim to have surveyed the latest entire repository. Earlier reports' accounts
of uncommitted Leant working-tree features remain attributed to those reports;
they are not silently treated as features of the public committed snapshot.
No measured usability improvement or reduction in formalization effort is
claimed. The evaluation plan explicitly permits a Lean library and document
view, rather than a new authored language, to be the successful outcome.
