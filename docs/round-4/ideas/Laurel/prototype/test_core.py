#!/usr/bin/env python3
"""Executable checks of Laurel-Core. None is a Lean-kernel run."""
from __future__ import annotations
from dataclasses import replace
from itertools import combinations
import json
from pathlib import Path
import platform
import random
import sys
import time
import unittest
from laurel_core import Profile, Rule, Proof, infer, check_proof, parse, export_lean, summary, reopen_known


def powerset(values):
    values = tuple(values)
    return [frozenset(c) for n in range(len(values) + 1) for c in combinations(values, n)]


def oracle(profile):
    """Independent oracle: enumerate assumptions, then Boolean forward closure."""
    supports = {a: [] for a in profile.atoms}
    for h in powerset(sorted(profile.offers)):
        closed = set(profile.known | h)
        while True:
            before = len(closed)
            for rule in profile.rules:
                if all(p in closed for p in rule.premises):
                    closed.add(rule.conclusion)
            if len(closed) == before:
                break
        for a in closed:
            supports[a].append(h)
    return {a: {h for h in hs if not any(j < h for j in hs)}
            for a, hs in supports.items()}


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.p = Profile('test', ('a', 'b', 'c'), frozenset({'a'}),
                         frozenset({'b'}), (Rule('ab', ('a',), 'b'),
                                             Rule('bc', ('b',), 'c')))

    def test_closes_without_offered_premise(self):
        r = infer(self.p)
        self.assertEqual(set(r.frontiers['c']), {frozenset()})
        check_proof(self.p, r.frontiers['c'][frozenset()], 'c', frozenset())

    def test_unseeded_cycle_does_not_close(self):
        p = replace(self.p, known=frozenset(), offers=frozenset(),
                    rules=(Rule('ab', ('a',), 'b'), Rule('ba', ('b',), 'a')))
        self.assertEqual(infer(p).frontiers['a'], {})

    def test_empty_rule(self):
        p = replace(self.p, known=frozenset(), offers=frozenset(),
                    rules=(Rule('fact', (), 'c'),))
        r = infer(p)
        check_proof(p, r.frontiers['c'][frozenset()], 'c', frozenset())

    def test_alternatives_not_conjunction(self):
        p = replace(self.p, known=frozenset(), offers=frozenset({'a', 'b'}),
                    rules=(Rule('ac', ('a',), 'c'), Rule('bc', ('b',), 'c')))
        self.assertEqual(set(infer(p).frontiers['c']),
                         {frozenset({'a'}), frozenset({'b'})})

    def test_duplicate_premise(self):
        p = replace(self.p, rules=(Rule('aac', ('a', 'a'), 'c'),))
        r = infer(p)
        check_proof(p, r.frontiers['c'][frozenset()], 'c', frozenset())

    def test_nonempty_support_is_conditional(self):
        p = replace(self.p, known=frozenset(), rules=(Rule('bc', ('b',), 'c'),))
        r = infer(p)
        self.assertEqual(summary(p, r, 'c')['status'], 'conditional')
        root = r.frontiers['c'][frozenset({'b'})]
        with self.assertRaises(ValueError):
            check_proof(p, root, 'c', frozenset())

    def test_budget_is_not_refutation(self):
        r = infer(self.p, 0)
        self.assertFalse(r.complete)
        self.assertEqual(summary(self.p, r, 'c')['status'], 'inconclusive')

    def test_wrong_target(self):
        r = infer(self.p)
        with self.assertRaises(ValueError):
            check_proof(self.p, r.frontiers['c'][frozenset()], 'a', frozenset())

    def test_changed_rule_profile(self):
        root = infer(self.p).frontiers['c'][frozenset()]
        p2 = replace(self.p, rules=(Rule('ab', ('c',), 'b'), Rule('bc', ('b',), 'c')))
        with self.assertRaises(ValueError):
            check_proof(p2, root, 'c', frozenset())

    def test_sibling_context(self):
        root = infer(self.p).frontiers['c'][frozenset()]
        with self.assertRaises(ValueError):
            check_proof(replace(self.p, context='sibling'), root, 'c', frozenset())

    def test_forged_rule(self):
        root = infer(self.p).frontiers['c'][frozenset()]
        with self.assertRaises(ValueError):
            check_proof(self.p, replace(root, rule='absent'), 'c', frozenset())

    def test_forged_known_leaf(self):
        fp = self.p.fingerprint()
        with self.assertRaises(ValueError):
            check_proof(self.p, Proof(fp, 'c', 'known'), 'c', frozenset())

    def test_forged_premise_order(self):
        p = replace(self.p, known=frozenset({'a', 'b'}),
                    rules=(Rule('abc', ('a', 'b'), 'c'),))
        root = infer(p).frontiers['c'][frozenset()]
        with self.assertRaises(ValueError):
            check_proof(p, replace(root, children=tuple(reversed(root.children))), 'c', frozenset())

    def test_bad_syntax(self):
        for s in ('context x\natoms a\nshow b',
                  'context x\natoms a a\nshow a',
                  'context x\natoms a\nrule r : b -> a\nshow a'):
            with self.assertRaises(ValueError):
                parse(s)

    def test_export_retains_assumptions(self):
        p = replace(self.p, known=frozenset(), rules=(Rule('bc', ('b',), 'c'),))
        s = export_lean(p, 'c', infer(p).frontiers['c'])
        self.assertIn('(h0 : P1)', s)
        self.assertIn('(r0 : P1 -> P2)', s)
        self.assertNotIn('sorry', s)
        self.assertNotIn('\naxiom ', s)

    def test_target_as_residual_is_only_conditional(self):
        p = replace(self.p, known=frozenset(), offers=frozenset({'c'}), rules=())
        r = infer(p)
        self.assertEqual(set(r.frontiers['c']), {frozenset({'c'})})
        self.assertEqual(summary(p, r, 'c')['status'], 'conditional')

    def test_loss_of_used_fact_reopens_obligation(self):
        root = infer(self.p).frontiers['c'][frozenset()]
        p, q, h = reopen_known(self.p, root, frozenset(), frozenset({'a'}), 'repaired')
        self.assertEqual(h, frozenset({'a'}))
        check_proof(p, q, 'c', h)
        with self.assertRaises(ValueError):
            check_proof(p, q, 'c', frozenset())

    def test_loss_of_unused_fact_does_not_add_premise(self):
        p = replace(self.p, known=frozenset({'a', 'b'}),
                    rules=(Rule('ac', ('a',), 'c'),))
        root = infer(p).frontiers['c'][frozenset()]
        p2, q, h = reopen_known(p, root, frozenset(), frozenset({'b'}), 'repaired')
        self.assertEqual(h, frozenset())
        check_proof(p2, q, 'c', h)

    def test_corrupted_cyclic_certificate(self):
        p = replace(self.p, known=frozenset(), offers=frozenset(),
                    rules=(Rule('aa', ('a',), 'a'),))
        root = Proof(p.fingerprint(), 'a', 'rule', 'aa')
        # Deliberately bypass the frozen constructor to simulate corruption.
        object.__setattr__(root, 'children', (root,))
        with self.assertRaises(ValueError):
            check_proof(p, root, 'a', frozenset())


