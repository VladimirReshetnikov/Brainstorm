# Sorrel — Contract-Typed Proof Plans for Human-Scale Mathematics

Prepared for Vladimir Reshetnikov, 6 September 2026, as a fourth-round proposal
for the Brainstorm proof-language campaign.

## Read the article

- `sorrel.pdf`: the complete article.
- `sorrel.tex`: self-contained LaTeX source with embedded bibliography.
- `sources.json`: inspected repository commit/blob identities and documentation.

The article proposes property-implicit interfaces and contract-typed proof plans
over Lean, with explicit residual telescopes and alternative sufficient-premise
supports. It includes worked reconstructions, finite-calculus proofs, an
implementation plan, and a controlled evaluation protocol.

## Run the executed reference model

Python 3.10 or newer is sufficient; no external packages are required.

```sh
python sorrel_model.py --test --json test_results.json
python sorrel_model.py examples/quotient.sorrel \
  --json examples/quotient_result.json --export-lean SelectedPlan.lean
python sorrel_model.py examples/cauchy.sorrel \
  --json examples/cauchy_result.json
```

`--budget N` limits rule-combination attempts. Exhaustion produces an incomplete
support inventory, not a refutation. Malformed input is rejected.

The included test run passed 31 named tests. It generated 80 finite rule systems
and compared all 1,280 assumption-subset closures against an independent oracle,
for 7,680 subset/atom comparisons. It also checked 517 retained certificates and
enumerated 5,120 Boolean valuations. See `test_results.json` for exact details.

## Scope and limitations

The Python implementation is a **finite propositional model**, not a Lean
elaborator, mathematical parser, CAS, or Leant integration. A `.sorrel` file
names atoms and supplies implication rules. Its rules are assumptions of the
model, not mathematical theorems established by the program. The companion's
certificate checker verifies finite derivations against that exact rule table.

`SelectedPlan.lean` is an exported conditional implication. Atom meanings and
used rule interfaces are theorem parameters. **It was not compiled in this
study**, because no Lean executable was available. Even compiling it would not
prove that the atom names have the arithmetic meanings suggested by their names.

The mathematical surface examples in the article are proposed Sorrel syntax;
only the small ground-rule format in `examples/` is accepted by the Python
parser. Source review, written mathematical proofs, finite-model execution,
Lean kernel checking, and user-productivity evaluation are distinguished
throughout. No whole-repository build or productivity gain is claimed.

## Rebuild the article

A standard TeX installation providing the packages named in the preamble is
required. No external figures, bibliography database, or font files are needed.

```sh
pdflatex -interaction=nonstopmode -halt-on-error sorrel.tex
pdflatex -interaction=nonstopmode -halt-on-error sorrel.tex
pdflatex -interaction=nonstopmode -halt-on-error sorrel.tex
```

The repeated passes resolve references and the table of contents. The delivered
PDF was rebuilt and visually inspected after layout corrections.

## Checksums

`SHA256SUMS.txt` records the archive's content files, excluding itself. The ZIP
contains no upstream repository source archive, toolchain, or font files.
