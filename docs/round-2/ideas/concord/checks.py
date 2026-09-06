#!/usr/bin/env python3
"""Exact finite sanity checks for the Concord design article.

Standard-library only. This is NOT a formally verified checker or a language
implementation. Passing these tests does not prove any universal theorem.
Run: python3 checks.py --output checks.json
"""
from __future__ import annotations
import argparse
import json
from fractions import Fraction
from math import comb, factorial
from pathlib import Path

# Sparse polynomials in a and x, with exact rational coefficients.
Poly = dict[tuple[int, int], Fraction]

def clean(p: Poly) -> Poly:
    return {m: c for m, c in p.items() if c}

def const(c: int | Fraction) -> Poly:
    return {} if not c else {(0, 0): Fraction(c)}

def mono(a: int, x: int, c: int | Fraction = 1) -> Poly:
    return {} if not c else {(a, x): Fraction(c)}

def add(p: Poly, q: Poly) -> Poly:
    out = dict(p)
    for m, c in q.items():
        out[m] = out.get(m, Fraction(0)) + c
    return clean(out)

def scale(p: Poly, c: int | Fraction) -> Poly:
    return clean({m: v * c for m, v in p.items()})

def mul(p: Poly, q: Poly) -> Poly:
    out: Poly = {}
    for (a, x), c in p.items():
        for (b, y), d in q.items():
            m = (a+b, x+y)
            out[m] = out.get(m, Fraction(0)) + c*d
    return clean(out)

def power(p: Poly, n: int) -> Poly:
    if n < 0:
        raise ValueError('Polynomial exponent must be nonnegative')
    out = const(1)
    for _ in range(n):
        out = mul(out, p)
    return out

def jet_mul(p: list[Poly], q: list[Poly]) -> list[Poly]:
    if len(p) != len(q):
        raise ValueError('Jet lengths must agree')
    out: list[Poly] = [{} for _ in p]
    for k in range(len(p)):
        for i in range(k+1):
            out[k] = add(out[k], mul(p[i], q[k-i]))
    return out

def jet_exp(p: list[Poly]) -> list[Poly]:
    """exp(p) modulo z^N for a zero-constant jet of length N."""
    if not p or p[0]:
        raise ValueError('Positive precision and zero constant are required')
    n = len(p)
    term = [const(1)] + [{} for _ in range(n-1)]
    out = [{} for _ in range(n)]
    for k in range(n):
        out = [add(v, scale(w, Fraction(1, factorial(k))))
               for v, w in zip(out, term)]
        term = jet_mul(term, p)
    return out

def encoded_poly(p: Poly) -> list[dict[str, int | str]]:
    return [{'a_power': a, 'x_power': x, 'coefficient': str(c)}
            for (a, x), c in sorted(p.items())]

def run_checks() -> dict:
    records: list[dict] = []
    def check(name: str, condition: bool, family: str) -> None:
        if not condition:
            raise AssertionError(f'Check failed: {name}')
        records.append({'name': name, 'family': family, 'passed': True})

    # Original integer kernel, including empty intervals when j > n.
    for n in range(21):
        for j in range(21):
            total = sum((-1)**(n-k) * comb(n, k) * comb(k, j)
                        for k in range(j, n+1))
            check(f'binomial_kernel_n{n}_j{j}', total == int(n == j),
                  'binomial finite instances')

    # A proposed implicit-series jet, not computed from the formula being tested.
    a, x = mono(1, 0), mono(0, 1)
    p = [{}, const(1), mono(1, 0, -1),
         mono(2, 0, Fraction(3, 2)), mono(3, 0, Fraction(-8, 3))]
    exp_minus_ap = jet_exp([scale(mul(a, c), -1) for c in p])
    psi = [{}] + exp_minus_ap[:-1]
    residual = [add(c, scale(d, -1)) for c, d in zip(p, psi)]
    for k, c in enumerate(residual):
        check(f'abel_residual_degree{k}', not c, 'formal residual coefficients')

    e = jet_exp([mul(x, c) for c in p])
    for k in range(1, 5):
        expected = scale(mul(x, power(add(x, scale(a, -k)), k-1)),
                         Fraction(1, factorial(k)))
        check(f'abel_exp_coefficient_degree{k}', e[k] == expected,
              'Abel coefficient polynomial identities')

    # Perturbing the fourth coefficient must be detected by the residual.
    bad = [dict(c) for c in p]
    bad[4] = add(bad[4], const(1))
    bad_psi = [{}] + jet_exp([scale(mul(a, c), -1) for c in bad])[:-1]
    bad_res = [add(c, scale(d, -1)) for c, d in zip(bad, bad_psi)]
    check('perturbed_degree4_residual_is_nonzero', bool(bad_res[4]),
          'negative neighbors')

    # Exact counterexamples to unsafe translations or conclusions.
    check('truncated_subtraction_not_integer_subtraction', max(0-1, 0) != 0-1,
          'negative neighbors')
    check('natural_division_not_rational_division', Fraction(3//2) != Fraction(3,2),
          'negative neighbors')
    check('mod2_equality_does_not_reflect_integer_equality',
          0 % 2 == 2 % 2 and 0 != 2, 'negative neighbors')
    check('square_zero_not_zero_in_Zmod4', (2*2) % 4 == 0 and 2 % 4 != 0,
          'negative neighbors')
    check('lost_endpoint_changes_singleton_sum', sum(range(0)) != 1,
          'negative neighbors')
    # F=0 and G=z^3 agree below degree 3, but F' and G' disagree at degree 2.
    f, g = [0,0,0,0], [0,0,0,1]
    df, dg = [k*f[k] for k in range(1,4)], [k*g[k] for k in range(1,4)]
    check('differentiation_requires_extra_precision', f[:3] == g[:3] and df != dg,
          'negative neighbors')

    check('sqrt2_lower_squared_bound', Fraction(7,5)**2 < 2, 'root enclosure')
    check('sqrt2_upper_squared_bound', 2 < Fraction(3,2)**2, 'root enclosure')

    counts: dict[str, int] = {}
    for rec in records:
        counts[rec['family']] = counts.get(rec['family'], 0) + 1
    return {
        'status': 'all finite checks passed',
        'scope': 'Exact finite arithmetic and polynomial sanity checks only; not Lean verification.',
        'total_checks': len(records),
        'counts_by_family': counts,
        'abel_jet_precision': 5,
        'abel_exp_degree4': encoded_poly(e[4]),
        'checks': records,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('checks.json'))
    args = parser.parse_args()
    report = run_checks()
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, indent=2))

if __name__ == '__main__':
    main()
