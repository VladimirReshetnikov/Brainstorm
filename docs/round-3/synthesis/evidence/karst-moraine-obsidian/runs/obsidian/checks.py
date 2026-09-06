#!/usr/bin/env python3
"""Executable design probes, NOT Lean kernel proofs.

Uses exact integers/rationals for arithmetic. The tiny scoped contract model
has deliberately fixed rules; it is not a Lean elaborator or a general prover.
Run: python3 experiments/checks.py > experiments/results.json
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import json


@dataclass(frozen=True)
class Poly:
    variables: int
    terms: tuple[tuple[tuple[int, ...], int], ...]

    @staticmethod
    def make(m: int, terms: dict[tuple[int, ...], int]) -> 'Poly':
        if type(m) is not int or m < 0:
            raise ValueError('invalid variable count')
        for exps, coeff in terms.items():
            if len(exps) != m or any(type(k) is not int or k < 0 for k in exps):
                raise ValueError('invalid monomial')
            if type(coeff) is not int:
                raise ValueError('integer coefficient required')
        return Poly(m, tuple(sorted((e, c) for e, c in terms.items() if c)))

    def __add__(self, other: 'Poly') -> 'Poly':
        if self.variables != other.variables:
            raise ValueError('variable spaces differ')
        d = dict(self.terms)
        for e, c in other.terms:
            d[e] = d.get(e, 0) + c
        return Poly.make(self.variables, d)

    def __neg__(self) -> 'Poly':
        return Poly.make(self.variables, {e: -c for e, c in self.terms})

    def __sub__(self, other: 'Poly') -> 'Poly':
        return self + -other

    def __mul__(self, other: 'Poly') -> 'Poly':
        if self.variables != other.variables:
            raise ValueError('variable spaces differ')
        d: dict[tuple[int, ...], int] = {}
        for a, c in self.terms:
            for b, v in other.terms:
                e = tuple(i + j for i, j in zip(a, b))
                d[e] = d.get(e, 0) + c * v
        return Poly.make(self.variables, d)

    def __pow__(self, n: int) -> 'Poly':
        if type(n) is not int or n < 0:
            raise ValueError('natural literal exponent required')
        r = Poly.make(self.variables, {(0,) * self.variables: 1})
        b = self
        while n:
            if n & 1:
                r = r * b
            b = b * b
            n //= 2
        return r

    def evaluate(self, values: tuple[int, ...]) -> int:
        if len(values) != self.variables:
            raise ValueError('valuation arity mismatch')
        return sum(c * prod(v ** k for v, k in zip(values, e)) for e, c in self.terms)


def prod(values):
    r = 1
    for v in values:
        r *= v
    return r


def check_certificate(g: Poly, equations: list[Poly], multipliers: list[Poly],
                      domain: str = 'commutative-ring') -> bool:
    if domain != 'commutative-ring' or len(equations) != len(multipliers):
        return False
    if any(p.variables != g.variables for p in equations + multipliers):
        return False
    residual = g
    for f, q in zip(equations, multipliers):
        residual = residual - q * f
    return not residual.terms


@dataclass(frozen=True)
class Fact:
    claim: tuple
    scope: tuple[str, ...] = ()
    origin: str = 'request-A'


@dataclass(frozen=True)
class Node:
    fact: Fact
    rule: str
    parents: tuple[int, ...] = ()


def visible(source: tuple[str, ...], destination: tuple[str, ...]) -> bool:
    return destination[:len(source)] == source


def validate_plan(givens: list[Fact], nodes: list[Node], requested: Fact) -> bool:
    """Fixed schematic proof rules; givens are assumed, not proved by Python."""
    accepted: list[Fact] = []
    for i, n in enumerate(nodes):
        if n.fact.origin != requested.origin:
            return False
        if any(j < 0 or j >= i for j in n.parents):
            return False  # includes cycles and forward references
        ps = [accepted[j] for j in n.parents]
        if any(p.origin != n.fact.origin or not visible(p.scope, n.fact.scope) for p in ps):
            return False
        c = n.fact.claim
        ok = False
        if n.rule == 'given':
            ok = not ps and any(g.claim == c and g.origin == n.fact.origin
                                and visible(g.scope, n.fact.scope) for g in givens)
        elif n.rule == 'jet-restrict' and len(ps) == 1:
            p = ps[0].claim
            ok = len(c) == 4 and len(p) == 4 and c[0] == p[0] == 'jet' and c[1:3] == p[1:3] \
                and type(c[3]) is int and type(p[3]) is int and 0 <= c[3] <= p[3]
        elif n.rule == 'jet-derivative' and len(ps) == 1:
            p = ps[0].claim
            ok = len(p) == 4 and p[0] == 'jet' and type(p[3]) is int and p[3] >= 1 \
                and c == ('jet', ('D', p[1]), ('D', p[2]), p[3] - 1)
        elif n.rule == 'open-to-germ' and len(ps) == 3:
            p, op, mem = (x.claim for x in ps)
            ok = len(p) == 4 and p[0] == 'eq-on' and op == ('open', p[3]) \
                and len(mem) == 3 and mem[0] == 'member' and mem[2] == p[3] \
                and c == ('germ', p[1], p[2], mem[1])
        if not ok:
            return False
        accepted.append(n.fact)
    return bool(accepted) and accepted[-1].claim == requested.claim \
        and visible(accepted[-1].scope, requested.scope)


def main() -> dict:
    cases: list[dict] = []
    def test(name: str, condition: bool, kind: str):
        if not condition:
            raise AssertionError(name)
        cases.append({'name': name, 'passed': True, 'kind': kind})

    # The arithmetic contract deliberately does NOT assume an FLT counterexample.
    admissible = 0
    for a, b, p in product(range(-9, 12), range(-10, 11), range(5, 16, 2)):
        if a % 4 == 3 and b % 2 == 0:
            n2, n4 = b**p - 1 - a**p, -(a**p) * b**p
            test(f'frey-exact/{a}/{b}/{p}', n2 % 4 == 0 and n4 % 16 == 0
                 and Fraction(n2 // 4) == Fraction(n2, 4)
                 and Fraction(n4 // 16) == Fraction(n4, 16), 'arithmetic-instance')
            admissible += 1
    for name, a, b, p, denominator in [
        ('drop-odd', 3, 2, 4, 4), ('drop-residue', 1, 2, 5, 4),
        ('drop-even-b', 3, 3, 5, 4), ('drop-exponent-bound', 3, 2, 3, 16)]:
        numerator = b**p - 1 - a**p if denominator == 4 else -(a**p) * b**p
        test(name, numerator % denominator != 0, 'negative-neighbor')
    test('nonzero-denominator-not-exact', Fraction(5 // 2) != Fraction(5, 2), 'negative-neighbor')
    test('satisfiable-local-contract', 3 % 4 == 3 and 2 % 2 == 0 and 5 % 2 == 1, 'positive-neighbor')

    x = Poly.make(2, {(1, 0): 1})
    y = Poly.make(2, {(0, 1): 1})
    one = Poly.make(2, {(0, 0): 1})
    for n in range(1, 33):
        q = Poly.make(2, {})
        for k in range(n):
            q = q + x**(n-1-k) * y**k
        g = x**n - y**n
        test(f'polynomial-certificate/{n}', check_certificate(g, [x-y], [q]), 'symbolic-identity')
        test(f'polynomial-corrupt/{n}', not check_certificate(g, [x-y], [q+one]), 'negative-neighbor')
    test('arity-rejection', not check_certificate(x-y, [x-y], [one, one]), 'negative-neighbor')
    test('noncommutative-rejection', not check_certificate(x*x-y*y, [x-y], [x+y], 'ring'), 'negative-neighbor')
    test('variable-space-rejection', not check_certificate(x-y, [x-y], [Poly.make(1,{(0,):1})]), 'negative-neighbor')
    try:
        Poly.make(2, {(0,0): Fraction(1,2)})
        invalid = False
    except ValueError:
        invalid = True
    test('rational-coefficient-rejection', invalid, 'negative-neighbor')
    for a,b in product(range(-3,4), repeat=2):
        test(f'evaluation/{a}/{b}', ((x+y)**3).evaluate((a,b)) == (a+b)**3, 'arithmetic-instance')

    base = Fact(('jet','f','g',6))
    d5 = Fact(('jet',('D','f'),('D','g'),5))
    ns = [Node(base,'given'),Node(d5,'jet-derivative',(0,))]
    test('derivative-positive', validate_plan([base],ns,d5), 'protocol-model')
    d6 = Fact(('jet',('D','f'),('D','g'),6))
    test('precision-laundering-rejected', not validate_plan([base],[ns[0],Node(d6,'jet-derivative',(0,))],d6), 'protocol-model')
    j3 = Fact(('jet','f','g',3))
    test('restriction-positive',validate_plan([base],[ns[0],Node(j3,'jet-restrict',(0,))],j3),'protocol-model')
    test('cyclic-parent-rejected',not validate_plan([base],[Node(base,'jet-restrict',(0,))],base),'protocol-model')
    sibling = Fact(base.claim,('left',))
    wrongscope = Fact(base.claim,('right',))
    test('sibling-scope-rejected',not validate_plan([sibling],[Node(wrongscope,'given')],wrongscope),'protocol-model')
    stale = Fact(base.claim,origin='request-old')
    test('stale-origin-rejected',not validate_plan([stale],[Node(stale,'given')],base),'protocol-model')
    other = Fact(('jet','other-f','g',3))
    test('object-change-rejected',not validate_plan([base],[ns[0],Node(other,'jet-restrict',(0,))],other),'protocol-model')
    eq = Fact(('eq-on','f','g','U')); op = Fact(('open','U')); mem = Fact(('member','x','U'))
    germ = Fact(('germ','f','g','x'))
    gs = [Node(eq,'given'),Node(op,'given'),Node(mem,'given'),Node(germ,'open-to-germ',(0,1,2))]
    test('open-domain-to-germ',validate_plan([eq,op,mem],gs,germ),'protocol-model')
    point = Fact(('point-eq','f','g','x'))
    gs[0] = Node(point,'given')
    test('point-equality-not-germ',not validate_plan([point,op,mem],gs,germ),'protocol-model')

    # Exact L1 norms for g_n=f_(n+1)-f_n, f_n=n*1_(0,1/n).
    for n in range(1,81):
        integral = Fraction(1,n+1) - n*(Fraction(1,n)-Fraction(1,n+1))
        norm_integral = Fraction(1,n+1) + n*(Fraction(1,n)-Fraction(1,n+1))
        test(f'pulse/{n}', integral == 0 and norm_integral == Fraction(2,n+1), 'arithmetic-instance')
    totals = {}
    for c in cases:
        totals[c['kind']] = totals.get(c['kind'],0)+1
    return {'status':'all executed design probes passed','lean_kernel_checked':False,
            'source_repositories_built':False,'test_count':len(cases),
            'admissible_frey_parameter_instances':admissible,'counts_by_kind':totals,
            'limits':'Finite model and arithmetic tests; not a verified Lean frontend, checker, or repository audit.',
            'cases':cases}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
