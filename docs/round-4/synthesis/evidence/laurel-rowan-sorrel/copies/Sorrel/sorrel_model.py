#!/usr/bin/env python3
"""Sorrel's finite support model, not a Lean elaborator.

Rules are supplied propositional implications, not discovered mathematics.
The engine records inclusion-minimal sufficient assumption sets and a finite
proof tree for each. A separate checker validates the returned conditional
proof trees against the exact rule table and lexical context. No third-party
packages are required. Python 3.10+.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass, replace
from itertools import product
import json
from pathlib import Path
import random
import re
import sys
from typing import Iterable

@dataclass(frozen=True, order=True)
class Atom:
    context: str
    name: str

@dataclass(frozen=True)
class Rule:
    name: str
    premises: tuple[Atom, ...]
    conclusion: Atom

@dataclass(frozen=True)
class Proof:
    conclusion: Atom
    source: str                 # '@assumption' or exact rule identifier
    children: tuple['Proof', ...] = ()

Support = frozenset[Atom]

@dataclass
class Problem:
    context: str
    atoms: frozenset[Atom]
    assumptions: frozenset[Atom]
    available: frozenset[Atom]
    rules: tuple[Rule, ...]
    goal: Atom

@dataclass
class Result:
    labels: dict[Atom, dict[Support, Proof]]
    complete: bool
    attempts: int
    insertions: int
    rounds: int

def ordered_sets(sets: Iterable[Support]) -> list[Support]:
    return sorted(sets, key=lambda s: (len(s), tuple(sorted(s))))

def minimal(sets: Iterable[Support]) -> list[Support]:
    out: list[Support] = []
    for s in ordered_sets(set(sets)):
        if not any(t <= s for t in out):
            out.append(s)
    return out

def validate(problem: Problem) -> None:
    if not problem.context or not problem.atoms:
        raise ValueError('a nonempty lexical context and atom universe are required')
    if any(a.context != problem.context for a in problem.atoms):
        raise ValueError('cross-context atoms require a separate checked transport')
    if not problem.assumptions <= problem.atoms:
        raise ValueError('undeclared assumption')
    if not problem.available <= problem.assumptions:
        raise ValueError('available leaves must be declared assumptions')
    if problem.goal not in problem.atoms:
        raise ValueError('undeclared goal')
    ids: set[str] = set()
    for rule in problem.rules:
        if rule.name in ids or rule.name.startswith('@'):
            raise ValueError('duplicate or reserved rule identifier')
        ids.add(rule.name)
        if rule.conclusion not in problem.atoms or not set(rule.premises) <= problem.atoms:
            raise ValueError('undeclared rule atom')

def solve(problem: Problem, max_attempts: int | None = None) -> Result:
    """Exact saturation unless the explicit attempt budget is exhausted.

    A partial result still contains valid certificates, but is not a complete
    inventory of minimal supports. Rule policy must be fixed BEFORE this call.
    """
    validate(problem)
    if max_attempts is not None and max_attempts < 0:
        raise ValueError('budget must be nonnegative')
    labels: dict[Atom, dict[Support, Proof]] = {a: {} for a in problem.atoms}
    for a in sorted(problem.assumptions):
        labels[a][frozenset({a})] = Proof(a, '@assumption')
    attempts = insertions = rounds = 0
    while True:
        rounds += 1
        changed = False
        for rule in problem.rules:
            pools = [list(labels[a].items()) for a in rule.premises]
            for choices in product(*pools):
                if max_attempts is not None and attempts >= max_attempts:
                    return Result(labels, False, attempts, insertions, rounds)
                attempts += 1
                s = frozenset().union(*(v[0] for v in choices))
                dst = labels[rule.conclusion]
                if any(t <= s for t in dst):
                    continue
                children = tuple(v[1] for v in choices)
                proof = Proof(rule.conclusion, rule.name, children)
                for old in [t for t in dst if s < t]:
                    del dst[old]
                dst[s] = proof
                insertions += 1
                changed = True
        if not changed:
            return Result(labels, True, attempts, insertions, rounds)

def check_proof(problem: Problem, proof: Proof, target: Atom) -> Support:
    """Check one finite proof tree; return exactly its assumption leaves.

    This checks implication syntax in a finite model, NOT the truth of user
    rule declarations in Lean. The checker does not consult solver labels.
    """
    validate(problem)
    rules = {r.name: r for r in problem.rules}
    active: set[int] = set()
    def visit(p: Proof, expected: Atom) -> Support:
        if p.conclusion != expected or expected not in problem.atoms:
            raise ValueError('certificate proves a different target or context')
        if id(p) in active:
            raise ValueError('cyclic proof object')
        active.add(id(p))
        try:
            if p.source == '@assumption':
                if p.children or p.conclusion not in problem.assumptions:
                    raise ValueError('invalid assumption leaf')
                return frozenset({p.conclusion})
            r = rules.get(p.source)
            if r is None or r.conclusion != p.conclusion:
                raise ValueError('unknown rule or altered conclusion')
            if len(p.children) != len(r.premises):
                raise ValueError('certificate arity mismatch')
            return frozenset().union(*(visit(c, q) for c, q in zip(p.children, r.premises)))
        finally:
            active.remove(id(p))
    return visit(proof, target)

def frontier(problem: Problem, result: Result, goal: Atom | None = None) -> list[Support]:
    g = goal or problem.goal
    return minimal(s - problem.available for s in result.labels[g])

def reachable(problem: Problem, seeds: Support) -> frozenset[Atom]:
    """Independent Boolean Horn closure used as a small exhaustive oracle."""
    current = set(seeds)
    while True:
        following = current | {r.conclusion for r in problem.rules if set(r.premises) <= current}
        if following == current:
            return frozenset(current)
        current = following

def powerset(items: Iterable[Atom]) -> Iterable[Support]:
    xs = sorted(items)
    for bits in product((False, True), repeat=len(xs)):
        yield frozenset(x for x, bit in zip(xs, bits) if bit)

NAME = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')
def parse(text: str) -> Problem:
    """Parse only the documented ground-rule .sorrel mini-language."""
    context: str | None = None
    names: set[str] = set()
    leaves: set[str] = set()
    available: set[str] = set()
    rule_rows: list[tuple[str, tuple[str, ...], str]] = []
    goal: str | None = None
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        try:
            kind, body = line.split(None, 1)
            if kind == 'context':
                if context is not None or not NAME.fullmatch(body):
                    raise ValueError('one identifier context is required')
                context = body
            elif kind in {'atom', 'assumption', 'available'}:
                fields = body.split()
                if not fields or not all(NAME.fullmatch(x) for x in fields):
                    raise ValueError('invalid identifier')
                if kind == 'atom':
                    if names.intersection(fields) or len(set(fields)) != len(fields):
                        raise ValueError('duplicate atom declaration')
                    names.update(fields)
                elif kind == 'assumption':
                    leaves.update(fields)
                else:
                    available.update(fields)
            elif kind == 'rule':
                rid, formula = body.split(':', 1)
                lhs, rhs = formula.split('->')
                rid, rhs = rid.strip(), rhs.strip()
                args = tuple(x.strip() for x in lhs.split('&')) if lhs.strip() else ()
                if not NAME.fullmatch(rid) or not NAME.fullmatch(rhs) or not all(NAME.fullmatch(a) for a in args):
                    raise ValueError('invalid rule syntax')
                rule_rows.append((rid, args, rhs))
            elif kind == 'goal':
                if goal is not None or not NAME.fullmatch(body):
                    raise ValueError('one goal is required')
                goal = body
            else:
                raise ValueError('unsupported command')
        except ValueError as exc:
            raise ValueError(f'line {line_no}: {exc}') from exc
    if context is None or goal is None:
        raise ValueError('missing context or goal')
    atom = lambda x: Atom(context, x)
    p = Problem(context, frozenset(map(atom, names)), frozenset(map(atom, leaves)),
                frozenset(map(atom, available)),
                tuple(Rule(r, tuple(map(atom, ps)), atom(q)) for r, ps, q in rule_rows), atom(goal))
    validate(p)
    return p

def export_lean(problem: Problem, proof: Proof, name: str = 'selectedPlan') -> str:
    """Export a CONDITIONAL propositional theorem with rules as hypotheses.

    NOT a proof that the abstract rule names describe real mathematics.
    Output has not been compiled in this study.
    """
    support = check_proof(problem, proof, problem.goal)
    atoms = sorted(problem.atoms)
    ids = {a: f'A{i}' for i, a in enumerate(atoms)}
    rule_ids = {r.name: f'r{i}' for i, r in enumerate(problem.rules)}
    used: set[str] = set()
    def term(p: Proof) -> str:
        if p.source == '@assumption':
            return f'h{ids[p.conclusion]}'
        used.add(p.source)
        return '(' + ' '.join([rule_ids[p.source]] + [term(c) for c in p.children]) + ')'
    body = term(proof)
    lines = ['-- Generated finite-model implication; NOT compiled in this study.',
             '-- Atom meanings and rule truth remain theorem parameters.', 'import Init',
             'set_option autoImplicit false', f'theorem {name}',
             '    (' + ' '.join(ids[a] for a in atoms) + ' : Prop)']
    for r in problem.rules:
        if r.name in used:
            rt = ' -> '.join([ids[a] for a in r.premises] + [ids[r.conclusion]])
            lines.append(f'    ({rule_ids[r.name]} : {rt})')
    for a in sorted(support):
        lines.append(f'    (h{ids[a]} : {ids[a]})')
    lines.append(f'    : {ids[problem.goal]} := {body}')
    lines.append('\n-- Atom key (lexical names, not Lean expressions):')
    lines.extend(f'-- {ids[a]} = {a.context}.{a.name}' for a in atoms)
    return '\n'.join(lines) + '\n'

def report(problem: Problem, result: Result) -> dict:
    supports = ordered_sets(result.labels[problem.goal])
    for s in supports:
        assert check_proof(problem, result.labels[problem.goal][s], problem.goal) == s
    return {
        'context': problem.context, 'goal': problem.goal.name,
        'status': 'supported_in_model' if any(s <= problem.available for s in supports) else 'open',
        'support_inventory_complete': result.complete,
        'minimal_supports': [[a.name for a in sorted(s)] for s in supports],
        'residual_frontier': [[a.name for a in sorted(s)] for s in frontier(problem, result)],
        'attempts': result.attempts, 'insertions': result.insertions, 'rounds': result.rounds,
        'scope': 'finite propositional model, not mathematical or Lean-kernel verification',
    }

def test_all() -> dict:
    tests: list[str] = []
    counts = {'generated_systems': 0, 'seed_subsets': 0, 'reachability_comparisons': 0,
              'checked_certificates': 0, 'boolean_valuations': 0, 'semantic_support_checks': 0}
    def ok(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        tests.append(name)
    def rejected(name: str, action) -> None:
        try:
            action()
        except ValueError:
            tests.append(name)
        else:
            raise AssertionError(name)
    base = parse('''context Demo
atom P Q R S T
assumption P Q S
available P
rule pq: P -> R
rule qr: Q -> R
rule rs: R & S -> T
goal T
''')
    ans = solve(base)
    names = lambda sets: {frozenset(a.name for a in s) for s in sets}
    ok('alternative_minimal_supports', names(ans.labels[base.goal]) == {frozenset({'P','S'}),frozenset({'Q','S'})})
    ok('frontier_minimizes_missing_assumptions', names(frontier(base, ans)) == {frozenset({'S'})})
    ok('conditional_not_published_as_closed', report(base, ans)['status'] == 'open')
    active = replace(base, available=frozenset(a for a in base.assumptions if a.name in {'P','S'}))
    ok('available_proofs_close_selected_route', report(active, solve(active))['status'] == 'supported_in_model')
    s, proof = next(iter(ans.labels[base.goal].items()))
    ok('certificate_leaf_support_is_exact', check_proof(base, proof, base.goal) == s)
    rejected('altered_target_rejected', lambda: check_proof(base, proof, Atom('Demo','R')))
    rejected('sibling_context_rejected', lambda: check_proof(base, proof, Atom('Sibling','T')))
    rejected('corrupt_arity_rejected', lambda: check_proof(base, replace(proof,children=()),base.goal))
    changed = replace(base, rules=tuple(replace(r, premises=(Atom('Demo','Q'),)) if r.name=='rs' else r for r in base.rules))
    rejected('changed_rule_invalidates_certificate', lambda: check_proof(changed, proof, changed.goal))
    limited = solve(base, max_attempts=0)
    ok('budget_exhaustion_is_not_refutation', not limited.complete and report(base, limited)['status']=='open')
    cyc = parse('''context Cycle
atom P Q
rule pq: P -> Q
rule qp: Q -> P
goal Q
''')
    ok('unseeded_cycle_derives_nothing', not solve(cyc).labels[cyc.goal])
    grounded = replace(cyc, assumptions=frozenset({Atom('Cycle','P')}), available=frozenset({Atom('Cycle','P')}))
    ok('seeded_cycle_has_finite_proof', bool(solve(grounded).labels[grounded.goal]))
    ok('deleting_seed_rebuilds_without_circular_support', not solve(cyc).labels[cyc.goal])
    theorem = parse('''context EmptySupport
atom P
rule known: -> P
goal P
''')
    ok('zero_premise_rule_has_empty_support', list(solve(theorem).labels[theorem.goal]) == [frozenset()])
    policy = replace(base, rules=tuple(r for r in base.rules if r.name!='pq'))
    ok('policy_filter_before_saturation_preserves_alternative', names(solve(policy).labels[policy.goal]) == {frozenset({'Q','S'})})
    rev = solve(replace(base, rules=tuple(reversed(base.rules))))
    ok('rule_order_changes_no_support_set', set(rev.labels[base.goal]) == set(ans.labels[base.goal]))
    rejected('duplicate_rule_rejected',lambda: solve(replace(base,rules=base.rules+(base.rules[0],))))
    rejected('unknown_available_leaf_rejected',lambda:parse('context X\natom P\navailable Q\ngoal P'))
    rejected('undeclared_rule_atom_rejected',lambda:parse('context X\natom P\nrule r: Q -> P\ngoal P'))
    rejected('unsupported_syntax_rejected',lambda:parse('context X\natom P\nmagic P\ngoal P'))
    ok('export_is_conditional_and_has_no_sorry', 'theorem selectedPlan' in export_lean(base,proof) and 'sorry' not in export_lean(base,proof))
    # Exact arithmetic fixtures, not a universal proof of a Frey theorem.
    a,b,p=3,2,5
    n2,n4=b**p-1-a**p,-a**p*b**p
    ok('frey_inhabited_fixture', p>=4 and p%2==1 and a%4==3 and b%2==0)
    ok('frey_exact_coefficients', n2%4==0 and n4%16==0 and (n2//4,n4//16)==(-53,-486))
    for name,a,b,p,d,k in [('odd',3,2,4,4,2),('even',3,3,5,4,2),('bound',3,2,3,16,4),('residue',1,2,5,4,2)]:
        num=b**p-1-a**p if k==2 else -a**p*b**p
        ok('frey_removed_'+name+'_premise',num%d!=0)
    def realize_length(n: int, element: object | None) -> list:
        if n < 0 or (n > 0 and element is None):
            raise ValueError('no admitted realization')
        return [element] * n
    rejected('empty_domain_positive_length_realization_rejected', lambda: realize_length(1, None))
    # None denotes absence of an element witness in this finite interface;
    # this is not a Lean theorem characterizing the type Empty.
    assert realize_length(0, None) == []
    assert len(realize_length(3, 0)) == 3
    # Random finite theories, tested against independent closure for EVERY
    # seed subset and EVERY atom; plus all Boolean valuations of each theory.
    rng = random.Random(20260906)
    for i in range(80):
        context=f'Generated{i}'
        ats=tuple(Atom(context,f'A{j}') for j in range(6))
        leaves=frozenset(ats[:4])
        rules=[]
        for k in range(10):
            arity=rng.randrange(4)
            rules.append(Rule(f'r{k}',tuple(rng.sample(ats,arity)),rng.choice(ats)))
        p=Problem(context,frozenset(ats),leaves,frozenset(),tuple(rules),ats[-1])
        result=solve(p)
        assert result.complete
        counts['generated_systems']+=1
        for atom in ats:
            for support,prf in result.labels[atom].items():
                assert check_proof(p,prf,atom)==support
                counts['checked_certificates']+=1
        for seeds in powerset(leaves):
            truth=reachable(p,seeds)
            counts['seed_subsets']+=1
            for atom in ats:
                predicted=any(s<=seeds for s in result.labels[atom])
                assert predicted==(atom in truth)
                counts['reachability_comparisons']+=1
        for true_atoms in powerset(ats):
            counts['boolean_valuations']+=1
            if all(not set(r.premises)<=true_atoms or r.conclusion in true_atoms for r in rules):
                for atom in ats:
                    for support in result.labels[atom]:
                        assert not support<=true_atoms or atom in true_atoms
                        counts['semantic_support_checks']+=1
    ok('exhaustive_seed_subset_oracle_agreement',True)
    ok('all_generated_certificates_check',True)
    ok('all_boolean_models_validate_returned_supports',True)
    return {'status':'passed','named_tests':len(tests),'tests':tests,**counts,
            'seed':20260906,'python':sys.version.split()[0],
            'limits':'Finite-model tests only. No Lean compiler, mathematical frontend, authoring study, or Leant integration was executed.'}

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('file',nargs='?',type=Path)
    ap.add_argument('--test',action='store_true')
    ap.add_argument('--json',type=Path)
    ap.add_argument('--export-lean',type=Path)
    ap.add_argument('--budget',type=int)
    args=ap.parse_args()
    try:
        if args.test:
            out=test_all()
        elif args.file:
            p=parse(args.file.read_text(encoding='utf-8'))
            result=solve(p,args.budget)
            out=report(p,result)
            if args.export_lean:
                supports=ordered_sets(result.labels[p.goal])
                if not supports:
                    raise ValueError('no conditional proof to export')
                args.export_lean.write_text(export_lean(p,result.labels[p.goal][supports[0]]),encoding='utf-8')
        else:
            ap.error('supply a file or --test')
        text=json.dumps(out,indent=2)+'\n'
        if args.json:
            args.json.write_text(text,encoding='utf-8')
        print(text,end='')
    except (ValueError,OSError) as exc:
        ap.exit(2,f'error: {exc}\n')

if __name__=='__main__':
    main()
