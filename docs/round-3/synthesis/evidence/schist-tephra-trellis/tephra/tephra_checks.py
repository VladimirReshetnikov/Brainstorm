#!/usr/bin/env python3
"""Executable boundary models accompanying Tephra (Python 3.10+).

These tests are NOT a Lean implementation and do NOT establish Lean theorems.
They exercise exact finite arithmetic, a tiny list-expression semantics, and
request/scope bookkeeping. The article proves generic mathematical statements
separately. No external package, solver, or network access is required.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path
import platform
import random
import sys
import unittest
from typing import Iterable

Monomial = tuple[int, ...]


def natural(value: int, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")
    return value


@dataclass(frozen=True)
class Poly:
    """Canonical finite Z-polynomial; variable indices are part of its type model."""
    variables: int
    terms: tuple[tuple[Monomial, int], ...]

    def __post_init__(self) -> None:
        natural(self.variables, "variable count")
        previous: Monomial | None = None
        for powers, coefficient in self.terms:
            if len(powers) != self.variables:
                raise ValueError("monomial arity mismatch")
            for e in powers:
                natural(e, "exponent")
            if type(coefficient) is not int or coefficient == 0:
                raise ValueError("canonical coefficients must be nonzero integers")
            if previous is not None and powers <= previous:
                raise ValueError("monomials must be unique and strictly sorted")
            previous = powers

    @staticmethod
    def make(variables: int, terms: Iterable[tuple[Monomial, int]]) -> Poly:
        natural(variables, "variable count")
        collected: dict[Monomial, int] = {}
        for powers, coefficient in terms:
            if type(coefficient) is not int:
                raise ValueError("integer coefficient domain required")
            if len(powers) != variables:
                raise ValueError("monomial arity mismatch")
            for e in powers:
                natural(e, "exponent")
            collected[powers] = collected.get(powers, 0) + coefficient
        return Poly(variables, tuple(sorted((m, c) for m, c in collected.items() if c)))

    @staticmethod
    def const(variables: int, value: int) -> Poly:
        return Poly.make(variables, [((0,) * variables, value)])

    @staticmethod
    def var(variables: int, index: int) -> Poly:
        natural(index, "variable index")
        if index >= variables:
            raise ValueError("variable index outside declared valuation")
        powers = tuple(int(i == index) for i in range(variables))
        return Poly.make(variables, [(powers, 1)])

    def _same(self, other: Poly) -> None:
        if self.variables != other.variables:
            raise ValueError("coefficient-expression contexts differ")

    def __add__(self, other: Poly) -> Poly:
        self._same(other)
        return Poly.make(self.variables, self.terms + other.terms)

    def __neg__(self) -> Poly:
        return Poly.make(self.variables, ((m, -c) for m, c in self.terms))

    def __sub__(self, other: Poly) -> Poly:
        return self + (-other)

    def __mul__(self, other: Poly) -> Poly:
        self._same(other)
        return Poly.make(self.variables,
            ((tuple(a + b for a, b in zip(m, n)), c * d)
             for m, c in self.terms for n, d in other.terms))

    def __pow__(self, exponent: int) -> Poly:
        natural(exponent, "power")
        result = Poly.const(self.variables, 1)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def evaluate(self, values: tuple[int, ...], modulus: int | None = None) -> int:
        if len(values) != self.variables or any(type(x) is not int for x in values):
            raise ValueError("exact integer valuation with matching arity required")
        if modulus is not None and (type(modulus) is not int or modulus <= 0):
            raise ValueError("positive modulus required")
        total = 0
        for powers, coefficient in self.terms:
            term = coefficient
            for x, e in zip(values, powers):
                term *= x ** e
            total += term
        return total if modulus is None else total % modulus

    def trunc(self, precision: int) -> Poly:
        natural(precision, "precision")
        if self.variables != 1:
            raise ValueError("this jet interface is univariate")
        return Poly.make(1, ((m, c) for m, c in self.terms if m[0] < precision))

    def derivative(self) -> Poly:
        if self.variables != 1:
            raise ValueError("this derivative interface is univariate")
        return Poly.make(1, (((m[0] - 1,), m[0] * c)
                            for m, c in self.terms if m[0]))


def certificate_ok(target: Poly, premises: tuple[Poly, ...],
                   multipliers: tuple[Poly, ...]) -> bool:
    """Check p = sum(q_i*f_i), NOT its connection to a source Lean goal."""
    if len(premises) != len(multipliers):
        return False  # Never silently zip away unmatched premises or witnesses.
    if any(p.variables != target.variables for p in premises + multipliers):
        return False
    total = Poly.const(target.variables, 0)
    for q, f in zip(multipliers, premises):
        total = total + q * f
    return total == target


@dataclass(frozen=True)
class Request:
    origin: str
    object_id: str
    scope: tuple[str, ...]


@dataclass(frozen=True)
class JetReceipt:
    """Bookkeeping only: no claim that Python objects constitute proof evidence."""
    request: Request
    precision: int
    polynomial: Poly

    def serves(self, request: Request, precision: int) -> bool:
        natural(precision, "requested precision")
        old = self.request
        return (old.origin == request.origin and old.object_id == request.object_id
                and request.scope[:len(old.scope)] == old.scope
                and 0 <= precision <= self.precision)


def acyclic(dependencies: dict[str, tuple[str, ...]]) -> bool:
    """Reject unknown prerequisite IDs as well as cycles."""
    completed: set[str] = set()
    active: set[str] = set()
    def visit(node: str) -> bool:
        if node not in dependencies or node in active:
            return False
        if node in completed:
            return True
        active.add(node)
        if not all(visit(d) for d in dependencies[node]):
            return False
        active.remove(node)
        completed.add(node)
        return True
    return all(visit(node) for node in dependencies)


# A deliberately small, closed syntax. There is no unproved provider-law import.
@dataclass(frozen=True)
class ListExpr:
    tag: str
    index: int = 0
    left: ListExpr | None = None
    right: ListExpr | None = None

    def evaluate(self, inputs: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
        if self.tag == "input":
            if not 0 <= self.index < len(inputs):
                raise ValueError("missing input")
            return inputs[self.index]
        if self.tag == "nil":
            return ()
        if self.tag == "reverse" and self.left is not None:
            return self.left.evaluate(inputs)[::-1]
        if self.tag == "append" and self.left is not None and self.right is not None:
            return self.left.evaluate(inputs) + self.right.evaluate(inputs)
        raise ValueError("unsupported or malformed list expression")

    def length_form(self, arity: int) -> tuple[int, ...]:
        natural(arity, "input arity")
        if self.tag == "input" and 0 <= self.index < arity:
            return tuple(int(i == self.index) for i in range(arity))
        if self.tag == "nil":
            return (0,) * arity
        if self.tag == "reverse" and self.left is not None:
            return self.left.length_form(arity)
        if self.tag == "append" and self.left is not None and self.right is not None:
            return tuple(a + b for a, b in zip(self.left.length_form(arity),
                                             self.right.length_form(arity)))
        raise ValueError("no length theorem for this syntax node")


class BoundaryTests(unittest.TestCase):
    def test_polynomial_certificate_positive(self) -> None:
        x, y = Poly.var(2, 0), Poly.var(2, 1)
        self.assertTrue(certificate_ok(x*x-y*y, (x-y,), (x+y,)))

    def test_corrupted_multiplier_rejected(self) -> None:
        x, y = Poly.var(2, 0), Poly.var(2, 1)
        self.assertFalse(certificate_ok(x*x-y*y, (x-y,),
                                       (x+y+Poly.const(2, 1),)))

    def test_arity_mismatch_rejected(self) -> None:
        z = Poly.const(1, 0)
        self.assertFalse(certificate_ok(z, (z,), ()))
        self.assertFalse(certificate_ok(z, (), (z,)))

    def test_variable_context_mismatch_rejected(self) -> None:
        self.assertFalse(certificate_ok(Poly.const(1, 0),
                                       (Poly.const(2, 0),), (Poly.const(2, 0),)))

    def test_rational_witness_not_integer_witness(self) -> None:
        with self.assertRaises(ValueError):
            Poly.make(1, [((0,), Fraction(1, 2))])

    def test_canonical_representation(self) -> None:
        self.assertEqual(Poly.make(1, [((1,), 1), ((1,), -1)]), Poly.const(1, 0))
        for terms in [(((1,), 0),), (((1,), 1), ((1,), 1)), (((-1,), 1),)]:
            with self.assertRaises(ValueError):
                Poly(1, terms)

    def test_multivariate_denotation_samples(self) -> None:
        rng = random.Random(20260906)
        x, y, z = (Poly.var(3, i) for i in range(3))
        one = Poly.const(3, 1)
        f, g = x-y, x*z-one
        q, r = x+y, z*z+one
        p = q*f+r*g
        self.assertTrue(certificate_ok(p, (f, g), (q, r)))
        # 100 valuations, in Z and Z/4Z: finite cross-checks, not a proof.
        for _ in range(100):
            a = tuple(rng.randrange(-7, 8) for _ in range(3))
            for modulus in (None, 4):
                lhs = p.evaluate(a, modulus)
                rhs = q.evaluate(a)*f.evaluate(a)+r.evaluate(a)*g.evaluate(a)
                self.assertEqual(lhs, rhs if modulus is None else rhs % modulus)

    def test_catalan_residual_finite_not_exact(self) -> None:
        x, one = Poly.var(1, 0), Poly.const(1, 1)
        j = Poly.make(1, [((i,), c) for i, c in enumerate([1, 1, 2, 5, 14, 42])])
        residual = j-one-x*j*j
        self.assertEqual(residual.trunc(6), Poly.const(1, 0))
        self.assertNotEqual(residual, Poly.const(1, 0))
        self.assertEqual(dict(residual.terms)[(6,)], -132)

    def test_differentiation_precision(self) -> None:
        x, zero = Poly.var(1, 0), Poly.const(1, 0)
        p = x**5
        self.assertEqual(p.trunc(5), zero)
        self.assertEqual(p.derivative().trunc(4), zero)
        self.assertNotEqual(p.derivative().trunc(5), zero)

    def test_nonunit_residual_counterexample(self) -> None:
        # F(Y)=2Y, J=2t in (Z/4Z)[[t]]: residual zero, jet not zero.
        derivative, j1 = 2, 2
        self.assertNotEqual(derivative % 4, 0)
        self.assertEqual((derivative*j1) % 4, 0)
        self.assertNotEqual(j1 % 4, 0)
        self.assertFalse(any(derivative*x % 4 == 1 for x in range(4)))

    def test_observation_weakening(self) -> None:
        origin = Request("r1", "Delta", ("root",))
        rec = JetReceipt(origin, 6, Poly.const(1, 0))
        self.assertTrue(rec.serves(origin, 4))
        self.assertTrue(rec.serves(Request("r1", "Delta", ("root", "child")), 6))
        self.assertFalse(rec.serves(origin, 7))

    def test_stale_and_different_objects(self) -> None:
        rec = JetReceipt(Request("r1", "Delta", ("root",)), 6, Poly.const(1, 0))
        self.assertFalse(rec.serves(Request("r2", "Delta", ("root",)), 6))
        self.assertFalse(rec.serves(Request("r1", "Other", ("root",)), 6))

    def test_sibling_scope_rejected(self) -> None:
        rec = JetReceipt(Request("r1", "x", ("root", "left")), 2, Poly.const(1, 0))
        self.assertFalse(rec.serves(Request("r1", "x", ("root", "right")), 2))
        self.assertFalse(rec.serves(Request("r1", "x", ("root",)), 2))

    def test_dependency_dag(self) -> None:
        self.assertTrue(acyclic({"a": (), "b": ("a",), "c": ("a", "b")}))
        self.assertFalse(acyclic({"guard": ("result",), "result": ("guard",)}))
        self.assertFalse(acyclic({"result": ("unknown",)}))

    def test_length_semantics(self) -> None:
        a, b = ListExpr("input", 0), ListExpr("input", 1)
        expr = ListExpr("reverse", left=ListExpr("append", left=a, right=b))
        self.assertEqual(expr.length_form(2), (1, 1))
        for n in range(8):
            for m in range(8):
                inputs = (tuple(range(n)), tuple(range(m)))
                self.assertEqual(len(expr.evaluate(inputs)), n+m)

    def test_length_does_not_determine_order(self) -> None:
        a = ListExpr("input", 0)
        reverse = ListExpr("reverse", left=a)
        self.assertEqual(a.length_form(1), reverse.length_form(1))
        self.assertNotEqual(a.evaluate(((1, 2),)), reverse.evaluate(((1, 2),)))

    def test_length_counterexample_realized(self) -> None:
        a = ListExpr("input", 0)
        duplicate = ListExpr("append", left=a, right=a)
        self.assertEqual(duplicate.length_form(1), (2,))
        self.assertNotEqual(len(duplicate.evaluate(((7,),))), 1)

    def test_abstract_length_requires_realizable_input(self) -> None:
        # The mathematical article proves List Empty has only the empty list.
        # This finite model contrasts that input image with an abstract n=1.
        all_empty_element_lists: tuple[tuple[int, ...], ...] = ((),)
        constant_nil = ListExpr("nil")
        self.assertTrue(all(len(constant_nil.evaluate((xs,))) == len(xs)
                            for xs in all_empty_element_lists))
        abstract_counterexample_length = 1
        self.assertNotEqual(0, abstract_counterexample_length)
        self.assertFalse(any(len(xs) == abstract_counterexample_length
                             for xs in all_empty_element_lists))

    def test_unknown_provider_not_assumed(self) -> None:
        with self.assertRaises(ValueError):
            ListExpr("mysterious_provider").length_form(1)

    def test_total_vs_partial_division(self) -> None:
        def total_div(a: Fraction, b: Fraction) -> Fraction:
            return a/b if b else Fraction(0)
        x = Fraction(1)
        self.assertEqual(total_div(x*x-1, x-1), 0)
        self.assertNotEqual(total_div(x*x-1, x-1), x+1)
        for x in (Fraction(-2), Fraction(0), Fraction(3)):
            self.assertEqual(total_div(x*x-1, x-1), x+1)

    def test_complete_solution_needs_both_directions(self) -> None:
        universe = (-1, 0, 1)
        predicate = lambda x: x == 0
        bad_set = {0, 1}
        self.assertTrue(all((not predicate(x)) or x in bad_set for x in universe))
        self.assertFalse(all(predicate(x) for x in bad_set))
        good_set = {0}
        self.assertTrue(all(predicate(x) == (x in good_set) for x in universe))

    def test_prefix_shift_counterexample(self) -> None:
        # Exact coordinate calculations for the infinite zero/impulse streams.
        zero = lambda k: 0
        impulse = lambda k: int(k == 0)
        left = lambda s: lambda k: s(k+1)
        right = lambda s: lambda k: 0 if k == 0 else s(k-1)
        for k in range(10):
            self.assertEqual(left(right(impulse))(k), impulse(k))
        self.assertNotEqual(right(left(impulse))(0), impulse(0))
        later_impulse = lambda k: int(k == 1)
        self.assertEqual(zero(0), later_impulse(0))
        self.assertNotEqual(left(zero)(0), left(later_impulse)(0))

    def test_triangular_finite_inverse(self) -> None:
        # I-S and I+S+...+S^(N-1), with S the strict subdiagonal shift.
        for n in range(1, 9):
            a = [[int(i == j)-int(i == j+1) for j in range(n)] for i in range(n)]
            b = [[int(j <= i) for j in range(n)] for i in range(n)]
            for x, y in ((a, b), (b, a)):
                product = [[sum(x[i][k]*y[k][j] for k in range(n))
                            for j in range(n)] for i in range(n)]
                self.assertEqual(product, [[int(i == j) for j in range(n)] for i in range(n)])


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BoundaryTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {
        "status": "passed" if result.wasSuccessful() else "failed",
        "python": platform.python_version(),
        "test_methods": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "evidence_kind": "finite executable checks, not Lean kernel proofs",
        "additional_iteration_counts": {
            "multivariate_valuations": 100,
            "coefficient_domains_per_valuation": 2,
            "length_input_pairs": 64,
            "matrix_sizes": 8
        }
    }
    Path(__file__).with_name("check_results.json").write_text(
        json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
