"""A small evidence-boundary model accompanying the Reason design article.

This is NOT Lean, a dependent type theory, or a security boundary. It checks
simply typed lambda terms with products. Atomic types have no built-in
inhabitants. Candidate generation is deliberately separate from checking.
Python certificate constructors are public: replay always rechecks evidence.

Run the tests with:
    python -m unittest discover -s supplement -p 'test_*.py' -v
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, TypeAlias


class CheckError(ValueError):
    """An expression or request fails the model's typing/identity rules."""


class ResourceLimit(RuntimeError):
    """Checking was not completed within its operation budget."""


@dataclass(frozen=True)
class Atom:
    name: str


@dataclass(frozen=True)
class Arrow:
    domain: Type
    codomain: Type


@dataclass(frozen=True)
class Product:
    left: Type
    right: Type


Type: TypeAlias = Atom | Arrow | Product


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Lam:
    name: str
    annotation: Type
    body: Term


@dataclass(frozen=True)
class App:
    function: Term
    argument: Term


@dataclass(frozen=True)
class Pair:
    left: Term
    right: Term


@dataclass(frozen=True)
class Fst:
    pair: Term


@dataclass(frozen=True)
class Snd:
    pair: Term


Term: TypeAlias = Var | Lam | App | Pair | Fst | Snd
Context: TypeAlias = tuple[tuple[str, Type], ...]


@dataclass
class _Fuel:
    remaining: int

    def tick(self) -> None:
        if self.remaining <= 0:
            raise ResourceLimit("checker operation budget exhausted")
        self.remaining -= 1


def _natural(value: int, name: str) -> None:
    if type(value) is not int or value < 0:
        raise CheckError(f"{name} must be a nonnegative integer")


def _name(value: str) -> None:
    if type(value) is not str or not value:
        raise CheckError("names must be nonempty strings")


def _validate_type(ty: Type, fuel: _Fuel) -> None:
    fuel.tick()
    if type(ty) is Atom:
        _name(ty.name)
    elif type(ty) is Arrow:
        _validate_type(ty.domain, fuel)
        _validate_type(ty.codomain, fuel)
    elif type(ty) is Product:
        _validate_type(ty.left, fuel)
        _validate_type(ty.right, fuel)
    else:
        raise CheckError("unknown type constructor")


def _validate_context(context: Context, fuel: _Fuel) -> None:
    if type(context) is not tuple:
        raise CheckError("a context must be an ordered immutable tuple")
    names: set[str] = set()
    for binding in context:
        if type(binding) is not tuple or len(binding) != 2:
            raise CheckError("malformed context binding")
        name, ty = binding
        _name(name)
        if name in names:
            raise CheckError("duplicate name in external context")
        names.add(name)
        _validate_type(ty, fuel)


def _infer(term: Term, context: Context, fuel: _Fuel) -> Type:
    fuel.tick()
    if type(term) is Var:
        _name(term.name)
        # Reverse lookup implements ordinary lexical binder shadowing.
        for name, ty in reversed(context):
            if name == term.name:
                return ty
        raise CheckError(f"unbound variable: {term.name}")
    if type(term) is Lam:
        _name(term.name)
        _validate_type(term.annotation, fuel)
        body_ty = _infer(term.body,
                         context + ((term.name, term.annotation),), fuel)
        return Arrow(term.annotation, body_ty)
    if type(term) is App:
        function_ty = _infer(term.function, context, fuel)
        if type(function_ty) is not Arrow:
            raise CheckError("application of a nonfunction")
        argument_ty = _infer(term.argument, context, fuel)
        if argument_ty != function_ty.domain:
            raise CheckError("application argument has the wrong type")
        return function_ty.codomain
    if type(term) is Pair:
        return Product(_infer(term.left, context, fuel),
                       _infer(term.right, context, fuel))
    if type(term) in (Fst, Snd):
        pair_ty = _infer(term.pair, context, fuel)
        if type(pair_ty) is not Product:
            raise CheckError("projection from a nonproduct")
        return pair_ty.left if type(term) is Fst else pair_ty.right
    raise CheckError("unknown term constructor")