def exhaustive():
    atoms = ('a', 'b', 'c')
    all_rules = []
    for goal in atoms:
        others = tuple(a for a in atoms if a != goal)
        for prem in powerset(others):
            if prem:
                all_rules.append(Rule('r' + str(len(all_rules)), tuple(sorted(prem)), goal))
    assert len(all_rules) == 9
    profiles = targets = certificates = 0
    max_width = 0
    for chosen in powerset(range(len(all_rules))):
        rules = tuple(all_rules[i] for i in sorted(chosen))
        for known in powerset(atoms):
            for offers in powerset(atoms):
                p = Profile('exhaustive', atoms, known, offers, rules)
                result = infer(p)
                expected = oracle(p)
                assert result.complete
                for a in atoms:
                    got = result.frontiers[a]
                    assert set(got) == expected[a], (p, a, set(got), expected[a])
                    max_width = max(max_width, len(got))
                    for h, pr in got.items():
                        check_proof(p, pr, a, h)
                        certificates += 1
                    targets += 1
                profiles += 1
    return {'rule_schemas': len(all_rules), 'rule_subsets': 512,
            'profiles': profiles, 'target_frontiers_compared': targets,
            'conditional_certificates_checked': certificates,
            'maximum_frontier_width': max_width}


def randomized():
    rng = random.Random(20260906)
    cases = comparisons = checked = 0
    atoms = tuple('abcdef')
    for i in range(500):
        rules = tuple(Rule(f'r{j}', tuple(rng.sample(atoms, rng.randrange(4))), rng.choice(atoms))
                      for j in range(rng.randrange(1, 15)))
        p = Profile('random', atoms,
                    frozenset(a for a in atoms if rng.randrange(4) == 0),
                    frozenset(a for a in atoms if rng.randrange(2) == 0), rules)
        r = infer(p)
        expected = oracle(p)
        for a in atoms:
            assert set(r.frontiers[a]) == expected[a]
            for h, pr in r.frontiers[a].items():
                check_proof(p, pr, a, h)
                checked += 1
            comparisons += 1
        # A work cap cannot turn a nonempty residual into a closed derivation.
        limited = infer(p, rng.randrange(12))
        for a in atoms:
            for h, pr in limited.frontiers[a].items():
                check_proof(p, pr, a, h)
                assert any(s <= h for s in expected[a])
        cases += 1
    return {'seed': 20260906, 'profiles': cases, 'target_frontiers_compared': comparisons,
            'conditional_certificates_checked': checked,
            'budgeted_profiles_also_checked': cases}


