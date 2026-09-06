#!/usr/bin/env python3
"""Laurel-Core: a finite, symbolic, certificate-carrying residualizer.

This is NOT a Lean elaborator. Atoms and ground Horn rules are declared input;
a rule is a logical assumption here, not a theorem fetched from a Lean library.
The independent checker validates derivations relative to that exact profile.
The exporter emits conditional ordinary-Lean declarations, not a claim that
Lean has compiled them. No nonempty residual is promoted to an established fact.
Python 3.10+, standard library only.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import hashlib
from itertools import product
import json
from pathlib import Path
import re
from typing import Iterable, Mapping

Support = frozenset[str]
_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")

@dataclass(frozen=True)
class Rule:
    name: str
    premises: tuple[str, ...]
    conclusion: str

@dataclass(frozen=True)
class Profile:
    context: str
    atoms: tuple[str, ...]
    known: frozenset[str]
    offers: frozenset[str]
    rules: tuple[Rule, ...]

    def __post_init__(self) -> None:
        names = (self.context, *self.atoms, *(r.name for r in self.rules))
        if any(not _NAME.fullmatch(n) for n in names):
            raise ValueError('Names must be ASCII identifiers beginning with a letter')
        if len(set(self.atoms)) != len(self.atoms):
            raise ValueError('Duplicate atom')
        if len({r.name for r in self.rules}) != len(self.rules):
            raise ValueError('Duplicate rule name')
        atoms = set(self.atoms)
        mentioned = set(self.known) | set(self.offers)
        for r in self.rules:
            mentioned.update(r.premises)
            mentioned.add(r.conclusion)
        if not mentioned <= atoms:
            raise ValueError(f'Undeclared atoms: {sorted(mentioned - atoms)}')

    def fingerprint(self) -> str:
        # This is an exact symbolic-profile identity check, NOT a logical proof
        # of equivalence or a typed context transport.
        obj = {'context': self.context, 'atoms': self.atoms,
               'known': sorted(self.known), 'offers': sorted(self.offers),
               'rules': [(r.name, r.premises, r.conclusion) for r in self.rules]}
        return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

@dataclass(frozen=True)
class Proof:
    profile: str
    atom: str
    kind: str                     # known | offer | rule
    rule: str = ''
    children: tuple['Proof', ...] = ()

@dataclass
class Result:
    profile: str
    frontiers: dict[str, dict[Support, Proof]]
    complete: bool
    rounds: int
    combinations: int
    insertions: int


def infer(profile: Profile, max_combinations: int | None = None) -> Result:
    """Compute minimal residual supports, or return a sound partial result.

    No heuristic support cap is used. A work cap counts candidate premise
    combinations; when hit, complete=False. Minimality relative to *all*
    derivations is promised only when complete=True.
    """
    if max_combinations is not None and max_combinations < 0:
        raise ValueError('Budget must be nonnegative')
    fp = profile.fingerprint()
    fs: dict[str, dict[Support, Proof]] = {a: {} for a in profile.atoms}
    count = 0

    def insert(a: str, h: Support, p: Proof) -> bool:
        nonlocal count
        old = fs[a]
        if any(s <= h for s in old):
            return False
        for s in tuple(old):
            if h < s:
                del old[s]
        old[h] = p
        count += 1
        return True

    for a in sorted(profile.known):
        insert(a, frozenset(), Proof(fp, a, 'known'))
    for a in sorted(profile.offers):
        insert(a, frozenset({a}), Proof(fp, a, 'offer'))
    rounds = combinations = 0
    while True:
        rounds += 1
        changed = False
        for r in profile.rules:
            options = [tuple(fs[a].items()) for a in r.premises]
            for parts in product(*options):
                if max_combinations is not None and combinations >= max_combinations:
                    return Result(fp, fs, False, rounds, combinations, count)
                combinations += 1
                support = frozenset().union(*(h for h, _ in parts))
                p = Proof(fp, r.conclusion, 'rule', r.name,
                          tuple(child for _, child in parts))
                changed = insert(r.conclusion, support, p) or changed
        if not changed:
            return Result(fp, fs, True, rounds, combinations, count)


def check_proof(profile: Profile, proof: Proof, target: str,
                claimed: Support) -> None:
    """Check one conditional derivation independently of inference.

    Recomputes its support. Rejects stale profiles, wrong targets, ill-shaped
    leaves, missing rules, premise mismatch, and cycles. Does not use frontiers
    or the minimal-support algorithm. Raises ValueError on invalid evidence.
    """
    fp = profile.fingerprint()
    rules = {r.name: r for r in profile.rules}
    memo: dict[int, Support] = {}
    active: set[int] = set()

    def visit(p: Proof) -> Support:
        key = id(p)
        if key in active:
            raise ValueError('Cyclic certificate')
        if key in memo:
            return memo[key]
        active.add(key)
        if p.profile != fp or p.atom not in profile.atoms:
            raise ValueError('Profile or atom mismatch')
        if p.kind in ('known', 'offer'):
            if p.rule or p.children:
                raise ValueError('Malformed leaf')
            if p.kind == 'known':
                if p.atom not in profile.known:
                    raise ValueError('Unavailable known premise')
                support = frozenset()
            else:
                if p.atom not in profile.offers:
                    raise ValueError('Unauthorized residual premise')
                support = frozenset({p.atom})
        elif p.kind == 'rule':
            r = rules.get(p.rule)
            if r is None or r.conclusion != p.atom:
                raise ValueError('Wrong rule or conclusion')
            if tuple(c.atom for c in p.children) != r.premises:
                raise ValueError('Wrong premise sequence')
            support = frozenset().union(*(visit(c) for c in p.children))
        else:
            raise ValueError('Unknown certificate constructor')
        active.remove(key)
        memo[key] = support
        return support

    if proof.atom != target:
        raise ValueError('Requested target changed')
    if visit(proof) != claimed:
        raise ValueError('Claimed support does not match the derivation')


def reopen_known(profile: Profile, root: Proof, support: Support,
                 removed: Support, new_context: str) -> tuple[Profile, Proof, Support]:
    """Turn lost *used* known premises into explicit residuals.

    Only this narrowly specified change is supported: atoms and rules stay
    exactly fixed, known premises are deleted, and those atoms become offers.
    This constructs a new derivation; it never accepts old profile hashes as
    context transport. It is not dependent Lean-context migration.
    """
    check_proof(profile, root, root.atom, support)
    if not removed <= profile.known:
        raise ValueError('Can only reopen known premises')
    new = Profile(new_context, profile.atoms, profile.known - removed,
                  profile.offers | removed, profile.rules)
    fp = new.fingerprint()
    memo: dict[int, Proof] = {}
    used: set[str] = set()
    def copy(p: Proof) -> Proof:
        if id(p) in memo:
            return memo[id(p)]
        kind = p.kind
        if kind == 'known' and p.atom in removed:
            kind = 'offer'
            used.add(p.atom)
        q = Proof(fp, p.atom, kind, p.rule, tuple(copy(c) for c in p.children))
        memo[id(p)] = q
        return q
    repaired = copy(root)
    residual = support | frozenset(used)
    check_proof(new, repaired, repaired.atom, residual)
    return new, repaired, residual


def parse(text: str) -> tuple[Profile, str]:
    """Parse the documented symbolic DSL; comments start with '#'."""
    context = target = None
    atoms: list[str] = []
    known: set[str] = set()
    offers: set[str] = set()
    rules: list[Rule] = []
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        try:
            cmd, rest = line.split(None, 1)
            if cmd == 'context':
                if context is not None:
                    raise ValueError('Duplicate context')
                context = rest.strip()
            elif cmd == 'atoms':
                atoms.extend(rest.split())
            elif cmd == 'known':
                known.update(rest.split())
            elif cmd == 'offer':
                offers.update(rest.split())
            elif cmd == 'rule':
                name, body = rest.split(':', 1)
                left, right = body.split('->', 1)
                rules.append(Rule(name.strip(), tuple(left.split()), right.strip()))
            elif cmd == 'show':
                if target is not None:
                    raise ValueError('Duplicate target')
                target = rest.strip()
            else:
                raise ValueError(f'Unknown command {cmd}')
        except ValueError as e:
            raise ValueError(f'Line {line_no}: {e}') from e
    if context is None or target is None:
        raise ValueError('A context and a target are required')
    p = Profile(context, tuple(atoms), frozenset(known), frozenset(offers), tuple(rules))
    if target not in p.atoms:
        raise ValueError('Target must be declared')
    return p, target


def export_lean(profile: Profile, target: str,
                routes: Mapping[Support, Proof]) -> str:
    """Export proof terms for symbolic conditional theorems (UNCOMPILED here)."""
    namespace = 'LaurelGenerated.C' + hashlib.sha256((profile.fingerprint() + ':' + target).encode()).hexdigest()[:12]
    lines = ['-- Generated by Laurel-Core. Ordinary Lean syntax; NOT compiled here.',
             '-- Atoms are arbitrary propositions; rules are explicit hypotheses.',
             '-- This is NOT a proof that the named mathematical rules are true.',
             'set_option autoImplicit false', f'namespace {namespace}', '']
    amap = {a: f'P{i}' for i, a in enumerate(profile.atoms)}
    rmap = {r.name: f'r{i}' for i, r in enumerate(profile.rules)}
    for a in profile.atoms:
        lines.append(f'-- {amap[a]} = {a}')
    for i, (support, root) in enumerate(sorted(routes.items(), key=lambda hp: (len(hp[0]), sorted(hp[0])))):
        check_proof(profile, root, target, support)
        used_rules: set[str] = set()
        used_known: set[str] = set()
        visited: set[int] = set()
        order: list[Proof] = []
        def walk(p: Proof) -> None:
            if id(p) in visited:
                return
            visited.add(id(p))
            for c in p.children:
                walk(c)
            if p.kind == 'rule':
                used_rules.add(p.rule)
                order.append(p)
            if p.kind == 'known':
                used_known.add(p.atom)
        walk(root)
        kn = {a: f'k{j}' for j, a in enumerate(sorted(used_known))}
        hn = {a: f'h{j}' for j, a in enumerate(sorted(support))}
        lines.extend(['', f'-- Residual support: {", ".join(sorted(support)) or "none"}',
                      f'theorem route_{i} ({" ".join(amap.values())} : Prop)'])
        for r in profile.rules:
            if r.name in used_rules:
                typ = ' -> '.join(amap[a] for a in (*r.premises, r.conclusion))
                lines.append(f'    ({rmap[r.name]} : {typ})')
        for a in sorted(used_known):
            lines.append(f'    ({kn[a]} : {amap[a]})')
        for a in sorted(support):
            lines.append(f'    ({hn[a]} : {amap[a]})')
        lines.append(f'    : {amap[target]} := by')
        node_names: dict[int, str] = {}
        def ref(p: Proof) -> str:
            return kn[p.atom] if p.kind == 'known' else hn[p.atom] if p.kind == 'offer' else node_names[id(p)]
        for j, p in enumerate(order):
            name = f'd{j}'
            expression = ' '.join([rmap[p.rule], *(ref(c) for c in p.children)])
            lines.append(f'  have {name} : {amap[p.atom]} := {expression}')
            node_names[id(p)] = name
        lines.append(f'  exact {ref(root)}')
    lines.extend(['', f'end {namespace}', ''])
    return '\n'.join(lines)


def summary(profile: Profile, result: Result, target: str) -> dict:
    routes = result.frontiers[target]
    for support, proof in routes.items():
        check_proof(profile, proof, target, support)
    status = ('established_in_profile' if frozenset() in routes else
              'conditional' if routes else 'no_route_in_profile' if result.complete
              else 'inconclusive')
    return {'context': profile.context, 'profile_sha256': result.profile,
            'target': target, 'status': status, 'complete': result.complete,
            'supports': [sorted(h) for h in sorted(routes, key=lambda h: (len(h), sorted(h)))],
            'rounds': result.rounds, 'premise_combinations': result.combinations,
            'support_insertions': result.insertions,
            'certificate_boundary': 'symbolic Horn assumptions; not Lean-checked'}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('--lean', type=Path)
    ap.add_argument('--json', type=Path)
    ap.add_argument('--budget', type=int)
    args = ap.parse_args()
    try:
        profile, target = parse(args.input.read_text(encoding='utf-8'))
        result = infer(profile, args.budget)
        out = json.dumps(summary(profile, result, target), indent=2) + '\n'
        if args.json:
            args.json.write_text(out, encoding='utf-8')
        if args.lean:
            args.lean.write_text(export_lean(profile, target, result.frontiers[target]), encoding='utf-8')
        print(out, end='')
    except (OSError, ValueError) as e:
        ap.exit(2, f'Laurel-Core: {e}\n')

if __name__ == '__main__':
    main()
