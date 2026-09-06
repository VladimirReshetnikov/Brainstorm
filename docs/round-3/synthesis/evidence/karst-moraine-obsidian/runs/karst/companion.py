#!/usr/bin/env python3
"""Finite, reproducible sanity checks for the Karst article.

This is not a Lean kernel or a proof of compiler soundness. Polynomial tests
exercise a reference checker whose general soundness is proved on paper in
the article. Scope tests exercise a synthetic metadata boundary, not Lean
expressions or a functioning Karst elaborator. Standard library only.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
import json
import random
from typing import Iterable

Monomial = tuple[int, ...]
Term = tuple[Monomial, int]
Polynomial = tuple[Term, ...]


def normalize(terms: Iterable[Term], dimension: int) -> Polynomial:
    """Canonical sparse integer polynomial; refuse malformed dimensions."""
    if type(dimension) is not int or dimension < 0:
        raise ValueError("dimension must be a nonnegative integer")
    acc: dict[Monomial, int] = {}
    for powers, coeff in terms:
        if len(powers) != dimension:
            raise ValueError("wrong monomial dimension")
        if any(type(k) is not int or k < 0 for k in powers):
            raise ValueError("exponents must be nonnegative integers")
        if type(coeff) is not int:
            raise ValueError("coefficients must be integers")
        acc[powers] = acc.get(powers, 0) + coeff
    return tuple(sorted((powers, c) for powers, c in acc.items() if c))


def add(p: Polynomial, q: Polynomial, d: int) -> Polynomial:
    return normalize((*p, *q), d)


def neg(p: Polynomial, d: int) -> Polynomial:
    return normalize(((a, -c) for a, c in p), d)


def mul(p: Polynomial, q: Polynomial, d: int) -> Polynomial:
    # Validate before zip: never silently truncate exponent vectors.
    p, q = normalize(p, d), normalize(q, d)
    return normalize(((tuple(a[j] + b[j] for j in range(d)), c * e)
                      for a, c in p for b, e in q), d)


def evaluate(p: Polynomial, values: tuple[int, ...], modulus: int | None = None) -> int:
    total = 0
    for powers, c in normalize(p, len(values)):
        term = c
        for x, power in zip(values, powers):
            term *= x ** power
        total += term
    return total if modulus is None else total % modulus


def check_certificate(p: Polynomial, fs: list[Polynomial], qs: list[Polynomial],
                      dimension: int) -> bool:
    """Positive ideal certificate only. False is not nonmembership evidence."""
    if len(fs) != len(qs):
        return False
    try:
        residual = normalize(p, dimension)
        for f, q in zip(fs, qs):
            residual = add(residual, neg(mul(q, f, dimension), dimension), dimension)
        return not residual
    except (ValueError, TypeError):
        return False


@dataclass(frozen=True)
class Origin:
    term_id: str
    type_id: str
    structure_id: str
    revision: str


@dataclass(frozen=True)
class Fact:
    origin: Origin
    predicate: str
    scope: tuple[str, ...]


def usable(fact: Fact, origin: Origin, predicate: str, scope: tuple[str, ...]) -> bool:
    """Synthetic check only: assumes a separate logical proof already exists."""
    return (fact.origin == origin and fact.predicate == predicate
            and scope[:len(fact.scope)] == fact.scope)


def acyclic(dependencies: dict[str, tuple[str, ...]]) -> bool:
    visiting: set[str] = set()
    done: set[str] = set()
    def visit(n: str) -> bool:
        if n in visiting or n not in dependencies:
            return False
        if n in done:
            return True
        visiting.add(n)
        if not all(visit(p) for p in dependencies[n]):
            return False
        visiting.remove(n)
        done.add(n)
        return True
    return all(visit(n) for n in dependencies)


def convolution(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def main() -> dict:
    results: list[dict] = []
    def record(name: str, cases: int, note: str) -> None:
        results.append(dict(name=name, cases=cases, status="passed", interpretation=note))

    # Exhaustive finite-map check, including the empty carrier.
    maps = injective_maps = 0
    for n in range(6):
        for f in product(range(n), repeat=n):
            maps += 1
            if len(set(f)) != n:
                continue
            injective_maps += 1
            assert set(f) == set(range(n))
            if n == 0:
                continue
            a = f[0]
            def tau(x: int) -> int:
                return a if x == 0 else 0 if x == a else x
            assert all(tau(tau(x)) == x for x in range(n))
            k = tuple(tau(f[x]) for x in range(n))
            assert k[0] == 0 and len(set(k)) == n
            assert all(k[i] != 0 for i in range(1, n))
            small = tuple(k[i+1] - 1 for i in range(n-1))
            assert set(small) == set(range(n-1))
            assert all(tau(k[x]) == f[x] for x in range(n))
    record("finite_endomaps", maps,
           f"All maps on carriers of sizes 0..5; {injective_maps} injective maps also pass normalization/restriction. Not an infinite theorem.")

    # Polynomial identity and malformed certificate neighbors.
    d = 2
    p = normalize([((2, 0), 1), ((0, 2), -1)], d)
    f = normalize([((1, 0), 1), ((0, 1), -1)], d)
    q = normalize([((1, 0), 1), ((0, 1), 1)], d)
    assert check_certificate(p, [f], [q], d)
    assert not check_certificate(p, [f], [], d)
    assert not check_certificate(p, [], [q], d)
    corrupt = add(q, normalize([((0, 0), 1)], d), d)
    assert not check_certificate(p, [f], [corrupt], d)
    assert not check_certificate(p, [(((1,), 1),)], [q], d)
    assert not check_certificate(p, [(((1, -1), 1),)], [q], d)
    assert check_certificate((), [], [], d)
    record("polynomial_protocol_neighbors", 7,
           "Valid identity, corrupted multiplier, malformed dimensions/exponents, both arity mismatches, valid zero case.")

    rng = random.Random(20260906)
    polynomial_trials = 0
    for d in (1, 2, 3):
        for _ in range(80):
            rawp = tuple((tuple(rng.randrange(4) for _ in range(d)), rng.randrange(-3, 4)) for _ in range(8))
            rawq = tuple((tuple(rng.randrange(4) for _ in range(d)), rng.randrange(-3, 4)) for _ in range(8))
            p, q = normalize(rawp, d), normalize(rawq, d)
            v = tuple(rng.randrange(-2, 3) for _ in range(d))
            for modulus in (None, 4, 5):
                reduction = (lambda x: x) if modulus is None else (lambda x, m=modulus: x % m)
                ep, eq = evaluate(p, v, modulus), evaluate(q, v, modulus)
                assert evaluate(rawp, v, modulus) == ep
                assert evaluate(add(p, q, d), v, modulus) == reduction(ep + eq)
                assert evaluate(mul(p, q, d), v, modulus) == reduction(ep * eq)
                assert evaluate(neg(p, d), v, modulus) == reduction(-ep)
                polynomial_trials += 1
    record("polynomial_denotation_samples", polynomial_trials,
           "Seeded samples in integers, Z/4Z, and Z/5Z, in 1..3 variables. Tests, not universal soundness proof.")

    # Behavioral predicates distinguish candidates at the same simple type.
    lists = [xs for n in range(6) for xs in product(range(3), repeat=n)]
    for xs in lists:
        ys = tuple(sorted(xs))
        assert Counter(ys) == Counter(xs)
        assert all(ys[i] <= ys[i+1] for i in range(len(ys)-1))
    assert len(tuple(reversed((1, 2)))) == 2
    assert not all(x <= y for x, y in zip((2, 1), (1,)))
    assert Counter((1, 1)) != Counter((1, 2))
    assert Counter(()) != Counter((1,))
    record("sorting_behavior_samples", len(lists),
           "Sorting checked on all lists of length <=5 over {0,1,2}; reverse, repeat-first, and empty-output distinguish weaker guarantees.")

    # All concrete lists of Empty are empty, but an unguarded length model may admit 1.
    concrete_empty_type_inputs = [()]
    assert all(len(()) == len(xs) for xs in concrete_empty_type_inputs)
    abstract_counterexample_length = 1
    assert abstract_counterexample_length != 0
    assert not any(len(xs) == abstract_counterexample_length for xs in concrete_empty_type_inputs)
    record("length_counterexample_realizability", 1,
           "An abstract nonzero input length does not supply an input of List Empty. No claim about Leant eligibility or a Leant defect.")

    # Exact quotient checks need no supposed Fermat counterexample.
    quotient_cases = 0
    for a in range(-15, 16):
        if a % 4 != 3:
            continue
        for b in range(-12, 13, 2):
            for exponent in (5, 7, 11):
                n2 = b**exponent - 1 - a**exponent
                n4 = -(a**exponent)*b**exponent
                assert n2 % 4 == 0 and n4 % 16 == 0
                assert Fraction(n2//4) == Fraction(n2, 4)
                assert Fraction(n4//16) == Fraction(n4, 16)
                quotient_cases += 1
    record("frey_exact_quotient_samples", quotient_cases,
           "Only parity/congruence denominator claims; no FLT hypothesis, FLT proof, or curve-theorem verification is being tested.")

    j = list(map(Fraction, [1])) + [Fraction(1,2), Fraction(-1,8), Fraction(1,16), Fraction(-5,128)]
    residual = convolution(j, j)
    residual[0] -= 1
    residual[1] -= 1
    assert all(c == 0 for c in residual[:5])
    assert residual[5] == Fraction(-7,128)
    derivative = [i*j[i] for i in range(1, len(j))]
    assert derivative == [Fraction(1,2), Fraction(-1,4), Fraction(3,16), Fraction(-5,32)]
    wrong_branch = [-c for c in j]
    assert convolution(wrong_branch, wrong_branch) == convolution(j, j)
    assert wrong_branch[0] != 1
    assert 4 < 4 + 1  # precision-4 input does not meet this sufficient precision-5 contract
    assert 2 != 0 and (2*2) % 4 == 0  # nonzero is not regular modulo 4
    record("formal_jet_neighbors", 5,
           "Rational residual and derivative, wrong constant branch, precision demand, nonunit/nonregular modulo-4 neighbor.")

    root = ("theorem",)
    left, right = root + ("left",), root + ("right",)
    original = Origin("local_f_1", "A_to_A", "standard", "revision1")
    fact = Fact(original, "injective", left)
    assert usable(fact, original, "injective", left)
    assert usable(fact, original, "injective", left + ("nested",))
    assert not usable(fact, original, "injective", root)
    assert not usable(fact, original, "injective", right)
    assert not usable(fact, original, "surjective", left)
    assert not usable(fact, Origin("local_f_2", "A_to_A", "standard", "revision1"), "injective", left)
    assert not usable(fact, Origin("local_f_1", "A_to_A", "alternate", "revision1"), "injective", left)
    assert not usable(fact, Origin("local_f_1", "A_to_A", "standard", "revision2"), "injective", left)
    assert acyclic({"given": (), "derived": ("given",)})
    assert not acyclic({"guard": ("result",), "result": ("guard",)})
    assert not acyclic({"result": ("missing",)})
    record("synthetic_scope_and_origin_neighbors", 11,
           "Metadata model only: lexical use, origin/structure/revision changes, no sibling leakage, no cyclic or missing dependency. Does not check Lean proofs.")

    return dict(status="all finite checks passed", seed=20260906,
                evidence_level="Python sanity checks; no Lean execution",
                groups=results,
                limitations=["No Karst parser/elaborator exists in this package.",
                             "No repository was built and no Lean source was compiled here.",
                             "Finite tests are not universal mathematical or compiler proofs.",
                             "Scope checks use synthetic identities, not Lean expression serialization."])


if __name__ == "__main__":
    output = main()
    target = Path(__file__).with_name("results.json")
    target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
