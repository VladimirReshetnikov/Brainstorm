#!/usr/bin/env python3
"""Exact-arithmetic companions to the Locus proof-language design.

Python 3.9+; standard library only. Run:
    python certificate_demo.py --json test-results.json

This is NOT a Lean implementation or a formally verified checker. The small,
independently structured checks exercise the mathematical certificate contracts
proved on paper in the article. Finite tests do not prove universal identities.
All algebraic and interval calculations use exact rational arithmetic.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path
from typing import Iterable, Tuple

Poly = Tuple[F, ...]  # low degree first; trailing zeros removed
Biquad = Tuple[F, F, F, F]  # 1, sqrt(2), sqrt(3), sqrt(6)


def poly(values: Iterable[F]) -> Poly:
    result = list(map(F, values))
    while result and result[-1] == 0:
        result.pop()
    return tuple(result)


def coefficient(p: Poly, k: int) -> F:
    return p[k] if 0 <= k < len(p) else F(0)


def add(p: Poly, q: Poly) -> Poly:
    return poly(coefficient(p, i) + coefficient(q, i)
                for i in range(max(len(p), len(q))))


def scale(a: F, p: Poly) -> Poly:
    return poly(F(a) * x for x in p)


def mul(p: Poly, q: Poly) -> Poly:
    if not p or not q:
        return ()
    result = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            result[i + j] += a * b
    return poly(result)


def derivative(p: Poly) -> Poly:
    return poly(i * p[i] for i in range(1, len(p)))


def truncate(p: Poly, n: int) -> Poly:
    if type(n) is not int or n < 0:
        raise ValueError("precision must be a nonnegative integer")
    return poly(p[:n])


def evaluate(p: Poly, x: F) -> F:
    y = F(0)
    for a in reversed(p):
        y = y * x + a
    return y


def synthesize_dyadic_jet(n: int) -> Poly:
    """Producer: triangular coefficient recurrence, not the checker below."""
    if type(n) is not int or n < 1:
        raise ValueError("jet precision must be a positive integer")
    a = [F(0)] * n
    if n > 1:
        a[1] = F(4, 9)
    for k in range(2, n):
        a[k] = -4 * sum((a[i] * a[k - i] for i in range(1, k)), F(0))
    return poly(a)


def dyadic_residual(j: Poly) -> Poly:
    # F(J,q) = J + 4 J^2 - (4/9) q
    return add(add(j, scale(F(4), mul(j, j))), (F(0), F(-4, 9)))


def check_dyadic_jet(j: Poly, n: int) -> bool:
    """Checks a canonical finite candidate, its branch, and residual precision.

    The paper proves that these premises imply J = Delta mod q^n, using
    existence of Delta and invertibility of 1 + 4(J+Delta). This function
    checks the finite premises, not that metatheorem or existence theorem.
    """
    if type(n) is not int or n < 1:
        return False
    if not isinstance(j, tuple) or any(not isinstance(x, F) for x in j):
        return False
    if poly(j) != j or len(j) > n or coefficient(j, 0) != 0:
        return False
    return truncate(dyadic_residual(j), n) == ()


def catalan_coefficient(n: int) -> F:
    if n < 1:
        return F(0)
    catalan = math.comb(2 * n - 2, n - 1) // n
    return F((-1) ** (n - 1) * 4 ** (2 * n - 1) * catalan, 9 ** n)


def biquad_mul(a: Biquad, b: Biquad) -> Biquad:
    # Bit 0 represents sqrt(2), bit 1 represents sqrt(3).
    result = [F(0)] * 4
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            common = i & j
            factor = (2 if common & 1 else 1) * (3 if common & 2 else 1)
            result[i ^ j] += x * y * factor
    return tuple(result)  # type: ignore[return-value]


RADICAL_TARGET: Biquad = (F(5), F(0), F(0), F(2))
RADICAL_CANDIDATE: Biquad = (F(0), F(1), F(1), F(0))
RADICAL_BOUNDS = ((F(1), F(1)), (F(7, 5), F(3, 2)),
                  (F(17, 10), F(7, 4)), (F(12, 5), F(5, 2)))


def valid_radical_bounds(bounds) -> bool:
    if len(bounds) != 4 or bounds[0] != (F(1), F(1)):
        return False
    for m, (lo, hi) in zip((1, 2, 3, 6), bounds):
        if not (isinstance(lo, F) and isinstance(hi, F)):
            return False
        if not (0 <= lo <= hi and lo * lo <= m <= hi * hi):
            return False
    return True


def biquad_enclosure(a: Biquad, bounds=RADICAL_BOUNDS):
    if not valid_radical_bounds(bounds):
        raise ValueError("invalid rational root enclosures")
    lower, upper = F(0), F(0)
    for c, (lo, hi) in zip(a, bounds):
        lower += c * (lo if c >= 0 else hi)
        upper += c * (hi if c >= 0 else lo)
    return lower, upper


def check_principal_radical(a: Biquad, bounds=RADICAL_BOUNDS) -> bool:
    if len(a) != 4 or any(not isinstance(x, F) for x in a):
        return False
    if not valid_radical_bounds(bounds) or biquad_mul(a, a) != RADICAL_TARGET:
        return False
    # A sufficient positivity certificate, deliberately incomplete as a solver.
    return biquad_enclosure(a, bounds)[0] >= 0


def total_div(a: F, b: F) -> F:
    return F(0) if b == 0 else a / b


def binomial_kernel(n: int, j: int, omit_upper: bool = False) -> int:
    upper = n if omit_upper else n + 1
    return sum((-1) ** (n - k) * math.comb(n, k) * math.comb(k, j)
               for k in range(j, upper))


CUBIC = (F(-1), F(-1), F(0), F(1))


def bisect_cubic(steps: int = 48):
    a, b = F(1), F(2)
    for _ in range(steps):
        m = (a + b) / 2
        if evaluate(CUBIC, m) < 0:
            a = m
        else:
            b = m
    return a, b


def check_cubic_bracket(a: F, b: F) -> bool:
    # Continuity and strict monotonicity on [1,infinity) are proved on paper.
    return (isinstance(a, F) and isinstance(b, F) and
            1 <= a < b and evaluate(CUBIC, a) < 0 < evaluate(CUBIC, b))


class CertificateTests(unittest.TestCase):
    def test_polynomial_arithmetic(self):
        self.assertEqual(mul((F(-1), F(1)), (F(1), F(1))), (F(-1), F(0), F(1)))
        self.assertEqual(derivative((F(2), F(3), F(4))), (F(3), F(8)))
        self.assertEqual(evaluate((F(1), F(2), F(3)), F(2)), F(17))

    def test_zero_polynomials(self):
        self.assertEqual(poly([0, 0]), ())
        self.assertEqual(mul((), (F(1),)), ())
        self.assertEqual(derivative(()), ())

    def test_positive_jets(self):
        for n in range(1, 25):
            with self.subTest(precision=n):
                self.assertTrue(check_dyadic_jet(synthesize_dyadic_jet(n), n))

    def test_coefficient_formula(self):
        j = synthesize_dyadic_jet(25)
        for n in range(1, 25):
            with self.subTest(degree=n):
                self.assertEqual(coefficient(j, n), catalan_coefficient(n))

    def test_mutated_coefficients(self):
        for n in range(2, 25):
            j = list(synthesize_dyadic_jet(n))
            j[n - 1] += 1
            with self.subTest(precision=n):
                self.assertFalse(check_dyadic_jet(poly(j), n))

    def test_no_precision_promotion(self):
        for n in range(1, 24):
            j = synthesize_dyadic_jet(n)
            with self.subTest(precision=n):
                self.assertTrue(check_dyadic_jet(j, n))
                self.assertFalse(check_dyadic_jet(j, n + 1))

    def test_wrong_root_branch(self):
        j = synthesize_dyadic_jet(9)
        other = add((F(-1, 4),), scale(F(-1), j))
        self.assertEqual(truncate(dyadic_residual(other), 9), ())
        self.assertFalse(check_dyadic_jet(other, 9))

    def test_invalid_precision(self):
        for n in (0, -1, True, F(2)):
            self.assertFalse(check_dyadic_jet((), n))
        with self.assertRaises(ValueError):
            synthesize_dyadic_jet(0)

    def test_noncanonical_or_untyped_candidate(self):
        self.assertFalse(check_dyadic_jet((F(0), F(0)), 2))
        self.assertFalse(check_dyadic_jet((0, F(4, 9)), 2))
        self.assertFalse(check_dyadic_jet([F(0)], 2))

    def test_derivative_loses_one_order(self):
        for n in range(1, 25):
            p = (F(0),) * n + (F(1),)
            with self.subTest(precision=n):
                self.assertEqual(truncate(p, n), ())
                self.assertEqual(truncate(derivative(p), n - 1), ())
                self.assertNotEqual(truncate(derivative(p), n), ())

    def test_formal_residual_factorization(self):
        for n in range(2, 18):
            p, q = synthesize_dyadic_jet(n), synthesize_dyadic_jet(n + 2)
            lhs = add(dyadic_residual(p), scale(F(-1), dyadic_residual(q)))
            rhs = mul(add(p, scale(F(-1), q)), add((F(1),), scale(F(4), add(p, q))))
            self.assertEqual(lhs, rhs)

    def test_radical_arithmetic(self):
        self.assertEqual(biquad_mul(RADICAL_CANDIDATE, RADICAL_CANDIDATE), RADICAL_TARGET)
        self.assertTrue(check_principal_radical(RADICAL_CANDIDATE))

    def test_radical_negative_branch(self):
        neg = tuple(-x for x in RADICAL_CANDIDATE)
        self.assertEqual(biquad_mul(neg, neg), RADICAL_TARGET)
        self.assertFalse(check_principal_radical(neg))

    def test_radical_wrong_magnitude(self):
        self.assertFalse(check_principal_radical((F(0), F(2), F(1), F(0))))

    def test_forged_root_enclosure(self):
        bad = list(RADICAL_BOUNDS)
        bad[1] = (F(2), F(3))
        self.assertFalse(valid_radical_bounds(bad))
        self.assertFalse(check_principal_radical(RADICAL_CANDIDATE, bad))

    def test_rational_function_cross_multiplication(self):
        self.assertEqual(mul((F(1), F(1)), (F(-1), F(1))), (F(-1), F(0), F(1)))
        for x in map(F, range(-10, 11)):
            if x != 1:
                self.assertEqual(total_div(x * x - 1, x - 1), x + 1)

    def test_totalized_singularity(self):
        self.assertEqual(total_div(F(0), F(0)), F(0))
        self.assertNotEqual(total_div(F(0), F(0)), F(2))

    def test_binomial_orthogonality_instances(self):
        for n in range(26):
            for j in range(27):
                with self.subTest(n=n, j=j):
                    self.assertEqual(binomial_kernel(n, j), int(n == j))

    def test_missing_endpoint(self):
        for n in range(26):
            self.assertEqual(binomial_kernel(n, n, omit_upper=True), 0)
            self.assertEqual(binomial_kernel(n, n), 1)

    def test_zero_and_empty_intervals(self):
        self.assertEqual(binomial_kernel(0, 0), 1)
        self.assertEqual(binomial_kernel(0, 1), 0)
        self.assertEqual(binomial_kernel(2, 5), 0)

    def test_cubic_brackets(self):
        for steps in (0, 1, 8, 24, 48, 64):
            a, b = bisect_cubic(steps)
            self.assertTrue(check_cubic_bracket(a, b))
            self.assertEqual(b - a, F(1, 2 ** steps))

    def test_cubic_invalid_brackets(self):
        for a, b in ((F(1), F(6, 5)), (F(3, 2), F(2)),
                     (F(2), F(1)), (F(1), F(1))):
            self.assertFalse(check_cubic_bracket(a, b))

    def test_nonzero_is_not_unit(self):
        self.assertNotEqual(2 % 6, 0)
        self.assertFalse(any(2 * k % 6 == 1 for k in range(6)))
        self.assertEqual((2 * 0) % 6, (2 * 3) % 6)

    def test_natural_transport_guards(self):
        self.assertNotEqual(F(max(2 - 3, 0)), F(2) - F(3))
        self.assertNotEqual(F(3 // 2), F(3, 2))
        self.assertEqual(F(4 // 2), F(4, 2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="write machine-readable execution results")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CertificateTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    a, b = bisect_cubic(48)
    report = {
        "status": "passed" if result.wasSuccessful() else "failed",
        "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "evidence_scope": "Executed Python exact-arithmetic contract tests, not Lean/kernel verification.",
        "python": sys.version,
        "positive_jet_precisions": {"min": 1, "max": 24},
        "binomial_instances": 26 * 27,
        "jet_mod_q6": [str(coefficient(synthesize_dyadic_jet(6), k)) for k in range(6)],
        "cubic_bracket_48": {"left": str(a), "right": str(b), "width": str(b - a)},
        "radical_candidate_enclosure": list(map(str, biquad_enclosure(RADICAL_CANDIDATE))),
        "universal_mathematical_proofs": "See article; finite tests alone are not universal proofs."
    }
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
