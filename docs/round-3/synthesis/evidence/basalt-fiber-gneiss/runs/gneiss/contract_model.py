#!/usr/bin/env python3
"""Executable acceptance model for GNEISS, not a Lean proof checker.

The caller's assumptions are treated as already-authorized inputs. Built-in
rule names model theorem interfaces; they are not discovered online or taken
from a provider. A successful run validates exact claim matching, dependency
order, and the small rule's parameters. It does not establish that the caller's
assumptions have Lean proofs or that this Python program is formally verified.
Only standard-library Python is required. Run: python3 contract_model.py
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path
import unittest

@dataclass(frozen=True)
class Claim:
    kind: str
    args: tuple

@dataclass(frozen=True)
class Step:
    rule: str
    premises: tuple[int, ...]
    conclusion: Claim
    parameter: int | None = None

class Rejected(ValueError):
    pass

def derive(rule: str, p: tuple[Claim, ...], parameter: int | None) -> Claim:
    """Compute the exact conclusion authorized by one closed rule schema."""
    if rule == 'positive_nonzero' and len(p) == 1 and p[0].kind == 'positive':
        return Claim('nonzero', p[0].args)
    if rule == 'jet_weaken' and len(p) == 1 and p[0].kind == 'jet':
        a, b, n = p[0].args
        if type(parameter) is not int or not 0 <= parameter <= n:
            raise Rejected('invalid precision weakening')
        return Claim('jet', (a, b, parameter))
    if rule == 'jet_derivative' and len(p) == 1 and p[0].kind == 'jet':
        a, b, n = p[0].args
        if type(n) is not int or n < 1:
            raise Rejected('positive input precision required')
        return Claim('jet', (('D', a), ('D', b), n - 1))
    if rule == 'open_to_near' and len(p) == 2:
        if p[0].kind == 'eq_on' and p[1].kind == 'open_contains':
            domain, a, b = p[0].args
            domain2, x = p[1].args
            if domain == domain2:
                return Claim('eq_near', (x, a, b))
    if rule == 'complete' and len(p) == 2:
        if p[0].kind == 'sound' and p[1].kind == 'covers' and p[0].args == p[1].args:
            return Claim('complete', p[0].args)
    if rule == 'collapsed_bounds' and len(p) == 1 and p[0].kind == 'bounds':
        x, lo, hi = p[0].args
        if lo == hi:
            return Claim('exact', (x, lo))
    raise Rejected('rule, arity, domain, or premise mismatch')

def validate(assumptions: tuple[Claim, ...], steps: tuple[Step, ...],
             target: Claim, *, max_nodes: int = 256) -> bool:
    """No forward references, self-justifying guards, or target substitution."""
    if len(assumptions) + len(steps) > max_nodes:
        raise Rejected('resource bound exceeded')
    known = list(assumptions)
    for step in steps:
        if any(type(i) is not int or i < 0 or i >= len(known) for i in step.premises):
            raise Rejected('invalid or cyclic dependency')
        actual = derive(step.rule, tuple(known[i] for i in step.premises), step.parameter)
        if actual != step.conclusion:
            raise Rejected('advertised conclusion differs from rule conclusion')
        known.append(actual)
    if not known or known[-1] != target:
        raise Rejected('original target not established')
    return True

# Executable integer polynomials, coefficients in increasing degree order.
# The paper proves the denotational identity for these operations, not the
# correctness of a compiled Lean implementation of this Python checker.
def trim(a: tuple[int, ...]) -> tuple[int, ...]:
    while a and a[-1] == 0:
        a = a[:-1]
    return a

def add(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return trim(tuple((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                      for i in range(max(len(a), len(b)))))

def mul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    if not a or not b:
        return ()
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(tuple(out))

def evaluate(a: tuple[int, ...], x: Fraction) -> Fraction:
    result = Fraction(0)
    for c in reversed(a):
        result = result * x + c
    return result

def check_combination(target: tuple[int, ...], generators: tuple[tuple[int, ...], ...],
                      multipliers: tuple[tuple[int, ...], ...]) -> bool:
    if len(generators) != len(multipliers):
        return False
    if any(type(c) is not int for p in (target, *generators, *multipliers) for c in p):
        return False
    rhs: tuple[int, ...] = ()
    for a, b in zip(generators, multipliers):
        rhs = add(rhs, mul(a, b))
    return trim(target) == rhs

class AcceptanceTests(unittest.TestCase):
    def rejected(self, assumptions, step, target=None):
        with self.assertRaises(Rejected):
            validate(tuple(assumptions), (step,), target or step.conclusion)
    def test_positive(self):
        t = Claim('nonzero', ('scope0:x:Real',))
        self.assertTrue(validate((Claim('positive', t.args),),
                                 (Step('positive_nonzero', (0,), t),), t))
    def test_wrong_anchor(self):
        self.rejected([Claim('positive', ('scope0:x:Real',))],
                      Step('positive_nonzero', (0,), Claim('nonzero', ('scope1:x:Real',))))
    def test_sibling_scope(self):
        self.rejected([], Step('positive_nonzero', (0,), Claim('nonzero', ('x',))))
    def test_forward_reference(self):
        self.rejected([Claim('positive', ('x',))],
                      Step('positive_nonzero', (2,), Claim('nonzero', ('x',))))
    def test_cyclic_guard(self):
        self.rejected([Claim('positive', ('x',))],
                      Step('positive_nonzero', (1,), Claim('nonzero', ('x',))))
    def test_jet_weaken(self):
        t = Claim('jet', ('f', 'g', 3))
        self.assertTrue(validate((Claim('jet', ('f', 'g', 6)),),
                                 (Step('jet_weaken', (0,), t, 3),), t))
    def test_jet_strengthen(self):
        self.rejected([Claim('jet', ('f', 'g', 3))],
                      Step('jet_weaken', (0,), Claim('jet', ('f', 'g', 6)), 6))
    def test_differentiate(self):
        t = Claim('jet', (('D', 'f'), ('D', 'g'), 4))
        self.assertTrue(validate((Claim('jet', ('f', 'g', 5)),),
                                 (Step('jet_derivative', (0,), t),), t))
    def test_differentiate_same_precision(self):
        self.rejected([Claim('jet', ('f', 'g', 5))],
                      Step('jet_derivative', (0,), Claim('jet', (('D','f'), ('D','g'), 5))))
    def test_jet_not_global(self):
        self.rejected([Claim('jet', ('f', 'g', 5))],
                      Step('jet_weaken', (0,), Claim('equal', ('f', 'g')), 3))
    def test_neighborhood(self):
        a = (Claim('eq_on', ('U', 'f', 'g')), Claim('open_contains', ('U', 'x')))
        t = Claim('eq_near', ('x', 'f', 'g'))
        self.assertTrue(validate(a, (Step('open_to_near', (0,1), t),), t))
    def test_point_not_neighborhood(self):
        self.rejected([Claim('eq_at', ('x','f','g')), Claim('open_contains', ('U','x'))],
                      Step('open_to_near', (0,1), Claim('eq_near', ('x','f','g'))))
    def test_wrong_domain(self):
        self.rejected([Claim('eq_on', ('V','f','g')), Claim('open_contains', ('U','x'))],
                      Step('open_to_near', (0,1), Claim('eq_near', ('x','f','g'))))
    def test_complete(self):
        a = (Claim('sound', ('P','S')), Claim('covers', ('P','S')))
        t = Claim('complete', ('P','S'))
        self.assertTrue(validate(a, (Step('complete', (0,1), t),), t))
    def test_witness_not_soundness(self):
        self.rejected([Claim('witness', ('P','w')), Claim('covers', ('P','S'))],
                      Step('complete', (0,1), Claim('complete', ('P','S'))))
    def test_mismatched_solution_predicate(self):
        self.rejected([Claim('sound', ('P','S')), Claim('covers', ('P','T'))],
                      Step('complete', (0,1), Claim('complete', ('P','S'))))
    def test_collapsed_bounds(self):
        t = Claim('exact', ('x', Fraction(2)))
        self.assertTrue(validate((Claim('bounds', ('x', Fraction(2), Fraction(2))),),
                                 (Step('collapsed_bounds', (0,), t),), t))
    def test_noncollapsed_bounds(self):
        self.rejected([Claim('bounds', ('x', 1, 3))],
                      Step('collapsed_bounds', (0,), Claim('exact', ('x', 2))))
    def test_wrong_target(self):
        self.rejected([Claim('positive', ('x',))],
                      Step('positive_nonzero', (0,), Claim('nonzero', ('x',))),
                      Claim('nonzero', ('y',)))
    def test_unknown_rule(self):
        self.rejected([Claim('positive', ('x',))],
                      Step('trust_cas', (0,), Claim('equal', ('x','y'))))
    def test_resource_limit(self):
        with self.assertRaises(Rejected):
            validate((Claim('positive', ('x',)),), (), Claim('positive', ('x',)), max_nodes=0)
    def test_composed_precision(self):
        a = (Claim('jet', ('f','g', 8)),)
        d = Claim('jet', (('D','f'),('D','g'),7))
        t = Claim('jet', (('D','f'),('D','g'),3))
        self.assertTrue(validate(a, (Step('jet_derivative',(0,),d), Step('jet_weaken',(1,),t,3)), t))
    def test_polynomial_geometric(self):
        for n in range(1, 65):
            self.assertTrue(check_combination((-1,) + (0,)*(n-1) + (1,),
                                             ((-1,1),), ((1,)*n,)))
    def test_polynomial_corruption(self):
        self.assertFalse(check_combination((-1,0,0,1), ((-1,1),), ((1,2,1),)))
    def test_polynomial_arity(self):
        self.assertFalse(check_combination((), (), ((1,),)))
    def test_polynomial_zero_and_padding(self):
        self.assertTrue(check_combination((0,0), ((0,),), ((5,),)))
    def test_polynomial_noninteger(self):
        self.assertFalse(check_combination((True,), ((1,),), ((1,),)))
    def test_denotation_examples(self):
        polys = [(), (0,), (1,), (-1,2), (3,0,-4), (0,0,1)]
        for a in polys:
            for b in polys:
                for x in [Fraction(-2), Fraction(0), Fraction(1,3), Fraction(3)]:
                    self.assertEqual(evaluate(add(a,b), x), evaluate(a,x)+evaluate(b,x))
                    self.assertEqual(evaluate(mul(a,b), x), evaluate(a,x)*evaluate(b,x))

    def test_frey_integrality_local_premises(self):
        # These are normalization premises only, NOT Fermat counterexamples.
        for p in [5,7,9,11]:
            for a in [-9,-5,-1,3,7]:
                for b in [-6,-2,0,2,4,8]:
                    self.assertEqual((b**p-1-a**p) % 4, 0)
                    self.assertEqual((-a**p*b**p) % 16, 0)
    def test_frey_missing_oddness(self):
        a,b,p = 3,2,2
        self.assertNotEqual((b**p-1-a**p) % 4, 0)
    def test_triangular_binomial_matrices(self):
        from math import comb
        for n in range(1,9):
            a = [[comb(i,j) if j<=i else 0 for j in range(n)] for i in range(n)]
            b = [[(-1)**(i-j)*comb(i,j) if j<=i else 0 for j in range(n)] for i in range(n)]
            for left,right in [(a,b),(b,a)]:
                self.assertEqual([[sum(left[i][k]*right[k][j] for k in range(n))
                                   for j in range(n)] for i in range(n)],
                                 [[int(i==j) for j in range(n)] for i in range(n)])
    def test_infinite_shift_observations(self):
        e = lambda n: int(n == 0)
        shift = lambda f: lambda n: 0 if n == 0 else f(n-1)
        tail = lambda f: lambda n: f(n+1)
        self.assertTrue(all(tail(shift(e))(n)==e(n) for n in range(10)))
        self.assertNotEqual(shift(tail(e))(0), e(0))

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AcceptanceTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {'model': 'GNEISS acceptance model v1', 'tests': result.testsRun,
               'failures': len(result.failures), 'errors': len(result.errors),
               'status': 'passed' if result.wasSuccessful() else 'failed',
               'lean_compiled': False, 'formal_verification_of_python': False,
               'scope': 'contract assembly and exact finite arithmetic only'}
    Path(__file__).with_name('test_results.json').write_text(json.dumps(receipt, indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
