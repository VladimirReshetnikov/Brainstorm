# Noema — second-round proof-language proposal

**Noema: Mathematical Objects, Scoped Relations, and Certified Computation**

Prepared for Vladimir Reshetnikov, 5 September 2026 (Pacific time).

## Contents

- `noema.pdf`: the compiled article.
- `noema.tex`: self-contained LaTeX source, including the bibliography.
- `certificate_demo.py`: an exact-rational Python reference experiment.
- `experiment-results.json`: results of the executed 25-test experiment.
- `source-register.json`: pinned repository sources and the scope of the review.
- `build.sh`: local test and PDF build script.

## Scope and status

This is a detailed design proposal, not an implemented language. The proposed
surface blocks are pseudocode, not compiled Lean. No Lean or Leant builds or
runtime tests were performed for this article. The two specified Brainstorm
syntheses were read closely; selected ProveIt and Leant sources were inspected
at the revisions recorded in `source-register.json`. Findings concerning the
syntheses' modified working trees are explicitly attributed to those reports.

The accompanying Python program is **not formally verified**, is **not a Lean
kernel**, and is **not a Noema implementation**. It is a small exact-arithmetic
model of a proposed certificate boundary, plus negative-neighbor tests. Its
successful rational-function checks retain denominator conditions. It does not
prove real-analysis theorems, and its finite binomial checks do not prove the
universal binomial identity. The mathematical arguments are given in the article.

The recorded run passed 25 tests with zero failures and zero errors. One test
includes 182 finite binomial instances. The JSON record also contains exact root
bracketing values, the Python version, and the program's SHA-256 digest.

## Rebuild

Use Python 3.10 or newer and a standard TeX Live / MiKTeX installation containing
`latexmk`, `pdflatex`, Latin Modern, AMS packages, `stmaryrd`, TikZ, `listings`,
`enumitem`, `etoolbox`, `needspace`, `hyperref`, and the other common packages listed in the
LaTeX preamble. All required fonts are standard distribution packages; no font
files are included in this archive.

```sh
python3 certificate_demo.py --output experiment-results.json
latexmk -pdf -interaction=nonstopmode -halt-on-error noema.tex
```

Or run `./build.sh`. The bibliography is embedded, so BibTeX and network access
are not required. Re-running the experiment may update the Python version in its
JSON output. No random or numerical sampling is used to validate the polynomial
certificate identities.
