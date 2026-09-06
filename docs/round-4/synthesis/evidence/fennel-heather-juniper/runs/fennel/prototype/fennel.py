#!/usr/bin/env python3
"""Fennel finite-Horn authoring experiment (Python 3.10+, standard library).

This is NOT a Lean elaborator. Atoms are opaque propositions; registered rules
are explicit theorem parameters in exported Lean. The independent checker below
checks the finite implication calculus, not arbitrary Lean terms or mathematics.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass, asdict
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re
from typing import Any

IDENT = r"[A-Za-z][A-Za-z0-9_]*"

class FennelError(ValueError):
    """A malformed program, certificate, or request."""

@dataclass(frozen=True)
class Root:
    name: str
    atom: str
    pending: bool

@dataclass(frozen=True)
class Rule:
    name: str
    premises: tuple[str, ...]
    conclusion: str

@dataclass(frozen=True)
class Query:
    name: str
    atom: str
    only: tuple[str, ...] | None = None

@dataclass(frozen=True)
class Program:
    name: str
    atoms: tuple[str, ...]
    roots: tuple[Root, ...]
    rules: tuple[Rule, ...]
    queries: tuple[Query, ...]

@dataclass(frozen=True)
class Node:
    kind: str
    atom: str
    name: str
    children: tuple[int, ...]
    support: frozenset[str]

@dataclass
class Plan:
    program: Program
    query: Query
    labels: dict[str, dict[frozenset[str], int]]
    nodes: list[Node]
    complete: bool
    attempts: int
    rounds: int

    def routes(self) -> list[tuple[frozenset[str], int]]:
        return sorted(self.labels[self.query.atom].items(),
                      key=lambda item: (len(item[0]), tuple(sorted(item[0]))))


def parse(source: str) -> Program:
    """Parse a closed, line-oriented, ASCII grammar. No evaluated code strings."""
    name = None
    atoms: list[str] = []
    roots: list[Root] = []
    rules: list[Rule] = []
    queries: list[Query] = []
    names: set[str] = set()
    for lineno, original in enumerate(source.splitlines(), 1):
        line = original.split('#', 1)[0].strip()
        if not line:
            continue
        try:
            match = re.fullmatch(rf'module ({IDENT})', line)
            if match:
                if name is not None or atoms or roots or rules or queries:
                    raise FennelError('module must be the first declaration')
                name = match[1]
                continue
            if name is None:
                raise FennelError('missing module declaration')
            if line.startswith('atom '):
                new = line[5:].split()
                if not new or any(not re.fullmatch(IDENT, x) for x in new):
                    raise FennelError('invalid atom declaration')
                if len(set(new)) != len(new) or set(new) & set(atoms):
                    raise FennelError('duplicate atom')
                atoms.extend(new)
                continue
            match = re.fullmatch(rf'(given|ask) ({IDENT})\s*:\s*({IDENT})', line)
            if match:
                _, rootname, atom = match.groups()
                if rootname in names:
                    raise FennelError('duplicate declaration name')
                names.add(rootname)
                roots.append(Root(rootname, atom, match[1] == 'ask'))
                continue
            match = re.fullmatch(rf'rule ({IDENT})\s*:\s*(.*?)\s*->\s*({IDENT})', line)
            if match:
                rname, left, right = match.groups()
                premises = tuple(x.strip() for x in left.split('&')) if left.strip() else ()
                if any(not re.fullmatch(IDENT, x) for x in premises):
                    raise FennelError('premises must be atoms separated by &')
                if rname in names:
                    raise FennelError('duplicate declaration name')
                names.add(rname)
                rules.append(Rule(rname, premises, right))
                continue
            match = re.fullmatch(rf'show ({IDENT})\s*:\s*({IDENT})(?: using only (.*))?', line)
            if match:
                qname, atom, selection = match.groups()
                if qname in names:
                    raise FennelError('duplicate declaration name')
                names.add(qname)
                only = None if selection is None else tuple(selection.split())
                if only is not None and (not only or any(not re.fullmatch(IDENT, s) for s in only)):
                    raise FennelError('using only requires one or more rule names')
                queries.append(Query(qname, atom, only))
                continue
            raise FennelError('unsupported syntax')
        except FennelError as exc:
            raise FennelError(f'line {lineno}: {exc}') from exc
    if name is None:
        raise FennelError('missing module declaration')
    known = set(atoms)
    mentioned = {r.atom for r in roots} | {q.atom for q in queries}
    for rule in rules:
        mentioned.update(rule.premises)
        mentioned.add(rule.conclusion)
    if mentioned - known:
        raise FennelError(f'undeclared atoms: {sorted(mentioned - known)}')
    rnames = {r.name for r in rules}
    for query in queries:
        if query.only is not None and set(query.only) - rnames:
            raise FennelError(f'unknown permitted rule in {query.name}')
    return Program(name, tuple(atoms), tuple(roots), tuple(rules), tuple(queries))


def fingerprint(program: Program, query: Query) -> str:
    # Identity guard, not proof of semantic correspondence or hash injectivity.
    raw = json.dumps({'program': asdict(program), 'request': asdict(query)},
                     sort_keys=True, separators=(',', ':')).encode()
    return sha256(raw).hexdigest()


def plan(program: Program, query: Query, max_attempts: int = 100000,
         max_nodes: int = 10000) -> Plan:
    """Least fixed point of upward-closed supports, represented by antichains.

    Resource exhaustion preserves sound discovered routes but not completeness.
    Rule generation is outside this fragment: all rules are already ground.
    """
    if max_attempts < 0 or max_nodes < 0:
        raise FennelError('budgets must be nonnegative')
    labels: dict[str, dict[frozenset[str], int]] = {a: {} for a in program.atoms}
    result = Plan(program, query, labels, [], True, 0, 0)

    def add(node: Node) -> bool:
        bucket = labels[node.atom]
        if any(old <= node.support for old in bucket):
            return False
        if len(result.nodes) >= max_nodes:
            raise OverflowError
        for old in list(bucket):
            if node.support < old:
                del bucket[old]
        bucket[node.support] = len(result.nodes)
        result.nodes.append(node)
        return True

    selected = [r for r in program.rules if query.only is None or r.name in query.only]
    try:
        for root in program.roots:
            add(Node('root', root.atom, root.name, (),
                     frozenset([root.name]) if root.pending else frozenset()))
        changed = True
        while changed:
            result.rounds += 1
            changed = False
            for rule in selected:
                choices = [tuple(labels[p].items()) for p in rule.premises]
                for combo in product(*choices):
                    if result.attempts >= max_attempts:
                        raise OverflowError
                    result.attempts += 1
                    support = frozenset().union(*(s for s, _ in combo))
                    node = Node('rule', rule.conclusion, rule.name,
                                tuple(i for _, i in combo), support)
                    changed = add(node) or changed
    except OverflowError:
        result.complete = False
    return result


def certificate(result: Plan, node_id: int) -> dict[str, Any]:
    """Serialize only the selected proof's reachable, topologically ordered DAG."""
    seen: set[int] = set()
    def visit(i: int) -> None:
        if i not in seen:
            seen.add(i)
            for child in result.nodes[i].children:
                visit(child)
    visit(node_id)
    ordered = sorted(seen)
    remap = {old: new for new, old in enumerate(ordered)}
    nodes = []
    for i in ordered:
        n = result.nodes[i]
        nodes.append({'kind': n.kind, 'atom': n.atom, 'name': n.name,
                      'children': [remap[x] for x in n.children],
                      'support': sorted(n.support)})
    return {'format': 'fennel-horn-1', 'fingerprint': fingerprint(result.program, result.query),
            'target': result.query.atom, 'root': remap[node_id], 'nodes': nodes}


