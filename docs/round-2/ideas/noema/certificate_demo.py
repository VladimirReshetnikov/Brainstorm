#!/usr/bin/env python3
"""Executable reference experiment for Noema's proposed CAS boundary.

This is NOT a formally verified program, a Lean kernel, or a Noema implementation.
It checks univariate rational-polynomial data using Python's exact Fraction
arithmetic. A successful rational certificate establishes only the conditional
identity whose denominator guards are returned. No supplied 'proved' flag is
accepted and no numerical sampling is used to validate a polynomial identity.

Run: python3 certificate_demo.py --output experiment-results.json
Only the Python standard library is required (Python 3.10 or newer).
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass, replace
from fractions import Fraction as Q
import hashlib
import json
from math import comb
from pathlib import Path
import platform
import unittest

Poly = tuple[Q, ...]                 # coefficients in increasing degree order


def poly(*a: int | Q) -> Poly:
    r = tuple(Q(x) for x in a)
    while r and r[-1] == 0:
        r = r[:-1]
    return r


ZERO, ONE, X = poly(), poly(1), poly(0, 1)


def add(a: Poly, b: Poly) -> Poly:
    return poly(*( (a[i] if i < len(a) else Q(0)) +
                   (b[i] if i < len(b) else Q(0))
                   for i in range(max(len(a), len(b))) ))


def scale(a: Poly, q: int | Q) -> Poly:
    return poly(*(Q(q)*v for v in a))


def sub(a: Poly, b: Poly) -> Poly:
    return add(a, scale(b, -1))


def mul(a: Poly, b: Poly) -> Poly:
    if not a or not b:
        return ZERO
    r = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i+j] += x*y
    return poly(*r)


def deriv(a: Poly) -> Poly:
    return poly(*(i*a[i] for i in range(1, len(a))))


def at(a: Poly, x: int | Q) -> Q:
    ans = Q(0)
    for c in reversed(a):
        ans = ans*Q(x) + c
    return ans


def monic(a: Poly) -> Poly:
    if not a:
        raise ValueError("identically zero denominator: unsupported by this contract")
    return scale(a, 1/a[-1])


def encode(a: Poly) -> list[str]:
    return [str(c) for c in a]


@dataclass(frozen=True)
class Request:
    """Caller-owned target; the producer is not allowed to replace this object."""
    p: Poly
    q: Poly
    r: Poly
    s: Poly
    scope_id: str = "root"
    revision: int = 0

    def identity(self) -> str:
        obj = [encode(v) for v in (self.p, self.q, self.r, self.s)]
        payload = ["conditional-equality-over-Q", obj, self.scope_id, self.revision]
        return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()

    def guards(self) -> tuple[Poly, ...]:
        """q != 0 and s != 0; nonzero constant guards are discharged exactly."""
        result: list[Poly] = []
        for den in (self.q, self.s):
            m = monic(den)
            if len(m) > 1 and m not in result:
                result.append(m)
        return tuple(result)


@dataclass(frozen=True)
class Certificate:
    origin: str
    guards: tuple[Poly, ...]
    residual: Poly


@dataclass(frozen=True)
class CheckedConditional:
    origin: str
    guards: tuple[Poly, ...]

    def unconditional(self) -> bool:
        # A local proof of a nontrivial guard is deliberately outside this model.
        return not self.guards


def propose(req: Request) -> Certificate:
    """Untrusted producer. The checker recomputes everything that matters."""
    return Certificate(req.identity(), req.guards(), sub(mul(req.p, req.s), mul(req.r, req.q)))


def check(req: Request, cert: Certificate) -> CheckedConditional:
    if cert.origin != req.identity():
        raise ValueError("stale or mismatched request origin")
    expected = req.guards()
    if cert.guards != expected:
        raise ValueError("denominator guards changed or omitted")
    residual = sub(mul(req.p, req.s), mul(req.r, req.q))
    if cert.residual != residual or residual != ZERO:
        raise ValueError("polynomial identity certificate rejected")
    return CheckedConditional(req.identity(), expected)


def total_div(a: Q, b: Q) -> Q:
    """Field-style total division, used only to display negative neighbors."""
    return Q(0) if b == 0 else a/b


def equality_at(req: Request, x: int | Q) -> bool:
    return total_div(at(req.p, x), at(req.q, x)) == total_div(at(req.r, x), at(req.s, x))


def jet_equal(a: Poly, b: Poly, order: int) -> bool:
    """Agreement in degrees strictly less than order, NOT polynomial equality."""
    if not isinstance(order, int) or order < 0:
        raise ValueError("jet order must be a nonnegative integer")
    return poly(*a[:order]) == poly(*b[:order])


def derivative_order(order: int) -> int:
    if order < 1:
        raise ValueError("a positive input order is required")
    return order-1


CANCELLATION = Request(poly(-1, 0, 1), poly(-1, 1), poly(1, 1), ONE)
CUBIC = poly(-1, -1, 0, 1)
LOWER, UPPER = Q(331, 250), Q(53, 40)  # 1.324 and 1.325


class BoundaryTests(unittest.TestCase):
    def test_01_polynomial_normalization(self):
        self.assertEqual(poly(1, 0, 0), ONE)

    def test_02_factorization_identity(self):
        self.assertEqual(mul(poly(-1, 1), poly(1, 1)), poly(-1, 0, 1))

    def test_03_conditional_acceptance(self):
        self.assertEqual(check(CANCELLATION, propose(CANCELLATION)).guards, (poly(-1, 1),))

    def test_04_not_unconditional(self):
        self.assertFalse(check(CANCELLATION, propose(CANCELLATION)).unconditional())

    def test_05_zero_guard_mutation(self):
        cert = replace(propose(CANCELLATION), guards=())
        with self.assertRaisesRegex(ValueError, "guards"):
            check(CANCELLATION, cert)

    def test_06_guard_substitution_mutation(self):
        cert = replace(propose(CANCELLATION), guards=(X,))
        with self.assertRaisesRegex(ValueError, "guards"):
            check(CANCELLATION, cert)

    def test_07_false_global_neighbor(self):
        self.assertFalse(equality_at(CANCELLATION, 1))

    def test_08_valid_point(self):
        self.assertTrue(equality_at(CANCELLATION, 2))

    def test_09_stale_revision(self):
        with self.assertRaisesRegex(ValueError, "origin"):
            check(replace(CANCELLATION, revision=1), propose(CANCELLATION))

    def test_10_sibling_scope(self):
        with self.assertRaisesRegex(ValueError, "origin"):
            check(replace(CANCELLATION, scope_id="other-case"), propose(CANCELLATION))

    def test_11_target_substitution(self):
        with self.assertRaisesRegex(ValueError, "origin"):
            check(replace(CANCELLATION, r=poly(2, 1)), propose(CANCELLATION))

    def test_12_forged_residual(self):
        bad = replace(CANCELLATION, r=poly(2, 1))
        with self.assertRaisesRegex(ValueError, "identity"):
            check(bad, replace(propose(bad), residual=ZERO))

    def test_13_wrong_honest_result(self):
        bad = replace(CANCELLATION, r=poly(2, 1))
        with self.assertRaisesRegex(ValueError, "identity"):
            check(bad, propose(bad))

    def test_14_zero_denominator_unsupported(self):
        with self.assertRaisesRegex(ValueError, "zero denominator"):
            propose(replace(CANCELLATION, q=ZERO))

    def test_15_unconditional_polynomial_identity(self):
        req = Request(mul(poly(-1, 1), poly(1, 1)), ONE, poly(-1, 0, 1), ONE)
        self.assertTrue(check(req, propose(req)).unconditional())

    def test_16_constant_denominator(self):
        req = Request(poly(2, 2), poly(2), poly(1, 1), ONE)
        self.assertTrue(check(req, propose(req)).unconditional())

    def test_17_equivalent_guard_deduplication(self):
        req = Request(poly(2), scale(X, 2), ONE, X)
        self.assertEqual(check(req, propose(req)).guards, (X,))

    def test_18_cubic_endpoint_signs(self):
        self.assertLess(at(CUBIC, LOWER), 0)
        self.assertGreater(at(CUBIC, UPPER), 0)

    def test_19_derivative_lower_bound_identity(self):
        # p'(x) = 2 + 3(x-1)(x+1); the real interval theorem is in the article.
        self.assertEqual(deriv(CUBIC), add(poly(2), scale(mul(poly(-1, 1), poly(1, 1)), 3)))

    def test_20_root_interval_endpoints(self):
        self.assertTrue(Q(1) < LOWER < UPPER < Q(2))
        self.assertEqual(UPPER-LOWER, Q(1, 1000))

    def test_21_jet_is_not_equality(self):
        a, b = poly(0, 1), poly(0, 1, 0, 1)
        self.assertTrue(jet_equal(a, b, 3))
        self.assertNotEqual(a, b)

    def test_22_derivative_loses_precision(self):
        a, b = poly(0, 1), poly(0, 1, 0, 1)
        self.assertTrue(jet_equal(deriv(a), deriv(b), derivative_order(3)))
        self.assertFalse(jet_equal(deriv(a), deriv(b), 3))

    def test_23_bad_precision(self):
        with self.assertRaises(ValueError):
            jet_equal(ONE, X, -1)
        with self.assertRaises(ValueError):
            derivative_order(0)

    def test_24_binomial_orthogonality_samples(self):
        for n in range(13):
            for j in range(14):
                value = sum((-1)**(n-k)*comb(n,k)*comb(k,j) for k in range(j,n+1))
                self.assertEqual(value, int(n == j))

    def test_25_natural_transport_negative_neighbors(self):
        self.assertNotEqual(Q(max(2-3, 0)), Q(2)-Q(3))
        self.assertNotEqual(Q(3//2), Q(3)/Q(2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiment-results.json"))
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BoundaryTests))
    output = {
        "status": "passed" if result.wasSuccessful() else "failed",
        "evidence_scope": "Python reference experiment only; not formal verification or a Lean execution",
        "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "binomial_instances_inside_test_24": 13*14,
        "root_interval": [str(LOWER), str(UPPER)],
        "endpoint_polynomial_values": [str(at(CUBIC, LOWER)), str(at(CUBIC, UPPER))],
        "cancellation_guard": "x - 1 != 0",
        "python_version": platform.python_version(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output.write_text(json.dumps(output, indent=2)+"\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
