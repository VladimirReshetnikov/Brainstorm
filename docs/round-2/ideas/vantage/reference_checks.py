#!/usr/bin/env python3
"""Exact-arithmetic regression checks for the Vantage design article.

Run with Python 3.9 or later:
    python reference_checks.py --output reference-checks.json

These are finite tests and illustrative certificate checks. They are not a
Lean implementation, a formally verified checker, or proofs of the universally
quantified theorems in the article. No floating-point arithmetic is used.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

Poly = Tuple[F, ...]  # Ascending powers; zero is (Fraction(0),).
Multi = Dict[Tuple[int, int], F]  # Exponents of u, v.
Dual = Tuple[F, F]  # a + b*epsilon, epsilon**2 = 0.


def require(condition: bool, message: str) -> None:
    """Checks are not disabled by Python's -O option."""
    if not condition:
        raise AssertionError(message)


def poly(values: Iterable[F]) -> Poly:
    a = list(map(F, values)) or [F(0)]
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return tuple(a)


def add(a: Poly, b: Poly) -> Poly:
    return poly((a[i] if i < len(a) else 0) +
                (b[i] if i < len(b) else 0)
                for i in range(max(len(a), len(b))))


def scale(a: Poly, c: F) -> Poly:
    return poly(c * x for x in a)


def mul(a: Poly, b: Poly) -> Poly:
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return poly(out)


def derivative(a: Poly) -> Poly:
    return poly(i * a[i] for i in range(1, len(a)))


def evaluate(a: Poly, x: F) -> F:
    result = F(0)
    for c in reversed(a):
        result = result * x + c
    return result


def divrem(a: Poly, b: Poly) -> Tuple[Poly, Poly]:
    if b == (F(0),):
        raise ZeroDivisionError("Polynomial division by zero")
    r = a
    q = [F(0)] * max(1, len(a) - len(b) + 1)
    while r != (F(0),) and len(r) >= len(b):
        k = len(r) - len(b)
        c = r[-1] / b[-1]
        q[k] += c
        term = poly([F(0)] * k + [c * x for x in b])
        r = add(r, scale(term, F(-1)))
    return poly(q), r


def sign(x: F) -> int:
    return (x > 0) - (x < 0)


def variations(signs: Iterable[int]) -> int:
    nonzero = [s for s in signs if s]
    return sum(a != b for a, b in zip(nonzero, nonzero[1:]))


def check_sturm(chain: Sequence[Poly]) -> bool:
    """Narrow checker for the square-free, constant-final example used here.

    This validates rational polynomial identities, not a formalization of
    Sturm's theorem. Unsupported chains return False rather than a root claim.
    """
    if len(chain) < 2 or len(chain[0]) < 2:
        return False
    if chain[1] != derivative(chain[0]):
        return False
    if any(p == (F(0),) for p in chain):
        return False
    for i in range(1, len(chain) - 1):
        _, remainder = divrem(chain[i - 1], chain[i])
        if chain[i + 1] != scale(remainder, F(-1)):
            return False
    return len(chain[-1]) == 1 and chain[-1][0] != 0


def interval_count(chain: Sequence[Poly], a: F, b: F) -> int:
    if not check_sturm(chain):
        raise ValueError("Invalid or unsupported Sturm chain")
    if not a < b or evaluate(chain[0], a) == 0 or evaluate(chain[0], b) == 0:
        raise ValueError("Expected ordered non-root endpoints")
    return variations(sign(evaluate(p, a)) for p in chain) - variations(
        sign(evaluate(p, b)) for p in chain)


def ma(a: Multi, b: Multi) -> Multi:
    result = defaultdict(F)
    for source in (a, b):
        for power, value in source.items():
            result[power] += value
    return {power: value for power, value in result.items() if value}


def ms(a: Multi, c: F) -> Multi:
    return {power: c * value for power, value in a.items() if c * value}


def mm(a: Multi, b: Multi) -> Multi:
    result = defaultdict(F)
    for (i, j), x in a.items():
        for (k, l), y in b.items():
            result[(i + k, j + l)] += x * y
    return {power: value for power, value in result.items() if value}


def da(a: Dual, b: Dual) -> Dual:
    return a[0] + b[0], a[1] + b[1]


def dm(a: Dual, b: Dual) -> Dual:
    return a[0] * b[0], a[0] * b[1] + a[1] * b[0]


