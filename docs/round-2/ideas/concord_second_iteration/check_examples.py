#!/usr/bin/env python3
"""Exact-arithmetic checks for the Concord design article.

These tests are NOT a Lean implementation or a formally verified checker.
They check finite polynomial certificates and examples using Python's integers
and Fraction. The universal mathematical arguments are in the article.
Run: python3 check_examples.py [--json results.json]
"""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
from typing import Callable

# Dense univariate polynomials, lowest coefficient first; () is zero.
Poly = tuple[Q, ...]

def poly(values: list[int | Q] | tuple[int | Q, ...]) -> Poly:
    out = [Q(v) for v in values]
    while out and out[-1] == 0:
        out.pop()
    return tuple(out)

def add(a: Poly, b: Poly) -> Poly:
    return poly([(a[i] if i < len(a) else 0) +
                 (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))])

def scale(k: int | Q, a: Poly) -> Poly:
    return poly([Q(k) * c for c in a])

def mul(a: Poly, b: Poly) -> Poly:
    if not a or not b:
        return ()
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return poly(out)

def deriv(a: Poly) -> Poly:
    return poly([i*a[i] for i in range(1, len(a))])

def evaluate(a: Poly, x: Q) -> Q:
    value = Q(0)
    for c in reversed(a):
        value = value*x + c
    return value

def lambert_next(n: int, p: Poly) -> Poly:
    if n < 0:
        raise ValueError('n must be nonnegative')
    return add(mul(poly([1, 1]), deriv(p)),
               scale(-1, mul(poly([3*n+2, n+1]), p)))

@dataclass(frozen=True)
class RestrictedRational:
    """Rational expression with retained exclusions; finite example only."""
    numerator: Poly
    denominator: Poly
    excluded: frozenset[Q]

    def at(self, x: Q) -> Q:
        if x in self.excluded:
            raise ValueError('point outside retained validity domain')
        den = evaluate(self.denominator, x)
        if den == 0:
            raise ValueError('zero denominator')
        return evaluate(self.numerator, x) / den


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path, help='write an execution receipt')
    args = parser.parse_args()
    tests: list[dict[str, object]] = []

    def check(name: str, test: Callable[[], bool]) -> None:
        try:
            passed = bool(test())
        except Exception as exc:
            tests.append({'name': name, 'passed': False, 'error': str(exc)})
        else:
            tests.append({'name': name, 'passed': passed})

    x = poly([0, 1])
    one = poly([1])
    num = poly([-1, 0, 1])
    den = poly([-1, 1])
    check('cancellation polynomial identity', lambda: mul(den, poly([1, 1])) == num)
    original = RestrictedRational(num, den, frozenset({Q(1)}))
    reduced = RestrictedRational(poly([1, 1]), one, original.excluded)
    check('partial equation root -1', lambda: original.at(Q(-1)) == reduced.at(Q(-1)) == 0)
    check('partial values at 2', lambda: original.at(Q(2)) == reduced.at(Q(2)) == 3)

    def excludes_one() -> bool:
        try:
            reduced.at(Q(1))
        except ValueError:
            return True
        return False
    check('simplified expression retains excluded point', excludes_one)
    check('totalized value and extension differ at 1', lambda: Q(0) != evaluate(poly([1, 1]), Q(1)))
    check('negative-neighbor cancellation mutation rejected', lambda: mul(den, poly([2, 1])) != num)

    ps = [one]
    for n in range(5):
        ps.append(lambert_next(n, ps[-1]))
    expected = [poly([1]), poly([-2, -1]), poly([9, 8, 2]),
                poly([-64, -79, -36, -6])]
    for n, p in enumerate(expected):
        check(f'Lambert P_{n}', lambda n=n, p=p: ps[n] == p)
    # The quotient/product-rule numerator identity for a generic P, P'.
    # a := n+1, k := 2*n+1: (1+w)P' - [a(1+w)+k]P
    # equals (1+w)P' - [(n+1)w+3n+2]P.
    # Check the coefficient in the indeterminate n using pairs (constant,n).
    check('parametric Lambert constant coefficient identity',
          lambda: add(poly([1, 1]), poly([1, 2])) == poly([2, 3]))
    for n in range(5):
        p = ps[n]
        lhs = add(mul(poly([1, 1]), deriv(p)),
                  scale(-1, mul(add(scale(n+1, poly([1, 1])), poly([2*n+1])), p)))
        check(f'Lambert quotient numerator n={n}', lambda lhs=lhs, n=n: lhs == ps[n+1])
    check('Lambert 3n+1 mutation rejected',
          lambda: add(mul(poly([1, 1]), deriv(ps[2])),
                      scale(-1, mul(poly([7, 3]), ps[2]))) != ps[3])

    catalan = [1]
    for n in range(1, 7):
        catalan.append(sum(catalan[i]*catalan[n-1-i] for i in range(n)))
    check('Catalan coefficients through degree six', lambda: catalan == [1, 1, 2, 5, 14, 42, 132])
    c = poly(catalan[:6])
    residual = add(add(c, scale(-1, one)), scale(-1, mul(x, mul(c, c))))
    check('Catalan jet residual vanishes below degree six', lambda: all(v == 0 for v in residual[:6]))
    check('Catalan jet is not a full polynomial solution', lambda: bool(residual) and residual[6] == -132)

    lo, hi = Q(1414213, 10**6), Q(1414214, 10**6)
    check('exact square-root lower bound certificate', lambda: lo >= 0 and lo*lo < 2)
    check('exact square-root upper bound certificate', lambda: hi >= 0 and hi*hi > 2)
    check('wrong square-root upper bound rejected', lambda: not (lo*lo > 2))
    check('integer ideal certificate requires noninteger scalar',
          lambda: mul(poly([Q(1, 2)]), poly([0, 2])) == x and Q(1, 2).denominator != 1)
    check('zero-divisor cancellation counterexample mod 6',
          lambda: (2*0) % 6 == (2*3) % 6 and 0 != 3)
    check('natural subtraction transport counterexample', lambda: Q(max(2-3, 0)) != Q(2)-Q(3))
    check('natural exact division counterexample', lambda: Q(3//2) != Q(3, 2))

    receipt = {
        'status': 'exact-arithmetic sanity checks; not formal verification',
        'tests': tests,
        'passed': sum(bool(t['passed']) for t in tests),
        'total': len(tests),
        'lambert_polynomials_lowest_coefficient_first': [[str(v) for v in p] for p in ps],
        'catalan_jet_residual_lowest_coefficient_first': [str(v) for v in residual],
        'sqrt_two_squared_bound_numerators': [1414213**2, 2*10**12, 1414214**2],
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(f"{receipt['passed']}/{receipt['total']} exact-arithmetic checks passed")
    for test in tests:
        if not test['passed']:
            print('FAILED:', test)
    if receipt['passed'] != receipt['total']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
