#!/usr/bin/env python3
"""Heather reference front end: finite, domain-aware list-length contracts.

This program is an executable design model, not a Lean kernel or a verified
compiler. It parses a tiny typed language, constructs a mathematical certificate,
rechecks the certificate, and emits ordinary Lean proof *candidates*. The latter
have NOT been compiled in the environment that produced this archive.

Only the Python standard library is required. No input is evaluated with eval.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import itertools
import json
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Any, Iterable


class HeatherError(ValueError):
    """A source, type, scope, or certificate error (not mathematical negation)."""


@dataclass(frozen=True)
class Expr:
    op: str
    args: tuple[Expr, ...] = ()
    index: int = -1

    def size(self) -> int:
        return 1 + sum(x.size() for x in self.args)


@dataclass(frozen=True)
class Affine:
    constant: int
    coefficients: tuple[int, ...]

    def add(self, other: Affine) -> Affine:
        if len(self.coefficients) != len(other.coefficients):
            raise HeatherError('affine arity mismatch')
        return Affine(self.constant + other.constant,
                      tuple(a+b for a,b in zip(self.coefficients, other.coefficients)))

    def at(self, values: tuple[int, ...]) -> int:
        if len(values) != len(self.coefficients):
            raise HeatherError('valuation arity mismatch')
        return self.constant + sum(a*n for a,n in zip(self.coefficients, values))


@dataclass(frozen=True)
class Request:
    name: str
    domain: str
    variables: tuple[str, ...]
    lhs: Expr
    rhs: Expr

    def digest(self) -> str:
        # Routing identity, not a mathematical proof. Checkers also receive the
        # original Request and reconstruct all mathematical fields from it.
        raw = json.dumps(asdict(self), sort_keys=True, separators=(',', ':')).encode()
        return hashlib.sha256(raw).hexdigest()


def parse_expression(text: str, variables: tuple[str, ...], domain: str) -> Expr:
    try:
        tree = ast.parse(text, mode='eval')
    except (SyntaxError, RecursionError) as exc:
        raise HeatherError('invalid expression syntax') from exc
    seen = 0

    def go(node: ast.AST, depth: int = 0) -> Expr:
        nonlocal seen
        seen += 1
        if depth > 32 or seen > 256:
            raise HeatherError('expression resource bound exceeded')
        if isinstance(node, ast.Name) and node.id in variables:
            return Expr('input', index=variables.index(node.id))
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.keywords:
            raise HeatherError('expected a declared list or nil/one/append/reverse call')
        op = node.func.id
        arities = {'nil': 0, 'one': 0, 'append': 2, 'reverse': 1}
        if op not in arities or len(node.args) != arities[op]:
            raise HeatherError(f'unsupported operation or wrong arity: {op}')
        if domain == 'empty' and op == 'one':
            raise HeatherError('cannot construct an element of Empty')
        return Expr(op, tuple(go(x, depth+1) for x in node.args))

    return go(tree.body)


def parse(source: str) -> Request:
    """Four-line grammar. Domain fixes the admitted type and input guard.

    heather NAME
    domain free|empty|diagonal|even
    inputs xs, ys
    claim length(EXPR) == length(EXPR)
    """
    lines = [s.split('#', 1)[0].strip() for s in source.splitlines()]
    lines = [s for s in lines if s]
    if len(lines) != 4:
        raise HeatherError('expected exactly four non-comment source lines')
    if not lines[0].startswith('heather ') or not lines[1].startswith('domain '):
        raise HeatherError('missing header or domain')
    name, domain = lines[0][8:].strip(), lines[1][7:].strip()
    if not name.isidentifier() or not name.isascii():
        raise HeatherError('name must be an ASCII identifier')
    if domain not in {'free', 'empty', 'diagonal', 'even'}:
        raise HeatherError('unsupported domain, not a refutation')
    if not lines[2].startswith('inputs '):
        raise HeatherError('missing inputs')
    variables = tuple(x.strip() for x in lines[2][7:].split(','))
    if not (1 <= len(variables) <= 8) or len(set(variables)) != len(variables):
        raise HeatherError('need one to eight distinct input names')
    if any(not x.isidentifier() or not x.isascii() or x in {'nil','one','append','reverse'}
           for x in variables):
        raise HeatherError('invalid or reserved input name')
    if domain == 'diagonal' and len(variables) != 2:
        raise HeatherError('diagonal domain requires exactly two inputs')
    if not lines[3].startswith('claim '):
        raise HeatherError('missing claim')
    claim = lines[3][6:]
    # Parse the equality with Python's AST; only two length calls are permitted.
    try:
        node = ast.parse(claim, mode='eval').body
    except (SyntaxError, RecursionError) as exc:
        raise HeatherError('invalid claim') from exc
    if not isinstance(node, ast.Compare) or len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
        raise HeatherError('only one equality claim is supported')
    def unwrap(n: ast.AST) -> str:
        if (not isinstance(n, ast.Call) or not isinstance(n.func, ast.Name)
            or n.func.id != 'length' or len(n.args) != 1 or n.keywords):
            raise HeatherError('both sides must be length expressions')
        return ast.unparse(n.args[0])
    return Request(name, domain, variables,
                   parse_expression(unwrap(node.left), variables, domain),
                   parse_expression(unwrap(node.comparators[0]), variables, domain))


def model(e: Expr, arity: int) -> Affine:
    z = (0,)*arity
    if e.op == 'input':
        if not 0 <= e.index < arity:
            raise HeatherError('invalid input index')
        return Affine(0, tuple(int(i == e.index) for i in range(arity)))
    if e.op == 'nil': return Affine(0, z)
    if e.op == 'one': return Affine(1, z)
    if e.op == 'append': return model(e.args[0], arity).add(model(e.args[1], arity))
    if e.op == 'reverse': return model(e.args[0], arity)
    raise HeatherError('unknown model constructor')


def evaluate(e: Expr, env: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    if e.op == 'input': return env[e.index]
    if e.op == 'nil': return ()
    if e.op == 'one': return (0,)
    if e.op == 'append': return evaluate(e.args[0], env) + evaluate(e.args[1], env)
    if e.op == 'reverse': return evaluate(e.args[0], env)[::-1]
    raise HeatherError('unknown evaluator constructor')


def admissible(domain: str, ns: tuple[int, ...]) -> bool:
    if any(type(n) is not int or n < 0 for n in ns): return False
    if domain == 'free': return True
    if domain == 'empty': return all(n == 0 for n in ns)
    if domain == 'diagonal': return len(ns) == 2 and ns[0] == ns[1]
    if domain == 'even': return all(n % 2 == 0 for n in ns)
    return False


def frame(domain: str, arity: int) -> tuple[tuple[int, ...], ...]:
    """Fixed mathematically justified covers; arbitrary user frames forbidden.

    Free: 0 and standard basis. Empty: only 0. Diagonal: 0,(1,1).
    Even: 0 and twice the standard basis. These determine AFFINE EQUALITY,
    not general predicates, ordering, permutation, or arbitrary programs.
    """
    zero = (0,)*arity
    if domain == 'empty': return (zero,)
    if domain == 'diagonal':
        if arity != 2: raise HeatherError('diagonal arity')
        return (zero, (1,1))
    if domain in {'free', 'even'}:
        step = 2 if domain == 'even' else 1
        return (zero,) + tuple(tuple(step if i == j else 0 for i in range(arity))
                               for j in range(arity))
    raise HeatherError('unsupported observation cover')


def certificate(req: Request) -> dict[str, Any]:
    a, b = model(req.lhs, len(req.variables)), model(req.rhs, len(req.variables))
    points = frame(req.domain, len(req.variables))
    bad = next((n for n in points if a.at(n) != b.at(n)), None)
    return {'schema': 1, 'request': req.digest(), 'lhs': asdict(a), 'rhs': asdict(b),
            'frame': points, 'status': 'model_proved' if bad is None else 'counterexample',
            'witness_lengths': bad,
            'witness_lists': None if bad is None else tuple((0,)*n for n in bad),
            'lean_status': 'not_compiled'}


def canonical(x: Any) -> Any:
    return json.loads(json.dumps(x, sort_keys=True))


def check_certificate(req: Request, cert: dict[str, Any]) -> bool:
    """Recompute the exact model and fixed cover from the original request.

    This checker shares parser/data/model code with the producer. It is NOT an
    independently verified checker; tests and the article's written induction
    are the present evidence for its implementation.
    """
    try:
        if not isinstance(cert, dict): return False
        if type(cert.get('schema')) is not int or cert['schema'] != 1: return False
        if cert.get('request') != req.digest(): return False
        # JSON booleans/floats must not pass as integer coefficients merely
        # because Python's numeric equality equates True, 1, and 1.0.
        for side in ('lhs', 'rhs'):
            f = cert[side]
            if type(f['constant']) is not int: return False
            if any(type(c) is not int for c in f['coefficients']): return False
        if any(type(n) is not int for point in cert['frame'] for n in point): return False
        a, b = model(req.lhs, len(req.variables)), model(req.rhs, len(req.variables))
        points = frame(req.domain, len(req.variables))
        if canonical(cert['lhs']) != canonical(asdict(a)) or canonical(cert['rhs']) != canonical(asdict(b)):
            return False
        if canonical(cert['frame']) != canonical(points): return False
        if cert['lean_status'] != 'not_compiled': return False
        if cert['status'] == 'model_proved':
            return (cert['witness_lengths'] is None and cert['witness_lists'] is None
                    and all(a.at(p) == b.at(p) for p in points))
        if cert['status'] != 'counterexample': return False
        ns = tuple(cert['witness_lengths'])
        env = tuple(tuple(xs) for xs in cert['witness_lists'])
        return (len(ns) == len(req.variables) == len(env)
                and admissible(req.domain, ns)
                and tuple(map(len, env)) == ns
                and all(type(x) is int and x >= 0 for xs in env for x in xs)
                and (req.domain != 'empty' or all(not xs for xs in env))
                and len(evaluate(req.lhs, env)) != len(evaluate(req.rhs, env)))
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def lean_expression(e: Expr, variables: tuple[str, ...], element_type: str = 'Nat') -> str:
    if e.op == 'input': return variables[e.index]
    if e.op == 'nil': return f'([] : List {element_type})'
    if e.op == 'one': return '([0] : List Nat)'
    if e.op == 'append': return f'({lean_expression(e.args[0], variables, element_type)} ++ {lean_expression(e.args[1], variables, element_type)})'
    if e.op == 'reverse': return f'({lean_expression(e.args[0], variables, element_type)}).reverse'
    raise HeatherError('cannot render unknown constructor')


def lean_export(req: Request, cert: dict[str, Any]) -> str:
    if not check_certificate(req, cert): raise HeatherError('certificate refused')
    if cert['status'] != 'model_proved': raise HeatherError('no positive theorem to export')
    typ = 'Empty' if req.domain == 'empty' else 'Nat'
    # Internal names prevent source identifiers from shadowing types or guards.
    variables = tuple(f'v{i}' for i in range(len(req.variables)))
    names = ' '.join(variables)
    left, right = (lean_expression(e, variables, typ) for e in (req.lhs, req.rhs))
    guard = ''
    if req.domain == 'diagonal':
        guard = f' (h : {variables[0]}.length = {variables[1]}.length)'
    elif req.domain == 'even':
        guard = ''.join(f' (h_{x} : 2 ∣ {x}.length)' for x in variables)
    proof = ''
    if req.domain == 'empty':
        for x in variables:
            proof += (f'  have hx_{x} : {x} = [] := by\n'
                      f'    cases {x} with\n'
                      '    | nil => rfl\n'
                      '    | cons a _ => exact nomatch a\n')
        proof += '  subst_vars\n  simp\n'
    else:
        proof = '  simp only [List.length_append, List.length_reverse, List.length_nil, List.length_cons]\n  omega\n'
    return ('-- GENERATED PROOF CANDIDATE; NOT COMPILED IN THIS DELIVERY.\n'
            '-- Python acceptance does not establish Lean acceptance.\n'
            'import Mathlib\nset_option autoImplicit false\n\n'
            f'-- Source inputs: {dict(zip(req.variables, variables))}\n'
            f'theorem heather_{req.name} ({names} : List {typ}){guard} :\n'
            f'    ({left}).length = ({right}).length := by\n{proof}')


# A second, deliberately tiny use-site experiment. Facts have exact object
# identities and elaboration epochs. The only two inference rules are ordinary
# valid Nat implications; cycles do not introduce facts without a seed.
@dataclass(frozen=True)
class Fact:
    predicate: str
    arguments: tuple[str, ...]


@dataclass(frozen=True)
class Evidence:
    epoch: str
    fact: Fact
    rule: str
    parents: tuple[int, ...]
    lean: str


class Context:
    def __init__(self, epoch: str, variables: Iterable[str], structure: str = 'Nat'):
        self.epoch = epoch
        self.variables = tuple(variables)
        self.structure = structure
        if structure != 'Nat': raise HeatherError('only fixed Nat structure is supported')
        self.evidence: list[Evidence] = []
        self.assumptions: dict[str, Fact] = {}
        self.firings = 0

    def assume(self, name: str, fact: Fact) -> None:
        arity = {'positive': 1, 'nonzero': 1, 'divides': 2}.get(fact.predicate)
        if arity != len(fact.arguments) or any(a not in self.variables for a in fact.arguments):
            raise HeatherError('ill-typed fact or unknown object')
        if name in self.assumptions: raise HeatherError('duplicate assumption')
        self.assumptions[name] = fact
        self.evidence.append(Evidence(self.epoch, fact, 'assume:'+name, (), name))

    def close(self) -> None:
        known = {e.fact for e in self.evidence}
        cursor = 0
        while cursor < len(self.evidence):
            e = self.evidence[cursor]
            if e.fact.predicate in {'positive', 'nonzero'}:
                pred, lemma = ('nonzero','Nat.ne_of_gt') if e.fact.predicate == 'positive' else ('positive','Nat.pos_of_ne_zero')
                f = Fact(pred, e.fact.arguments)
                if f not in known:
                    known.add(f)
                    self.evidence.append(Evidence(self.epoch, f, lemma, (cursor,), f'({lemma} {e.lean})'))
                    self.firings += 1
            cursor += 1

    def check(self, e: Evidence) -> bool:
        if e.epoch != self.epoch: return False
        if e.rule.startswith('assume:'):
            name = e.rule[7:]
            return not e.parents and self.assumptions.get(name) == e.fact and e.lean == name
        if len(e.parents) != 1: return False
        j = e.parents[0]
        if j < 0 or j >= len(self.evidence): return False
        parent = self.evidence[j]
        # Verify the whole prefix in topological order, prohibiting a cyclic or
        # forward reference. This routine deliberately does not trust a hash.
        try: current = self.evidence.index(e)
        except ValueError: return False
        if j >= current or not self.check(parent): return False
        rules = {'Nat.ne_of_gt': ('positive','nonzero'),
                 'Nat.pos_of_ne_zero': ('nonzero','positive')}
        if e.rule not in rules: return False
        before, after = rules[e.rule]
        return (parent.fact.predicate == before and e.fact.predicate == after
                and parent.fact.arguments == e.fact.arguments
                and e.lean == f'({e.rule} {parent.lean})')

    def require(self, goal: Fact) -> Evidence | None:
        self.close()
        return next((e for e in self.evidence if e.fact == goal and self.check(e)), None)

    def exact_quotient_requirements(self, n: str, d: str) -> tuple[Evidence | None, Evidence | None]:
        # Resolves the consumer's premises; this does NOT calculate or prove an
        # exact quotient. The article treats full Frey transport separately.
        return self.require(Fact('nonzero',(d,))), self.require(Fact('divides',(d,n)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path)
    ap.add_argument('--output', type=Path, default=Path('generated'))
    args = ap.parse_args()
    req = parse(args.source.read_text(encoding='utf-8'))
    cert = certificate(req)
    if not check_certificate(req, cert): raise HeatherError('internal certificate check failed')
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / (req.name+'.json')).write_text(json.dumps(cert, indent=2)+'\n')
    if cert['status'] == 'model_proved':
        (args.output / (req.name+'.lean')).write_text(lean_export(req,cert))
    print(json.dumps({'name':req.name, 'status':cert['status'], 'lean_status':'not_compiled'}))


if __name__ == '__main__':
    main()
