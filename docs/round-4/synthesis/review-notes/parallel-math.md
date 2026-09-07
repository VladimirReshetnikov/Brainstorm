# Peer round-four mathematical audit

Read-only review of the peer package at Brainstorm commit
`c92ef058979fcb8f6c11030ac9ed80c64186e0f8`, 6 September 2026.
This lane read the complete peer TeX, appendix, README, the twenty supplied
Lean copies, the patched Heather file, both new Lean files, their relevant
logs, and the corresponding portions of our synthesis. No Lean/Lake command,
build, Git mutation, external write, or experiment execution was performed.
Compiler outcomes below are attributed to imported logs; fresh acceptance
belongs to the root's separate receipts.

Path abbreviations used in the precise locators below:

- `P` = `docs/round-4/unified_report/unified_report.tex`.
- `L` = `docs/round-4/unified_report/experiments/lean`.
- `S` = `docs/round-4/synthesis/unified-report.tex`.

## Recommendation

Incorporate the peer's **manual instantiation of fixed generated Frey
routes**, and the **concrete list-image/diagonal theorems**, after fresh
unchanged-source checks. Preserve the distinction between a particular
mathematical instantiation, a source-to-Lean compiler, and a verified
frontier checker. The new files do the first. They do not do the latter two.

The sharper first-coefficient interface is valuable but is already proved
in our `evidence/lean/followups/FreySharper.lean`; its rational cast theorem
also goes beyond the peer's sharpened divisibility theorem. The peer's
additional value is the explicit application of generated route schemas
to mathematical meanings, plus four core-Lean list facts. It does not
justify replacing our implementation distinctions or evidence boundaries
by the peer's claim of nine equivalent engines.

## Provenance and exact inventories

`git diff --exit-code c92ef058979fcb8f6c11030ac9ed80c64186e0f8 --
docs/round-4/unified_report` returned zero. All twenty flattened original
Lean copies have byte-identical SHA-256 hashes to their respective
`docs/round-4/ideas/<Report>/<file>` inputs. The inventory was enumerated
from `lean_files.csv`, then the declarations were counted from the actual
source, rather than trusting the table's labels.

| Source scope | Files | Lines | Named theorems | Anonymous examples | `#print axioms` queries |
|---|---:|---:|---:|---:|---:|
| Twenty original exports | 20 | 546 | 37 | 0 | 7 |
| Generic propositional portion of those originals | 13 | 399 | 22 | 0 | 0 |
| Clover concrete core and applications | 2 | 95 | 10 | 0 | 7 |
| Heather list/readiness portion | 5 | 52 | 5 | 0 | 0 |
| New `FreyRoutes.lean` | 1 | 133 | 13 | 7 | 5 |
| New `ListImage.lean` | 1 | 62 | **4** | 3 | **0** |
| Patched Heather specimen | 1 | 9 | 1 | 0 | 0 |

The thirteen generic files comprise Alder 2, Bryony 1, Fennel 4, Juniper 1,
Laurel 4, and Sorrel 1. Laurel's cycle file has no theorem; therefore only
twelve generic files contain declarations. The peer's repeated count of
fourteen generic exports (`P:144`, `P:348`, `P:425`) is incorrect.

Hashes of the principal reviewed inputs:

- `P`, SHA-256 `92932d4a0144b67fe65a4d266f9195a3f733768dbe4adc28c6ad3295956e028e`.
- `L/FreyRoutes.lean`, Git blob `10957ac8182271e47618147fc433bcc1acbbcb52`,
  SHA-256 `80aa41a7923da0f83fa6f2a531fc591b5053657716bd05790b6079a3ab1b5aba`.
- `L/ListImage.lean`, Git blob `7aab81c638dfde701846e3b347886332bb58d23f`,
  SHA-256 `909c18bfedfb7cfbe5e677e9769e0546fcfed998fd586b228b520e9faa371428`.
- `L/patched/even_reverse_length_noomega.lean`, SHA-256
  `b74473a1d30a60f8f5bc737a8c81430d2ce359da2220ff60a58c4c2bc6f75e1e`.

