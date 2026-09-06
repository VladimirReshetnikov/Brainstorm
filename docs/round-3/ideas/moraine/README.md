# Moraine — third-round proof-language proposal

**Evidence-Indexed Refinement and Behavioral Typing for Human-Scale Mathematics**

Prepared for Vladimir Reshetnikov, 6 September 2026.

## Read

`moraine.pdf` is the complete article. `moraine.tex` is its self-contained LaTeX
source. The article studies both requested round-two reports, four Lean source
examples from ProveIt and the Fermat repository, and the current inspected Leant
behavioral boundary. Full repository revisions and source paths are in
`sources.json` and the bibliography.

The design keeps mathematical objects fixed while adding scoped, proved
properties to their usable source-level types. It covers refinement subsumption,
relational and behavioral contracts, neighborhood scopes, bundled interfaces,
exact-target synthesis, CAS evidence, kernel-extension alternatives, and a
controlled evaluation against equally equipped ordinary Lean.

## Rebuild the PDF

Use a TeX Live installation providing pdfLaTeX and the standard packages named
in the preamble (including `lmodern`, `microtype`, `stmaryrd`, `listings`,
`tikz`, and `hyperref`). On a shell with Bash and Python 3.9 or later:

```sh
bash build.sh
```

The script compiles the article three times, copies the result to `moraine.pdf`,
and runs the Python regression suite. It does **not** invoke Lean.

On Windows, the PDF can also be rebuilt directly:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error moraine.tex
pdflatex -interaction=nonstopmode -halt-on-error moraine.tex
pdflatex -interaction=nonstopmode -halt-on-error moraine.tex
```

No external images, font files, bibliography database, network calls, or shell
escape are required to build the article.

## Run the executable reference checker

```sh
cd companion
python -m unittest -v test_length_contracts.py
```

The captured run in `companion/test-results.txt` passed **32 tests**. This includes
25,600 comparisons of the concrete list interpreter with the affine length model
and 729 pairs of small affine forms in the counterexample regression.

The checker supports only its closed grammar: input lists of natural numbers,
empty list, cons with a literal natural head, append, reverse, and elementwise
successor. It checks an exact universal affine length contract by reconstructing
coefficients, matching the original source expression and epoch, and validating
all arities. Resource limits are explicit.

## Validation boundaries

- The article contains mathematical proofs for the stated refinement fragment,
  composition rules, deletion budget, and affine length characterization.
- The Python companion was executed. It is **not Lean-verified** and is **not a
  security boundary**. Its epoch string and receipt dataclass are reference-model
  metadata, not the generative authority mechanism used by Leant.
- `companion/Contracts.lean` is an ordinary-Lean reference encoding with explicit
  proof bodies, not a Moraine implementation. **It was not compiler-tested in this
  session.** It covers basic contract laws and the structural/denotational half
  of length soundness, not the affine normalizer or its reflective bridge.
- The proposed Moraine syntax, general elaborator, neighborhood inference,
  naturality inference, and source reconstructions were not implemented or
  compiled. No whole-repository Lean build was performed.
- The article's integration/adversarial suite and multi-arm user evaluation are
  proposed experiments, not reported completed experiments.

To validate the reference Lean file in a pinned installation:

```sh
lean companion/Contracts.lean
```

The next verification step is to implement and prove the affine coefficient
normalizer inside Lean, then connect it to exact-target synthesis. No result from
the Python checker should be imported into Lean as an axiom.

## Contents

- `moraine.tex`, `moraine.pdf`: article.
- `sources.json`: source revisions and documentation references.
- `build.sh`: reproducible article build and Python test invocation.
- `companion/Contracts.lean`: uncompiled Lean reference semantics.
- `companion/length_contracts.py`: executed Python reference model.
- `companion/test_length_contracts.py`: regression suite.
- `companion/test-results.txt`: captured test run.
- `SHA256SUMS.txt`: checksums of the other delivered files.

Build intermediates and rendered inspection images are not included in the ZIP.
