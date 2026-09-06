#!/usr/bin/env python3
"""Bryony's finite, propositional requirement engine (Python 3.9+).

This is not a Lean elaborator. Atom names denote arbitrary propositions;
registered rules are input assumptions, not checked mathematical theorems.
The engine retains inclusion-minimal prospective premise sets and immutable
proof trees. A separate replay checker checks trees without rerunning search.
Exported Lean theorems quantify over the propositions and rule assumptions.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re
from typing import Dict, FrozenSet, List, Mapping, Optional, Sequence, Tuple

IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")

@dataclass(frozen=True)
class Rule:
    name: str
    premises: Tuple[str, ...]
    conclusion: str

@dataclass(frozen=True)
class Program:
    context: str
    candidate: str
    policy: str
    atoms: Tuple[str, ...]
    known: FrozenSet[str]
    prospective: FrozenSet[str]
    rules: Tuple[Rule, ...]
    goal: str

    def validate(self) -> None:
        names = (self.context, self.candidate, self.policy, *self.atoms,
                 *(r.name for r in self.rules))
        if any(not IDENT.fullmatch(n) for n in names):
            raise ValueError("Names must be nonempty ASCII identifiers")
        if len(set(self.atoms)) != len(self.atoms):
            raise ValueError("Duplicate atom")
        if len({r.name for r in self.rules}) != len(self.rules):
            raise ValueError("Duplicate rule name")
        used = self.known | self.prospective | {self.goal}
        for rule in self.rules:
            used |= set(rule.premises) | {rule.conclusion}
        if not used <= set(self.atoms):
            raise ValueError("Undeclared atoms: " + repr(sorted(used - set(self.atoms))))

    def snapshot(self) -> dict:
        return {"context": self.context, "candidate": self.candidate,
                "policy": self.policy, "atoms": list(self.atoms),
                "known": sorted(self.known), "prospective": sorted(self.prospective),
                "rules": [{"name": r.name, "premises": list(r.premises),
                           "conclusion": r.conclusion} for r in self.rules],
                "goal": self.goal}

    def digest(self) -> str:
        data = json.dumps(self.snapshot(), sort_keys=True, separators=(",", ":"))
        return sha256(data.encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class Proof:
    atom: str
    kind: str                  # known, prospective, or rule
    rule: str = ""
    children: Tuple[Proof, ...] = ()

    def encode(self) -> dict:
        return {"atom": self.atom, "kind": self.kind, "rule": self.rule,
                "children": [c.encode() for c in self.children]}

@dataclass
class SearchResult:
    labels: Dict[str, Dict[FrozenSet[str], Proof]]
    rounds: int
    insertions: int
    rule_combinations: int


def parse(text: str) -> Program:
    """Parse the intentionally tiny DSL. No expressions or implicit atoms."""
    scalars: Dict[str, str] = {}
    lists: Dict[str, List[str]] = {"atoms": [], "known": [], "prospect": []}
    rules: List[Rule] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            key, value = line.split(None, 1)
            if key in ("context", "candidate", "policy", "goal"):
                if key in scalars:
                    raise ValueError("Repeated " + key)
                scalars[key] = value.strip()
            elif key in lists:
                lists[key].extend(value.split())
            elif key == "rule":
                name, expression = value.split(":", 1)
                left, right = expression.split("=>", 1)
                premises = () if left.strip() == "true" else tuple(
                    part.strip() for part in left.split("&"))
                rules.append(Rule(name.strip(), premises, right.strip()))
            else:
                raise ValueError("Unknown command " + key)
        except ValueError as exc:
            raise ValueError(f"Line {lineno}: {exc}") from exc
    missing = {"context", "candidate", "policy", "goal"} - scalars.keys()
    if missing:
        raise ValueError("Missing declarations: " + repr(sorted(missing)))
    p = Program(scalars["context"], scalars["candidate"], scalars["policy"],
                tuple(lists["atoms"]), frozenset(lists["known"]),
                frozenset(lists["prospect"]), tuple(rules), scalars["goal"])
    p.validate()
    return p


def solve(p: Program, max_insertions: Optional[int] = None) -> SearchResult:
    """Least fixed point with antichain pruning; no completeness after a budget error.

    Equal-support alternatives keep their first proof. This does not optimize
    proof size, running time, or proof method. Policies must select the registry
    before this routine. Each proof node contains older immutable proof trees.
    """
    p.validate()
    labels: Dict[str, Dict[FrozenSet[str], Proof]] = {a: {} for a in p.atoms}
    insertions = 0
    combinations = 0

    def insert(atom: str, support: FrozenSet[str], proof: Proof) -> bool:
        nonlocal insertions
        table = labels[atom]
        if any(old <= support for old in table):
            return False
        if max_insertions is not None and insertions >= max_insertions:
            raise RuntimeError("Budget exhausted; no fixed-point completeness claim")
        for old in tuple(table):
            if support < old:
                del table[old]
        table[support] = proof
        insertions += 1
        return True

    for atom in sorted(p.known):
        insert(atom, frozenset(), Proof(atom, "known"))
    for atom in sorted(p.prospective):
        insert(atom, frozenset({atom}), Proof(atom, "prospective"))
    rounds = 0
    while True:
        rounds += 1
        changed = False
        for rule in p.rules:
            # Snapshot each premise table: a conclusion may equal a premise.
            options = [tuple(labels[a].items()) for a in rule.premises]
            for choices in product(*options):
                combinations += 1
                support = frozenset().union(*(s for s, _ in choices))
                proof = Proof(rule.conclusion, "rule", rule.name,
                              tuple(t for _, t in choices))
                changed = insert(rule.conclusion, support, proof) or changed
        if not changed:
            return SearchResult(labels, rounds, insertions, combinations)


def certificate(p: Program, support: FrozenSet[str], proof: Proof) -> dict:
    return {"schema": 1, "snapshot": p.snapshot(), "digest": p.digest(),
            "goal": p.goal, "support": sorted(support), "proof": proof.encode()}


def replay(p: Program, cert: Mapping, max_nodes: int = 100000) -> FrozenSet[str]:
    """Independent structural replay. Reject malformed or stale certificates.

    Full snapshot equality, not hash equality, is used at this model boundary.
    This is NOT a substitute for Lean checking of real contexts and theorem types.
    """
    p.validate()
    if cert.get("schema") != 1 or cert.get("snapshot") != p.snapshot():
        raise ValueError("Schema or exact source snapshot mismatch")
    if cert.get("digest") != p.digest() or cert.get("goal") != p.goal:
        raise ValueError("Digest or demanded goal mismatch")
    rules = {r.name: r for r in p.rules}
    count = 0
    active: set = set()

    def visit(node: Mapping, expected: str) -> FrozenSet[str]:
        nonlocal count
        count += 1
        if count > max_nodes:
            raise ValueError("Replay budget exhausted")
        if not isinstance(node, dict) or id(node) in active:
            raise ValueError("Malformed or cyclic certificate")
        if set(node) != {"atom", "kind", "rule", "children"}:
            raise ValueError("Malformed node fields")
        if node["atom"] != expected or not isinstance(node["children"], list):
            raise ValueError("Wrong proposition or children")
        active.add(id(node))
        try:
            kind = node["kind"]
            if kind in ("known", "prospective"):
                if node["children"] or node["rule"]:
                    raise ValueError("A leaf has a rule or children")
                pool = p.known if kind == "known" else p.prospective
                if expected not in pool:
                    raise ValueError("Unlicensed leaf")
                return frozenset() if kind == "known" else frozenset({expected})
            if kind != "rule" or node["rule"] not in rules:
                raise ValueError("Unknown rule")
            r = rules[node["rule"]]
            if r.conclusion != expected or len(r.premises) != len(node["children"]):
                raise ValueError("Rule head or arity mismatch")
            return frozenset().union(*(visit(c, a) for c, a in
                                       zip(node["children"], r.premises)))
        finally:
            active.remove(id(node))

    support = visit(cert.get("proof"), p.goal)
    if cert.get("support") != sorted(support):
        raise ValueError("Claimed support differs from replayed support")
    return support


def export_lean(p: Program, result: SearchResult) -> str:
    """Ordinary proof terms for the abstract rules; not a math reifier."""
    atom_names = {a: f"p{i}" for i, a in enumerate(p.atoms)}
    rule_names = {r.name: f"r{i}" for i, r in enumerate(p.rules)}
    known_names = {a: f"k{i}" for i, a in enumerate(sorted(p.known))}
    out = ["-- Generated by Bryony's finite propositional reference model.",
           "-- NOT compiled in the preparation environment.",
           "-- Rules below are explicit hypotheses, not verified mathematical registrations.",
           "set_option autoImplicit false", "namespace BryonyExport", ""]
    out += [f"-- {atom_names[a]} = {a}" for a in p.atoms]
    for index, (support, proof) in enumerate(sorted(result.labels[p.goal].items(),
                                                   key=lambda t: (len(t[0]), sorted(t[0])))):
        cert = certificate(p, support, proof)
        replay(p, cert)
        hyp_names = {a: f"h{i}" for i, a in enumerate(sorted(support))}
        out += ["", f"-- Prospective premises: {', '.join(sorted(support)) or '(none)'}",
                f"theorem route_{index}",
                "    (" + " ".join(atom_names.values()) + " : Prop)"]
        for r in p.rules:
            typ = " -> ".join(atom_names[a] for a in (*r.premises, r.conclusion))
            out.append(f"    ({rule_names[r.name]} : {typ})")
        out += [f"    ({known_names[a]} : {atom_names[a]})" for a in sorted(p.known)]
        out += [f"    ({hyp_names[a]} : {atom_names[a]})" for a in sorted(support)]

        def term(t: Proof) -> str:
            if t.kind == "known":
                return known_names[t.atom]
            if t.kind == "prospective":
                return hyp_names[t.atom]
            args = " ".join("(" + term(c) + ")" for c in t.children)
            return rule_names[t.rule] + (" " + args if args else "")
        out += [f"    : {atom_names[p.goal]} :=", "  " + term(proof)]
    out += ["", "end BryonyExport", ""]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("--output", type=Path, default=Path("bryony-output"))
    args = ap.parse_args()
    try:
        p = parse(args.source.read_text(encoding="utf-8"))
        result = solve(p)
        certs = [certificate(p, s, t) for s, t in sorted(result.labels[p.goal].items(),
                                                       key=lambda x: (len(x[0]), sorted(x[0])))]
        for c in certs:
            replay(p, c)
        args.output.mkdir(parents=True, exist_ok=True)
        report = {"goal": p.goal, "digest": p.digest(),
                  "status": "closed" if frozenset() in result.labels[p.goal] else
                            "conditional" if certs else "unresolved",
                  "rounds": result.rounds, "insertions": result.insertions,
                  "rule_combinations": result.rule_combinations, "certificates": certs}
        (args.output / "requirements.json").write_text(json.dumps(report, indent=2)+"\n")
        (args.output / "Requirements.lean").write_text(export_lean(p, result))
        print(json.dumps({k: v for k, v in report.items() if k != "certificates"}, indent=2))
        print("Alternative supports:", [c["support"] for c in certs])
    except (OSError, ValueError, RuntimeError) as exc:
        ap.exit(2, str(exc) + "\n")

if __name__ == "__main__":
    main()