The peer's first-pass `L/summary.txt` records eighteen zero exits, one
Clover missing-module failure, and the original Heather tactic failure.
`L/clover/GeneratedExamples.log` records the subsequent check against the
compiled Clover core. The later Heather patch log ends `rc=0`. Thus the
reported final result is nineteen accepted **original** files plus a
separate accepted repair. Twenty original files, a repair, and two new
files are twenty-three source artifacts; the failed original must not
silently be replaced in a success denominator. All seven original axiom
queries belong to CloverCore, at lines 45--51.

## FreyRoutes: exact mathematical contribution

Let `N2 = b^p - 1 - a^p` and `N4 = -(a^p * b^p)`, for integers `a,b`
and natural `p`. The file contains the following declarations, all in
namespace `FreyRoutes`:

| Declaration | Source line | Actual conclusion and hypotheses |
|---|---:|---|
| `sixteen_dvd_pow` | 16 | `2 ∣ b`, `4 ≤ p` imply `16 ∣ b^p`. |
| `four_dvd_pow` | 23 | `2 ∣ b`, `2 ≤ p` imply `4 ∣ b^p`. |
| `odd_pow_mod_four` | 30 | `Odd p`, `a ≡ 3 [ZMOD 4]` imply the same residue for `a^p`. |
| `four_dvd_a2` | 42 | `Odd p`, `2 ≤ p`, the residue, and even `b` imply `4 ∣ N2`. |
| `sixteen_dvd_a4` | 49 | Even `b` and `4 ≤ p` imply `16 ∣ N4`. |
| `laurel_route_0` | 56 | Generic direct-divisibility route. |
| `laurel_route_1` | 62 | Generic evenness/large-exponent route. |
| `bryony_route_1` | 69 | Generic three-rule route. |
| `sorrel_selectedPlan` | 75 | Generic selected conjunction plan. |
| `a4_cast_by_laurel_route_1` | 83 | `((N4 / 16 : Int) : Rat) = (N4 : Rat) / 16`, from even `b`, `4 ≤ p`. |
| `a4_cast_by_laurel_route_0` | 92 | Same cast identity, from `16 ∣ N4` directly. |
| `a4_cast_by_bryony_route_1` | 99 | Same cast identity, from even `b`, `4 ≤ p`. |
| `both_dvd_by_sorrel_plan` | 109 | `4 ∣ N2 ∧ 16 ∣ N4`, under all four sufficient hypotheses. |

The four generic route bodies and parameter types agree with the supplied
Laurel, Bryony, and Sorrel routes, apart from declaration names, namespaces,
layout, and documentation. This is semantic reuse of their fixed proof
assembly, not an import of an automatic generator. The two Laurel routes
also demonstrate that a consumer's direct guard can remain an alternative
to a stronger sufficient premise package.

The seven examples occur at `L/FreyRoutes.lean:119`--`126`: two exact
quotients at `(a,b,p)=(3,2,5)`; four failed neighboring divisibilities;
and the positive first-coefficient divisibility at `(3,2,3)`. No Fermat
equation, primality, nonzero, or coprimality premise is imported. These
are satisfiable coefficient interfaces, not the full Frey curve package.

The five explicit axiom queries are at lines 128--132. The imported log
reports `[propext, Classical.choice, Quot.sound]` for each queried theorem
and ends `rc=0`. These five queries do not directly inventory all thirteen
named declarations or seven examples. Do not describe them as zero-axiom
proofs or as a complete audit of every imported declaration.

Two qualifications matter when incorporating the result:

1. Bryony's `DivSixteen` and `NumeratorExact` are both interpreted as exactly
   `16 ∣ N4`, and the middle rule is `id` (`L/FreyRoutes.lean:97`--`104`).
   This is a legitimate instance, but it does not implement a distinct
   exact-integer object or validate such an object's semantics.
2. Sorrel's `Direct4` is supplied by the hand-written `four_dvd_a2` proof
   outside the generic route (`L/FreyRoutes.lean:115`--`116`). Its result is
   a conjunction of divisibilities, **not a fourth coefficient cast
   identity**. The peer's `P:409` wording “four coefficient identities”
   conflates three cast proofs with this conjunction. Nor does the file
   prove a first-coefficient cast identity under the sharpened bound;
   our `FreySharper.cast_a2_sharper` already supplies that additional step.

The peer itself correctly limits automation at `P:400`: registry validation,
metadata roles, term-pool extraction and epochs remain absent. Keep that
qualification next to the result, rather than the stronger “registry link
every report describes and none built” at `P:146`/`P:397`. Clover already
connects generated concrete statements to actual endomorphism theorems.
The introductory phrase “unconditional theorem” in `L/FreyRoutes.lean:10`
means that the generic rule premises have been supplied; the actual
mathematical theorem still has its explicitly displayed hypotheses.

