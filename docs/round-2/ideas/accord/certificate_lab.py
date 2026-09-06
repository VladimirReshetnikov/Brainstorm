#!/usr/bin/env python3
"""Small exact-arithmetic companion to the Accord design article.

This is an executable illustration, NOT a formally verified checker, Lean
integration, parser, or security boundary. All arithmetic is rational/integer.
Run: python3 certificate_lab.py --report test-results.json
"""
from __future__ import annotations
import argparse
import json
import unittest
from dataclasses import dataclass
from fractions import Fraction as Q
from math import comb
from pathlib import Path
from typing import Callable, Iterable

Monomial = tuple[int, ...]

@dataclass(frozen=True)
class Poly:
    """Canonical sparse rational polynomial in a fixed number of variables."""
    arity: int
    terms: tuple[tuple[Monomial, Q], ...]

    @staticmethod
    def make(arity: int, terms: Iterable[tuple[Monomial, Q | int]]) -> 'Poly':
        if arity < 0:
            raise ValueError('negative variable count')
        result: dict[Monomial, Q] = {}
        for m, c in terms:
            if len(m) != arity or any(type(e) is not int or e < 0 for e in m):
                raise ValueError('invalid monomial')
            result[m] = result.get(m, Q(0)) + Q(c)
        return Poly(arity, tuple(sorted((m, c) for m, c in result.items() if c)))

    @staticmethod
    def constant(arity: int, c: Q | int) -> 'Poly':
        return Poly.make(arity, [((0,) * arity, c)])

    @staticmethod
    def variable(arity: int, i: int) -> 'Poly':
        if not 0 <= i < arity:
            raise ValueError('variable index outside context')
        return Poly.make(arity, [(tuple(int(j == i) for j in range(arity)), 1)])

    def __add__(self, other: 'Poly') -> 'Poly':
        if self.arity != other.arity:
            raise ValueError('different polynomial contexts')
        return Poly.make(self.arity, self.terms + other.terms)

    def __neg__(self) -> 'Poly':
        return Poly.make(self.arity, ((m, -c) for m, c in self.terms))

    def __sub__(self, other: 'Poly') -> 'Poly':
        return self + (-other)

    def __mul__(self, other: 'Poly') -> 'Poly':
        if self.arity != other.arity:
            raise ValueError('different polynomial contexts')
        return Poly.make(self.arity,
            ((tuple(x+y for x, y in zip(m, n)), a*b)
             for m, a in self.terms for n, b in other.terms))

    def __pow__(self, n: int) -> 'Poly':
        if type(n) is not int or n < 0:
            raise ValueError('only natural powers are supported')
        out, base = Poly.constant(self.arity, 1), self
        while n:
            if n & 1:
                out = out * base
            base = base * base
            n //= 2
        return out


def check_combination(target: Poly, equations: list[Poly], multipliers: list[Poly]) -> bool:
    """Check target = sum multipliers[i]*equations[i] as a polynomial identity.

    Equations are polynomial residuals, not assumed true by this function.
    A zero-valued target follows only under the separately supplied hypotheses
    that each residual vanishes at the valuation of interest.
    """
    if len(equations) != len(multipliers):
        return False
    out = Poly.constant(target.arity, 0)
    try:
        for e, c in zip(equations, multipliers):
            out = out + c * e
    except ValueError:
        return False
    return target == out


def check_bijection(source: list[int], target: list[int], f: Callable[[int], int]) -> bool:
    """Finite enumerated sets only. No result about symbolic or infinite sets."""
    if len(set(source)) != len(source) or len(set(target)) != len(target):
        return False
    image = [f(i) for i in source]
    return len(set(image)) == len(image) and set(image) == set(target)

@dataclass(frozen=True)
class Quad2:
    """Exact a + b*sqrt(2), using the positive real square root interpretation."""
    a: Q
    b: Q

    def __add__(self, other: 'Quad2') -> 'Quad2':
        return Quad2(self.a + other.a, self.b + other.b)

    def __neg__(self) -> 'Quad2':
        return Quad2(-self.a, -self.b)

    def __mul__(self, other: 'Quad2') -> 'Quad2':
        return Quad2(self.a*other.a + 2*self.b*other.b,
                     self.a*other.b + self.b*other.a)

    def sign(self) -> int:
        def sgn(x: Q) -> int:
            return (x > 0) - (x < 0)
        if not self.b:
            return sgn(self.a)
        if not self.a:
            return sgn(self.b)
        if sgn(self.a) == sgn(self.b):
            return sgn(self.a)
        comparison = self.a*self.a - 2*self.b*self.b
        return sgn(self.a) * sgn(comparison)


def check_principal_square_root(value: Quad2, candidate: Quad2) -> bool:
    return candidate.sign() >= 0 and candidate*candidate == value


def orthogonality(n: int, j: int) -> int:
    if n < 0 or j < 0:
        raise ValueError('natural indices required')
    return sum((-1)**(n-k)*comb(n, k)*comb(k, j) for k in range(j, n+1))

class LabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Poly.variable(1, 0)
        self.c = lambda n: Poly.constant(1, n)
        self.rel = self.r**2 - self.c(2)
        self.q = self.c(1) + self.r
        self.target = self.q**2 - (self.c(3) + self.c(2)*self.r)

    def test_01_radical_polynomial_witness(self):
        self.assertTrue(check_combination(self.target, [self.rel], [self.c(1)]))
    def test_02_wrong_multiplier_rejected(self):
        self.assertFalse(check_combination(self.target, [self.rel], [self.c(2)]))
    def test_03_corrupt_target_rejected(self):
        self.assertFalse(check_combination(self.target+self.c(1), [self.rel], [self.c(1)]))
    def test_04_wrong_relation_rejected(self):
        self.assertFalse(check_combination(self.target, [self.r**2-self.c(3)], [self.c(1)]))
    def test_05_mismatched_witness_length(self):
        self.assertFalse(check_combination(self.target, [self.rel], []))
    def test_06_wrong_context_rejected(self):
        self.assertFalse(check_combination(self.target, [Poly.constant(2, 1)], [self.c(1)]))
    def test_07_negative_branch_has_same_square(self):
        t = (-self.q)**2 - (self.c(3)+self.c(2)*self.r)
        self.assertTrue(check_combination(t, [self.rel], [self.c(1)]))
    def test_08_positive_principal_branch(self):
        self.assertTrue(check_principal_square_root(Quad2(Q(3),Q(2)), Quad2(Q(1),Q(1))))
    def test_09_negative_principal_branch_rejected(self):
        self.assertFalse(check_principal_square_root(Quad2(Q(3),Q(2)), Quad2(Q(-1),Q(-1))))
    def test_10_incorrect_positive_candidate_rejected(self):
        self.assertFalse(check_principal_square_root(Quad2(Q(3),Q(2)), Quad2(Q(2),Q(1))))
    def test_11_exact_signs(self):
        cases = [(0,0,0),(1,0,1),(-1,0,-1),(0,1,1),(0,-1,-1),
                 (1,1,1),(-1,-1,-1),(1,-1,-1),(2,-1,1),(-1,1,1),(-2,1,-1)]
        for a,b,sign in cases:
            self.assertEqual(Quad2(Q(a),Q(b)).sign(), sign)
    def test_12_inclusive_reindexing(self):
        for j in range(6):
            for m in range(7):
                self.assertTrue(check_bijection(list(range(m+1)),list(range(j,j+m+1)),lambda i:i+j))
    def test_13_missing_endpoint(self):
        self.assertFalse(check_bijection(list(range(4)),list(range(2,7)),lambda i:i+2))
    def test_14_noninjective_map(self):
        self.assertFalse(check_bijection([0,1,2],[0,1],lambda i:i%2))
    def test_15_wrong_offset(self):
        self.assertFalse(check_bijection([0,1,2],[3,4,5],lambda i:i+2))
    def test_16_empty_bijection(self):
        self.assertTrue(check_bijection([],[],lambda i:i))
    def test_17_duplicate_enumeration_rejected(self):
        self.assertFalse(check_bijection([0,0],[0],lambda i:i))
    def test_18_sampled_binomial_orthogonality(self):
        for n in range(25):
            for j in range(28):
                self.assertEqual(orthogonality(n,j),int(n==j))
    def test_19_sampled_binomial_product(self):
        for j in range(6):
            for m in range(8):
                for i in range(m+1):
                    self.assertEqual(comb(j+m,j+i)*comb(j+i,j),comb(j+m,j)*comb(m,i))
    def test_20_sampled_rational_telescoping(self):
        for n in range(101):
            self.assertEqual(sum((Q(1,k*(k+1)) for k in range(1,n+1)),Q(0)),Q(n,n+1))
    def test_21_natural_subtraction_guard_counterexample(self):
        self.assertNotEqual(Q(max(2-3,0)),Q(2)-Q(3))
    def test_22_natural_division_guard_counterexample(self):
        self.assertNotEqual(Q(1//2),Q(1,2))
    def test_23_finite_jet_is_not_full_equality(self):
        zero = [0]*9
        monomial = [0]*8+[1]
        self.assertEqual(zero[:8],monomial[:8])
        self.assertNotEqual(zero,monomial)
    def test_24_multiple_relations(self):
        x,y = Poly.variable(2,0),Poly.variable(2,1)
        one = Poly.constant(2,1)
        self.assertTrue(check_combination(x*x-y*y,[x-y],[x+y]))
        self.assertTrue(check_combination(x+y,[x,y],[one,one]))
    def test_25_malformed_monomial(self):
        with self.assertRaises(ValueError):
            Poly.make(1,[((-1,),1)])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LabTests)
    names = [t.id() for t in suite]
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {'status':'passed' if result.wasSuccessful() else 'failed',
              'tests_run':result.testsRun,'failures':len(result.failures),
              'errors':len(result.errors),'test_names':names,
              'scope':'Exact-arithmetic Python illustrations; not formal verification, not Lean execution.'}
    if args.report:
        args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    raise SystemExit(main())
