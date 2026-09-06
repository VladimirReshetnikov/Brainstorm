#!/usr/bin/env python3
"""Clover's executable, restricted endomorphism-property elaboration model.

Standard library only, Python 3.9+. This is NOT a Lean elaborator and does not
claim kernel acceptance. It parses a tiny language, grounds a fixed registry,
checks proof plans independently, and exports ordinary Lean source. The
mathematical meaning of each registry rule is given in CloverCore.lean.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

@dataclass(frozen=True, order=True)
class Term:
    head: str
    args: Tuple['Term', ...] = ()

    def __str__(self) -> str:
        if self.head == 'compose':
            return f'({self.args[0]} . {self.args[1]})'
        return self.head

    def subterms(self) -> Set['Term']:
        out = {self}
        for a in self.args:
            out.update(a.subterms())
        return out

@dataclass(frozen=True, order=True)
class Atom:
    pred: str
    args: Tuple[Term, ...]

    def __str__(self) -> str:
        return self.pred + ' ' + ' '.join(map(str, self.args))

SIGNATURE = {'injective': 1, 'involutive': 1, 'left_inverse': 2, 'same': 2}

def V(name: str) -> Term:
    return Term('$' + name)

def comp(g: Term, f: Term) -> Term:
    return Term('compose', (g, f))

def atom(pred: str, *args: Term) -> Atom:
    if pred not in SIGNATURE or SIGNATURE[pred] != len(args):
        raise ValueError('unknown predicate or incorrect arity')
    return Atom(pred, tuple(args))

@dataclass(frozen=True)
class Rule:
    name: str
    variables: Tuple[str, ...]
    premises: Tuple[Atom, ...]
    conclusion: Atom

f, g, h = V('f'), V('g'), V('h')
RULES = (
    Rule('inv_from_involution', ('f',), (atom('involutive', f),),
         atom('left_inverse', f, f)),
    Rule('inj_from_left_inverse', ('f', 'g'), (atom('left_inverse', g, f),),
         atom('injective', f)),
    Rule('inj_comp', ('f', 'g'), (atom('injective', f), atom('injective', g)),
         atom('injective', comp(g, f))),
    Rule('same_symm', ('f', 'g'), (atom('same', f, g),), atom('same', g, f)),
    Rule('same_trans', ('f', 'g', 'h'), (atom('same', f, g), atom('same', g, h)),
         atom('same', f, h)),
    Rule('inj_transport', ('f', 'g'), (atom('same', f, g), atom('injective', f)),
         atom('injective', g)),
    Rule('same_refl', ('f',), (), atom('same', f, f)),
)
REGISTRY = {r.name: r for r in RULES}
REGISTRY_ID = hashlib.sha256(repr(RULES).encode()).hexdigest()

def subst_term(t: Term, s: Mapping[str, Term]) -> Term:
    if t.head.startswith('$'):
        return s[t.head[1:]]
    return Term(t.head, tuple(subst_term(a, s) for a in t.args))

def subst_atom(a: Atom, s: Mapping[str, Term]) -> Atom:
    return atom(a.pred, *(subst_term(t, s) for t in a.args))

def match_term(pattern: Term, value: Term, s: Dict[str, Term]) -> bool:
    if pattern.head.startswith('$'):
        key = pattern.head[1:]
        if key in s:
            return s[key] == value
        s[key] = value
        return True
    return (pattern.head == value.head and len(pattern.args) == len(value.args)
            and all(match_term(p, v, s) for p, v in zip(pattern.args, value.args)))

def match_atom(pattern: Atom, value: Atom) -> Optional[Dict[str, Term]]:
    if pattern.pred != value.pred or len(pattern.args) != len(value.args):
        return None
    s: Dict[str, Term] = {}
    return s if all(match_term(p, v, s) for p, v in zip(pattern.args, value.args)) else None

@dataclass(frozen=True)
class Proof:
    conclusion: Atom
    kind: str  # assumption or application
    name: str
    substitution: Tuple[Tuple[str, Term], ...] = ()
    premises: Tuple['Proof', ...] = ()

@dataclass(frozen=True)
class Request:
    source_id: str
    binders: Tuple[Term, ...]
    assumptions: Tuple[Tuple[str, Atom], ...]
    goal: Atom
    known: Tuple[Proof, ...] = ()
    allowed: Tuple[str, ...] = tuple(r.name for r in RULES)
    required_root: Optional[str] = None

    @property
    def identity(self) -> str:
        # A routing/replay guard, NOT a mathematical proof of correspondence.
        payload = (self.source_id, self.binders, self.assumptions, self.goal,
                   self.allowed, self.required_root, REGISTRY_ID)
        return hashlib.sha256(repr(payload).encode()).hexdigest()

@dataclass(frozen=True)
class GroundRule:
    name: str
    substitution: Tuple[Tuple[str, Term], ...]
    premises: Tuple[Atom, ...]
    conclusion: Atom

@dataclass(frozen=True)
class Plan:
    request_id: str
    goal: Atom
    proof: Proof

class ResourceLimit(Exception):
    pass

class PlanError(ValueError):
    pass

def well_formed_term(t: Term, binders: Set[Term]) -> bool:
    if t.head == 'compose':
        return len(t.args) == 2 and all(well_formed_term(a, binders) for a in t.args)
    return not t.args and t in binders

def well_formed_atom(a: Atom, binders: Set[Term]) -> bool:
    return (a.pred in SIGNATURE and len(a.args) == SIGNATURE[a.pred]
            and all(well_formed_term(t, binders) for t in a.args))

def check_plan(req: Request, plan: Plan, enforce_root: bool = True) -> Set[str]:
    """Independent of grounding and closure: reconstruct every rule application.

    Returns actual assumption support. It checks exact objects, rule identity,
    predicate arities and premise/conclusion matches. It does not invoke Lean.
    """
    if plan.request_id != req.identity or plan.goal != req.goal:
        raise PlanError('request/target mismatch')
    if plan.proof.conclusion != req.goal:
        raise PlanError('root does not establish target')
    binders = set(req.binders)
    assumptions = dict(req.assumptions)
    if len(assumptions) != len(req.assumptions):
        raise PlanError('duplicate assumption identity')
    if not well_formed_atom(req.goal, binders):
        raise PlanError('ill-formed goal')
    memo: Dict[int, Set[str]] = {}
    active: Set[int] = set()

    def visit(p: Proof) -> Set[str]:
        key = id(p)
        if key in active:
            raise PlanError('cyclic proof object')
        if key in memo:
            return memo[key]
        active.add(key)
        if not well_formed_atom(p.conclusion, binders):
            raise PlanError('out-of-scope object or malformed predicate')
        if p.kind == 'assumption':
            if (p.premises or p.substitution or assumptions.get(p.name) != p.conclusion):
                raise PlanError('assumption is absent, changed, or malformed')
            support = {p.name}
        elif p.kind == 'application':
            if p.name not in req.allowed or p.name not in REGISTRY:
                raise PlanError('rule forbidden or absent')
            r = REGISTRY[p.name]
            if tuple(k for k, _ in p.substitution) != r.variables:
                raise PlanError('wrong substitution domain/order')
            s = dict(p.substitution)
            if any(not well_formed_term(t, binders) for t in s.values()):
                raise PlanError('invalid rule argument')
            expected = tuple(subst_atom(a, s) for a in r.premises)
            if (subst_atom(r.conclusion, s) != p.conclusion or
                    expected != tuple(q.conclusion for q in p.premises)):
                raise PlanError('rule premises/conclusion do not match')
            support = set()
            for q in p.premises:
                support.update(visit(q))
        else:
            raise PlanError('unknown proof constructor')
        active.remove(key)
        memo[key] = support
        return support

    support = visit(plan.proof)
    if enforce_root and req.required_root is not None:
        if plan.proof.kind != 'application' or plan.proof.name != req.required_root:
            raise PlanError('required root rule not used')
    return support

def arena_for(req: Request) -> Tuple[Term, ...]:
    arena = set(req.binders)
    for a in [req.goal] + [a for _, a in req.assumptions] + [p.conclusion for p in req.known]:
        for t in a.args:
            arena.update(t.subterms())
    return tuple(sorted(arena))

def ground(req: Request, max_attempts: int, metrics: Dict[str, int]) -> List[GroundRule]:
    """Goal-triggered finite grounding, with premise-only parameters enumerated.

    No rule creates an arena term. All terms in instantiated premises must
    already occur in the source-derived arena. Truncation raises ResourceLimit;
    it is never reported as logical non-derivability.
    """
    arena = arena_for(req)
    arena_set = set(arena)
    metrics['arena_terms'] = len(arena)
    pending = [req.goal]
    seen: Set[Atom] = set()
    output: Dict[Tuple[str, Tuple[Tuple[str, Term], ...]], GroundRule] = {}
    while pending:
        a = pending.pop()
        if a in seen:
            continue
        seen.add(a)
        for r in RULES:
            if r.name not in req.allowed:
                continue
            base = match_atom(r.conclusion, a)
            if base is None:
                continue
            missing = tuple(k for k in r.variables if k not in base)
            for values in itertools.product(arena, repeat=len(missing)):
                metrics['instance_attempts'] += 1
                if metrics['instance_attempts'] > max_attempts:
                    raise ResourceLimit('grounding attempt limit reached')
                s = dict(base)
                s.update(zip(missing, values))
                premises = tuple(subst_atom(p, s) for p in r.premises)
                if any(t not in arena_set for p in premises for a0 in p.args for t in a0.subterms()):
                    continue
                substitution = tuple((k, s[k]) for k in r.variables)
                key = (r.name, substitution)
                if key not in output:
                    output[key] = GroundRule(r.name, substitution, premises, a)
                    pending.extend(premises)
    metrics['ground_atoms'] = len(seen)
    metrics['ground_rules'] = len(output)
    return sorted(output.values(), key=repr)

@dataclass
class Result:
    status: str
    plan: Optional[Plan]
    support: List[str]
    routes: List[dict]
    metrics: Dict[str, int]
    detail: str = ''

    def as_dict(self) -> dict:
        return {'status': self.status, 'kernel_checked': False,
                'goal': str(self.plan.goal) if self.plan else None,
                'support': self.support, 'routes': self.routes,
                'metrics': self.metrics, 'detail': self.detail}

def solve(req: Request, max_attempts: int = 50000, reverse_schedule: bool = False) -> Result:
    if max_attempts < 0:
        raise ValueError('negative resource limit')
    metrics = dict(arena_terms=0, instance_attempts=0, ground_atoms=0,
                   ground_rules=0, rule_tests=0, closure_additions=0, proof_nodes=0)
    if set(req.allowed) - set(REGISTRY):
        raise ValueError('unknown allowed rule')
    if req.required_root is not None and req.required_root not in req.allowed:
        return Result('unresolved', None, [], [], metrics, 'required root is not enabled')
    binders = set(req.binders)
    if any(not well_formed_atom(a, binders) for a in [req.goal] + [a for _, a in req.assumptions]):
        raise ValueError('request contains malformed or out-of-scope terms')
    facts: Dict[Atom, Proof] = {}
    for name, a in req.assumptions:
        facts.setdefault(a, Proof(a, 'assumption', name))
    for p in req.known:
        probe = Request(req.source_id, req.binders, req.assumptions, p.conclusion,
                        (), req.allowed, None)
        check_plan(probe, Plan(probe.identity, p.conclusion, p))
        facts.setdefault(p.conclusion, p)
    try:
        rules = ground(req, max_attempts, metrics)
    except ResourceLimit as e:
        return Result('resource_limit', None, [], [], metrics, str(e))
    if reverse_schedule:
        rules.reverse()
    changed = True
    while changed:
        changed = False
        for r in rules:
            metrics['rule_tests'] += 1
            if r.conclusion not in facts and all(p in facts for p in r.premises):
                facts[r.conclusion] = Proof(r.conclusion, 'application', r.name,
                                           r.substitution, tuple(facts[p] for p in r.premises))
                metrics['closure_additions'] += 1
                changed = True
    proof = facts.get(req.goal)
    if req.required_root is not None:
        proof = None
        for r in rules:
            if (r.name == req.required_root and r.conclusion == req.goal
                    and all(p in facts for p in r.premises)):
                proof = Proof(r.conclusion, 'application', r.name, r.substitution,
                              tuple(facts[p] for p in r.premises))
                break
    if proof is None:
        routes = [{'rule': r.name, 'missing': [str(p) for p in r.premises if p not in facts]}
                  for r in rules if r.conclusion == req.goal]
        routes.sort(key=lambda r: (len(r['missing']), r['rule'], repr(r)))
        return Result('unresolved', None, [], routes[:8], metrics,
                      'not derived in this finite rule/term fragment; not a refutation')
    plan = Plan(req.identity, req.goal, proof)
    support = check_plan(req, plan)
    metrics['proof_nodes'] = len(proof_order(proof))
    return Result('plan_checked', plan, sorted(support), [], metrics)

def proof_order(p: Proof) -> List[Proof]:
    out: List[Proof] = []
    seen: Set[int] = set()
    def visit(q: Proof) -> None:
        if id(q) in seen:
            return
        for child in q.premises:
            visit(child)
        seen.add(id(q))
        out.append(q)
    visit(p)
    return out

TOKEN = re.compile(r'[A-Za-z_][A-Za-z_0-9]*|[().]')

def parse_atom(text: str, env: Mapping[str, Term]) -> Atom:
    tokens = TOKEN.findall(text)
    if ''.join(tokens) != re.sub(r'\s+', '', text):
        raise ValueError('invalid atom token')
    if not tokens or tokens[0] not in SIGNATURE:
        raise ValueError('unknown property')
    pred, pos = tokens[0], 1
    def term() -> Term:
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError('missing term')
        tok = tokens[pos]
        pos += 1
        if tok == '(':
            a = term()
            if pos < len(tokens) and tokens[pos] == '.':
                pos += 1
                b = term()
                a = comp(a, b)
            if pos >= len(tokens) or tokens[pos] != ')':
                raise ValueError('expected closing parenthesis')
            pos += 1
            return a
        if tok not in env:
            raise ValueError('unknown function: ' + tok)
        return env[tok]
    args = tuple(term() for _ in range(SIGNATURE[pred]))
    if pos != len(tokens):
        raise ValueError('unexpected extra argument/token')
    return atom(pred, *args)

@dataclass
class Claim:
    name: str
    line: int
    request: Request
    result: Result

def elaborate(source: str, max_attempts: int = 50000) -> List[Claim]:
    source_id = hashlib.sha256(source.encode()).hexdigest()
    env: Dict[str, Term] = {}
    binders: List[Term] = []
    assumptions: List[Tuple[str, Atom]] = []
    known: List[Proof] = []
    stack: List[tuple] = []
    claims: List[Claim] = []
    claim_names: Set[str] = set()
    serial = 0
    for line_number, raw in enumerate(source.splitlines(), 1):
        line = raw.split('--', 1)[0].strip()
        if not line:
            continue
        try:
            if line == 'scope':
                stack.append((dict(env), list(binders), list(assumptions), list(known)))
            elif line == 'end':
                if not stack:
                    raise ValueError('unmatched end')
                env, binders, assumptions, known = stack.pop()
            elif line.startswith('fix '):
                lhs, rhs = line[4:].split(':', 1)
                if rhs.strip() != 'End' or not lhs.split():
                    raise ValueError('only nonempty End binder lists are supported')
                for name in lhs.split():
                    if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name):
                        raise ValueError('invalid binder name')
                    serial += 1
                    value = Term(f'{name}_{serial}')
                    env[name] = value
                    binders.append(value)
            elif line.startswith('assume ') or line.startswith('claim '):
                mode, rest = line.split(' ', 1)
                name, text = rest.split(':', 1)
                name = name.strip()
                if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name):
                    raise ValueError('invalid declaration name')
                a = parse_atom(text.strip(), env)
                if mode == 'assume':
                    serial += 1
                    assumptions.append((f'{name}_{serial}', a))
                else:
                    if name in claim_names:
                        raise ValueError('duplicate claim name')
                    claim_names.add(name)
                    req = Request(source_id, tuple(binders), tuple(assumptions), a, tuple(known))
                    result = solve(req, max_attempts)
                    claims.append(Claim(name, line_number, req, result))
                    if result.plan is not None:
                        known.append(result.plan.proof)
            else:
                raise ValueError('unsupported command')
        except (ValueError, IndexError) as e:
            raise ValueError(f'line {line_number}: {e}') from e
    if stack:
        raise ValueError('unclosed scope')
    return claims

LEAN_PRED = {'injective': 'Injective', 'involutive': 'Involutive',
             'left_inverse': 'LeftInverse', 'same': 'Same'}

def lean_term(t: Term) -> str:
    return f'(compose {lean_term(t.args[0])} {lean_term(t.args[1])})' if t.head == 'compose' else t.head

def lean_atom(a: Atom) -> str:
    return LEAN_PRED[a.pred] + ' ' + ' '.join(lean_term(t) for t in a.args)

def export_claim(c: Claim) -> str:
    if c.result.plan is None:
        return f'-- {c.name}: unresolved; no theorem exported.\n'
    check_plan(c.request, c.result.plan)
    req = c.request
    lines = [f'theorem {c.name} (A : Type u)']
    if req.binders:
        lines.append('    (' + ' '.join(t.head for t in req.binders) + ' : A -> A)')
    for name, a in req.assumptions:
        lines.append(f'    ({name} : {lean_atom(a)})')
    lines.append(f'    : {lean_atom(req.goal)} := by')
    refs: Dict[int, str] = {}
    for i, p in enumerate(proof_order(c.result.plan.proof)):
        if p.kind == 'assumption':
            refs[id(p)] = p.name
        else:
            name = f'clover_step_{i}'
            args = [lean_term(t) for _, t in p.substitution]
            args.extend(refs[id(q)] for q in p.premises)
            lines.append(f'  have {name} : {lean_atom(p.conclusion)} := {p.name} ' + ' '.join(args))
            refs[id(p)] = name
    lines.append('  exact ' + refs[id(c.result.plan.proof)])
    return '\n'.join(lines) + '\n'

def export_document(claims: Sequence[Claim]) -> str:
    return ('-- Generated by the restricted Python model; NOT compiled in this run.\n'
            'import CloverCore\nset_option autoImplicit false\nuniverse u\n'
            'namespace CloverGenerated\nopen CloverCore\n\n'
            + '\n'.join(export_claim(c) for c in claims) + '\nend CloverGenerated\n')

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--json', type=Path)
    parser.add_argument('--lean', type=Path)
    parser.add_argument('--max-attempts', type=int, default=50000)
    args = parser.parse_args()
    claims = elaborate(args.source.read_text(encoding='utf-8'), args.max_attempts)
    report = {'registry_sha256': REGISTRY_ID, 'kernel_checked': False,
              'document_plan_complete': all(c.result.status == 'plan_checked' for c in claims),
              'claims': [dict(name=c.name, line=c.line, source_goal=str(c.request.goal),
                              **c.result.as_dict()) for c in claims]}
    text = json.dumps(report, indent=2)
    if args.json:
        args.json.write_text(text + '\n', encoding='utf-8')
    else:
        print(text)
    if args.lean:
        args.lean.write_text(export_document(claims), encoding='utf-8')

if __name__ == '__main__':
    main()
