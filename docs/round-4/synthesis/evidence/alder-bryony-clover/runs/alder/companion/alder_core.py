#!/usr/bin/env python3
"""Alder-0: a small, executable, *propositional* residual-proof frontend.

This is not a Lean elaborator. Atoms denote opaque propositions; declared
rules become explicit hypotheses in generated Lean. The Python checker
validates propositional derivations, not the truth of a mathematical registry.
Only `show` requires a closed derivation. `explain` never adds an assumption.
Python >= 3.10, standard library only.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import product
import json
from pathlib import Path
import re
from typing import Iterable, Mapping

Support = frozenset[str]
IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")


class AlderError(ValueError):
    """Malformed input, invalid derivation, or an unresolved publication."""


@dataclass(frozen=True)
class Rule:
    name: str
    premises: tuple[str, ...]
    conclusion: str


@dataclass(frozen=True, eq=False)
class Proof:
    """Immutable DAG node. Leaf identities, not display names, carry scope."""
    kind: str                 # assumption, missing, rule
    atom: str
    reference: str
    children: tuple[Proof, ...] = ()


@dataclass
class Stats:
    rounds: int = 0
    insertions: int = 0
    combinations: int = 0
    max_antichain: int = 0


def validate_registry(atoms: Iterable[str], rules: Iterable[Rule]) -> tuple[tuple[str, ...], tuple[Rule, ...]]:
    aa, rr = tuple(atoms), tuple(rules)
    if len(set(aa)) != len(aa) or any(not IDENT.fullmatch(a) for a in aa):
        raise AlderError("Atoms must have unique ASCII identifiers")
    if len({r.name for r in rr}) != len(rr):
        raise AlderError("Duplicate rule identifier")
    for r in rr:
        if not IDENT.fullmatch(r.name):
            raise AlderError("Invalid rule identifier")
        if r.conclusion not in aa or any(p not in aa for p in r.premises):
            raise AlderError(f"Undeclared atom in rule {r.name}")
    return aa, rr


def check_proof(proof: Proof, target: str, rules: Mapping[str, Rule],
                assumptions: Mapping[str, str], residuals: frozenset[str] = frozenset()) -> Support:
    """Independent recursive checker; returns the *actual* missing support.

    Assumptions are exact active id -> proposition bindings. A stale leaf or a
    changed rule/target is refused. No engine support annotation is trusted.
    """
    active: set[int] = set()
    done: dict[int, Support] = {}

    def visit(p: Proof) -> Support:
        if not isinstance(p, Proof):
            raise AlderError("Not a proof node")
        key = id(p)
        if key in active:
            raise AlderError("Cyclic proof graph")
        if key in done:
            return done[key]
        active.add(key)
        if p.kind == "assumption":
            if p.children or assumptions.get(p.reference) != p.atom:
                raise AlderError("Unknown, stale, or reassociated assumption")
            s = frozenset()
        elif p.kind == "missing":
            if p.children or p.reference != p.atom or p.atom not in residuals:
                raise AlderError("Unauthorized missing-premise leaf")
            s = frozenset({p.atom})
        elif p.kind == "rule":
            r = rules.get(p.reference)
            if r is None or r.conclusion != p.atom:
                raise AlderError("Unknown rule or changed conclusion")
            if len(p.children) != len(r.premises):
                raise AlderError("Rule arity mismatch")
            if any(c.atom != a for c, a in zip(p.children, r.premises)):
                raise AlderError("Rule premise mismatch")
            s = frozenset().union(*(visit(c) for c in p.children))
        else:
            raise AlderError("Unknown proof constructor")
        active.remove(key)
        done[key] = s
        return s

    if proof.atom != target:
        raise AlderError("Proof does not prove the requested target")
    return visit(proof)


def infer(atoms: Iterable[str], rules: Iterable[Rule], known: Mapping[str, Proof],
          missing: Iterable[str] = (), *, max_insertions: int | None = None
          ) -> tuple[dict[str, dict[Support, Proof]], Stats]:
    """Least antichain fixed point, exact for the supplied finite Horn graph.

    A budget exception is UNKNOWN, never false. Existing derivations remain
    valid when their nonminimal support is removed from an index. Nodes are
    immutable and can keep references to those earlier derivations.
    """
    aa, rr = validate_registry(atoms, rules)
    mm = frozenset(missing)
    if not mm <= set(aa) or not set(known) <= set(aa):
        raise AlderError("Undeclared seed or repair atom")
    table: dict[str, dict[Support, Proof]] = {a: {} for a in aa}
    stats = Stats()

    def add(a: str, s: Support, p: Proof) -> bool:
        row = table[a]
        if any(t <= s for t in row):
            return False
        if max_insertions is not None and stats.insertions >= max_insertions:
            raise AlderError("UNKNOWN: inference insertion budget exhausted")
        for t in tuple(row):
            if s < t:
                del row[t]
        row[s] = p
        stats.insertions += 1
        stats.max_antichain = max(stats.max_antichain, len(row))
        return True

    for a, p in known.items():
        if p.atom != a:
            raise AlderError("Seed proof/atom mismatch")
        add(a, frozenset(), p)
    for a in sorted(mm):
        add(a, frozenset({a}), Proof("missing", a, a))

    changed = True
    while changed:
        changed = False
        stats.rounds += 1
        for r in rr:
            # Snapshot each row; recursive rules must only use existing nodes.
            choices = [tuple(table[a].items()) for a in r.premises]
            for selected in product(*choices):
                stats.combinations += 1
                support = frozenset().union(*(s for s, _ in selected))
                children = tuple(p for _, p in selected)
                changed |= add(r.conclusion, support,
                               Proof("rule", r.conclusion, r.name, children))
    return table, stats


def closure(atoms: Iterable[str], rules: Iterable[Rule], seeds: Iterable[str]) -> frozenset[str]:
    """Plain Boolean forward chaining: independent oracle for finite tests."""
    aa, rr = validate_registry(atoms, rules)
    out = set(seeds)
    if not out <= set(aa):
        raise AlderError("Unknown seed")
    while True:
        enlarged = out | {r.conclusion for r in rr if set(r.premises) <= out}
        if enlarged == out:
            return frozenset(out)
        out = enlarged


def lean_declaration(name: str, atoms: tuple[str, ...], rules: tuple[Rule, ...],
                     assumptions: Mapping[str, str], p: Proof,
                     residuals: Support = frozenset()) -> str:
    """Emit a theorem whose registry and assumptions are explicit parameters.

    Atom/rule/user names cannot inject Lean syntax: all generated identifiers
    are internally assigned. The checker is called again before emission.
    """
    validate_registry(atoms, rules)
    if not IDENT.fullmatch(name):
        raise AlderError("Invalid generated declaration name")
    if not set(assumptions.values()) <= set(atoms) or not residuals <= set(atoms):
        raise AlderError("Undeclared proposition in generated context")
    check_proof(p, p.atom, {r.name: r for r in rules}, assumptions, residuals)
    aa = {a: f"P{i}" for i, a in enumerate(atoms)}
    rr = {r.name: f"r{i}" for i, r in enumerate(rules)}
    hh = {h: f"h{i}" for i, h in enumerate(assumptions)}
    mm = {a: f"m{i}" for i, a in enumerate(sorted(residuals))}
    lines = [f"-- Source claim: {name}; target atom: {p.atom}",
             f"theorem {name} ({' '.join(aa.values())} : Prop)"]
    for r in rules:
        tp = " -> ".join(aa[a] for a in (*r.premises, r.conclusion))
        lines.append(f"    ({rr[r.name]} : {tp})")
    for h, a in assumptions.items():
        lines.append(f"    ({hh[h]} : {aa[a]})")
    for a in sorted(residuals):
        lines.append(f"    ({mm[a]} : {aa[a]})")
    lines.append(f"    : {aa[p.atom]} := by")
    # Emit let-bound DAG nodes rather than repeatedly expanding proof trees.
    ids: dict[int, str] = {}

    def emit(node: Proof) -> str:
        if node.kind == "assumption":
            return hh[node.reference]
        if node.kind == "missing":
            return mm[node.atom]
        if id(node) in ids:
            return ids[id(node)]
        args = [emit(c) for c in node.children]
        v = f"p{len(ids)}"
        ids[id(node)] = v
        rhs = " ".join([rr[node.reference], *args])
        lines.append(f"  have {v} : {aa[node.atom]} := {rhs}")
        return v
    final = emit(p)
    lines.extend([f"  exact {final}", ""])
    return "\n".join(lines)


@dataclass
class Compilation:
    lean: str
    events: list[dict]


def compile_source(text: str) -> Compilation:
    """Parse Alder-0. Rules/atoms precede executable commands; scopes are lexical.

    `begin`/`end` test assumption lifetime, NOT disjunction elimination. Every
    `show` is independently checked, including those not used by another show.
    Compilation raises before output is written if any displayed claim fails.
    """
    atoms: list[str] = []
    rules: list[Rule] = []
    known: dict[str, Proof] = {}
    assumptions: dict[str, str] = {}
    repairs: frozenset[str] = frozenset()
    stack: list[tuple[dict, dict, frozenset]] = []
    statements: list[str] = []
    events: list[dict] = []
    execution_started = False
    assumption_count = 0

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            op, _, rest = line.partition(" ")
            if op == "atoms":
                if execution_started:
                    raise AlderError("Atoms must be sealed before proof work")
                atoms.extend(rest.split())
                validate_registry(atoms, rules)
            elif op == "rule":
                if execution_started:
                    raise AlderError("Registry must be sealed before proof work")
                match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*?)\s*->\s*([A-Za-z][A-Za-z0-9_]*)", rest)
                if not match:
                    raise AlderError("Expected rule NAME : P & Q -> R")
                name, lhs, rhs = match.groups()
                premises = () if lhs == "_" else tuple(a.strip() for a in lhs.split("&"))
                rules.append(Rule(name, premises, rhs))
                validate_registry(atoms, rules)
            else:
                execution_started = True
                validate_registry(atoms, rules)
                if op == "begin":
                    if rest and not IDENT.fullmatch(rest):
                        raise AlderError("Invalid block name")
                    stack.append((dict(known), dict(assumptions), repairs))
                elif op == "end":
                    if rest or not stack:
                        raise AlderError("Unmatched or malformed end")
                    known, assumptions, repairs = stack.pop()
                elif op in {"assume", "repair"}:
                    names = rest.split()
                    if any(a not in atoms for a in names):
                        raise AlderError("Unknown atom")
                    if op == "repair":
                        repairs = frozenset(names)
                    else:
                        for a in names:
                            h = f"assumption_{assumption_count}"
                            assumption_count += 1
                            assumptions[h] = a
                            known[a] = Proof("assumption", a, h)
                elif op in {"show", "explain"}:
                    if rest not in atoms:
                        raise AlderError("Expected one declared target atom")
                    # Verify seed derivations before using them as known facts.
                    reg = {r.name: r for r in rules}
                    for a, p in known.items():
                        check_proof(p, a, reg, assumptions)
                    table, stats = infer(atoms, rules, known, repairs)
                    alternatives = sorted(table[rest], key=lambda s: (len(s), sorted(s)))
                    ev = {"line": lineno, "command": op, "target": rest,
                          "alternatives": [sorted(s) for s in alternatives],
                          "depth": len(stack), "stats": vars(stats)}
                    events.append(ev)
                    if op == "show":
                        p = table[rest].get(frozenset())
                        if p is None:
                            raise AlderError(f"Unresolved show {rest}; sufficient repair sets: {ev['alternatives']}")
                        check_proof(p, rest, reg, assumptions)
                        statements.append(lean_declaration(f"claim{len(statements)}", tuple(atoms),
                                                          tuple(rules), assumptions, p))
                        known[rest] = p
                    else:
                        for s in alternatives:
                            p = table[rest][s]
                            if check_proof(p, rest, reg, assumptions, s) != s:
                                raise AlderError("Engine/checker support discrepancy")
                            statements.append(lean_declaration(f"residual{len(statements)}", tuple(atoms),
                                                              tuple(rules), assumptions, p, s))
                else:
                    raise AlderError(f"Unknown command {op!r}")
        except AlderError as e:
            raise AlderError(f"line {lineno}: {e}") from e
    if stack:
        raise AlderError("Unclosed lexical block")
    header = ("-- Generated by Alder-0. NOT kernel-checked in this delivery.\n"
              "-- Rules are explicit theorem parameters, not asserted mathematical facts.\n"
              "set_option autoImplicit false\nnamespace AlderGenerated\n\n")
    return Compilation(header + "\n".join(statements) + "\nend AlderGenerated\n", events)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    ns = parser.parse_args()
    try:
        result = compile_source(ns.source.read_text(encoding="utf-8"))
    except (AlderError, OSError) as e:
        parser.exit(1, f"Alder: {e}\n")
    # No outputs are touched until the complete module has passed its checks.
    ns.lean.parent.mkdir(parents=True, exist_ok=True)
    ns.events.parent.mkdir(parents=True, exist_ok=True)
    ns.lean.write_text(result.lean, encoding="utf-8")
    ns.events.write_text(json.dumps(result.events, indent=2) + "\n", encoding="utf-8")
    print(f"Accepted {len(result.events)} proof/explanation requests; wrote {ns.lean}")


if __name__ == "__main__":
    main()
