#!/usr/bin/env python3
"""Finite exact-arithmetic sanity checks for the round-2 synthesis.

This is a Python regression aid, not a verified checker, Lean execution, language
implementation, or proof of the universal mathematical claims. Polynomial arrays
list coefficients in ascending degree. Only the Python standard library is used.

Run with bytecode disabled:
    python -B synthesis-math-checks.py --output synthesis-math-results.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from fractions import Fraction as Q
from math import comb
from pathlib import Path

Poly = tuple[Q, ...]


def require(condition: bool, message: str) -> None:
    # Unlike a bare assert, this check also runs if Python uses optimized mode.
    if not condition:
        raise AssertionError(message)


def poly(values) -> Poly:
    result = list(map(Q, values))
    while result and result[-1] == 0:
        result.pop()
    return tuple(result)


def add(a: Poly, b: Poly) -> Poly:
    return poly((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                for i in range(max(len(a), len(b))))


def scale(a: Poly, c: Q) -> Poly:
    return poly(c * x for x in a)


def mul(a: Poly, b: Poly) -> Poly:
    if not a or not b:
        return ()
    result = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return poly(result)


def derivative(a: Poly) -> Poly:
    return poly(i * a[i] for i in range(1, len(a)))


def power(a: Poly, n: int) -> Poly:
    require(n >= 0, "Nonnegative polynomial exponent required")
    result = poly([1])
    for _ in range(n):
        result = mul(result, a)
    return result


def below(a: Poly, n: int) -> Poly:
    require(n >= 0, "Nonnegative precision required")
    return poly(a[:n])


def text(a: Poly) -> list[str]:
    return list(map(str, a))


def run_checks() -> list[dict]:
    groups = []

    # Inclusive natural intervals can be empty. The displayed telescoping RHS
    # needs a range condition; a <= b is sufficient, not logically necessary.
    g = lambda k: k
    f = lambda k: g(k + 1) - g(k)
    a, b = 3, 1
    lhs = sum(f(k) for k in range(a, b + 1))
    rhs = g(b + 1) - g(a)
    require(lhs == 0 and rhs == -1 and lhs != rhs, "Empty-range counterexample")
    positive_cases = 0
    for a in range(8):
        for b in range(a, 8):
            lhs_good = sum((k + 1) ** 2 - k ** 2 for k in range(a, b + 1))
            require(lhs_good == (b + 1) ** 2 - a ** 2, "Ordered-range telescoping")
            positive_cases += 1
    require(sum(f(k) for k in range(2, 2)) == g(2) - g(2), "Adjacent empty case")
    groups.append({"name": "telescoping_range", "status": "passed",
                   "counterexample": {"a": 3, "b": 1, "sum": 0, "rhs": -1},
                   "ordered_positive_cases": positive_cases,
                   "scope": "Finite checks; a <= b is a sufficient contract, with empty ranges handled separately."})

    # In R = Z/4, F(Y)=2Y, Delta=0, J=2t, N=2. The residual is zero,
    # but the jet differs. The constant derivative 2 is nonzero and not a unit.
    delta, j = [0, 0], [0, 2]
    residual = [(2 * c) % 4 for c in j]
    require(residual == [0, 0], "Residual F(J) vanishes modulo 4")
    require(j[:2] != delta[:2] and j[0] == delta[0], "Residual does not identify jet")
    require(2 % 4 != 0 and all((2 * r) % 4 != 1 for r in range(4)),
            "Derivative constant is nonzero but not a unit")
    groups.append({"name": "nonunit_residual_z4", "status": "passed",
                   "ring": "Z/4", "F": "2Y", "Delta": delta, "J": j, "N": 2,
                   "residual": residual, "derivative_constant": 2,
                   "scope": "Concrete counterexample to replacing unit derivative by nonzero derivative."})

    # F=t^N and G=0 agree below N, but differentiation loses one order over Q.
    for n in range(1, 13):
        fpoly = poly([0] * n + [1])
        df = derivative(fpoly)
        require(below(fpoly, n) == (), "Input precision")
        require(below(df, n - 1) == (), "Valid derivative precision")
        require(below(df, n) != (), "Same derivative precision must fail")
        require(df[n - 1] == n, "Omitted derivative coefficient")
    groups.append({"name": "differentiation_precision", "status": "passed",
                   "orders": [1, 12], "input": "t^N versus 0 over Q",
                   "scope": "12 concrete counterexamples; not a formal proof of the general precision rule."})

    # x belongs to (2x) in Q[x] with multiplier 1/2. It does not in Z[x]:
    # every coefficient of (2x)q is even, while the x coefficient of x is odd.
    # Reduction modulo 2 is the paper obstruction; this code checks its finite
    # polynomial data and the two residue classes, not all integer polynomials.
    generator, target, rational_multiplier = poly([0, 2]), poly([0, 1]), poly([Q(1, 2)])
    require(mul(generator, rational_multiplier) == target, "Rational ideal membership witness")
    require([int(c) % 2 for c in generator] == [0, 0], "Generator maps to zero mod 2")
    require([int(c) % 2 for c in target] == [0, 1], "Target does not map to zero mod 2")
    require(all((2 * r) % 2 == 0 for r in range(2)), "Coefficient parity obstruction")
    groups.append({"name": "ideal_membership_reflection", "status": "passed",
                   "generator_Zx": text(generator), "target_Zx": text(target),
                   "multiplier_Qx": text(rational_multiplier),
                   "obstruction": "Every coefficient of (2x)q in Z[x] is even; the target x has coefficient 1.",
                   "scope": "Exact witness and modular data; the coefficient argument is supplied as mathematics, not machine formalization."})

    # Locus: J + 4J^2 = 4t/9 modulo t^6. Compare recurrence, listed coefficients,
    # Catalan expression and direct residual, so the residual check does not only
    # re-run the recurrence used as a producer.
    expected = [Q(4, 9), -Q(64, 81), Q(2048, 729), -Q(81920, 6561), Q(3670016, 59049)]
    coefficients = [Q(0)]
    for n in range(1, 6):
        coefficients.append(Q(4, 9) if n == 1 else
                            -4 * sum(coefficients[i] * coefficients[n - i] for i in range(1, n)))
    require(coefficients[1:] == expected, "Listed Locus coefficients")
    for n in range(1, 6):
        catalan = Q(comb(2 * (n - 1), n - 1), n)
        require(expected[n - 1] == (-1) ** (n - 1) * Q(4 ** (2 * n - 1), 9 ** n) * catalan,
                "Catalan coefficient cross-check")
    jet = poly([0] + expected)
    residual_q = add(add(jet, scale(mul(jet, jet), Q(4))), poly([0, -Q(4, 9)]))
    require(below(residual_q, 6) == (), "Locus residual below degree six")
    require(below(residual_q, 7) != (), "Finite jet is not the exact quadratic root")
    mutant = add(jet, poly([0, 1]))
    mutant_residual = add(add(mutant, scale(mul(mutant, mutant), Q(4))), poly([0, -Q(4, 9)]))
    require(below(mutant_residual, 6) != (), "Corrupted Locus coefficient")
    groups.append({"name": "locus_coefficients", "status": "passed",
                   "coefficients_degrees_1_to_5": list(map(str, expected)),
                   "precision": 6, "first_nonzero_residual_degree": 6,
                   "first_nonzero_residual_coefficient": str(residual_q[6]),
                   "scope": "Five coefficients and their exact residual; no universal existence/uniqueness or analytic claim."})

    # Synthesis uses index 0. These P_n are Prism's P_(n+1), not its P_n.
    # P_(n+1) = (1+w) P_n' - ((n+1)w + 3n+2) P_n.
    ps = [poly([1])]
    for n in range(3):
        next_p = add(mul(poly([1, 1]), derivative(ps[n])),
                     scale(mul(poly([3 * n + 2, n + 1]), ps[n]), Q(-1)))
        ps.append(next_p)
    listed = [poly([1]), poly([-2, -1]), poly([9, 8, 2]), poly([-64, -79, -36, -6])]
    require(ps == listed, "Lambert P0 through P3")
    # Independent quotient-rule polynomial identity, using m=n+1 in Prism's
    # formula. Analytic differentiation/exponential laws and w != -1 are outside
    # this exact-polynomial check and must be supplied by the theorem contract.
    for n in range(3):
        m = n + 1
        denom = power(poly([1, 1]), 2 * m - 1)
        numerator = add(add(mul(derivative(ps[n]), denom),
                            scale(mul(ps[n], derivative(denom)), Q(-1))),
                        scale(mul(ps[n], denom), Q(-m)))
        left = mul(numerator, power(poly([1, 1]), 2 * m + 1))
        right = mul(ps[n + 1], mul(mul(denom, denom), poly([1, 1])))
        require(left == right, "Lambert cross-multiplied quotient identity")
    groups.append({"name": "lambert_shifted_index", "status": "passed",
                   "polynomials_P0_to_P3": [text(p) for p in ps],
                   "index_relation": "Synthesis P_n equals Prism's P_(n+1)",
                   "cross_multiplied_steps": 3,
                   "scope": "Finite exact polynomial identities only; not analytic derivative existence or a universal-index proof."})
    return groups


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("synthesis-math-results.json"))
    args = parser.parse_args()
    groups = run_checks()
    result = {"status": "all_finite_sanity_checks_passed", "groups": groups,
              "group_count": len(groups), "python_version": platform.python_version(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "scope": "Finite exact arithmetic and concrete counterexamples only. No Lean, Leant, compiler, verified checker, or usability claim."}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
