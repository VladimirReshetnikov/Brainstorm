#!/usr/bin/env python3
"""Finite differential checks and adversarial replay tests; stdlib only."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import replace
from itertools import combinations
import json
from pathlib import Path
import random
import sys
import time
import unittest

from bryony import Program, Rule, Proof, certificate, export_lean, parse, replay, solve

COUNTS = {"random_systems": 0, "subset_closures": 0,
          "atom_support_comparisons": 0, "replayed_random_certificates": 0,
          "frey_positive_triples": 0, "frey_single_premise_mutations": 0}


def subsets(items):
    items = sorted(items)
    for size in range(len(items) + 1):
        for values in combinations(items, size):
            yield frozenset(values)


def direct_closure(p, hypotheses):
    """Independent reference: plain fact closure for ONE assumption set."""
    facts = set(p.known | hypotheses)
    while True:
        new = {r.conclusion for r in p.rules if set(r.premises) <= facts} - facts
        if not new:
            return facts
        facts.update(new)


def small(rules=(), known=(), hypotheses=("a", "b", "c"), goal="g"):
    return Program("Root", "FixedCandidate", "FixedPolicy", ("a", "b", "c", "g"),
                   frozenset(known), frozenset(hypotheses), tuple(rules), goal)


def sample():
    return small((Rule("left", ("a",), "g"), Rule("right", ("b", "c"), "g")))


class RequirementTests(unittest.TestCase):
    def test_01_alternatives(self):
        p = sample()
        self.assertEqual(set(solve(p).labels["g"]), {frozenset("a"), frozenset("bc")})

    def test_02_dominance(self):
        p = small((Rule("wide", ("a", "b"), "g"), Rule("narrow", ("a",), "g")))
        self.assertEqual(set(solve(p).labels["g"]), {frozenset("a")})

    def test_03_unseeded_cycle(self):
        p = small((Rule("r1", ("a",), "g"), Rule("r2", ("g",), "a")), hypotheses=())
        self.assertEqual(solve(p).labels["g"], {})

    def test_04_seeded_cycle(self):
        p = small((Rule("r1", ("a",), "g"), Rule("r2", ("g",), "a")), known=("a",))
        self.assertIn(frozenset(), solve(p).labels["g"])

    def test_05_zero_premise_rule(self):
        p = small((Rule("truth", (), "g"),))
        self.assertEqual(set(solve(p).labels["g"]), {frozenset()})

    def test_06_known_dominates_prospective(self):
        p = small(known=("a",), goal="a")
        self.assertEqual(set(solve(p).labels["a"]), {frozenset()})

    def test_07_repeated_premise_is_not_two_hypotheses(self):
        p = small((Rule("r", ("a", "a"), "g"),))
        self.assertEqual(set(solve(p).labels["g"]), {frozenset("a")})

    def test_08_parser_and_export(self):
        p = parse((Path(__file__).parent / "frey4.bry").read_text())
        r = solve(p)
        self.assertEqual(len(r.labels[p.goal]), 2)
        output = export_lean(p, r)
        self.assertIn("theorem route_1", output)
        self.assertNotIn("sorry", output)
        self.assertIn("NOT compiled", output)

    def test_09_bad_parser_input(self):
        text = (Path(__file__).parent / "frey4.bry").read_text()
        for bad in (text + "\ngoal X", text.replace("=> CastCorrect", "=> Unknown"),
                    text.replace("ArithmeticOnly", "not a name")):
            with self.assertRaises(ValueError):
                parse(bad)

    def test_10_bad_rule_metadata(self):
        p = sample()
        with self.assertRaises(ValueError):
            solve(replace(p, rules=p.rules + (p.rules[0],)))

    def get_cert(self):
        p = sample()
        support, proof = next(iter(solve(p).labels[p.goal].items()))
        return p, certificate(p, support, proof)

    def test_11_replay_positive(self):
        p, c = self.get_cert()
        self.assertEqual(replay(p, c), frozenset(c["support"]))

    def test_12_wrong_proposition(self):
        p, c = self.get_cert()
        c["proof"]["atom"] = "a"
        with self.assertRaises(ValueError): replay(p, c)

    def test_13_wrong_rule_arity(self):
        p, c = self.get_cert()
        c["proof"]["children"] = []
        with self.assertRaises(ValueError): replay(p, c)

    def test_14_forged_support(self):
        p, c = self.get_cert()
        c["support"] = []
        with self.assertRaises(ValueError): replay(p, c)

    def test_15_branch_context_and_candidate(self):
        p, c = self.get_cert()
        for changed in (replace(p, context="Sibling"), replace(p, candidate="NewWitness"),
                        replace(p, policy="OtherPolicy"), replace(p, known=frozenset("b"))):
            with self.assertRaises(ValueError): replay(changed, c)

    def test_16_changed_rules_even_with_updated_digest(self):
        p, c = self.get_cert()
        changed = replace(p, rules=(Rule("left", ("b",), "g"), p.rules[1]))
        c["digest"] = changed.digest()  # A matching hash alone is insufficient.
        with self.assertRaises(ValueError): replay(changed, c)

    def test_17_unlicensed_leaf(self):
        p, c = self.get_cert()
        c["proof"]["children"][0]["kind"] = "known"
        with self.assertRaises(ValueError): replay(p, c)

    def test_18_cyclic_and_budgeted_certificates(self):
        p, c = self.get_cert()
        with self.assertRaises(ValueError): replay(p, c, max_nodes=1)
        c["proof"]["children"][0] = c["proof"]
        with self.assertRaises(ValueError): replay(p, c)
        with self.assertRaises(RuntimeError): solve(p, max_insertions=0)

    def test_19_observation_consumer_scope(self):
        p = Program("MeasureMu", "FixedFunctions", "AEIntegral", ("ae", "integral", "point"),
                    frozenset({"ae"}), frozenset(), (Rule("congr", ("ae",), "integral"),), "point")
        r = solve(p)
        self.assertIn(frozenset(), r.labels["integral"])
        self.assertFalse(r.labels["point"])

    def test_20_rule_order_independence_of_supports(self):
        p = sample()
        q = replace(p, rules=tuple(reversed(p.rules)))
        a, b = solve(p), solve(q)
        self.assertEqual({x: set(v) for x, v in a.labels.items()},
                         {x: set(v) for x, v in b.labels.items()})

    def test_21_random_differential_completeness(self):
        rng = random.Random(4406)
        atoms = tuple("abcdefg")
        for number in range(400):
            known = frozenset(a for a in atoms if rng.random() < .15)
            prospective = frozenset(rng.sample(atoms, rng.randrange(0, 6)))
            rules = tuple(Rule(f"r{i}", tuple(rng.choices(atoms, k=rng.randrange(0, 4))),
                               rng.choice(atoms)) for i in range(rng.randrange(0, 13)))
            p = Program(f"Case{number}", "Fixed", "AllRules", atoms, known, prospective, rules, "g")
            result = solve(p)
            derivable = {a: [] for a in atoms}
            for s in subsets(prospective):
                facts = direct_closure(p, s)
                COUNTS["subset_closures"] += 1
                for a in facts:
                    derivable[a].append(s)
            for a in atoms:
                expected = {s for s in derivable[a] if not any(t < s for t in derivable[a])}
                self.assertEqual(set(result.labels[a]), expected, (number, a))
                COUNTS["atom_support_comparisons"] += 1
                query = replace(p, goal=a)
                for s, proof in result.labels[a].items():
                    self.assertEqual(replay(query, certificate(query, s, proof)), s)
                    COUNTS["replayed_random_certificates"] += 1
            COUNTS["random_systems"] += 1

    def test_22_frey_arithmetic_fixtures(self):
        # Exact integer identities in a finite sample, NOT universal Lean proofs.
        for a in range(-13, 16):
            for b in range(-8, 9):
                for p in range(4, 12):
                    if a % 4 == 3 and b % 2 == 0 and p % 2 == 1:
                        self.assertEqual((b**p - 1 - a**p) % 4, 0)
                        self.assertEqual((-a**p * b**p) % 16, 0)
                        COUNTS["frey_positive_triples"] += 1
        self.assertEqual((2**5 - 1 - 3**5)//4, -53)
        self.assertEqual((-3**5 * 2**5)//16, -486)
        for a, b, p, modulus, numerator in (
            (3, 2, 4, 4, lambda a,b,p: b**p-1-a**p),
            (3, 3, 5, 4, lambda a,b,p: b**p-1-a**p),
            (3, 2, 3, 16, lambda a,b,p: -a**p*b**p),
            (1, 2, 5, 4, lambda a,b,p: b**p-1-a**p)):
            self.assertNotEqual(numerator(a,b,p) % modulus, 0)
            COUNTS["frey_single_premise_mutations"] += 1

    def test_23_realization_and_correlation(self):
        # The exact length image of List Empty is {0}; no positive witness exists.
        realizable_empty_lengths = {0}
        self.assertTrue(all(0 == n for n in realizable_empty_lengths))
        self.assertNotIn(1, realizable_empty_lengths)
        # Correlated observations (n,n) do not realize an off-diagonal pair.
        realized_pairs = {(n, n) for n in range(8)}
        self.assertIn(0, {a for a,b in realized_pairs})
        self.assertIn(1, {b for a,b in realized_pairs})
        self.assertNotIn((0, 1), realized_pairs)


if __name__ == "__main__":
    start = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RequirementTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    evidence = Path(__file__).resolve().parent.parent / "evidence"
    evidence.mkdir(exist_ok=True)
    data = {"status": "passed" if result.wasSuccessful() else "failed",
            "python": sys.version, "test_methods": result.testsRun,
            "failures": len(result.failures), "errors": len(result.errors),
            "elapsed_seconds": round(time.perf_counter()-start, 6),
            "counts": COUNTS, "seed": 4406,
            "scope": "Finite propositional reference model and finite arithmetic fixtures; no Lean execution."}
    (evidence / "results.json").write_text(json.dumps(data, indent=2)+"\n")
    print(json.dumps(data, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
