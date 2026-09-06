# Heather executable reference model

This is a small Python implementation accompanying the Heather round-four article.
It is **not** a Lean elaborator, a verified compiler, a full language implementation,
or an integration with Leant. The generated `.lean` files are explicitly
**uncompiled proof candidates**. The article's mathematical arguments and these
executed tests are separate kinds of evidence.

## Run

Requires Python 3.10 or later, standard library only. From this directory:

```sh
python test_heather.py
python use_site_demo.py
python heather.py examples/diagonal.hthr --output generated
python heather.py examples/empty.hthr --output generated
python heather.py examples/free.hthr --output generated
python heather.py examples/even.hthr --output generated
python heather.py examples/refuted.hthr --output generated
```

`test_results.json` and `test_log.txt` retain the delivered execution. Re-running
changes the elapsed time in the JSON. The tests ran under Python 3.13.5. To attempt
Lean compilation separately, use a project with Mathlib and an appropriate pinned
Lean toolchain, then `lake env lean generated/UseSite.lean`, and likewise for the
other files. No such compilation result is claimed in this archive.

## Supported source language

A source file has four non-comment lines:

```text
heather diagonal_balance
domain diagonal
inputs xs, ys
claim length(append(xs, ys)) == length(append(ys, ys))
```

Expressions: declared list input, `nil()`, `one()` (the list `[0]`), `append(a,b)`,
and `reverse(a)`. Claims are equality of lengths only. Expressions are parsed with
the Python syntax parser but never evaluated as Python source. Only the named
constructors are admitted. There are explicit source depth/size/input-count bounds.

Domains:

- `free`: arbitrary lists of natural numbers, independently supplied.
- `empty`: lists of the empty type; only empty lists exist. `one()` is rejected.
- `diagonal`: exactly two lists of natural numbers, under equal-length hypothesis.
- `even`: lists of natural numbers whose input lengths are even.

The consumer certificate uses a fixed, domain-specific affine determining family.
Changing the domain changes the request identity and the family. A positive
`model_proved` status is an algorithmic conclusion under the *written* semantics
of this fragment; it is not a Lean theorem receipt. A negative result includes
actual lists satisfying the domain guard, and the checker evaluates the actual
list expressions on those lists. Arbitrary user-supplied cover theorems are not
supported.

The producer and checker share parser/model code. The checker recomputes the
normal forms and cover rather than trusting their serialized fields, but this is
not an independent implementation or a mechanically verified checker.

## Requirement-resolution experiment

`Context` and `use_site_demo.py` model an exact-object, exact-snapshot evidence
index with the two valid implications `0 < n -> n != 0` and the converse over
natural numbers. Resolving an exact-quotient consumer requires both nonzeroness
and divisibility; an absent divisibility assumption stays unresolved. The result
exports the proof of these two premises, **not** a quotient algorithm or the Frey
cast theorem. Rule cycles require a seed. A stale epoch is refused. General
rewriting and checked context migration are specified in the article, not
implemented here; the model refuses cross-anchor reuse.

## Evidence and limits

The test suite has 18 test methods. Its finite differential checks are not a
formal proof of the Python implementation. The counts for concrete comparisons,
negative witnesses, and mutations are separately reported rather than added into
a fictitious theorem count. No user study, full-repository build, Lean compilation,
independently implemented certificate checker, or general-purpose property
inference is included.