def check(program: Program, query: Query, cert: dict[str, Any]) -> frozenset[str]:
    """Check certificates without invoking the planner or trusting stored labels.

    The original Program and Query are inputs supplied by the caller, not read
    from the certificate. Every node, even unused ones, is checked. The final
    route must target the original requested atom. Arbitrary Lean checking is
    intentionally NOT implemented here.
    """
    try:
        if not isinstance(cert, dict):
            raise FennelError('certificate must be an object')
        if cert.get('format') != 'fennel-horn-1':
            raise FennelError('unknown certificate format')
        if cert.get('fingerprint') != fingerprint(program, query):
            raise FennelError('source/request identity changed')
        if cert.get('target') != query.atom:
            raise FennelError('target changed')
        roots = {r.name: r for r in program.roots}
        rules = {r.name: r for r in program.rules}
        computed: list[tuple[str, frozenset[str]]] = []
        nodes = cert['nodes']
        if not isinstance(nodes, list):
            raise FennelError('nodes must be a list')
        for i, node in enumerate(nodes):
            children = node['children']
            if not isinstance(children, list) or any(type(j) is not int or not 0 <= j < i for j in children):
                raise FennelError('non-topological child reference')
            if node['kind'] == 'root':
                root = roots.get(node['name'])
                if root is None or children or root.atom != node['atom']:
                    raise FennelError('invalid root')
                support = frozenset([root.name]) if root.pending else frozenset()
            elif node['kind'] == 'rule':
                rule = rules.get(node['name'])
                if rule is None or (query.only is not None and rule.name not in query.only):
                    raise FennelError('unavailable rule')
                if rule.conclusion != node['atom']:
                    raise FennelError('wrong rule conclusion')
                if tuple(computed[j][0] for j in children) != rule.premises:
                    raise FennelError('wrong arity, order, or premise')
                support = frozenset().union(*(computed[j][1] for j in children))
            else:
                raise FennelError('unknown inference kind')
            if sorted(support) != node['support']:
                raise FennelError('forged support')
            computed.append((node['atom'], support))
        root_id = cert['root']
        if type(root_id) is not int or not 0 <= root_id < len(computed):
            raise FennelError('invalid proof root')
        if computed[root_id][0] != query.atom:
            raise FennelError('proof is for a different target')
        return computed[root_id][1]
    except (KeyError, TypeError, IndexError) as exc:
        raise FennelError('malformed certificate') from exc


