#!/usr/bin/env python3
"""Finite, exact-arithmetic checks for the examples in facet.tex.

These are ordinary Python consistency checks, NOT formal proofs, NOT a Lean
implementation, and NOT tests of the proposed Facet language or protocol.
All calculations use integers and fractions.Fraction; no floating-point root
approximations or external CAS are used. Run: python3 math_checks.py
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as F
from math import comb, factorial
import json

Poly = list[F]  # coefficient order: constant term first
checks: Counter[str] = Counter()


def check(family: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(f"Failed consistency check in {family}")
    checks[family] += 1


def trim(p: Poly) -> Poly:
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p or [F(0)]


def mul(p: Poly, q: Poly) -> Poly:
    r = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    return trim(r)


def derivative(p: Poly) -> Poly:
    return trim([F(i) * p[i] for i in range(1, len(p))])


def exp_series(h: Poly, order: int) -> Poly:
    """Compute exp(h) through order, for h[0] = 0, using E' = h' E."""
    if order < 0 or not h or h[0] != 0:
        raise ValueError("Expected nonnegative order and zero constant term")
    e = [F(1)] + [F(0)] * order
    for n in range(1, order + 1):
        e[n] = sum((F(k) * h[k] * e[n-k]
                    for k in range(1, min(n, len(h)-1) + 1)), F(0)) / n
    return e


def abel_series(a: F, order: int) -> Poly:
    """Build T = t exp(-a T) recursively, only to the requested finite order."""
    t = [F(0)] * (order + 1)
    for n in range(1, order + 1):
        t[n] = exp_series([-a * c for c in t], n - 1)[n - 1]
    return t


# Finite binomial-kernel checks, including empty intervals and diagonal cases.
for n in range(25):
    for j in range(29):
        lhs = sum((-1)**(n-k) * comb(n, k) * comb(k, j)
                  for k in range(j, n+1))
        check("binomial_kernel_instances", lhs == int(n == j))

# An additive-group example with torsion, not a field computation.
a = [(n*n + 3*n + 1) % 6 for n in range(20)]
b = [sum(comb(n, k) * a[k] for k in range(n+1)) % 6 for n in range(20)]
restored = [sum((-1)**(n-k) * comb(n, k) * b[k] for k in range(n+1)) % 6
            for n in range(20)]
for original, recovered in zip(a, restored):
    check("binomial_inversion_Z_mod_6", original == recovered)

# Displayed autonomous-ODE polynomials: P[n+1] = (1 + X^2) P[n]'.
p = [F(0), F(1)]
expected = [
    [0, 1], [1, 0, 1], [0, 2, 0, 2],
    [2, 0, 8, 0, 6], [0, 16, 0, 40, 0, 24],
]
for coeffs in expected:
    check("ODE_polynomial_coefficients", p == [F(c) for c in coeffs])
    p = mul([F(1), F(0), F(1)], derivative(p))

# Independently compute finite Abel coefficients, then compare with the formula.
order = 12
for av in range(-2, 3):
    a0 = F(av)
    t = abel_series(a0, order)
    check("Abel_initial_coefficients", t[:5] ==
          [F(0), F(1), -a0, F(3, 2)*a0*a0, -F(8, 3)*a0**3])
    for xv in range(-2, 3):
        x = F(xv)
        e = exp_series([x*c for c in t], order)
        check("Abel_exponential_coefficients", e[0] == 1)
        for m in range(1, order+1):
            target = x * (x - m*a0)**(m-1) / factorial(m)
            check("Abel_exponential_coefficients", e[m] == target)

# Total-division counterexample and the two natural-arithmetic bridge failures.
def total_div(a: F, b: F) -> F:
    return a / b if b else F(0)

x = F(1)
check("domain_counterexamples", total_div(x*x-1, x-1) == 0 and x+1 == 2)
check("domain_counterexamples", F(max(2-3, 0)) != F(2)-F(3))
check("domain_counterexamples", F(3//2) != F(3, 2))

# Polynomial versus evaluation-function equality over F_2.
check("polynomial_function_counterexample_F2",
      all((v*v-v) % 2 == 0 for v in (0, 1)) and (-1 % 2, 1 % 2) != (0, 0))

# Jets through N of 0 and X^(N+1) agree; their derivatives differ in degree N.
for n in range(1, 9):
    g = [F(0)]*(n+1) + [F(1)]
    check("jet_precision_counterexamples", all(c == 0 for c in g[:n+1])
          and derivative(g)[n] == n+1)

# Algebra in Q[s,t]/(s^2-3,t^2-2) for the denesting square identity.
# This checks algebra only: the principal-root sign argument is in the article.
Quad = dict[tuple[int, int], F]


def qadd(a: Quad, b: Quad, scale: F = F(1)) -> Quad:
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, F(0)) + scale*v
    return {k: v for k, v in out.items() if v}


def qmul(a: Quad, b: Quad) -> Quad:
    out: Quad = {}
    for (i,j), u in a.items():
        for (k,l), v in b.items():
            r, s = i+k, j+l
            key = (r % 2, s % 2)
            out[key] = out.get(key, F(0)) + u*v*3**(r//2)*2**(s//2)
    return {k: v for k, v in out.items() if v}


y: Quad = {(1,0): F(1), (0,1): F(-1)}
y2 = qmul(y,y)
check("denesting_algebra_only", y2 == {(0,0): F(5), (1,1): F(-2)})
check("denesting_algebra_only", qadd(qadd(qmul(y2,y2), y2, F(-10)), {(0,0): F(1)}) == {})
neg_y = {k: -v for k,v in y.items()}
check("denesting_algebra_only", qmul(neg_y,neg_y) == y2)

# Rational values used by the cubic-root enclosure derivation.
def cubic(t: F) -> F:
    return t**3-t-1

q = F(53,40)
check("cubic_residual_arithmetic", cubic(F(1)) == -1)
check("cubic_residual_arithmetic", cubic(F(3,2)) == F(7,8))
check("cubic_residual_arithmetic", cubic(q) == F(77,64000))
check("cubic_residual_arithmetic", cubic(q)/2 == F(77,128000))
check("cubic_residual_arithmetic", F(1) < q-F(77,128000) < q < F(3,2))

print(json.dumps({
    "status": "all finite exact-arithmetic consistency checks passed",
    "total_checks": sum(checks.values()),
    "checks_by_family": dict(checks),
    "arithmetic": "Python integers and fractions.Fraction only",
    "limits": [
        "Not formal proofs or a verified implementation.",
        "No Lean code, Facet language, provider adapter, or protocol test was run.",
        "Finite samples do not establish universally quantified identities.",
        "Denesting checks are algebraic; principal-branch signs are proved in prose.",
        "Cubic checks verify rational calculations, not a machine-checked analytic theorem."
    ]
}, indent=2))
