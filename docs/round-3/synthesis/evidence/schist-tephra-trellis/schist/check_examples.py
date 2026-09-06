#!/usr/bin/env python3
"""Finite exact-arithmetic checks accompanying Schist.

These tests do NOT compile Lean, validate a proof language, or prove the generic
mathematical theorems. They independently exercise selected concrete examples and
negative neighbors. Standard Python only; run with Python 3.10 or newer.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as F
import unittest

@dataclass(frozen=True)
class Affine:
    tag: str
    n: int = 0
    left: Affine | None = None
    right: Affine | None = None

    def __post_init__(self) -> None:
        if self.tag not in {"lit", "var", "add", "scale"}:
            raise ValueError("Unsupported affine constructor")
        if self.n < 0:
            raise ValueError("Natural-number coefficients are required")
        if self.tag in {"add", "scale"} and self.left is None:
            raise ValueError("Missing child")
        if self.tag == "add" and self.right is None:
            raise ValueError("Missing right child")

    def evaluate(self, x: int) -> int:
        if x < 0:
            raise ValueError("Natural-number input required")
        if self.tag == "lit":
            return self.n
        if self.tag == "var":
            return x
        assert self.left is not None
        if self.tag == "scale":
            return self.n * self.left.evaluate(x)
        assert self.right is not None
        return self.left.evaluate(x) + self.right.evaluate(x)

    def normal(self) -> tuple[int, int]:
        if self.tag == "lit":
            return 0, self.n
        if self.tag == "var":
            return 1, 0
        assert self.left is not None
        a, b = self.left.normal()
        if self.tag == "scale":
            return self.n * a, self.n * b
        assert self.right is not None
        c, d = self.right.normal()
        return a + c, b + d


def total_div(a: F, b: F) -> F:
    return a / b if b else F(0)


def deriv(coeff: list[F]) -> list[F]:
    return [k * c for k, c in enumerate(coeff)][1:]


def coeff_equal_below(a: list[F], b: list[F], n: int) -> bool:
    return all((a[k] if k < len(a) else 0) ==
               (b[k] if k < len(b) else 0) for k in range(n))


def finite_affine_law(rho: dict[int, F], q: int,
                      mu: dict[int, F]) -> dict[int, F]:
    out: dict[int, F] = {}
    for d, pd in rho.items():
        for x, px in mu.items():
            z = d + q * x
            out[z] = out.get(z, F(0)) + pd * px
    return {x: p for x, p in out.items() if p}


class MathematicalNeighbors(unittest.TestCase):
    def test_affine_denotation_on_finite_inputs(self) -> None:
        base = [Affine("var")] + [Affine("lit", n=n) for n in range(4)]
        expressions = base + [Affine("add", left=a, right=b)
                              for a in base for b in base]
        expressions += [Affine("scale", n=n, left=a)
                        for a in base for n in range(4)]
        for e in expressions:
            a, b = e.normal()
            for x in range(13):
                self.assertEqual(e.evaluate(x), a * x + b)

    def test_affine_certificate_and_corruption(self) -> None:
        x = Affine("var")
        lhs = Affine("scale", n=3,
                     left=Affine("add", left=x, right=Affine("lit", n=2)))
        rhs = Affine("add", left=Affine("scale", n=3, left=x),
                     right=Affine("lit", n=6))
        wrong = Affine("add", left=Affine("scale", n=3, left=x),
                       right=Affine("lit", n=7))
        self.assertEqual(lhs.normal(), rhs.normal())
        self.assertNotEqual(lhs.normal(), wrong.normal())
        self.assertNotEqual(lhs.evaluate(0), wrong.evaluate(0))

    def test_sorted_length_is_not_permutation(self) -> None:
        xs = [2, 1]
        ys = [0] * len(xs)
        self.assertEqual(len(xs), len(ys))
        self.assertEqual(ys, sorted(ys))
        self.assertNotEqual(Counter(xs), Counter(ys))

    def test_total_and_partial_rational_cancellation(self) -> None:
        for x in map(F, [-2, -1, 0, 1, 2]):
            value = total_div(x*x - 1, x - 1)
            if x != 1:
                self.assertEqual(value, x + 1)
            else:
                self.assertEqual(value, 0)
                self.assertNotEqual(value, x + 1)
        total_roots = [x for x in map(F, [-1, 1])
                       if total_div(x*x - 1, x-1) == 0]
        partial_roots = [x for x in total_roots if x != 1]
        self.assertEqual(total_roots, [F(-1), F(1)])
        self.assertEqual(partial_roots, [F(-1)])

    def test_derivative_consumes_precision(self) -> None:
        a, b = list(map(F, [0, 1])), list(map(F, [0, 1, 0, 1]))
        self.assertTrue(coeff_equal_below(a, b, 3))
        self.assertTrue(coeff_equal_below(deriv(a), deriv(b), 2))
        self.assertFalse(coeff_equal_below(deriv(a), deriv(b), 3))

    def test_nonunit_residual_and_wrong_branch(self) -> None:
        self.assertNotEqual(2 % 4, 0)
        self.assertFalse(any((2 * k) % 4 == 1 for k in range(4)))
        self.assertEqual((2 * 2) % 4, 0)  # F(2t)=0, but 2t != 0 mod t^2
        self.assertNotEqual(2 % 4, 0)
        self.assertEqual((-1)**2 - 1, 0)
        self.assertEqual(1**2 - 1, 0)
        self.assertNotEqual(-1, 1)

    def test_identity_affine_operator_not_unique(self) -> None:
        rho = {0: F(1)}
        mu, nu = {0: F(1)}, {1: F(1)}
        self.assertEqual(finite_affine_law(rho, 1, mu), mu)
        self.assertEqual(finite_affine_law(rho, 1, nu), nu)
        self.assertNotEqual(mu, nu)

    def test_normalization_is_needed_for_generic_profiles(self) -> None:
        f, g = lambda _: 1, lambda _: 2
        for x in [-1, 0, 1]:
            self.assertEqual(f(x), f(0*x))
            self.assertEqual(g(x), g(0*x))
        self.assertNotEqual(f(0), g(0))

    def test_equal_marginals_do_not_imply_independence(self) -> None:
        correlated = {(0, 0): F(1, 2), (1, 1): F(1, 2)}
        marginal_x = {i: sum((p for (x, y), p in correlated.items() if x == i), F(0))
                      for i in [0, 1]}
        marginal_y = {i: sum((p for (x, y), p in correlated.items() if y == i), F(0))
                      for i in [0, 1]}
        self.assertEqual(marginal_x, marginal_y)
        self.assertNotEqual(correlated.get((0, 1), F(0)),
                            marginal_x[0] * marginal_y[1])

    def test_integer_and_rational_division_are_different(self) -> None:
        self.assertNotEqual(F(1 // 4), F(1, 4))
        for n in range(-3, 4):
            self.assertEqual(F((4*n) // 4), F(4*n, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