def export_lean(program: Program, query: Query, cert: dict[str, Any], theorem_name: str) -> str:
    """Export a closed conditional theorem of opaque Props; no axioms or sorry.

    Internal generated names avoid clashes or injection from source identifiers.
    This exporter has NOT been tested with a Lean compiler in this package.
    """
    support = check(program, query, cert)
    if not re.fullmatch(IDENT, theorem_name):
        raise FennelError('invalid exported theorem name')
    anames = {a: f'P{i}' for i, a in enumerate(program.atoms)}
    rnames = {r.name: f'r{i}' for i, r in enumerate(program.rules)}
    hnames = {r.name: f'h{i}' for i, r in enumerate(program.roots)}
    nodes = cert['nodes']
    used_rules = {n['name'] for n in nodes if n['kind'] == 'rule'}
    used_roots = {n['name'] for n in nodes if n['kind'] == 'root'}
    lines = [f'-- Source query: {query.name}; remaining assumptions: {sorted(support)}',
             '-- UNCOMPILED HERE. Rules below are theorem parameters, not proved arithmetic.',
             'set_option autoImplicit false', f'theorem {theorem_name}']
    if anames:
        lines.append('    (' + ' '.join(anames.values()) + ' : Prop)')
    for root in program.roots:
        if root.name in used_roots:
            lines.append(f'    ({hnames[root.name]} : {anames[root.atom]})')
    for rule in program.rules:
        if rule.name in used_rules:
            ty = ' -> '.join(anames[a] for a in (*rule.premises, rule.conclusion))
            lines.append(f'    ({rnames[rule.name]} : {ty})')
    lines.append(f'    : {anames[query.atom]} := by')
    for i, n in enumerate(nodes):
        if n['kind'] == 'root':
            term = hnames[n['name']]
        else:
            term = ' '.join([rnames[n['name']]] + [f'p{j}' for j in n['children']])
        lines.append(f'  have p{i} : {anames[n["atom"]]} := {term}')
    lines.append(f'  exact p{cert["root"]}')
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    parser.add_argument('--max-attempts', type=int, default=100000)
    args = parser.parse_args()
    try:
        program = parse(args.source.read_text(encoding='utf-8'))
        args.out.mkdir(parents=True, exist_ok=True)
        summaries = []
        for qi, query in enumerate(program.queries):
            result = plan(program, query, args.max_attempts)
            routes = result.routes()
            status = 'proved-in-fragment' if any(not s for s, _ in routes) else ('conditional' if routes else 'no-route-found')
            summaries.append({'query': query.name, 'status': status, 'closure_complete': result.complete,
                              'supports': [sorted(s) for s, _ in routes], 'attempts': result.attempts,
                              'stored_nodes': len(result.nodes), 'rounds': result.rounds})
            for ri, (_, node_id) in enumerate(routes):
                cert = certificate(result, node_id)
                check(program, query, cert)
                stem = f'query_{qi}_route_{ri}'
                (args.out / (stem + '.json')).write_text(json.dumps(cert, indent=2) + '\n')
                (args.out / (stem + '.lean')).write_text(export_lean(program, query, cert, f'fennel_{qi}_{ri}'))
        (args.out / 'summary.json').write_text(json.dumps(summaries, indent=2) + '\n')
        print(json.dumps(summaries, indent=2))
    except (FennelError, OSError) as exc:
        parser.exit(2, f'Fennel: {exc}\n')

if __name__ == '__main__':
    main()