## ListImage: four facts, not the full frame interface

All declarations are in namespace `ListImage`, with `autoImplicit false`
and no explicit import. Exact claims:

- `length_image`, `L/ListImage.lean:10`: for `α : Type` and `n : Nat`,
  `(∃ xs : List α, xs.length = n) ↔ n = 0 ∨ Nonempty α`. The reverse
  implication uses `List.replicate`; this is a useful explicit positive
  realization theorem. It needs existence of an element, not a chosen
  `Inhabited α` instance. The declaration is at `Type`, not universe
  polymorphic `Type u`; that is a scope detail, not a mathematical defect.
- `empty_one_point_frame`, line 23: `b = d` suffices for
  `∀ xs : List Empty, a*xs.length+b = c*xs.length+d`. This is the positive
  direction of the one-point criterion. The converse is immediate at `[]`
  but is not part of the declaration.
- `inhabited_two_point_frame`, line 32: `b=d` and `a+b=c+d` imply
  `∀ n : Nat, a*n+b=c*n+d`. Despite its name and comment, there is no list,
  element-type, nonemptiness, frame, or realization parameter. It proves
  scalar affine determination over natural indices. Combining it with
  `length_image` gives the intended inhabited-list application, but the
  file does not package that application or its converse as a theorem.
- `diagonal_frame`, line 40: an actual iff for `List Nat`,
  `(∀ xs, c+a*xs.length+b*xs.reverse.length=0) ↔ c=0 ∧ a+b=0`.
  The forward proof uses `[]` and `[0]`; the reverse proof uses the exact
  `List.length_reverse` identity. This is the strongest new concrete
  frame statement in the file.

Three examples occur at lines 55, 57, and 59. The first realizes independent
lengths `(1,0)`. The last refutes the independent-input append equality.
The middle example literally states
`∀ xs, (xs ++ xs).length = (xs ++ xs).length` and is `rfl`: it illustrates
one substituted diagonal case but is not a theorem about two distinct
inputs subject to an equal-length guard. Heather's existing
`heather_diagonal_balance` states the latter correctly
(`L/Heather__companion__generated__diagonal_balance.lean:7`).

There is **no even-length frame theorem**, general multidimensional frame
theorem, arbitrary guarded-domain coverage theorem, candidate grammar
interpretation, or exact Leant-source correspondence here. The peer's
table `P:470` correctly marks even-length completeness as unformalized,
but `P:251`/`P:403` incorrectly say all four previously listed frame
instances are checked. The count is four named facts including the image
characterization, not four domain instances of a single formal theorem.

`L/ListImage.log` is a zero-byte file. The source contains no axiom queries.
The claim “all five theorems are axiom-free” at `P:403` comes from a
hard-coded entry in `tools/make_tables.py:366`, propagated to
`new_experiments.csv:2`. Four is the actual count; no-declared-axioms and
no-imports are source facts, whereas transitive axiom-freedom needs an
audit. A silent log alone has neither an exit code nor such audit output.

## Mathematical and implementation claims to correct or decline

