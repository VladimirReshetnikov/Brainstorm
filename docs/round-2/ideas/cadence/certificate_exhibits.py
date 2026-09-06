#!/usr/bin/env python3
"""Exact-arithmetic exhibits for the Cadence design article.

These tests are not Lean proofs and do not implement Cadence. They exercise
small proposed certificate boundaries with Python's exact rational arithmetic.
No third-party packages or network access are required. Run with Python 3.10+.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json
import sys
from typing import Any


@dataclass(frozen=True)
class Dual:
    """The commutative Q-algebra Q[e]/(e^2), which is not a field."""
    real: Q
    eps: Q = Q(0)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'real', Q(self.real))
        object.__setattr__(self, 'eps', Q(self.eps))

    @staticmethod
    def coerce(v: Any) -> Dual:
        return v if isinstance(v, Dual) else Dual(Q(v))

    def __add__(self, other: Any) -> Dual:
        b = Dual.coerce(other)
        return Dual(self.real + b.real, self.eps + b.eps)

    __radd__ = __add__

    def __neg__(self) -> Dual:
        return Dual(-self.real, -self.eps)

    def __sub__(self, other: Any) -> Dual:
        return self + (-Dual.coerce(other))

    def __rsub__(self, other: Any) -> Dual:
        return Dual.coerce(other) - self

    def __mul__(self, other: Any) -> Dual:
        b = Dual.coerce(other)
        return Dual(self.real*b.real,
                    self.real*b.eps + self.eps*b.real)

    __rmul__ = __mul__

    def __pow__(self, n: int) -> Dual:
        if not isinstance(n, int) or n < 0:
            raise ValueError('Only nonnegative integral powers are supported')
        result, base = Dual(1), self
        while n:
            if n & 1:
                result = result * base
            base = base * base
            n >>= 1
        return result


# Dense, low-degree-first polynomials. Trailing zeroes are canonicalized.
def poly(values: list[Any] | tuple[Any, ...]) -> tuple[Any, ...]:
    p = list(values)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p) if p else (Q(0),)


def add(a: tuple[Any, ...], b: tuple[Any, ...]) -> tuple[Any, ...]:
    return poly([(a[i] if i < len(a) else 0) +
                 (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))])


def scale(a: tuple[Any, ...], s: Any) -> tuple[Any, ...]:
    return poly([v*s for v in a])


def mul(a: tuple[Any, ...], b: tuple[Any, ...]) -> tuple[Any, ...]:
    out: list[Any] = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] = out[i+j] + x*y
    return poly(out)


def derivative(a: tuple[Any, ...]) -> tuple[Any, ...]:
    return poly([i*a[i] for i in range(1, len(a))])


def evaluate(a: tuple[Any, ...], x: Any) -> Any:
    out: Any = Q(0)
    for c in reversed(a):
        out = out*x + c
    return out


def check_combination(target: tuple[Any, ...],
                      generators: list[tuple[Any, ...]],
                      multipliers: list[tuple[Any, ...]]) -> bool:
    """Check target = sum(multiplier_i * generator_i), not ideal completeness."""
    if len(generators) != len(multipliers):
        return False
    total = (Q(0),)
    for f, q in zip(generators, multipliers):
        total = add(total, mul(f, q))
    return poly(target) == total


def jet_mul(a: list[Any], b: list[Any], N: int) -> list[Any]:
    if N < 1:
        raise ValueError('Precision N must be positive')
    out: list[Any] = [Q(0)] * N
    for i, x in enumerate(a[:N]):
        for j, y in enumerate(b[:N-i]):
            out[i+j] = out[i+j] + x*y
    return out


def jet_exp(h: list[Any], N: int) -> list[Any]:
    """exp(h) modulo t^N; zero constant term is a required guard."""
    if N < 1 or not h:
        raise ValueError('A positive precision and nonempty series are required')
    z = h[0]
    is_zero = (z.real == 0 and z.eps == 0) if isinstance(z, Dual) else z == 0
    if not is_zero:
        raise ValueError('This formal exponential routine requires h[0] = 0')
    power: list[Any] = [Q(1)] + [Q(0)]*(N-1)
    result: list[Any] = [Q(0)] * N
    for k in range(N):
        result = [v + w*Q(1, factorial(k)) for v, w in zip(result, power)]
        power = jet_mul(power, h, N)
    return result


def abel_jet(a: Any, N: int) -> list[Any]:
    if N < 1:
        raise ValueError('Precision N must be positive')
    t: list[Any] = [Q(0)] * N
    # Each iteration fixes one more coefficient of T = t exp(-a T).
    for _ in range(N):
        e = jet_exp([-a*v for v in t], N)
        t = [Q(0)] + e[:N-1]
    return t


def linear_solutions(a: Q, b: Q) -> dict[str, Any]:
    if a:
        return {'kind': 'singleton', 'value': b/a}
    return {'kind': 'all' if b == 0 else 'empty'}


def member(result: dict[str, Any], x: Q) -> bool:
    return result['kind'] == 'all' or (
        result['kind'] == 'singleton' and x == result['value'])


def verify_bracket(lo: Q, hi: Q, steps: int) -> dict[str, str | int]:
    """Bisection data for p(x)=x^3-x-1 on [1,3/2].

    The article separately proves existence and derivative lower bound 2;
    the present code checks rational signs, interval inclusion, and width.
    """
    if not isinstance(steps, int) or steps < 0:
        raise ValueError('steps must be a nonnegative integer')
    p = lambda x: x*x*x-x-1
    if not (Q(1) <= lo < hi <= Q(3, 2) and p(lo) < 0 < p(hi)):
        raise ValueError('The supplied endpoints do not bracket this root')
    initial_width = hi-lo
    for _ in range(steps):
        mid = (lo+hi)/2
        pm = p(mid)
        if pm == 0:
            return {'lower': str(mid), 'upper': str(mid), 'steps': steps,
                    'midpoint': str(mid), 'residual_bound': '0', 'width': '0'}
        if pm < 0:
            lo = mid
        else:
            hi = mid
    if not (p(lo) < 0 < p(hi) and hi-lo == initial_width / (2**steps)):
        raise AssertionError('Bisection certificate failed')
    q = (lo+hi)/2
    return {'lower': str(lo), 'upper': str(hi), 'steps': steps,
            'midpoint': str(q), 'residual_bound': str(abs(p(q))/2),
            'width': str(hi-lo)}


def run() -> dict[str, Any]:
    counts: dict[str, int] = {}
    def record(group: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(f'Failed exhibit: {group}')
        counts[group] = counts.get(group, 0) + 1

    # Membership certificates: x^3-x=(x+1)(x^2-x). Corruptions must fail.
    f, target, q = poly([0, -1, 1]), poly([0, -1, 0, 1]), poly([1, 1])
    record('polynomial_certificate_positive', check_combination(target, [f], [q]))
    for i in range(4):
        bad = list(target)
        bad[i] += 1
        record('polynomial_certificate_corruptions',
               not check_combination(poly(bad), [f], [q]))
    record('polynomial_certificate_arity_rejected',
           not check_combination(target, [f], []))

    # Parametric solver sample equivalences, never a proof of all parameters.
    for a in map(Q, [-2, 0, 1, 3]):
        for b in map(Q, [-1, 0, 2]):
            result = linear_solutions(a, b)
            for x in [Q(-2), Q(0), Q(1), Q(2, 3), Q(2)]:
                record('linear_solution_sample_equivalence',
                       (a*x == b) == member(result, x))

    # Exact finite jets, including a Q-algebra with nonzero nilpotents.
    N = 10
    cases: list[tuple[Any, Any]] = [
        (a, x) for a in [Q(-2), Q(0), Q(1), Q(3, 2)]
        for x in [Q(-1), Q(0), Q(2), Q(5, 3)]]
    cases += [(Dual(1, 1), Dual(2, -3)),
              (Dual(0, 1), Dual(0, 2)),
              (Dual(-1, 2), Dual(1, 1))]
    for a, x in cases:
        t = abel_jet(a, N)
        lhs = jet_exp([x*v for v in t], N)
        for n in range(N):
            rhs = Q(1) if n == 0 else x*(x-n*a)**(n-1)*Q(1, factorial(n))
            if isinstance(rhs, Dual) or isinstance(lhs[n], Dual):
                lhs_n, rhs = Dual.coerce(lhs[n]), Dual.coerce(rhs)
            else:
                lhs_n = lhs[n]
            record('abel_coefficients_mod_t10', lhs_n == rhs)
    try:
        jet_exp([Q(1), Q(0)], 2)
    except ValueError:
        record('formal_exponential_guard_rejected', True)
    else:
        raise AssertionError('Missing formal exponential guard')
    record('nilpotent_nonfield_control',
           Dual(0, 1) != Dual(0) and Dual(0, 1)**2 == Dual(0))
    # Same jet does not imply equal full series: t^N and zero.
    record('jet_equality_not_series_equality',
           [0]*N == ([0]*N+[1])[:N] and [0]*(N+1) != [0]*N+[1])

    # Lambert derivative recurrence: P_{n+1}=(1+w)P'_n-(nw+3n-1)P_n.
    P = poly([Q(1)])
    rows: list[list[str]] = [[str(c) for c in P]]
    for n in range(1, 6):
        left = add(mul(poly([1, 1]), derivative(P)),
                   scale(mul(poly([3*n-1, n]), P), -1))
        # Independent split product-rule numerator of Q'_n * phi.
        right = add(add(mul(poly([1, 1]), derivative(P)),
                        scale(mul(poly([1, 1]), P), -n)),
                    scale(P, -(2*n-1)))
        record('lambert_derivative_numerator', left == right)
        P = left
        rows.append([str(c) for c in P])
    record('lambert_P3_control', rows[2] == ['9', '8', '2'])

    bracket = verify_bracket(Q(1), Q(3, 2), 20)
    record('rational_root_bracket', Q(bracket['width']) == Q(1, 2**21))
    try:
        verify_bracket(Q(1), Q(5, 4), 2)
    except ValueError:
        record('bad_root_bracket_rejected', True)
    else:
        raise AssertionError('False bracket accepted')

    return {'status': 'PASS', 'scope': 'Python exact-arithmetic exhibits; not Lean proofs',
            'python': sys.version.split()[0], 'checks': sum(counts.values()),
            'groups': counts, 'abel_precision': N, 'abel_parameter_pairs': len(cases),
            'lambert_coefficients_low_to_high': rows,
            'cubic_root_certificate': bracket}


if __name__ == '__main__':
    report = run()
    text = json.dumps(report, indent=2)
    print(text)
    if len(sys.argv) > 2:
        raise SystemExit('Usage: python certificate_exhibits.py [receipt.json]')
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(text + '\n', encoding='utf-8')
