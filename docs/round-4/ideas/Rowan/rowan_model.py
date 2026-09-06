#!/usr/bin/env python3
"""Rowan's executable reference model, not a Lean elaborator or kernel.

The symbolic engine checks derivability in a finite, explicitly supplied Horn
registry. Registry rules are assumptions of that model, not certified Lean
lemmas. The affine checker uses exact Python integers. Its source-level semantic
and image-adequacy theorems are written in Rowan.tex, not mechanized here.
Python 3.11+, standard library only. Run `python rowan_model.py` for a demo.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from itertools import product
from typing import Iterable, Mapping, Sequence
import json
import re


@dataclass(frozen=True, order=True)
class Term:
    name: str
    sort: str
    meaning: str = "standard"
    epoch: str = "demo"


@dataclass(frozen=True, order=True)
class Atom:
    predicate: str
    arguments: tuple[Term, ...]

    def text(self) -> str:
        return f"{self.predicate}({','.join(t.name for t in self.arguments)})"


@dataclass(frozen=True)
class Pattern:
    predicate: str
    variables: tuple[str, ...]


@dataclass(frozen=True)
class Schema:
    name: str
    variables: tuple[tuple[str, str], ...]
    premises: tuple[Pattern, ...]
    conclusion: Pattern


@dataclass(frozen=True)
class GroundRule:
    name: str
    premises: tuple[Atom, ...]
    conclusion: Atom


@dataclass(frozen=True)
class Assumption:
    name: str
    proposition: Atom
    scope: tuple[str, ...] = ()


@dataclass(frozen=True)
class Context:
    epoch: str
    terms: tuple[Term, ...]
    assumptions: tuple[Assumption, ...]
    scope: tuple[str, ...] = ()

    def visible(self, a: Assumption) -> bool:
        return (self.scope[:len(a.scope)] == a.scope
                and all(t.epoch == self.epoch and t in self.terms
                        for t in a.proposition.arguments))


@dataclass(frozen=True)
class Derivation:
    proposition: Atom
    rule: GroundRule | None = None
    premises: tuple[Derivation, ...] = ()
    assumption: Assumption | None = None

    def support(self) -> frozenset[str]:
        if self.assumption is not None:
            return frozenset((self.assumption.name,))
        return frozenset().union(*(p.support() for p in self.premises))


@dataclass(frozen=True)
class Request:
    context: Context
    target: Atom
    allowed_support: frozenset[str] | None = None
    allowed_rules: frozenset[str] | None = None


@dataclass
class Outcome:
    status: str
    proof: Derivation | None
    frontier: tuple[Atom, ...]
    metrics: dict[str, int]


def validate_schema(s: Schema, signatures: Mapping[str, tuple[str, ...]]) -> None:
    variables = dict(s.variables)
    if len(variables) != len(s.variables):
        raise ValueError("Duplicate schema variable")
    for p in (*s.premises, s.conclusion):
        if p.predicate not in signatures:
            raise ValueError("Unknown predicate")
        try:
            actual = tuple(variables[x] for x in p.variables)
        except KeyError as exc:
            raise ValueError("Unbound schema variable") from exc
        if actual != signatures[p.predicate]:
            raise ValueError("Ill-sorted rule")


def ground(schemas: Sequence[Schema], terms: Sequence[Term],
           signatures: Mapping[str, tuple[str, ...]],
           cap: int = 100_000) -> tuple[tuple[GroundRule, ...], int]:
    """Enumerate all sorted assignments. No rule creates a new term.

    The cap counts assignments, including duplicate ground instances. A budget
    exception means unsupported at this budget, never falsity of a goal.
    """
    if cap < 0:
        raise ValueError("Negative grounding cap")
    rules: list[GroundRule] = []
    seen: set[GroundRule] = set()
    count = 0
    if len({s.name for s in schemas}) != len(schemas):
        raise ValueError("Schema names must be unique")
    for s in schemas:
        validate_schema(s, signatures)
        pools = [tuple(t for t in terms if t.sort == ty) for _, ty in s.variables]
        for values in product(*pools):
            count += 1
            if count > cap:
                raise ValueError("Grounding budget exhausted")
            env = dict(zip((v for v, _ in s.variables), values, strict=True))
            def inst(p: Pattern) -> Atom:
                return Atom(p.predicate, tuple(env[v] for v in p.variables))
            r = GroundRule(s.name, tuple(inst(p) for p in s.premises), inst(s.conclusion))
            if r not in seen:
                rules.append(r)
                seen.add(r)
    return tuple(rules), count


def check_derivation(request: Request, proof: Derivation,
                     registry: Sequence[GroundRule]) -> bool:
    """Validate the original target, all leaves, and each registry application.

    This checks the *symbolic* derivation, not the truth of registry axioms.
    Metadata such as a claimed support set is never accepted as authority.
    """
    allowed = set(registry)
    active: set[int] = set()
    done: set[int] = set()
    def check(d: Derivation) -> bool:
        if id(d) in active:
            return False
        if id(d) in done:
            return True
        if any(t.epoch != request.context.epoch or t not in request.context.terms
               for t in d.proposition.arguments):
            return False
        active.add(id(d))
        if d.assumption is not None:
            a = d.assumption
            ok = (d.rule is None and not d.premises
                  and a in request.context.assumptions
                  and request.context.visible(a)
                  and d.proposition == a.proposition
                  and (request.allowed_support is None or a.name in request.allowed_support))
        else:
            r = d.rule
            ok = (r is not None and r in allowed
                  and (request.allowed_rules is None or r.name in request.allowed_rules)
                  and r.conclusion == d.proposition
                  and tuple(p.proposition for p in d.premises) == r.premises
                  and all(check(p) for p in d.premises))
        active.remove(id(d))
        if ok:
            done.add(id(d))
        return ok
    return proof.proposition == request.target and check(proof)


def solve(request: Request, registry: Sequence[GroundRule]) -> Outcome:
    """Backward-relevant cone, followed by finite forward closure.

    All derivations are rebuilt for this request. There is no cross-snapshot
    cache and no transport by pretty-printed names.
    """
    ctx = request.context
    if any(t.epoch != ctx.epoch or t not in ctx.terms for t in request.target.arguments):
        raise ValueError("Target is not well-scoped in this snapshot")
    rules = [r for r in registry
             if (request.allowed_rules is None or r.name in request.allowed_rules)
             and all(t.epoch == ctx.epoch and t in ctx.terms
                     for a in (*r.premises, r.conclusion) for t in a.arguments)]
    by_conclusion: dict[Atom, list[GroundRule]] = defaultdict(list)
    for r in rules:
        by_conclusion[r.conclusion].append(r)
    relevant: set[Atom] = {request.target}
    todo = [request.target]
    retained: set[GroundRule] = set()
    while todo:
        a = todo.pop()
        for r in by_conclusion[a]:
            retained.add(r)
            for p in r.premises:
                if p not in relevant:
                    relevant.add(p)
                    todo.append(p)
    ordered = [r for r in rules if r in retained]
    known: dict[Atom, Derivation] = {}
    for a in ctx.assumptions:
        if (ctx.visible(a) and a.proposition in relevant
                and (request.allowed_support is None or a.name in request.allowed_support)):
            known.setdefault(a.proposition, Derivation(a.proposition, assumption=a))
    queue = deque(known)
    remaining = [len(set(r.premises)) for r in ordered]
    waiting: dict[Atom, list[int]] = defaultdict(list)
    for i, r in enumerate(ordered):
        for p in set(r.premises):
            waiting[p].append(i)
    firings = 0
    def fire(i: int) -> None:
        nonlocal firings
        r = ordered[i]
        firings += 1
        if r.conclusion not in known:
            known[r.conclusion] = Derivation(r.conclusion, r,
                                             tuple(known[p] for p in r.premises))
            queue.append(r.conclusion)
    for i, n in enumerate(remaining):
        if n == 0:
            fire(i)
    while queue:
        p = queue.popleft()
        for i in waiting[p]:
            remaining[i] -= 1
            if remaining[i] == 0:
                fire(i)
    proof = known.get(request.target)
    if proof is not None and not check_derivation(request, proof, registry):
        raise AssertionError("Internal symbolic derivation failed replay")
    # A valid, nonminimal explanatory frontier. Cycles without a leaf retain
    # the original target, rather than being treated as false or assumed true.
    leaves = sorted(a for a in relevant if a not in known and not by_conclusion[a])
    frontier = () if proof else tuple(leaves or [request.target])
    return Outcome("derived" if proof else "open", proof, frontier,
                   {"ground_rules": len(registry), "relevant_rules": len(ordered),
                    "relevant_atoms": len(relevant), "known_atoms": len(known),
                    "rule_firings": firings})


FREY_SIGNATURES = {
    "Even": ("Int",), "ResidueThree": ("Int",),
    "AtLeastFour": ("Nat",), "Odd": ("Nat",),
    "Div16Pow": ("Int", "Nat"),
    "ExactA4": ("Int", "Int", "Nat"),
    "ExactA2": ("Int", "Int", "Nat"),
}
P = Pattern
FREY_SCHEMAS = (
    Schema("even-power", (("b", "Int"), ("p", "Nat")),
           (P("Even", ("b",)), P("AtLeastFour", ("p",))),
           P("Div16Pow", ("b", "p"))),
    Schema("multiply-exact", (("a", "Int"), ("b", "Int"), ("p", "Nat")),
           (P("Div16Pow", ("b", "p")),), P("ExactA4", ("a", "b", "p"))),
    Schema("residue-balance", (("a", "Int"), ("b", "Int"), ("p", "Nat")),
           (P("Even", ("b",)), P("AtLeastFour", ("p",)),
            P("Odd", ("p",)), P("ResidueThree", ("a",))),
           P("ExactA2", ("a", "b", "p"))),
)


def run_script(text: str, signatures: Mapping[str, tuple[str, ...]] = FREY_SIGNATURES,
               schemas: Sequence[Schema] = FREY_SCHEMAS) -> dict:
    """A tiny parsed object/assume/derive language for the finite model.

    Predicate arguments must be already declared object names. This is not a
    parser for the richer illustrative Rowan language in the article.
    """
    terms: dict[str, Term] = {}
    facts: list[Assumption] = []
    names: set[str] = set()
    answers: list[dict] = []
    def atom(s: str) -> Atom:
        m = re.fullmatch(r"([A-Za-z][\w]*)\(([^()]*)\)", s)
        if m is None:
            raise ValueError("Expected Predicate(object,...) syntax")
        pred, args = m.groups()
        try:
            ts = tuple(terms[x.strip()] for x in args.split(",") if x.strip())
            expected = signatures[pred]
        except KeyError as exc:
            raise ValueError("Unknown object or predicate") from exc
        if tuple(t.sort for t in ts) != expected:
            raise ValueError("Ill-sorted predicate application")
        return Atom(pred, ts)
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.split("--", 1)[0].strip()
        if not line:
            continue
        m = re.fullmatch(r"(object|assume|derive)\s+(\w+)\s*:\s*(.+)", line)
        if m is None:
            raise ValueError(f"Unsupported syntax on line {line_no}")
        kind, name, content = m.groups()
        if name in names:
            raise ValueError("Duplicate declaration name")
        names.add(name)
        if kind == "object":
            if content not in {t for sig in signatures.values() for t in sig}:
                raise ValueError("Unknown object sort")
            terms[name] = Term(name, content)
        elif kind == "assume":
            facts.append(Assumption(name, atom(content)))
        else:
            target = atom(content)
            ctx = Context("demo", tuple(terms.values()), tuple(facts))
            registry, assignments = ground(schemas, ctx.terms, signatures)
            result = solve(Request(ctx, target), registry)
            answers.append({"name": name, "target": target.text(),
                            "status": result.status,
                            "support": sorted(result.proof.support()) if result.proof else [],
                            "frontier": [a.text() for a in result.frontier],
                            "metrics": result.metrics | {"ground_assignments": assignments}})
    return {"kind": "symbolic Horn model; no Lean checking", "answers": answers}


@dataclass(frozen=True)
class Affine:
    constant: int
    coefficients: tuple[int, ...]

    def eval(self, x: Sequence[int]) -> int:
        if len(x) != len(self.coefficients):
            raise ValueError("Affine arity mismatch")
        return self.constant + sum(a*b for a, b in zip(self.coefficients, x, strict=True))

    def __add__(self, other: Affine) -> Affine:
        if len(self.coefficients) != len(other.coefficients):
            raise ValueError("Affine arity mismatch")
        return Affine(self.constant + other.constant,
                      tuple(a+b for a, b in zip(self.coefficients, other.coefficients, strict=True)))

    def __sub__(self, other: Affine) -> Affine:
        return self + Affine(-other.constant, tuple(-a for a in other.coefficients))


@dataclass(frozen=True)
class Component:
    base: tuple[int, ...]
    generators: tuple[tuple[int, ...], ...] = ()

    def __post_init__(self) -> None:
        if any(len(v) != len(self.base) for v in self.generators):
            raise ValueError("Generator dimension mismatch")
        if any(type(x) is not int or x < 0
               for v in (self.base, *self.generators) for x in v):
            raise ValueError("Image data must be natural numbers")

    def point(self, z: Sequence[int]) -> tuple[int, ...]:
        if len(z) != len(self.generators) or any(type(x) is not int or x < 0 for x in z):
            raise ValueError("Invalid natural generator coordinates")
        return tuple(b + sum(v[i]*c for v, c in zip(self.generators, z, strict=True))
                     for i, b in enumerate(self.base))


@dataclass(frozen=True)
class Image:
    dimension: int
    components: tuple[Component, ...]

    def __post_init__(self) -> None:
        if self.dimension < 0 or any(len(c.base) != self.dimension for c in self.components):
            raise ValueError("Image dimension mismatch")


@dataclass(frozen=True)
class AffineDecision:
    equal_on_image: bool
    witness: tuple[int, ...] | None
    component: int | None
    coordinates: tuple[int, ...] | None
    checks: int


def decide_affine(left: Affine, right: Affine, image: Image) -> AffineDecision:
    """Exact equality on a supplied semilinear image, with a basis witness.

    Image equality/coverage and a source denotation bridge are not established
    by this function. It must not on its own authorize a source refutation.
    """
    if len(left.coefficients) != image.dimension or len(right.coefficients) != image.dimension:
        raise ValueError("Affine/image dimension mismatch")
    d = left - right
    checks = 0
    for j, c in enumerate(image.components):
        checks += 1
        z = (0,) * len(c.generators)
        if d.eval(c.base) != 0:
            return AffineDecision(False, c.base, j, z, checks)
        for k, v in enumerate(c.generators):
            checks += 1
            slope = sum(a*b for a, b in zip(d.coefficients, v, strict=True))
            if slope:
                z = tuple(1 if i == k else 0 for i in range(len(c.generators)))
                return AffineDecision(False, c.point(z), j, z, checks)
    return AffineDecision(True, None, None, None, checks)


@dataclass(frozen=True)
class ListExpr:
    kind: str
    children: tuple[ListExpr, ...] = ()
    value: int = 0

    def __post_init__(self) -> None:
        arities = {"nil": 0, "input": 0, "cons": 1, "reverse": 1,
                   "mapSucc": 1, "append": 2}
        if self.kind not in arities or len(self.children) != arities[self.kind]:
            raise ValueError("Invalid list expression")
        if type(self.value) is not int or self.value < 0:
            raise ValueError("Natural literal or input index required")

    def model(self, ninputs: int) -> Affine:
        if ninputs < 0:
            raise ValueError("Negative input count")
        zero = Affine(0, (0,) * ninputs)
        if self.kind == "nil":
            return zero
        if self.kind == "input":
            if self.value >= ninputs:
                raise ValueError("Input index out of bounds")
            return Affine(0, tuple(int(i == self.value) for i in range(ninputs)))
        first = self.children[0].model(ninputs)
        if self.kind == "cons":
            return Affine(1, zero.coefficients) + first
        if self.kind == "append":
            return first + self.children[1].model(ninputs)
        return first

    def eval(self, env: Sequence[Sequence[int]]) -> tuple[int, ...]:
        if self.kind == "nil":
            return ()
        if self.kind == "input":
            if self.value >= len(env):
                raise ValueError("Input index out of bounds")
            return tuple(env[self.value])
        xs = self.children[0].eval(env)
        if self.kind == "cons":
            return (self.value,) + xs
        if self.kind == "append":
            return xs + self.children[1].eval(env)
        if self.kind == "reverse":
            return xs[::-1]
        return tuple(x + 1 for x in xs)


def exact_quotient(n: int, d: int) -> int:
    if d == 0:
        raise ValueError("Zero denominator")
    q, r = divmod(n, d)
    if r:
        raise ValueError("Division is not exact")
    return q


DEMO = """object a : Int
object b : Int
object p : Nat
assume even_b : Even(b)
assume bound_p : AtLeastFour(p)
derive fourth_coefficient : ExactA4(a,b,p)
derive second_coefficient : ExactA2(a,b,p)
assume odd_p : Odd(p)
assume residue_a : ResidueThree(a)
derive second_coefficient_completed : ExactA2(a,b,p)
"""


def demo() -> dict:
    diagonal = Image(2, (Component((0, 0), ((1, 1),)),))
    full = Image(2, (Component((0, 0), ((1, 0), (0, 1))),))
    f, g = Affine(0, (1, 0)), Affine(0, (0, 1))
    on_diagonal = decide_affine(f, g, diagonal)
    on_full = decide_affine(f, g, full)
    return {"symbolic": run_script(DEMO),
            "correlated_lengths": {"diagonal_equal": on_diagonal.equal_on_image,
                                   "independent_equal": on_full.equal_on_image,
                                   "independent_witness": on_full.witness},
            "frey_fixture": {"a": 3, "b": 2, "p": 5,
                             "a2": exact_quotient(2**5-1-3**5, 4),
                             "a4": exact_quotient(-3**5*2**5, 16)}}


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
