# Schist, Tephra, Trellis review evidence

Inputs are pinned to Brainstorm `58bb54219f494b29310ff77384732129411da887`.
All three full TeX sources, READMEs, Python companions, available Lean sources,
and supporting source/validation registers were inspected. The critical memo
is `../../review-notes/schist-tephra-trellis.md`; `convergence.json` records ten
editorial comparison dimensions with precise source locators.

Run `python -B reproduce.py` from this directory, or pass its full path from
elsewhere. It uses only the standard library, copies source scripts into these
evidence directories, and writes new execution receipts here. It does not
modify the source proposal directories or invoke Lean, Lake, TeX, or network.

The fresh run used Python 3.14.4 and passed Schist's 10 methods, Tephra's 23
methods, and Trellis's 31 cases (9 acceptance, 22 rejection). All 28 original
input file hashes remained unchanged. These are finite reference-model tests,
not frontend validation, Lean kernel proofs, or productivity measurements.

`receipt.json` records exact commands, runtime, exit codes, script/log/result
hashes, and before/after input hashes. Trellis's parsed result JSON equals the
imported result; Tephra's does after excluding the Python-version field.

One primary-source fact was independently checked online: the official Lean
Language Reference, [Axioms, section 8.2](https://lean-lang.org/doc/reference/latest/Axioms/),
accessed 2026-09-06, confirms that blanket parametricity is incompatible with
Lean's standard axioms and gives a noncomputable type-sensitive list function.
This supports Tephra's explicit-uniformity requirement; it is not a claim to
have run that example in Lean in this review lane.
