# Tephra: Refinement-Aware Mathematical Reasoning over Lean

Third-round proof-language proposal prepared for Vladimir Reshetnikov,
6 September 2026.

## Read the article

`tephra.pdf` is the rendered article. `tephra.tex` is its complete, self-contained
LaTeX source, including references and the source-snapshot register.

The proposal develops identity-preserving mathematical refinements, behavioral
contracts, object-bound structure selection, observation-directed inference,
and a conservative elaboration into ordinary Lean. Worked cases include
prefix-local linear inverses, restriction of actions to torsion, local derivative
transfer, and a proof-carrying polynomial/residual-jet interface.

The Leant discussion examines the current callback-verification,
behavioral-selection, length-contract, and adapter boundaries. It adds explicit
proof linkage and observation realizability, including the `List Empty`
counterexample to unrestricted abstract length-based rejection. It also explains
why arbitrary polymorphism in classical Lean is not a parametricity theorem.

## Files

- `tephra.tex`, `tephra.pdf`: the article.
- `tephra_checks.py`: executable finite boundary models; standard library only.
- `check_results.json`, `check_output.txt`: the actual Python run results.
- `TephraCore.lean`: a small reference encoding of semantic interfaces.
- `source_register.json`: 15 exact Git blob snapshots, source paths, and reading scope.
- `build.sh`, `build.ps1`: PDF build scripts.
- `SHA256SUMS.txt`: checksums of the other delivered files.

## Evidence status

The proposed Tephra language and elaborator are not implemented.

The Python companion was executed using Python 3.13.5. All **23 test methods
passed**, with zero failures and zero errors. These are finite executable checks,
not Lean kernel proofs. Internal repetitions include 100 multivariate valuations
in two coefficient domains, 64 list-length input pairs, and finite matrix sizes
1 through 8. They are not additional theorem counts.

`TephraCore.lean` was **not compiled** in the preparation environment, where no
Lean toolchain was available. It is a reference encoding, not a tested release.
It is not a formalization of the polynomial checker or the general prefix-local
inverse theorem. The article supplies written proofs and identifies the remaining
implementation work explicitly. No Lean kernel-check transcript is claimed.

The two round-two synthesis TeX sources were read in full. Other source reading
was bounded as recorded in `source_register.json`. The large FLT repository was
not rebuilt or independently audited. Per-file blob identities do not assert a
single atomic multi-repository checkout.

## Rebuild the PDF

A pdfLaTeX installation with the packages listed in the source is required.
No external figures, bibliography database, shell escape, or network calls are
needed during compilation. Latin Modern is used; no font files are redistributed.

On a POSIX shell:

```sh
./build.sh
```

On PowerShell:

```powershell
./build.ps1
```

Or run the following command three times in this directory:

```text
pdflatex -interaction=nonstopmode -halt-on-error tephra.tex
```

The final PDF was checked for LaTeX warnings and rendered for visual inspection.

## Run the finite tests

Python 3.10 or later is required, with no third-party packages:

```text
python tephra_checks.py
```

The run regenerates `check_results.json`; unittest output goes to the terminal.
To capture it, redirect standard output and standard error to a local file.

To examine the Lean reference separately in a configured Lean 4 environment:

```text
lean TephraCore.lean
```

That last command is supplied as a reproduction step; it was not executed
successfully during preparation.
