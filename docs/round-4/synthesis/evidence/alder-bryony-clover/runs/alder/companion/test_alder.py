#!/usr/bin/env python3
"""Run exhaustive finite and deterministic regression tests; retain exact counts.

No Lean toolchain is invoked. Exhaustive means ONLY the explicitly specified
finite family (three atoms / six possible unary edges), not all Horn theories.
"""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction
from itertools import product
import hashlib
import json
from pathlib import Path
import platform
import random
import time
from alder_core import (AlderError, Rule, Proof, infer, closure, check_proof,
                        compile_source)
from observations import (Affine, ListExpr, frame_equal, germ_coefficients,
                          germ_closed_coefficient, residual)


def subsets(items):
    items = tuple(items)
    return [frozenset(a for i, a in enumerate(items) if mask >> i & 1)
            for mask in range(1 << len(items))]


def expect_error(f):
    try:
        f()
    except (AlderError, ValueError):
        return
    raise AssertionError("Expected a rejection")


def run():
    start = time.perf_counter()
    counts = {}
    aa = ("a", "b", "c")
    edges = [(a, b) for a in aa for b in aa if a != b]
    graphs = seeds_count = support_probes = checks = 0
    for mask in range(1 << len(edges)):
        rr = tuple(Rule(f"r{i}", (a,), b) for i, (a, b) in enumerate(edges) if mask >> i & 1)
        graphs += 1
        for known_set in subsets(aa):
            ass = {f"h{i}": a for i, a in enumerate(sorted(known_set))}
            known = {a: Proof("assumption", a, h) for h, a in ass.items()}
            for missing in subsets(aa):
                seeds_count += 1
                table, stats = infer(aa, rr, known, missing)
                for a in aa:
                    for s, p in table[a].items():
                        assert check_proof(p, a, {r.name: r for r in rr}, ass, missing) == s
                        checks += 1
                for support in subsets(missing):
                    truth = closure(aa, rr, known_set | support)
                    support_probes += 1
                    for a in aa:
                        assert (a in truth) == any(s <= support for s in table[a])
    counts["unary_graphs"] = graphs
    counts["unary_seed_repair_configurations"] = seeds_count
    counts["unary_support_oracle_probes"] = support_probes
    counts["unary_returned_derivations_checked"] = checks

    rng = random.Random(20260906)
    aa = tuple(f"p{i}" for i in range(5))
    probes = derivations = 0
    for case in range(200):
        rr = tuple(Rule(f"r{i}", tuple(rng.sample(aa, rng.randrange(4))), rng.choice(aa))
                   for i in range(9))
        known_set = frozenset(a for a in aa if rng.randrange(3) == 0)
        missing = frozenset(a for a in aa if rng.randrange(2))
        ass = {f"h{i}": a for i, a in enumerate(sorted(known_set))}
        known = {a: Proof("assumption", a, h) for h, a in ass.items()}
        table, _ = infer(aa, rr, known, missing)
        for a in aa:
            for s, p in table[a].items():
                assert check_proof(p, a, {r.name: r for r in rr}, ass, missing) == s
                derivations += 1
        for support in subsets(missing):
            truth = closure(aa, rr, known_set | support)
            for a in aa:
                assert (a in truth) == any(s <= support for s in table[a])
            probes += 1
    counts["conjunctive_random_graphs"] = 200
    counts["conjunctive_support_oracle_probes"] = probes
    counts["conjunctive_returned_derivations_checked"] = derivations

    # Error cases run at the actual parser and/or independent checker boundary.
    rr = {"r": Rule("r", ("a",), "b")}
    h = Proof("assumption", "a", "scope0_h")
    p = Proof("rule", "b", "r", (h,))
    ass = {"scope0_h": "a"}
    bad = [
        lambda: check_proof(p, "a", rr, ass),
        lambda: check_proof(p, "b", rr, {}),
        lambda: check_proof(p, "b", rr, {"scope0_h": "b"}),
        lambda: check_proof(replace(p, children=()), "b", rr, ass),
        lambda: check_proof(replace(p, reference="unknown"), "b", rr, ass),
        lambda: check_proof(p, "b", {"r": Rule("r", ("a",), "c")}, ass),
        lambda: check_proof(Proof("missing", "b", "b"), "b", rr, ass),
        lambda: compile_source("atoms a\nshow a"),
        lambda: compile_source("atoms a\nrepair a\nexplain a\nshow a"),
        lambda: compile_source("atoms a b\nrule r : a -> b\nassume a\nshow b\natoms c"),
        lambda: compile_source("atoms a\nbegin block\nassume a"),
        lambda: compile_source("atoms a\nend"),
        lambda: infer(("a", "b"), tuple(rr.values()), {"a": h}, (), max_insertions=1),
    ]
    cyc = Proof("rule", "a", "loop")
    object.__setattr__(cyc, "children", (cyc,))
    bad.append(lambda: check_proof(cyc, "a", {"loop": Rule("loop", ("a",), "a")}, {}))
    for f in bad:
        expect_error(f)
    here = Path(__file__).parent
    for name in ("scope_rejected", "unused_claim_rejected"):
        expect_error(lambda name=name: compile_source((here / "examples" / (name + ".alder")).read_text()))
    counts["parser_checker_expected_rejections"] = len(bad) + 2
    good = []
    for name in ("quotient", "locality"):
        result = compile_source((here / "examples" / (name + ".alder")).read_text())
        good.extend(result.events)
        (here / "generated" / (name.capitalize() + ".lean")).write_text(result.lean)
        (here / "generated" / (name + ".json")).write_text(json.dumps(result.events, indent=2) + "\n")
    assert good[0]["alternatives"] == [["positive"], ["unit"]]
    assert good[2]["alternatives"] == good[0]["alternatives"]
    counts["accepted_source_requests"] = len(good)

    # Soundness of the grammar's affine length model on finite environments.
    def expr(depth):
        if depth == 0:
            return ListExpr("var", rng.randrange(3)) if rng.randrange(2) else ListExpr("nil")
        tag = rng.choice(("nil", "var", "cons", "append", "reverse", "map"))
        n = {"nil": 0, "var": 0, "cons": 1, "append": 2, "reverse": 1, "map": 1}[tag]
        return ListExpr(tag, rng.randrange(3), tuple(expr(depth-1) for _ in range(n)))
    evaluations = 0
    for _ in range(300):
        e = expr(4)
        model = e.model(3)
        for lengths in product(range(4), repeat=3):
            env = [list(range(n)) for n in lengths]
            assert len(e.evaluate(env)) == model(lengths)
            evaluations += 1
    counts["list_grammar_expressions"] = 300
    counts["list_interpreter_model_comparisons"] = evaluations

    # Pairs of affine forms, tested on three genuinely different images.
    forms = [Affine(c, (a, b)) for c, a, b in product(range(-2, 3), repeat=3)]
    domains = [
        ("independent", ((0, 0), (1, 0), (0, 1)), tuple(product(range(6), repeat=2))),
        ("empty", ((0, 0),), ((0, 0),)),
        ("diagonal", ((0, 0), (1, 1)), tuple((n, n) for n in range(12))),
    ]
    image_pairs = 0
    for name, frame, inputs in domains:
        for f, g in product(forms, repeat=2):
            assert frame_equal(f, g, frame) == all(f(x) == g(x) for x in inputs)
            image_pairs += 1
    # Raw coefficients differ but the *source laws* are equal on these images.
    x, y, z = Affine(0, (1, 0)), Affine(0, (0, 1)), Affine(0, (0, 0))
    assert x != y and frame_equal(x, y, ((0, 0), (1, 1)))
    assert x != z and frame_equal(x, z, ((0, 0),))
    assert not frame_equal(x, z, ((0, 0), (1, 0), (0, 1)))
    expect_error(lambda: frame_equal(x, z, ((1,),)))
    counts["affine_domain_kinds"] = len(domains)
    counts["affine_form_pair_frame_comparisons"] = image_pairs
    counts["observation_arity_expected_rejections"] = 1

    jet = germ_coefficients(33)
    for n in range(33):
        assert jet[n] == germ_closed_coefficient(n)
    assert all(c == 0 for c in residual(jet))
    changed = 0
    for k in range(1, 25):
        for delta in (-1, 1):
            perturbed = list(jet)
            perturbed[k] += delta
            r = residual(perturbed)
            assert all(r[j] == 0 for j in range(k)) and r[k] == delta
            changed += 1
    other = tuple((-Fraction(1, 4) - c if i == 0 else -c) for i, c in enumerate(jet))
    assert all(c == 0 for c in residual(other)) and other[0] != 0
    counts["germ_closed_formula_coefficients"] = len(jet)
    counts["germ_residual_mutations"] = changed
    counts["wrong_branch_residual_control"] = 1
    # Nonzero derivative 2 in Z/4 is not a unit: 2*(2Q)=0.
    assert 2 % 4 != 0 and (2 * 2) % 4 == 0
    counts["nonunit_derivative_control"] = 1

    elapsed = time.perf_counter() - start
    return {"status": "passed", "python": platform.python_version(),
            "elapsed_seconds_including_oracles": round(elapsed, 6), "counts": counts,
            "lean_execution": "NOT RUN: no Lean executable available in this environment",
            "scope": "Finite propositional frontend; exact arithmetic companions. Not a Lean elaborator or usability study.",
            "sources_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(here.glob("*.py"))}}


if __name__ == "__main__":
    result = run()
    target = Path(__file__).parent.parent / "evidence" / "test_results.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