def math_fixtures():
    """Finite examples only, not generic mathematical proofs."""
    valid = 0
    for a in range(-13, 14):
        for b in range(-10, 11):
            for p in range(4, 12):
                if a % 4 == 3 and b % 2 == 0 and p % 2 == 1:
                    assert (b**p - 1 - a**p) % 4 == 0
                    assert (-(a**p) * b**p) % 16 == 0
                    valid += 1
    negative = [((3, 2, 4), 4, lambda a,b,p:b**p-1-a**p),
                ((3, 3, 5), 4, lambda a,b,p:b**p-1-a**p),
                ((3, 2, 3), 16, lambda a,b,p:-(a**p)*b**p),
                ((1, 2, 5), 4, lambda a,b,p:b**p-1-a**p)]
    for triple, d, f in negative:
        assert f(*triple) % d != 0
    assert (2**5 - 1 - 3**5)//4 == -53
    assert (-(3**5)*2**5)//16 == -486
    # Finite representation of the exact observation image for List Empty.
    realizable_lengths = {0}
    assert all(0 == n for n in realizable_lengths)
    assert 1 not in realizable_lengths
    # Same-input observation (n,n) cannot realize (0,1).
    assert all((n, n) != (0, 1) for n in range(20))
    return {'admissible_frey_triples': valid, 'single_premise_negative_neighbors': 4,
            'coefficient_value_assertions': 2,
            'realization_fixtures': 2,
            'scope': 'finite arithmetic tests and explicitly modeled observation images'}


def run():
    t = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BoundaryTests)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    if not outcome.wasSuccessful():
        raise SystemExit(1)
    data = {'python': platform.python_version(), 'platform': platform.platform(),
            'claim': 'executed symbolic tests; no Lean compilation or human study',
            'boundary_test_methods': outcome.testsRun,
            'exhaustive': exhaustive(), 'randomized': randomized(),
            'mathematical_fixtures': math_fixtures()}
    data['elapsed_seconds'] = round(time.perf_counter() - t, 6)
    dest = Path(__file__).resolve().parents[1] / 'evidence' / 'test_results.json'
    dest.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    run()