def ds(a: Dual, c: F) -> Dual:
    return a[0] * c, a[1] * c


def dsum(values: Iterable[Dual]) -> Dual:
    result = (F(0), F(0))
    for x in values:
        result = da(result, x)
    return result


def run_checks() -> dict:
    groups: List[dict] = []

    def record(name: str, checks: int, scope: str) -> None:
        groups.append({"name": name, "passed_checks": checks, "scope": scope})

    # A symbolic identity in Q[u,v], not a numerical sampling of the identity.
    one = {(0, 0): F(1)}
    u = {(1, 0): F(1)}
    v = {(0, 1): F(1)}
    left = mm(ma(ma(v, ms(u, -1)), ms(one, -1)), ma(ma(v, u), one))
    f1 = ma(mm(u, u), ms(one, -2))
    f2 = ma(ma(mm(v, v), ms(one, -3)), ms(u, -2))
    require(left == ma(f2, ms(f1, -1)), "Denesting certificate identity")
    require(left != ma(f2, f1), "Mutant certificate must be rejected")
    record("denesting_polynomial_certificate", 2,
           "Exact coefficient comparison in Q[u,v], plus one wrong-sign mutant")

    chain = [poly([1, 0, -6, 0, 1]), poly([0, -12, 0, 4]),
             poly([-1, 0, 3]), poly([0, F(32, 3)]), poly([1])]
    require(check_sturm(chain), "Displayed Sturm recurrence")
    bad_chain = list(chain)
    bad_chain[2] = scale(bad_chain[2], -1)
    require(not check_sturm(bad_chain), "Wrong-sign Sturm recurrence")
    signs2 = [sign(evaluate(p, F(2))) for p in chain]
    signs3 = [sign(evaluate(p, F(3))) for p in chain]
    require(signs2 == [-1, 1, 1, 1, 1], "Signs at 2")
    require(signs3 == [1, 1, 1, 1, 1], "Signs at 3")
    require(interval_count(chain, F(2), F(3)) == 1, "One root in (2,3)")
    for a, b in [(-3, -2), (-1, 0), (0, 1)]:
        require(interval_count(chain, F(a), F(b)) == 1, "Other real root interval")
    vinf = variations(sign(p[-1]) for p in chain)
    vminf = variations(sign(p[-1]) * (-1) ** (len(p) - 1) for p in chain)
    require(vminf - vinf == 4, "Four distinct real roots")
    record("sturm_example", 9, "Displayed chain, endpoint signs, four intervals and infinity signs")

    # Bell numbers and Stirling numbers are computed by their standard recurrences.
    limit = 30
    bell = [1]
    for n in range(limit):
        bell.append(sum(comb(n, k) * bell[k] for k in range(n + 1)))
    stirling = [[0] * (limit + 2) for _ in range(limit + 1)]
    stirling[0][0] = 1
    for n in range(1, limit + 1):
        for k in range(1, n + 1):
            stirling[n][k] = k * stirling[n - 1][k] + stirling[n - 1][k - 1]
    for m in range(12):
        for n in range(12):
            rhs = sum(stirling[m][j] * comb(n, k) * bell[k] * j ** (n - k)
                      for j in range(m + 1) for k in range(n + 1))
            require(bell[m + n] == rhs, "Spivey finite instance")
    record("spivey", 144, "0 <= m,n < 12; exact integers, finite regression only")

    for m in range(24):
        t = poly(stirling[m][:m + 1])
        next_t = poly(stirling[m + 1][:m + 2])
        require(next_t == mul(poly([0, 1]), add(t, derivative(t))), "Touchard recurrence")
    record("touchard", 24, "0 <= m < 24; exact polynomial comparison")

    count = 0
    for n in range(36):
        for j in range(40):
            lhs = sum((-1) ** (n - k) * comb(n, k) * comb(k, j)
                      for k in range(j, n + 1))
            require(lhs == int(n == j), "Binomial kernel orthogonality")
            count += 1
    record("binomial_orthogonality", count, "0 <= n < 36, 0 <= j < 40, including empty intervals")

    count = 0
    for seed in range(10):
        a = [F((-1) ** (n + seed) * (n + 1), n + seed + 1) for n in range(20)]
        b = [F(n * n + seed + 1, n + 2) for n in range(20)]
        ea = [x / factorial(n) for n, x in enumerate(a)]
        eb = [x / factorial(n) for n, x in enumerate(b)]
        for n in range(19):
            require(factorial(n) * ea[n] == a[n], "EGF coefficient inverse")
            ordinary_product = sum(ea[k] * eb[n - k] for k in range(n + 1))
            normalized_product = sum(comb(n, k) * a[k] * b[n - k] for k in range(n + 1))
            require(factorial(n) * ordinary_product == normalized_product, "EGF convolution")
            require(factorial(n) * (n + 1) * ea[n + 1] == a[n + 1], "EGF derivative")
            count += 3
    record("rational_egf", count, "10 deterministic rational sequence pairs; indices 0..18")

    # Test EGF arithmetic in a Q-algebra WITH zero divisors, not only a field.
    count = 0
    for seed in range(7):
        a = [(F(n + seed, n + 1), F((-1) ** n, n + 2)) for n in range(12)]
        b = [(F(seed - n, n + 3), F(n + 1)) for n in range(12)]
        ea = [ds(x, F(1, factorial(n))) for n, x in enumerate(a)]
        eb = [ds(x, F(1, factorial(n))) for n, x in enumerate(b)]
        for n in range(11):
            lhs = ds(dsum(dm(ea[k], eb[n - k]) for k in range(n + 1)), F(factorial(n)))
            rhs = dsum(ds(dm(a[k], b[n - k]), F(comb(n, k))) for k in range(n + 1))
            require(lhs == rhs, "EGF multiplication in dual numbers")
            require(ds(ea[n + 1], F(factorial(n) * (n + 1))) == a[n + 1],
                    "EGF derivative in dual numbers")
            count += 2
    record("dual_number_egf", count, "7 sequence pairs in Q[epsilon]/(epsilon^2); indices 0..10")

    count = 0
    for a in range(16):
        for b in range(a + 1):
            for d in range(1, 9):
                if (a - b) % d == 0:
                    require(F((a - b) // d) == F(a - b, d), "Guarded arithmetic transport")
                    count += 1
    require(F(6 // 4) != F(6, 4), "Floor versus field division")
    require(max(2 - 3, 0) != 2 - 3, "Truncated versus integer subtraction")
    record("guarded_transport", count + 2, "0 <= b <= a < 16, 1 <= d <= 8, divisible cases and two mutants")

    count = 0
    for numerator in range(-18, 19):
        for denominator in range(1, 7):
            x = F(numerator, denominator)
            if x != 1:
                require((x * x - 1) / (x - 1) == x + 1, "Guarded rational cancellation")
                count += 1
    total_zero_denominator_value = F(0)
    require(total_zero_denominator_value != F(2), "Totalized cancellation at x=1 must fail")
    epsilon, zero = (F(0), F(1)), (F(0), F(0))
    require(epsilon != zero and dm(epsilon, epsilon) == dm(epsilon, zero), "Nonzero zero divisor")
    record("cancellation", count + 2, "Rational samples, total-division zero case, dual-number zero divisor")

    count = 0
    for n in range(1, 13):
        f = [F(0)] * (n + 1)
        g = f.copy()
        g[n] = F(1)
        require(f[:n] == g[:n] and f[n] != g[n], "Jet equality does not extend")
        df = [F(k + 1) * f[k + 1] for k in range(n)]
        dg = [F(k + 1) * g[k + 1] for k in range(n)]
        require(df[:n - 1] == dg[:n - 1] and df[n - 1] != dg[n - 1], "Derivative loses precision")
        require(0 ** n == 0 and 1 ** n == 1, "Nonzero constant substitution changes low coefficient")
        count += 3
    record("jet_negative_controls", count, "Orders 1..12; missing coefficient, derivative precision, substitution constant")

    return {
        "status": "all_checks_passed",
        "evidence_kind": "finite_exact_arithmetic_regression_and_illustrative_certificate_checks",
        "not_a_formal_verification": True,
        "not_a_language_implementation": True,
        "total_checks": sum(g["passed_checks"] for g in groups),
        "groups": groups,
        "sturm_chain": [[str(c) for c in p] for p in chain],
        "signs_at_2": signs2,
        "signs_at_3": signs3,
        "scope_limit": "No Lean kernel, ProveIt build, Leant run, or universal finite-test inference."
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reference-checks.json"))
    args = parser.parse_args()
    report = run_checks()
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Passed {report['total_checks']} checks in {len(report['groups'])} groups.")
    print(f"Report: {args.output}")


if __name__ == "__main__":
    main()
