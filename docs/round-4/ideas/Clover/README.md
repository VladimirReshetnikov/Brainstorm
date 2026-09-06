# Clover
## Scoped Mathematical Reasoning with Obligation-Directed Types

Prepared for Vladimir Reshetnikov, 6 September 2026.

`Clover.pdf` is the article. `Clover.tex` is its self-contained LaTeX source.
`SOURCE_MANIFEST.json` records the exact upstream references and inspection scope.
The `companion` directory contains the executed restricted model and saved results.

## Status

The article is a round-four language design with written mathematical proofs.
The full proposed Clover language is not implemented. The Python companion does
parse a much smaller source language, generate finite proof plans, check them,
and export ordinary Lean source. It is not a Lean elaborator or a Lean kernel.

The 35 Python unit-test methods passed. Two of those methods respectively include
32 schedule-comparison cases and 136 finite semantic valuations. These are not
additional unit-test methods. The separate exact-arithmetic program completed
1,576 assertion checks involving 625 affine forms, their test bases and realizers,
finite grids, and a few mathematical fixtures.

`CloverCore.lean` and `GeneratedExamples.lean` were written/generated and reviewed,
but NOT compiled in the preparation environment. No Lean or Lake executable was
available there. Saved model outputs explicitly retain `kernel_checked: false`.
A successful Python plan is never labeled a kernel proof. No usability or Lean
performance improvement has been measured.

The demo intentionally includes an unfinished claim. Its three earlier claims
have checked model plans; `document_plan_complete` is false. Exporting those three
independent theorem bodies does not certify the entire source document.

## Build the article

Use a standard TeX Live or MiKTeX installation with pdfLaTeX and the packages named
in the preamble (Latin Modern, AMS packages, hyperref, listings, xurl, etc.).
No font files are shipped and no external bibliography processor is required.

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error Clover.tex
```

Alternatively, run `pdflatex Clover.tex` enough times to resolve the table of
contents and cross-references (normally three runs).

## Run the executable model

Python 3.9 or newer, standard library only. From `companion`:

```text
python -m unittest -v test_clover_slice
python clover_slice.py demo.clover --json demo-result.json --lean GeneratedExamples.lean
python affine_basis.py
python compare_profiles.py
```

The last command regenerates `profile-comparison.json`. On the first demo
request the full registry generates 211 ground instances, while its two-rule
profile generates 16. Both retain a four-node proof plan, including assumption
nodes. These are algorithm counters, not timings of Lean or comparisons with
Mathlib automation.

### The actual parsed grammar

```text
command ::= fix name+ : End
          | assume name : atom
          | claim name : atom
          | scope
          | end

atom ::= injective term
       | involutive term
       | left_inverse term term
       | same term term

term ::= name | (term) | (term . term)
```

All functions are endomorphisms of one arbitrary carrier. `(g . f)` means
composition with `g` outside `f`. Whitespace is insignificant within an atom;
commands occupy one line. `--` starts a line comment. Binder shadowing creates
new internal identities. Local scopes do not export their assumptions or facts.
An unresolved claim is not an assumption for later claims.

The programmatic API also supports an allowed-rule profile, a required root rule,
a resource cap, and reversal of the rule schedule. Those options are not added
to the parsed grammar. The richer `where`, `operation`, `on U`, `differentiate`,
`construct`, and `without_loss` notation in the article is proposed syntax.

The four logical predicates and seven fixed rule schemas are interpreted in
`CloverCore.lean`. The Python replay checker reconstructs proof applications
independently of the search result but shares the expression representation and
substitution utilities. It is not an independently verified semantics engine.

## Check the Lean files separately

The campaign's Lean 4.32.0 baseline is the intended first integration target.
A current installation can also be tested, with its actual version recorded.
No successful run of these commands is asserted by the package.

Bash, from `companion`:

```bash
lean --version
export LEAN_PATH="$PWD${LEAN_PATH:+:$LEAN_PATH}"
lean -o CloverCore.olean CloverCore.lean
lean GeneratedExamples.lean
```

PowerShell, from `companion`:

```powershell
lean --version
$oldLeanPath = $env:LEAN_PATH
try {
    $env:LEAN_PATH = (Get-Location).Path + [IO.Path]::PathSeparator + $oldLeanPath
    lean -o CloverCore.olean CloverCore.lean
    if ($LASTEXITCODE -ne 0) { throw 'CloverCore.lean did not compile.' }
    lean GeneratedExamples.lean
    if ($LASTEXITCODE -ne 0) { throw 'GeneratedExamples.lean did not compile.' }
} finally {
    $env:LEAN_PATH = $oldLeanPath
}
```

The reference uses ordinary Lean definitions and elementary proof terms, without
Mathlib imports. Its axiom-printing commands are intended to make a future
actual run's dependency inventory visible. A source file containing no `sorry`
or added axioms is not by itself evidence that it was accepted by Lean.

## What the affine companion establishes

`affine_basis.py` performs exact rational calculations for a realizable affine
basis of the observation `(total length, left length, right length)` on pairs of
lists. It checks concrete realizers of `(0,0,0)`, `(1,1,0)`, and `(1,0,1)`.
It also tests the singleton image for lists over an empty element type and for
a length-100 guard. The article proves the general affine test-basis theorem.

The code is not an end-to-end Leant candidate verifier. Promotion to a universal
source theorem still needs a checked candidate denotation bridge, an affine-model
soundness theorem, and the coverage/realization evidence described in the article.

## Provenance and packaging

Both round-three main synthesis reports and the cited source blocks were read
through the GitHub connector. Upstream repositories were not built. The directly
inspected Leant snapshot is `3a40904be8a410d832d9ab6900b3d3e7b425eccb`.
The newer `823259f7...` snapshot mentioned in the article is reported by the
syntheses and is not conflated with that direct inspection.

`SHA256SUMS.txt` provides checksums for the delivered article, sources, and
companion files. It is an integrity convenience, not evidence of mathematical
correctness or a replacement for rechecking generated proofs.
