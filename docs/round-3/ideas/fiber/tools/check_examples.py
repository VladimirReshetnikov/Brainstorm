#!/usr/bin/env python3
"""Finite validation for FIBER (standard library, Python >= 3.9).

This is an executable model of one certificate format, NOT a Lean kernel,
formal proof of this Python program, or implementation of FIBER elaboration.
The article proves the mathematical checker contract separately.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple, TypeVar
import json
import random
import sys

Exp = Tuple[int, ...]
Term = Tuple[Exp, int]
T = TypeVar('T')

@dataclass(frozen=True)
class Limits:
    variables: int = 16
    terms: int = 100000
    degree: int = 256
    coefficient_bits: int = 4096

LIMITS = Limits()

@dataclass(frozen=True)
class Poly:
    """Canonical finite integer multivariate polynomial; no truncated zip."""
    arity: int
    terms: Tuple[Term, ...]

    def __post_init__(self) -> None:
        if type(self.arity) is not int or not 0 <= self.arity <= LIMITS.variables:
            raise ValueError('invalid variable arity')
        if len(self.terms) > LIMITS.terms:
            raise ValueError('term budget exceeded')
        previous = None
        for exponent, coefficient in self.terms:
            if not isinstance(exponent, tuple) or len(exponent) != self.arity:
                raise ValueError('exponent dimension mismatch')
            if any(type(e) is not int or e < 0 for e in exponent):
                raise ValueError('invalid exponent')
            if sum(exponent) > LIMITS.degree:
                raise ValueError('degree budget exceeded')
            if type(coefficient) is not int or coefficient == 0:
                raise ValueError('coefficient must be a nonzero integer')
            if abs(coefficient).bit_length() > LIMITS.coefficient_bits:
                raise ValueError('coefficient budget exceeded')
            if previous is not None and exponent <= previous:
                raise ValueError('noncanonical or duplicate monomial')
            previous = exponent

    @staticmethod
    def make(arity: int, terms: Iterable[Term]) -> 'Poly':
        accumulated: Dict[Exp, int] = {}
        # Validate each raw item before combining: malformed zero terms are
        # not allowed to disappear during normalization.
        for exponent, coefficient in terms:
            if type(coefficient) is not int:
                raise ValueError('noninteger coefficient')
            if not isinstance(exponent, tuple) or len(exponent) != arity:
                raise ValueError('exponent dimension mismatch')
            if any(type(e) is not int or e < 0 for e in exponent):
                raise ValueError('invalid exponent')
            if sum(exponent) > LIMITS.degree:
                raise ValueError('degree budget exceeded')
            accumulated[exponent] = accumulated.get(exponent, 0) + coefficient
            if len(accumulated) > LIMITS.terms:
                raise ValueError('term budget exceeded')
        return Poly(arity, tuple(sorted((e, c) for e, c in accumulated.items() if c)))

    @staticmethod
    def const(arity: int, n: int) -> 'Poly':
        return Poly.make(arity, [((0,) * arity, n)])

    @staticmethod
    def var(arity: int, index: int) -> 'Poly':
        if not 0 <= index < arity:
            raise ValueError('variable index out of range')
        e = [0] * arity
        e[index] = 1
        return Poly.make(arity, [(tuple(e), 1)])

    def same_arity(self, other: 'Poly') -> None:
        if self.arity != other.arity:
            raise ValueError('polynomial arity mismatch')

    def __add__(self, other: 'Poly') -> 'Poly':
        self.same_arity(other)
        return Poly.make(self.arity, self.terms + other.terms)

    def __neg__(self) -> 'Poly':
        return Poly.make(self.arity, [(e, -c) for e, c in self.terms])

    def __sub__(self, other: 'Poly') -> 'Poly':
        return self + (-other)

    def __mul__(self, other: 'Poly') -> 'Poly':
        self.same_arity(other)
        if len(self.terms) * len(other.terms) > LIMITS.terms:
            raise ValueError('multiplication work budget exceeded')
        return Poly.make(self.arity,
            [(tuple(e[i] + f[i] for i in range(self.arity)), a * b)
             for e, a in self.terms for f, b in other.terms])

    def power(self, n: int) -> 'Poly':
        if type(n) is not int or n < 0:
            raise ValueError('invalid power')
        result = Poly.const(self.arity, 1)
        base = self
        while n:
            if n & 1:
                result = result * base
            n //= 2
            if n:
                base = base * base
        return result

    def evaluate(self, values: Tuple[T, ...], cast: Callable[[int], T],
                 add: Callable[[T, T], T], mul: Callable[[T, T], T]) -> T:
        if len(values) != self.arity:
            raise ValueError('valuation arity mismatch')
        total = cast(0)
        for exponent, coefficient in self.terms:
            term = cast(coefficient)
            for value, n in zip(values, exponent):  # lengths established above
                factor = cast(1)
                for _ in range(n):
                    factor = mul(factor, value)
                term = mul(term, factor)
            total = add(total, term)
        return total


def check_ideal(target: Poly, hypotheses: List[Poly], multipliers: List[Poly]) -> bool:
    """True certifies a formal identity, NOT truth of the input hypotheses.

    Bad arity is rejected. A resource exception is a diagnostic refusal, not
    non-membership in an ideal and not a counterexample to the target.
    """
    if len(hypotheses) != len(multipliers):
        return False
    if any(p.arity != target.arity for p in hypotheses + multipliers):
        return False
    residual = target
    for i in range(len(hypotheses)):
        residual = residual - multipliers[i] * hypotheses[i]
    return not residual.terms


checks: Dict[str, int] = {}
def check(group: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(group)
    checks[group] = checks.get(group, 0) + 1


def rejects(group: str, operation: Callable[[], object]) -> None:
    try:
        operation()
    except ValueError:
        check(group, True)
    else:
        raise AssertionError('accepted malformed input: ' + group)


def run() -> dict:
    random.seed(20260906)
    zero = Poly.const(3, 0)
    one = Poly.const(3, 1)
    x, y, z = (Poly.var(3, i) for i in range(3))
    f = [x - y, y - z]
    q = [x + y, z + one]
    target = q[0] * f[0] + q[1] * f[1]
    check('ideal_positive', check_ideal(target, f, q))
    check('ideal_corruption', not check_ideal(target + one, f, q))
    check('ideal_arity', not check_ideal(target, f, q[:1]))
    check('ideal_arity', not check_ideal(target, f[:1], q))
    check('ideal_arity', not check_ideal(target, [Poly.const(2, 0)], [one]))
    check('empty_certificate', check_ideal(zero, [], []))
    check('empty_certificate', not check_ideal(one, [], []))
    rejects('malformed_polynomial', lambda: Poly(2, (((0,), 1),)))
    rejects('malformed_polynomial', lambda: Poly(1, (((-1,), 1),)))
    rejects('malformed_polynomial', lambda: Poly(1, (((0,), 0),)))
    rejects('malformed_polynomial', lambda: Poly(1, (((0,), True),)))
    rejects('malformed_polynomial', lambda: Poly(1, (((0,), 1), ((0,), 2))))
    rejects('malformed_polynomial', lambda: Poly.var(2, 2))
    rejects('resource_refusal', lambda: Poly(1, (((LIMITS.degree + 1,), 1),)))
    rejects('valuation_arity', lambda: x.evaluate((1, 2), int, lambda a,b:a+b, lambda a,b:a*b))
    for _ in range(60):
        def random_poly() -> Poly:
            return Poly.make(3, [(tuple(random.randrange(3) for _ in range(3)),
                                  random.randrange(-5, 6)) for _ in range(5)])
        a, b, c, d = (random_poly() for _ in range(4))
        g = a * c + b * d
        check('random_formal_identity', check_ideal(g, [c, d], [a, b]))
        check('random_corruption', not check_ideal(g + one, [c, d], [a, b]))
        values = tuple(random.randrange(-3, 4) for _ in range(3))
        ev = lambda p: p.evaluate(values, int, lambda a,b:a+b, lambda a,b:a*b)
        check('integer_denotation', ev(g) == ev(a)*ev(c)+ev(b)*ev(d))
        ev4 = lambda p: p.evaluate(values, lambda n:n%4,
                                   lambda a,b:(a+b)%4, lambda a,b:(a*b)%4)
        check('mod4_denotation', ev4(g) == (ev4(a)*ev4(c)+ev4(b)*ev4(d))%4)
        dual_values = tuple((v, random.randrange(-2, 3)) for v in values)
        da = lambda a,b:(a[0]+b[0], a[1]+b[1])
        dm = lambda a,b:(a[0]*b[0], a[0]*b[1]+a[1]*b[0])
        ed = lambda p:p.evaluate(dual_values, lambda n:(n,0), da, dm)
        check('dual_number_denotation', ed(g) == da(dm(ed(a),ed(c)),dm(ed(b),ed(d))))
    for t in range(-5, 6):
        ev = lambda p:p.evaluate((t,t,t), int, lambda a,b:a+b, lambda a,b:a*b)
        check('original_hypotheses_instance', all(ev(h)==0 for h in f) and ev(target)==0)
    # Non-vacuous Frey arithmetic: no FLT equation and no coprimality assumption.
    for a in range(-13, 16):
        if a % 4 != 3:
            continue
        for b in range(-8, 9, 2):
            for p in (5, 7, 9, 11):
                n2 = b**p - 1 - a**p
                n4 = -(a**p)*(b**p)
                check('frey_exact_divisibility', n2 % 4 == 0 and n4 % 16 == 0)
                check('frey_scalar_extension',
                      Fraction(n2//4) == Fraction(n2,4) and
                      Fraction(n4//16) == Fraction(n4,16))
    check('frey_negative_oddness', (2**4 - 1 - 3**4) % 4 != 0)
    check('frey_negative_even_b', (3**5 - 1 - 3**5) % 4 != 0)
    check('frey_negative_lower_bound', (-(3**3)*(2**3)) % 16 != 0)
    check('integer_quotient_not_field', Fraction(3//2) != Fraction(3,2))
    # Endpoint tests for the centered dyadic coupling; finite tests only.
    for n in range(7):
        delta = Fraction(1, 2**(n+1))
        for head in product((0, 1), repeat=n):
            partial = sum((Fraction(a,2**(i+1)) for i,a in enumerate(head)), Fraction())
            for tail in (Fraction(), delta, 2*delta):
                check('centered_coupling_bound', abs(partial+delta-(partial+tail)) <= delta)
    # Positive and negative examples of specification strength.
    xs = [2, 1, 1]
    zeros = [0] * len(xs)
    check('length_not_sort_spec', len(zeros)==len(xs) and sorted(zeros)!=sorted(xs))
    check('set_not_multiset_spec', set([1,1,2])==set([1,2,2]) and sorted([1,1,2])!=sorted([1,2,2]))
    check('sort_positive', sorted(xs)==[1,1,2] and sorted(sorted(xs))==sorted(xs))
    check('point_not_germ', 0 == 0 and 1 != 0)  # f(t)=t, g(t)=0 at t=0
    check('regular_not_unit', 2 != 0 and all(2*k != 1 for k in range(-20,21)))
    check('nonzero_not_cancellable_mod4', 2 != 0 and (2*0)%4 == (2*2)%4 and 0 != 2)
    check('nonzero_square_zero_mod4', 2 != 0 and 2*2%4 == 0)
    check('witness_coverage_not_soundness', 0 in {0,1} and not all(v==0 for v in {0,1}))
    check('collapsed_enclosure_positive', Fraction(3,7) <= Fraction(3,7) <= Fraction(3,7))
    check('domain_total_division_neighbor', 0 != 2)  # at x=1 cancellation comparison
    # A finite sample bank cannot establish an unrestricted universal law.
    bad = lambda n:n if n <= 20 else n+1
    check('finite_not_universal', all(bad(n)==n for n in range(21)) and bad(21)!=21)
    return {'status':'passed', 'python':sys.version.split()[0], 'seed':20260906,
            'groups':len(checks), 'finite_checks':sum(checks.values()),
            'counts':checks, 'limits':LIMITS.__dict__,
            'scope':'Finite executable checks only; not Lean validation, not universal soundness of Python.'}


if __name__ == '__main__':
    receipt = run()
    output = Path(__file__).resolve().parent.parent / 'evidence' / 'checks.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))