def check(term: Term, target: Type, context: Context = (),
          *, operation_limit: int = 10_000) -> None:
    """Check a term at an EXACT target. No proof search or target inference.

    ResourceLimit does not mean the requested proposition is false.
    The host recursion limit is also conservatively treated as exhaustion.
    """
    _natural(operation_limit, "operation_limit")
    fuel = _Fuel(operation_limit)
    try:
        _validate_type(target, fuel)
        _validate_context(context, fuel)
        inferred = _infer(term, context, fuel)
        if inferred != target:
            raise CheckError("candidate does not prove the frozen target")
    except RecursionError as exc:
        raise ResourceLimit("host recursion limit reached") from exc


@dataclass(frozen=True)
class Query:
    # In this model the generation is an opaque origin label, not an actual
    # Lean environment digest. Exact equality is intentional and conservative.
    generation: str
    context: Context
    target: Type


@dataclass(frozen=True)
class Certificate:
    origin: Query
    term: Term


def certify(query: Query, term: Term) -> Certificate:
    _name(query.generation)
    check(term, query.target, query.context)
    return Certificate(query, term)


def replay(certificate: Certificate, expected: Query) -> None:
    """Never promote a stored wrapper or matching printed text to evidence."""
    if certificate.origin != expected:
        raise CheckError("certificate origin differs from the current query")
    _name(expected.generation)
    check(certificate.term, expected.target, expected.context)


class Status(Enum):
    CHECKED = "checked_proof"
    BUDGET_EXHAUSTED = "candidate_budget_exhausted"
    POOL_ENDED = "candidate_pool_ended_without_proof"
    # No result here asserts mathematical negation.


@dataclass(frozen=True)
class SearchResult:
    status: Status
    inspected: int
    certificate: Certificate | None = None
    checker_exhaustions: int = 0


def select_candidate(query: Query, candidates: Iterable[Term],
                     limit: int) -> SearchResult:
    """Examine at most `limit` candidates; successes are independently checked.

    The candidate iterable is ordinary trusted Python caller code, not a
    sandboxed interface. A limit of zero does not even obtain its iterator.
    """
    _natural(limit, "candidate limit")
    if limit == 0:
        return SearchResult(Status.BUDGET_EXHAUSTED, 0)
    iterator = iter(candidates)
    exhausted = 0
    for inspected in range(1, limit + 1):
        try:
            candidate = next(iterator)
        except StopIteration:
            return SearchResult(Status.POOL_ENDED, inspected - 1,
                                checker_exhaustions=exhausted)
        try:
            certificate = certify(query, candidate)
        except CheckError:
            continue
        except ResourceLimit:
            exhausted += 1
            continue
        return SearchResult(Status.CHECKED, inspected, certificate, exhausted)
    return SearchResult(Status.BUDGET_EXHAUSTED, limit,
                        checker_exhaustions=exhausted)


@dataclass(frozen=True)
class Claim:
    name: str
    target: Type
    term: Term


def assemble_plan(query: Query, claims: tuple[Claim, ...],
                  conclusion: Term) -> Certificate:
    """Check sequential claims before adding their names to the context.

    Compile the sequence to nested lambda applications (typed `let`s).
    Checking the assembled term under the original context verifies that
    temporary claim hypotheses have actually been discharged.
    """
    context = query.context
    used = {name for name, _ in context}
    for claim in claims:
        _name(claim.name)
        if claim.name in used:
            raise CheckError("claim name already exists in this scope")
        check(claim.term, claim.target, context)
        context += ((claim.name, claim.target),)
        used.add(claim.name)
    check(conclusion, query.target, context)
    assembled = conclusion
    for claim in reversed(claims):
        assembled = App(Lam(claim.name, claim.target, assembled), claim.term)
    return certify(query, assembled)
