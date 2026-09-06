# Accord — second-round proof-language proposal

**Accord: A Mathematical Language of Certified Transformations**

Prepared for Vladimir Reshetnikov, 5 September 2026 (Pacific time).
The article is 38 PDF pages, including its source discussion, worked examples,
implementation and evaluation plans, responses to all 22 synthesis questions,
protocol sketch, and references.

## Contents

- `accord.pdf`: the rendered article.
- `accord.tex`: self-contained LaTeX source, including the bibliography and vector diagram.
- `certificate_exhibits.py`: exact-arithmetic Python exhibits; no third-party dependencies.
- `exhibit_results.json`: the executed exhibit receipt (267 checks passed).
- `source_register.json`: immutable repository revisions, source paths, Git blob identities,
  inspected ranges, external sources, and provenance limitations.
- `validation.json`: build and execution status.
- `SHA256SUMS.txt`: SHA-256 hashes for the other files.

## Build

With a standard TeX Live or equivalent installation providing the packages named
in the preamble:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error accord.tex
```

No external bibliography, image, or custom font files are needed. The final build
had no unresolved citations or references and no overfull-box warnings. The PDF
was rendered and visually reviewed.

## Reproduce the arithmetic exhibits

Use Python 3.10 or later:

```sh
python certificate_exhibits.py exhibit_results.json
```

The recorded run used Python 3.13.5. The calculations use exact rational numbers,
finite formal series, polynomial coefficients, and the non-field rational algebra
Q[epsilon]/(epsilon^2). The JSON records the individual check groups and the exact
root enclosure.

## Evidence status

This is a design proposal, not an implemented language or a verified CAS release.
The proposed surface examples are not executable Lean syntax. No Lean, ProveIt,
or Leant build was run for this article. Mathematical arguments in the article
are paper proofs and applications of the cited source theorems. The 267 Python
checks are finite executable exhibits, not kernel-checked proofs or usability
measurements.

Both requested Brainstorm synthesis reports were read closely. The three ProveIt
modules and selected Leant implementation ranges were inspected directly at the
revisions in the source register. The reports' local and uncommitted implementation
claims are attributed rather than treated as part of the inspected committed
snapshots. The nine individual proposals were considered through the syntheses,
not independently reread in full.

The archive does not redistribute the source repositories, their reports, third-party
libraries, or font files.
