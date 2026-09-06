#!/usr/bin/env python3
"""Executable specification for the Trellis article (Python 3.10+).

This is NOT a Lean implementation or kernel proof. It checks exact rational
certificates for affine inequalities and tests request binding / a restricted
scope-weakening rule. Soundness of the mathematical certificate format is
proved in the article; this Python implementation has not been formally proved.
Only Python's standard library is required. Run with --output results.json.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction
from hashlib import sha256
import argparse
import json
from pathlib import Path
from typing import Union

Rational = Union[int, Fraction]

def rat(x: Rational) -> Fraction:
    if isinstance(x, bool) or not isinstance(x, (int, Fraction)):
        raise TypeError("coefficients must be exact integers or Fractions")
    return Fraction(x)

@dataclass(frozen=True)
class Expr:
    op: str
    data: object
    children: tuple[Expr, ...] = ()

def const(q: Rational) -> Expr:
    return Expr("const", rat(q))

def atom(handle: str) -> Expr:
    return Expr("atom", handle)

def add(a: Expr, b: Expr) -> Expr:
    return Expr("add", None, (a, b))

def scale(q: Rational, a: Expr) -> Expr:
    return Expr("scale", rat(q), (a,))

def sub(a: Expr, b: Expr) -> Expr:
    return add(a, scale(-1, b))

def encode(e: Expr) -> object:
    payload = str(e.data) if isinstance(e.data, Fraction) else e.data
    return [e.op, payload, [encode(c) for c in e.children]]

def reify(e: Expr, atoms: tuple[str, ...], depth: int = 0) -> tuple[Fraction, ...]:
    """Coefficients are [constant, coefficient of atoms[0], ...]."""
    if depth > 128 or len(atoms) > 4096:
        raise ValueError("reference reifier budget exceeded")
    if len(set(atoms)) != len(atoms):
        raise ValueError("duplicate atom handle")
    zero = (Fraction(0),) * (len(atoms) + 1)
    if e.op == "const" and not e.children:
        return (rat(e.data),) + zero[1:]
    if e.op == "atom" and not e.children:
        if e.data not in atoms:
            raise ValueError("unknown atom handle")
        values = list(zero)
        values[atoms.index(e.data) + 1] = Fraction(1)
        return tuple(values)
    if e.op == "add" and len(e.children) == 2:
        a, b = (reify(c, atoms, depth + 1) for c in e.children)
        return tuple(x + y for x, y in zip(a, b, strict=True))
    if e.op == "scale" and len(e.children) == 1:
        return tuple(rat(e.data) * x for x in reify(e.children[0], atoms, depth + 1))
    raise ValueError("not an affine expression")

@dataclass(frozen=True)
class Origin:
    environment: str
    structures: str
    context: tuple[str, ...]
    revision: int
    policy: str = "reference-only"

@dataclass(frozen=True)
class Request:
    origin: Origin
    atoms: tuple[str, ...]
    hypotheses: tuple[Expr, ...]  # Each denotes a quantity assumed >= 0.
    target: Expr                 # Request: target >= 0, NOT target = 0 or > 0.
    kind: str = "affine_nonnegative"

    def digest(self) -> str:
        content = {
            "environment": self.origin.environment,
            "structures": self.origin.structures,
            "context": self.origin.context,
            "revision": self.origin.revision,
            "policy": self.origin.policy,
            "atoms": self.atoms,
            "hypotheses": [encode(e) for e in self.hypotheses],
            "target": encode(self.target),
            "kind": self.kind,
        }
        return sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

@dataclass(frozen=True)
class Certificate:
    request_digest: str
    weights: tuple[Fraction, ...]

@dataclass(frozen=True)
class Verdict:
    accepted: bool
    reason: str

def certify_for(req: Request, weights: tuple[Rational, ...]) -> Certificate:
    """Construct a candidate; no proof authority is conferred here."""
    return Certificate(req.digest(), tuple(rat(q) for q in weights))

def check(req: Request, cert: Certificate) -> Verdict:
    try:
        if req.kind != "affine_nonnegative":
            return Verdict(False, "unsupported guarantee kind")
        if req.digest() != cert.request_digest:
            return Verdict(False, "request origin or specification mismatch")
        if len(cert.weights) != len(req.hypotheses):
            return Verdict(False, "certificate arity mismatch")
        weights = tuple(rat(q) for q in cert.weights)
        if any(q < 0 for q in weights):
            return Verdict(False, "negative multiplier")
        target = reify(req.target, req.atoms)
        rows = [reify(e, req.atoms) for e in req.hypotheses]
        combined = [Fraction(0)] * len(target)
        for w, row in zip(weights, rows, strict=True):
            for j, c in enumerate(row):
                combined[j] += w * c
        if tuple(combined) != target:
            return Verdict(False, "coefficient identity failed")
        return Verdict(True, "exact affine certificate passed reference check")
    except (TypeError, ValueError, RecursionError) as ex:
        return Verdict(False, str(ex))

def weaken_to_child(source: Request, cert: Certificate, dest: Request) -> Verdict:
    """Restricted demonstration, NOT general dependent-context transport.

    Only a scope-prefix extension with all mathematical fields unchanged is
    supported. The certificate is rechecked at the destination, not trusted
    because of a hash or a previous status label.
    """
    if not check(source, cert).accepted:
        return Verdict(False, "source certificate was not accepted")
    a, b = source.origin, dest.origin
    if (a.environment, a.structures, a.revision, a.policy) != (
            b.environment, b.structures, b.revision, b.policy):
        return Verdict(False, "semantic environment changed")
    if b.context[:len(a.context)] != a.context:
        return Verdict(False, "not a child scope")
    if (source.atoms, source.hypotheses, source.target, source.kind) != (
            dest.atoms, dest.hypotheses, dest.target, dest.kind):
        return Verdict(False, "not scope-only weakening")
    return check(dest, Certificate(dest.digest(), cert.weights))

def run_tests() -> dict:
    checks = []
    def record(name: str, actual: Verdict, expected: bool) -> None:
        if actual.accepted != expected:
            raise AssertionError(f"{name}: expected {expected}, got {actual}")
        checks.append({"name": name, "expected_acceptance": expected,
                       "observed_acceptance": actual.accepted, "reason": actual.reason})

    origin = Origin("example-env-v1", "real-standard-v1", ("root",), 1)
    u, a, b = atom("u@t1"), atom("u@t2"), atom("u@t3")
    one, two = const(1), const(2)
    fabius = Request(origin, ("u@t1",), (u, sub(one, u)), sub(two, scale(2, u)))
    good = certify_for(fabius, (0, 2))
    record("Fabius derivative upper bound", check(fabius, good), True)
    nonneg = replace(fabius, target=scale(2, u))
    record("Fabius derivative nonnegativity", check(nonneg, certify_for(nonneg, (2, 0))), True)
    hyp = (a, sub(one, a), b, sub(one, b))
    upper = Request(origin, ("u@t2", "u@t3"), hyp, sub(two, scale(2, sub(a, b))))
    lower = replace(upper, target=add(two, scale(2, sub(a, b))))
    record("Rvachev derivative upper bound", check(upper, certify_for(upper, (0, 2, 2, 0))), True)
    record("Rvachev derivative lower bound", check(lower, certify_for(lower, (2, 0, 0, 2))), True)
    record("corrupted multiplier", check(fabius, certify_for(fabius, (0, 3))), False)
    record("too few multipliers", check(fabius, certify_for(fabius, (2,))), False)
    record("too many multipliers", check(fabius, certify_for(fabius, (0, 2, 0))), False)
    neg = replace(fabius, hypotheses=(u,), target=scale(-1, u))
    record("negative multiplier despite exact identity", check(neg, certify_for(neg, (-1,))), False)
    empty = Request(origin, (), (), const(0))
    record("empty certificate for zero", check(empty, certify_for(empty, ())), True)
    badempty = replace(empty, target=const(1))
    record("positive constant needs a supported certificate", check(badempty, certify_for(badempty, ())), False)
    alien = replace(fabius, origin=replace(origin, environment="different-env"))
    record("changed environment", check(alien, good), False)
    alien = replace(fabius, origin=replace(origin, structures="different-real-structure"))
    record("changed structure selection", check(alien, good), False)
    alien = replace(fabius, origin=replace(origin, revision=2))
    record("stale revision", check(alien, good), False)
    alien = replace(fabius, origin=replace(origin, policy="different-policy"))
    record("changed policy", check(alien, good), False)
    alien = replace(fabius, hypotheses=(u,))
    record("removed hypothesis", check(alien, good), False)
    alien = replace(fabius, target=scale(2, u))
    record("changed target", check(alien, good), False)
    eq = replace(fabius, kind="exact_equality")
    record("inequality cannot answer equality", check(eq, certify_for(eq, (0, 2))), False)
    strict = replace(fabius, kind="strict_positive")
    record("nonstrict cannot answer strict", check(strict, certify_for(strict, (0, 2))), False)
    unknown = replace(fabius, target=atom("unknown"))
    record("unbound atom", check(unknown, certify_for(unknown, (0, 2))), False)
    duplicate = replace(fabius, atoms=("u@t1", "u@t1"))
    record("duplicate atom handles", check(duplicate, certify_for(duplicate, (0, 2))), False)
    distinct = Request(origin, ("u@t1", "u@t2"), (u,), a)
    record("two applications of u are distinct atoms", check(distinct, certify_for(distinct, (1,))), False)
    same = replace(distinct, target=u)
    record("correct atom retained", check(same, certify_for(same, (1,))), True)
    record("forged request digest", check(fabius, replace(good, request_digest="0" * 64)), False)
    nonlinear = replace(fabius, target=Expr("mul", None, (u, u)))
    record("unsupported nonlinear expression", check(nonlinear, certify_for(nonlinear, (0, 2))), False)
    child = replace(fabius, origin=replace(origin, context=("root", "case-a")))
    record("explicit scope weakening to child", weaken_to_child(fabius, good, child), True)
    childcert = certify_for(child, (0, 2))
    sibling = replace(child, origin=replace(origin, context=("root", "case-b")))
    record("sibling scope not a weakening", weaken_to_child(child, childcert, sibling), False)
    record("branch cannot escape to parent", weaken_to_child(child, childcert, fabius), False)
    record("scope weakening cannot hide changed target", weaken_to_child(fabius, good, replace(child, target=u)), False)
    weakened = replace(fabius, hypotheses=fabius.hypotheses + (one,), target=sub(const(3), scale(2, u)))
    record("weaker upper bound with constant premise", check(weakened, certify_for(weakened, (0, 2, 1))), True)
    rational = Request(origin, ("u@t1",), (u,), scale(Fraction(2, 3), u))
    record("exact rational multiplier", check(rational, certify_for(rational, (Fraction(2, 3),))), True)
    floatcert = Certificate(fabius.digest(), (0.0, 2.0))  # deliberately malformed input
    record("floating-point multiplier forbidden", check(fabius, floatcert), False)
    return {"status": "all reference tests passed", "test_count": len(checks),
            "positive_count": sum(c["expected_acceptance"] for c in checks),
            "negative_count": sum(not c["expected_acceptance"] for c in checks),
            "lean_executed": False,
            "scope": "Exact affine certificate and request-binding reference tests, not formal verification or a language evaluation.",
            "tests": checks}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write reproducible test results as JSON")
    args = parser.parse_args()
    results = run_tests()
    text = json.dumps(results, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(f"{results['test_count']} tests passed ({results['positive_count']} positive, {results['negative_count']} negative).")
    print("No Lean compiler or kernel was run.")

if __name__ == "__main__":
    main()