| Peer anchor | Problem | Correct qualification |
|---|---|---|
| `P:249` | Says affine-hull dimension `r` is the number of required points. | `r+1` affinely independent points for the full affine scalar class on a nonempty `r`-dimensional domain; `P:337` states this correctly. Our `S:629`--`637` already gives the full qualification. |
| `P:459` | Claims a guard lowers observation dimension and hence test count. | A guard can leave the affine hull unchanged. Even lengths have the same rational affine hull as unrestricted natural lengths, and need the same constant/slope tests. Realization constraints can change without changing positive affine equalities. Our `S:647` already records this. |
| `P:163` | Finite tensor-family algebra is finite/free “only if every factor is.” | The cited result assumes finite/free factors as sufficient hypotheses; do not assert a converse. In conventions allowing the zero algebra, `Q[X] tensor_Q 0 = 0` is finite/free although `Q[X]` is not finite. Even if nonzero factors are intended, necessity needs its own hypotheses and theorem. Our `S:827`--`835` preserves the sufficient-condition distinction. |
| `P:99`, `P:364`, `P:386`, `P:425` | All nine exporters are generic, no route has mathematical meanings, or exports prove “nothing.” | Rowan supplies no Lean file. Clover's core proves seven concrete function-property rules and its generated file applies them three times. Heather has four concrete list targets plus one readiness target; one original list file fails. Generic implications themselves are valid conditional mathematical claims, while opaque atom names have no supplied arithmetic meaning. |
| `P:383`, `P:414`, `P:501` | Nine engines implement the antichain theorem; a disagreement is necessarily a bug or underspecification. | Six compute all minimal supports. Clover and Rowan compute selected closure/proof results; Heather's main program checks affine behavior and has a toy resolver. Cross-testing needs a common fragment, observable output contract, and adapters. Their certificate schemas and meanings are not interchangeable JSON. Our 128-profile Fennel/Juniper cross-check is deliberately bounded. |
| `P:492` | Antichain theorem and exporters are “both done and compiled.” | None of these Lean sources formalizes the general finite antichain termination/soundness/completeness theorem. Compiling finitely many exported implications does not prove that theorem or correctness of its producer. |
| `P:425`, `P:435` | Heather is the only mathematical exception; the lack of a toolchain was the sole missing step. | Clover is a substantive implemented grounder/registry exception. Actual parser, target correspondence, allowed methods and exporter hygiene remain design and implementation issues even after a successful chosen-file compilation. Our independent Clover adversarial exports expose this distinction. |

The proposed question “Where is a coverage proof hard?” (`P:504`) is worth
retaining. It complements our domain-certificate reuse proposal at
`S:1364`--`1376`: measure the amortized benefit of proving domain coverage
once, rather than inferring usability from short elementary frame proofs.
The question about whether a second minimal route changes an author's
decision (`P:509`) is also useful and does not require agreement that every
implementation should enumerate a full antichain.

## Original and repaired Lean boundaries

The original-copy comparison confirms that the peer's twenty original
files add no new source relative to our already checked input corpus.
Their artifact dependency and warnings should not be described as source
repairs. `CloverCore.lean:18`--`43` contains actual theorems, and
`GeneratedExamples.lean:8`, `:17`, `:28` applies them to concrete function
properties. Needing the imported core's `.olean` is an environment
requirement, not an ill-typed generated theorem.

The sole peer Heather patch deletes line 10, `omega`, from the failing
original. A read-only diff confirms that no statement or other proof line
changes. This is a specimen repair. Our existing repair changes the line to
`all_goals omega`, which also handles files where the preceding simplifier
leaves goals; the two repairs must retain distinct hashes and attribution.
Neither isolated patch constitutes an implemented fix to Heather's Python
exporter. The evenness premise is unnecessary for reversal preserving
length, so this specimen is not an even-domain completeness theorem.

## Conditions for fresh root checks

1. Check byte-identical `FreyRoutes.lean` with the already selected Lean
   4.32.0/Mathlib environment. Expect thirteen named declarations, seven
   examples, four unused-variable warnings and five explicit axiom-query
   outputs. Record actual outcomes, source hash, command, dependency
   artifacts, and exit code; do not inherit peer timing or execution claims.
2. Check byte-identical `ListImage.lean` under core Lean. Expect four named
   declarations and three examples; the unchanged source has zero queries.
   In a separately named audit harness, query all four fully qualified
   declarations: `ListImage.length_image`, `empty_one_point_frame`,
   `inhabited_two_point_frame`, and `diagonal_frame`. Keep original source
   acceptance and appended/imported audit evidence distinct.
3. Existing original-file receipts already cover the twenty identical
   inputs. The peer repair is a one-line alternative to our checked repair;
   compile it only if documenting that alternative is useful. Preserve the
   failing original result and label the repaired file separately.
4. If adding new list statements, report them as our extensions: an inhabited
   `List α` iff, an even-length iff, or an actual grammar-denotation bridge.
   They cannot be attributed to the unchanged `ListImage.lean`.

Suggested incorporation wording: “The peer synthesis supplies manual
mathematical instantiations of four fixed exported route schemas and a
four-theorem core-Lean list-image/frame specimen. These provide concrete
interfaces to reuse. They do not formalize the frontier algorithm or
establish automatic source-to-target correspondence. The exact declarations,
examples, audits, and fresh outcomes are recorded separately.”
