#!/usr/bin/env python3
"""Juniper's executable *ground propositional* obligation-frontier model.

Not a Lean elaborator. Atom names denote arbitrary propositions; rule declarations
are assumed implications. The Lean exporter proves only generic implications
parameterized by those assumptions. No arithmetic/analysis is inferred from names.
Standard library only; Python 3.10 or newer.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re
from typing import Iterable

IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
Support = frozenset[str]

@dataclass(frozen=True)
class Rule:
    name: str
    premises: tuple[str, ...]
    conclusion: str

@dataclass(frozen=True)
class Profile:
    name: str
    atoms: tuple[str, ...]
    known: tuple[str, ...]
    offers: tuple[str, ...]
    rules: tuple[Rule, ...]
    goals: tuple[str, ...]

    def validate(self) -> None:
        if not IDENT.fullmatch(self.name):
            raise ValueError("invalid profile identifier")
        if not self.atoms or len(set(self.atoms)) != len(self.atoms):
            raise ValueError("atoms must be nonempty and distinct")
        if any(not IDENT.fullmatch(a) for a in self.atoms):
            raise ValueError("invalid atom identifier")
        for label, items in (("given", self.known), ("offer", self.offers),
                             ("need", self.goals)):
            if len(items) != len(set(items)) or not set(items) <= set(self.atoms):
                raise ValueError(f"invalid or repeated {label} atom")
        if set(self.known) & set(self.offers):
            raise ValueError("given and offer must be disjoint")
        if not self.goals:
            raise ValueError("at least one need is required")
        names = [r.name for r in self.rules]
        if len(names) != len(set(names)) or any(not IDENT.fullmatch(n) for n in names):
            raise ValueError("rule names must be valid and distinct")
        for r in self.rules:
            if not set(r.premises + (r.conclusion,)) <= set(self.atoms):
                raise ValueError(f"undeclared atom in rule {r.name}")

    def fingerprint(self) -> str:
        payload = [self.name, self.atoms, self.known, self.offers,
                   [(r.name, r.premises, r.conclusion) for r in self.rules], self.goals]
        return sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()

@dataclass(frozen=True)
class Node:
    atom: str
    support: Support
    kind: str
    rule: int | None = None
    parents: tuple[int, ...] = ()

@dataclass
class Result:
    fingerprint: str
    frontier: dict[str, dict[Support, int]]
    nodes: list[Node]
    complete: bool
    attempts: int
    sweeps: int

    def status(self, goal: str) -> str:
        if frozenset() in self.frontier[goal]:
            return "closed_in_profile"
        if self.frontier[goal]:
            return "conditional" if self.complete else "conditional_incomplete"
        return "no_route_in_profile" if self.complete else "budget_exhausted"


def parse(text: str) -> Profile:
    """Parse the deliberately small grammar; refuse unknown directives."""
    name = None
    fields: dict[str, list[str]] = {k: [] for k in ("atoms", "given", "offer", "need")}
    rules: list[Rule] = []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.partition("#")[0].strip()
        if not line:
            continue
        try:
            if line.startswith("rule "):
                label, body = line[5:].split(":", 1)
                left, right = body.split("->")
                if len(right.split()) != 1:
                    raise ValueError("rule needs exactly one conclusion")
                rules.append(Rule(label.strip(), tuple(left.split()), right.strip()))
            else:
                command, *args = line.split()
                if command == "profile" and len(args) == 1 and name is None:
                    name = args[0]
                elif command in fields and args:
                    fields[command].extend(args)
                else:
                    raise ValueError("unknown or malformed directive")
        except ValueError as exc:
            raise ValueError(f"line {number}: {exc}") from exc
    if name is None:
        raise ValueError("missing profile declaration")
    p = Profile(name, tuple(fields["atoms"]), tuple(fields["given"]),
                tuple(fields["offer"]), tuple(rules), tuple(fields["need"]))
    p.validate()
    return p


def solve(p: Profile, max_attempts: int | None = None) -> Result:
    """Compute inclusion-minimal sufficient offer sets, retaining an acyclic DAG.

    A nonempty support is never promoted to an unconditional known fact. When a
    budget interrupts closure, all retained routes remain valid, but coverage and
    minimality relative to the full profile are not asserted.
    """
    p.validate()
    if max_attempts is not None and max_attempts < 0:
        raise ValueError("max_attempts must be nonnegative")
    f: dict[str, dict[Support, int]] = {a: {} for a in p.atoms}
    nodes: list[Node] = []

    def add(node: Node) -> bool:
        current = f[node.atom]
        if any(old <= node.support for old in current):
            return False
        for old in list(current):
            if node.support < old:
                del current[old]
        current[node.support] = len(nodes)
        nodes.append(node)  # Parent identifiers were minted before this append.
        return True

    for a in p.known:
        add(Node(a, frozenset(), "known"))
    for a in p.offers:
        add(Node(a, frozenset((a,)), "offer"))
    attempts = 0
    sweeps = 0
    while True:
        sweeps += 1
        changed = False
        for rid, r in enumerate(p.rules):
            choices = [tuple(f[a].values()) for a in r.premises]
            for parents in product(*choices):
                if max_attempts is not None and attempts >= max_attempts:
                    return Result(p.fingerprint(), f, nodes, False, attempts, sweeps)
                attempts += 1
                support = frozenset().union(*(nodes[i].support for i in parents))
                changed = add(Node(r.conclusion, support, "rule", rid, parents)) or changed
        if not changed:
            return Result(p.fingerprint(), f, nodes, True, attempts, sweeps)


def check(p: Profile, result: Result) -> None:
    """Independent local derivation validation (not a Lean kernel check).

    This checks every retained node, including superseded ones, and the current
    antichains. For a result marked complete it also verifies seed coverage and
    closure under every ground rule. Together with valid derivations, those
    conditions certify exactness relative to this finite profile.
    """
    p.validate()
    if result.fingerprint != p.fingerprint():
        raise ValueError("profile changed: reconstruct or explicitly revalidate")
    for i, n in enumerate(result.nodes):
        if n.atom not in p.atoms or not n.support <= set(p.offers):
            raise ValueError("invalid node proposition or support")
        if n.kind == "known":
            ok = n.atom in p.known and not n.support and not n.parents and n.rule is None
        elif n.kind == "offer":
            ok = (n.atom in p.offers and n.support == frozenset((n.atom,))
                  and not n.parents and n.rule is None)
        elif n.kind == "rule":
            ok = n.rule is not None and 0 <= n.rule < len(p.rules)
            if not ok:
                raise ValueError("invalid rule index")
            r = p.rules[n.rule]
            ok = (n.atom == r.conclusion and len(n.parents) == len(r.premises)
                  and all(0 <= j < i for j in n.parents))
            if ok:
                ps = [result.nodes[j] for j in n.parents]
                ok = (tuple(x.atom for x in ps) == r.premises
                      and n.support == frozenset().union(*(x.support for x in ps)))
        else:
            ok = False
        if not ok:
            raise ValueError(f"invalid derivation node {i}")
    if set(result.frontier) != set(p.atoms):
        raise ValueError("frontier atom mismatch")
    for a, entries in result.frontier.items():
        for s, node_id in entries.items():
            if not 0 <= node_id < len(result.nodes):
                raise ValueError("invalid frontier node")
            n = result.nodes[node_id]
            if n.atom != a or n.support != s:
                raise ValueError("frontier and node disagree")
            if any(t < s for t in entries):
                raise ValueError("frontier is not an antichain")
    if result.complete:
        def covered(atom: str, support: Support) -> bool:
            return any(t <= support for t in result.frontier[atom])
        for a in p.known:
            if not covered(a, frozenset()):
                raise ValueError("complete frontier omits a given fact")
        for a in p.offers:
            if not covered(a, frozenset((a,))):
                raise ValueError("complete frontier omits an offered premise")
        for r in p.rules:
            choices = [tuple(result.frontier[a]) for a in r.premises]
            for supports in product(*choices):
                union = frozenset().union(*supports)
                if not covered(r.conclusion, union):
                    raise ValueError("complete frontier is not rule-closed")


def summary(p: Profile, result: Result) -> dict:
    check(p, result)
    return {
        "profile": p.name, "fingerprint": result.fingerprint,
        "complete": result.complete, "nodes": len(result.nodes),
        "rule_combination_attempts": result.attempts, "sweeps": result.sweeps,
        "goals": {a: {"status": result.status(a), "routes":
                   [sorted(s) for s in sorted(result.frontier[a], key=lambda x: (len(x), sorted(x)))]}
                  for a in p.goals},
        "evidence": "Python-validated abstract derivations; not Lean compilation"
    }


def export_lean(p: Profile, result: Result) -> str:
    """Export generic Prop theorems with shared DAG nodes, no sorry/axiom commands.

    Real mathematical interpretation and actual registered theorem proofs are not
    supplied by this exporter. All rule hypotheses are explicit parameters.
    """
    check(p, result)
    atom = {a: f"A{i}" for i, a in enumerate(p.atoms)}
    known = {a: f"k{i}" for i, a in enumerate(p.known)}
    output = ["/- Generated by Juniper's finite ground model.",
              "   Generic implication proofs, NOT a mathematical source reifier.",
              "   This file has not been compiled in the supplied environment. -/",
              "set_option autoImplicit false", "namespace JuniperGenerated", ""]
    for goal_id, goal in enumerate(p.goals):
        for route_id, support in enumerate(sorted(result.frontier[goal], key=lambda x:(len(x),sorted(x)))):
            root = result.frontier[goal][support]
            reachable: set[int] = set()
            def visit(i: int) -> None:
                if i in reachable:
                    return
                reachable.add(i)
                for j in result.nodes[i].parents:
                    visit(j)
            visit(root)
            offers = {a: f"h{i}" for i, a in enumerate(sorted(support))}
            output.append(f"-- Need {goal}; additional premises: {', '.join(sorted(support)) or '(none)'}")
            output.append(f"theorem need_{goal_id}_route_{route_id}")
            output.append("    (" + " ".join(atom.values()) + " : Prop)")
            for i, r in enumerate(p.rules):
                ty = " -> ".join(atom[a] for a in r.premises + (r.conclusion,))
                output.append(f"    (r{i} : {ty})")
            for a, name in known.items():
                output.append(f"    ({name} : {atom[a]})")
            for a, name in offers.items():
                output.append(f"    ({name} : {atom[a]})")
            output.append(f"    : {atom[goal]} := by")
            for i in sorted(reachable):
                node = result.nodes[i]
                if node.kind == "known":
                    rhs = known[node.atom]
                elif node.kind == "offer":
                    rhs = offers[node.atom]
                else:
                    rhs = " ".join([f"r{node.rule}"] + [f"n{j}" for j in node.parents])
                output.append(f"  have n{i} : {atom[node.atom]} := {rhs}")
            output.extend([f"  exact n{root}", ""])
    output.extend(["end JuniperGenerated", ""])
    return "\n".join(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--lean", type=Path)
    parser.add_argument("--max-attempts", type=int)
    args = parser.parse_args()
    try:
        p = parse(args.input.read_text(encoding="utf-8"))
        result = solve(p, args.max_attempts)
        rendered = json.dumps(summary(p, result), indent=2) + "\n"
        if args.json:
            args.json.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        if args.lean:
            args.lean.write_text(export_lean(p, result), encoding="utf-8")
    except (ValueError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")

if __name__ == "__main__":
    main()
