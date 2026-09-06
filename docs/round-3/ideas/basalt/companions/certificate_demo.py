#!/usr/bin/env python3
"""Exact, finite demonstrations accompanying BASALT.

This is NOT a Lean kernel, a verified implementation, or a BASALT compiler.
The polynomial checker implements the finite algorithm analyzed in the article.
The length interpreter illustrates a restricted observational abstraction.
Run with Python 3.10+; no third-party packages are needed.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest
from typing import Iterable, Sequence

Monomial = tuple[int, ...]
Term = tuple[Monomial, int]

@dataclass(frozen=True)
class Poly:
    dimension: int
    terms: tuple[Term, ...]

    def __post_init__(self) -> None:
        if type(self.dimension) is not int or self.dimension < 0:
            raise ValueError("dimension must be a nonnegative integer")
        previous = None
        for exponents, coefficient in self.terms:
            if not isinstance(exponents, tuple) or len(exponents) != self.dimension:
                raise ValueError("monomial dimension mismatch")
            if any(type(e) is not int or e < 0 for e in exponents):
                raise ValueError("exponents must be nonnegative integers")
            if type(coefficient) is not int or coefficient == 0:
                raise ValueError("canonical coefficients must be nonzero integers")
            if previous is not None and not previous < exponents:
                raise ValueError("monomials must be strictly sorted and unique")
            previous = exponents

    @classmethod
    def normalize(cls, d: int, terms: Iterable[Term]) -> Poly:
        if type(d) is not int or d < 0:
            raise ValueError("invalid dimension")
        accumulator: dict[Monomial, int] = {}
        for exponents, coefficient in terms:
            if not isinstance(exponents, tuple) or len(exponents) != d:
                raise ValueError("monomial dimension mismatch")
            if any(type(e) is not int or e < 0 for e in exponents):
                raise ValueError("invalid exponent")
            if type(coefficient) is not int:
                raise ValueError("coefficient must be an integer")
            accumulator[exponents] = accumulator.get(exponents, 0) + coefficient
        return cls(d, tuple(sorted((m, c) for m, c in accumulator.items() if c)))

    @classmethod
    def constant(cls, d: int, n: int) -> Poly:
        return cls.normalize(d, [((0,) * d, n)])

    @classmethod
    def variable(cls, d: int, i: int) -> Poly:
        if type(i) is not int or not 0 <= i < d:
            raise ValueError("variable out of range")
        return cls.normalize(d, [(tuple(int(j == i) for j in range(d)), 1)])

    def _compatible(self, other: Poly) -> None:
        if self.dimension != other.dimension:
            raise ValueError("coefficient-domain arity mismatch")

    def __add__(self, other: Poly) -> Poly:
        self._compatible(other)
        return Poly.normalize(self.dimension, self.terms + other.terms)

    def __neg__(self) -> Poly:
        return Poly(self.dimension, tuple((m, -c) for m, c in self.terms))

    def __sub__(self, other: Poly) -> Poly:
        return self + (-other)

    def __mul__(self, other: Poly) -> Poly:
        self._compatible(other)
        return Poly.normalize(self.dimension, (
            (tuple(a + b for a, b in zip(m, n)), c * e)
            for m, c in self.terms for n, e in other.terms
        ))

    def __pow__(self, n: int) -> Poly:
        if type(n) is not int or n < 0:
            raise ValueError("power must be a natural number")
        result = Poly.constant(self.dimension, 1)
        base = self
        while n:
            if n & 1:
                result = result * base
            base = base * base
            n //= 2
        return result

    def evaluate(self, values: Sequence[Fraction | int]) -> Fraction:
        if len(values) != self.dimension:
            raise ValueError("valuation dimension mismatch")
        total = Fraction(0)
        for monomial, coefficient in self.terms:
            term = Fraction(coefficient)
            for x, exponent in zip(values, monomial):
                term *= Fraction(x) ** exponent
            total += term
        return total


def check_combination(target: Poly, generators: Sequence[Poly],
                      multipliers: Sequence[Poly]) -> bool:
    """Check a polynomial combination, with exact arity (never zip-truncate)."""
    if len(generators) != len(multipliers):
        raise ValueError("certificate/generator list length mismatch")
    result = Poly.constant(target.dimension, 0)
    for generator, multiplier in zip(generators, multipliers):
        target._compatible(generator)
        target._compatible(multiplier)
        result = result + multiplier * generator
    return target == result


@dataclass(frozen=True)
class ListExpr:
    op: str
    args: tuple[ListExpr, ...] = ()
    index: int = 0

    def __post_init__(self) -> None:
        arities = {"input": 0, "nil": 0, "reverse": 1, "append": 2}
        if self.op not in arities or len(self.args) != arities[self.op]:
            raise ValueError("unsupported node or wrong arity")
        if type(self.index) is not int or self.index < 0:
            raise ValueError("invalid input index")

    def run(self, inputs: Sequence[Sequence[int]]) -> list[int]:
        if self.op == "input":
            return list(inputs[self.index])
        if self.op == "nil":
            return []
        if self.op == "reverse":
            return list(reversed(self.args[0].run(inputs)))
        return self.args[0].run(inputs) + self.args[1].run(inputs)

    def length_expression(self, input_count: int) -> tuple[int, ...]:
        """Coefficient vector for output length, in a very small exact grammar."""
        if self.op == "input":
            if self.index >= input_count:
                raise ValueError("input outside bound context")
            return tuple(int(i == self.index) for i in range(input_count))
        if self.op == "nil":
            return (0,) * input_count
        if self.op == "reverse":
            return self.args[0].length_expression(input_count)
        a = self.args[0].length_expression(input_count)
        b = self.args[1].length_expression(input_count)
        return tuple(x + y for x, y in zip(a, b))


class Demonstrations(unittest.TestCase):
    def setUp(self) -> None:
        self.x = Poly.variable(2, 0)
        self.y = Poly.variable(2, 1)
        self.one = Poly.constant(2, 1)

    def test_multivariate_certificate(self) -> None:
        self.assertTrue(check_combination(self.x**2 - self.y**2,
                                         [self.x-self.y], [self.x+self.y]))

    def test_corrupt_multiplier_rejected(self) -> None:
        self.assertFalse(check_combination(self.x**2-self.y**2,
                                          [self.x-self.y], [self.x+self.y+self.one]))

    def test_two_generator_certificate(self) -> None:
        p = self.x*self.y + self.x + self.y + self.one
        self.assertTrue(check_combination(p, [self.x, self.one],
                                         [self.y+self.one, self.y+self.one]))

    def test_arity_mismatch_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_combination(self.x, [self.x, self.y], [self.one])

    def test_dimension_mismatch_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_combination(self.x, [Poly.variable(1, 0)], [self.one])

    def test_fraction_coefficient_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Poly.normalize(1, [((1,), Fraction(1, 2))])

    def test_negative_exponent_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Poly.normalize(1, [((-1,), 1)])

    def test_duplicate_normalization(self) -> None:
        self.assertEqual(Poly.normalize(1, [((1,), 2), ((1,), -1)]),
                         Poly.variable(1, 0))

    def test_noncanonical_input_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Poly(1, (((1,), 1), ((1,), 2)))

    def test_ring_evaluation_instances(self) -> None:
        for a in range(-3, 4):
            for b in range(-3, 4):
                self.assertEqual((self.x**2-self.y**2).evaluate([a,b]),
                                 ((self.x-self.y)*(self.x+self.y)).evaluate([a,b]))

    def test_zero_divisor_power_negative(self) -> None:
        self.assertEqual(2**2 % 4, 0)
        self.assertNotEqual(2 % 4, 0)

    def test_cancellation_pole_negative(self) -> None:
        # Lean-style total division by zero is modeled explicitly here.
        def div(a: Fraction, b: Fraction) -> Fraction:
            return a/b if b else Fraction(0)
        for x in (Fraction(-1), Fraction(0), Fraction(2), Fraction(3,2)):
            self.assertEqual(div(x*x-1, x-1), x+1)
        self.assertNotEqual(div(Fraction(0), Fraction(0)), Fraction(2))

    def test_atomless_reflection_finite_negative(self) -> None:
        # Dirac at zero: F(x)=1 exactly when x>=0; symmetry at zero fails.
        F = lambda x: int(x >= 0)
        self.assertNotEqual(F(0), 1-F(0))

    def test_flatness_negative(self) -> None:
        # Multiplication by 2 on Z/2: two distinct inputs have same output.
        self.assertEqual((2*0) % 2, (2*1) % 2)
        self.assertNotEqual(0, 1)

    def test_nonpreserving_quotient_map_negative(self) -> None:
        # Representatives 0 and 2 agree modulo 2 but not modulo 3.
        self.assertEqual(0 % 2, 2 % 2)
        self.assertNotEqual(0 % 3, 2 % 3)

    def test_complete_set_needs_soundness(self) -> None:
        candidate = {0, 1}
        self.assertIn(0, candidate) # witness and coverage for P(x): x=0
        self.assertFalse(all(x == 0 for x in candidate))

    def test_length_transfer_instances(self) -> None:
        expr = ListExpr("append", (ListExpr("reverse", (ListExpr("input", index=0),)),
                                    ListExpr("input", index=1)))
        self.assertEqual(expr.length_expression(2), (1,1))
        for n in range(7):
            for m in range(7):
                self.assertEqual(len(expr.run([list(range(n)), list(range(m))])), n+m)

    def test_length_not_identity(self) -> None:
        expr = ListExpr("reverse", (ListExpr("input", index=0),))
        self.assertEqual(expr.length_expression(1), (1,))
        self.assertNotEqual(expr.run([[1,2]]), [1,2])

    def test_length_not_sorting(self) -> None:
        expr = ListExpr("input", index=0)
        output = expr.run([[2,1]])
        self.assertEqual(expr.length_expression(1), (1,))
        self.assertNotEqual(output, sorted(output))

    def test_unsupported_length_node_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ListExpr("arbitraryLeanFunction")

    def test_context_input_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ListExpr("input", index=1).length_expression(1)

    def test_finite_jet_is_not_exact(self) -> None:
        t = Poly.variable(1, 0)
        c = sum((Poly.constant(1, a) * t**i for i,a in enumerate([1,1,2,5,14,42])),
                Poly.constant(1, 0))
        r = c - Poly.constant(1, 1) - t*c*c
        coeff = dict(r.terms)
        self.assertTrue(all(coeff.get((i,), 0) == 0 for i in range(6)))
        self.assertEqual(coeff[(6,)], -132)

    def test_collapsed_enclosure_positive(self) -> None:
        lower = value = upper = Fraction(3,7)
        self.assertTrue(lower <= value <= upper)
        self.assertEqual(lower, upper)
        self.assertEqual(value, lower)

    def test_boolean_not_integer_input(self) -> None:
        with self.assertRaises(ValueError):
            Poly.normalize(1, [((1,), True)])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Demonstrations)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {
        "status": "passed" if result.wasSuccessful() else "failed",
        "python": sys.version,
        "test_methods_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "scope": "Finite Python demonstrations only; no Lean compilation or kernel checking.",
    }
    (Path(__file__).parent / "test_results.json").write_text(json.dumps(receipt, indent=2)+"\n")
    sys.exit(0 if result.wasSuccessful() else 1)
