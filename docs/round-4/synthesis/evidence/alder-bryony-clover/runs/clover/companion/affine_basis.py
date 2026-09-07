#!/usr/bin/env python3
"""Exact finite calculations illustrating Clover's realizable affine test bases.

A finite basis verdict is a model-level result. Universal source promotion
requires the coverage theorem and realizers specified in the article; Python
execution is not a substitute for that Lean bridge.
"""
from dataclasses import dataclass
from fractions import Fraction
import itertools
import json
from pathlib import Path
from typing import Optional, Sequence, Tuple

Vector = Tuple[Fraction, ...]

@dataclass(frozen=True)
class Affine:
    constant: Fraction
    coefficients: Vector

    def __call__(self, value: Sequence[Fraction]) -> Fraction:
        if len(value) != len(self.coefficients):
            raise ValueError('affine evaluation arity mismatch')
        return self.constant + sum((a*x for a, x in zip(self.coefficients, value)), Fraction(0))

@dataclass(frozen=True)
class TestBasis:
    base: Vector
    directions: Tuple[Vector, ...]

    def __post_init__(self) -> None:
        if any(len(v) != len(self.base) for v in self.directions):
            raise ValueError('basis vector arity mismatch')

    def points(self) -> Tuple[Vector, ...]:
        return (self.base,) + tuple(tuple(b + v for b, v in zip(self.base, d))
                                  for d in self.directions)

    def first_mismatch(self, p: Affine, q: Affine) -> Optional[int]:
        for i, point in enumerate(self.points()):
            if p(point) != q(point):
                return i
        return None

PAIR_BASIS = TestBasis((Fraction(0),)*3,
                      ((Fraction(1), Fraction(1), Fraction(0)),
                       (Fraction(1), Fraction(0), Fraction(1))))

def observe_pair(xs, ys) -> Vector:
    return tuple(map(Fraction, (len(xs + ys), len(xs), len(ys))))

def pair_realizer(i: int):
    if i not in (0, 1, 2):
        raise ValueError('not a basis index')
    return ([0] if i == 1 else [], [0] if i == 2 else [])

def run_checks() -> dict:
    checks = 0
    for i, point in enumerate(PAIR_BASIS.points()):
        assert observe_pair(*pair_realizer(i)) == point
        checks += 1
    # Difference d(n,p,q)=c+a*n+b*p+e*q. It vanishes on the image
    # n=p+q precisely when c=0, a+b=0 and a+e=0.
    zero = Affine(Fraction(0), (Fraction(0),)*3)
    affine_forms = 0
    for c, a, b, e in itertools.product(range(-2, 3), repeat=4):
        d = Affine(Fraction(c), tuple(map(Fraction, (a,b,e))))
        verdict = PAIR_BASIS.first_mismatch(d, zero)
        expected = c == 0 and a+b == 0 and a+e == 0
        assert (verdict is None) == expected
        checks += 1
        affine_forms += 1
        if verdict is not None:
            xs, ys = pair_realizer(verdict)
            assert d(observe_pair(xs, ys)) != 0
            checks += 1
        else:
            for p, q in itertools.product(range(8), repeat=2):
                assert d(observe_pair([0]*p, [0]*q)) == 0
                checks += 1
    # Empty element type: only two empty input lists exist.
    empty_basis = TestBasis((Fraction(0),), ())
    n = Affine(Fraction(0), (Fraction(1),))
    z = Affine(Fraction(0), (Fraction(0),))
    assert empty_basis.first_mismatch(n, z) is None
    checks += 1
    ordinary_basis = TestBasis((Fraction(0),), ((Fraction(1),),))
    assert ordinary_basis.first_mismatch(n, z) == 1
    checks += 1
    # Guard len(xs)=100: a singleton affine image, not all natural lengths.
    length100 = TestBasis((Fraction(100),), ())
    hundred = Affine(Fraction(100), (Fraction(0),))
    assert length100.first_mismatch(n, hundred) is None
    checks += 1
    # Frey helper's satisfiable fixture and single-premise negative neighbors.
    def values(a,b,p):
        return b**p-1-a**p, -a**p*b**p
    n2,n4 = values(3,2,5)
    assert n2 % 4 == 0 and n4 % 16 == 0 and (n2//4,n4//16)==(-53,-486)
    checks += 1
    assert values(3,2,4)[0] % 4 != 0
    assert values(3,3,5)[0] % 4 != 0
    assert values(3,2,3)[1] % 16 != 0
    assert values(1,2,5)[0] % 4 != 0
    checks += 4
    return {'status':'finite_checks_passed', 'kernel_checked':False,
            'assertion_checks':checks, 'affine_forms':affine_forms,
            'pair_basis':[list(map(str,p)) for p in PAIR_BASIS.points()],
            'scope':'Exact finite arithmetic and explicit realizers; not a verified source bridge.'}

if __name__ == '__main__':
    result = run_checks()
    Path(__file__).with_name('affine-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
