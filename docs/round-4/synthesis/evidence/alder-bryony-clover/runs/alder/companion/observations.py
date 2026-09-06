"""Exact arithmetic companions to Alder's affine observation-frame theorem.

These functions check finite arithmetic. The article separately proves when
an affine frame covers all admissible observations. No Python frame value is
itself a Lean proof of that coverage or of source-program correspondence.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import comb
from typing import Sequence


@dataclass(frozen=True)
class Affine:
    constant: int
    coefficients: tuple[int, ...]

    def __call__(self, x: Sequence[int]) -> int:
        if len(x) != len(self.coefficients):
            raise ValueError("Affine input arity mismatch")
        return self.constant + sum(a * n for a, n in zip(self.coefficients, x))

    def __add__(self, other: Affine) -> Affine:
        if len(self.coefficients) != len(other.coefficients):
            raise ValueError("Affine addition arity mismatch")
        return Affine(self.constant + other.constant,
                      tuple(a + b for a, b in zip(self.coefficients, other.coefficients)))


def frame_equal(left: Affine, right: Affine, probes: Sequence[Sequence[int]]) -> bool:
    if len(left.coefficients) != len(right.coefficients):
        raise ValueError("Target arity mismatch")
    # Empty probes mean a vacuous finite test; the coverage theorem must then
    # establish an empty concrete domain before this licenses a universal claim.
    return all(left(p) == right(p) for p in probes)


@dataclass(frozen=True)
class ListExpr:
    tag: str
    index: int = 0
    children: tuple[ListExpr, ...] = ()

    def validate(self, arity: int) -> None:
        count = {"nil": 0, "var": 0, "cons": 1, "append": 2, "reverse": 1, "map": 1}
        if self.tag not in count or len(self.children) != count[self.tag]:
            raise ValueError("Ill-formed list expression")
        if self.tag == "var" and not 0 <= self.index < arity:
            raise ValueError("List variable out of range")
        for c in self.children:
            c.validate(arity)

    def model(self, arity: int) -> Affine:
        self.validate(arity)
        zero = Affine(0, (0,) * arity)
        if self.tag == "nil":
            return zero
        if self.tag == "var":
            return Affine(0, tuple(int(i == self.index) for i in range(arity)))
        if self.tag == "cons":
            return Affine(1, (0,) * arity) + self.children[0].model(arity)
        if self.tag == "append":
            return self.children[0].model(arity) + self.children[1].model(arity)
        return self.children[0].model(arity)

    def evaluate(self, env: Sequence[Sequence[int]]) -> list[int]:
        self.validate(len(env))
        if self.tag == "nil":
            return []
        if self.tag == "var":
            return list(env[self.index])
        if self.tag == "cons":
            return [0] + self.children[0].evaluate(env)
        if self.tag == "append":
            return self.children[0].evaluate(env) + self.children[1].evaluate(env)
        xs = self.children[0].evaluate(env)
        if self.tag == "reverse":
            return list(reversed(xs))
        # A fixed map, successor over Nat, whose length law is structural.
        return [x + 1 for x in xs]


def germ_coefficients(order: int) -> tuple[Fraction, ...]:
    """Coefficients through Q^(order-1) of S+4S^2=(4/9)Q, S(0)=0."""
    if order < 0:
        raise ValueError("Negative truncation order")
    a = [Fraction(0) for _ in range(order)]
    for n in range(1, order):
        a[n] = (Fraction(4, 9) if n == 1 else Fraction(0)) - 4 * sum(
            (a[i] * a[n-i] for i in range(1, n)), Fraction(0))
    return tuple(a)


def germ_closed_coefficient(n: int) -> Fraction:
    if n < 0:
        raise ValueError("Negative coefficient index")
    if n == 0:
        return Fraction(0)
    catalan = comb(2*(n-1), n-1) // n
    return Fraction((-1)**(n-1) * catalan * 4**(2*n-1), 9**n)


def residual(coefficients: Sequence[Fraction]) -> tuple[Fraction, ...]:
    out = []
    for n, c in enumerate(coefficients):
        sq = sum((coefficients[i] * coefficients[n-i] for i in range(n+1)), Fraction(0))
        out.append(c + 4*sq - (Fraction(4, 9) if n == 1 else 0))
    return tuple(out)
