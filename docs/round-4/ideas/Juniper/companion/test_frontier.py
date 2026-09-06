#!/usr/bin/env python3
"""Tests and independent finite-oracle experiments for the Juniper ground model."""
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
from juniper_frontier import Profile, Rule, Node, parse, solve, check, summary, export_lean

HERE = Path(__file__).resolve().parent

def closure(p: Profile, support: frozenset[str]) -> set[str]:
    # Deliberately does not reuse the antichain solver's implementation.
    facts = set(p.known) | set(support)
    while True:
        additions = {r.conclusion for r in p.rules if set(r.premises) <= facts}
        if additions <= facts:
            return facts
        facts |= additions

def oracle(p: Profile) -> dict[str, set[frozenset[str]]]:
    good = {a: set() for a in p.atoms}
    for size in range(len(p.offers) + 1):
        for parts in combinations(p.offers, size):
            s = frozenset(parts)
            for a in closure(p, s):
                if not any(t <= s for t in good[a]):
                    good[a].add(s)
    return good

BASE = '''profile Demo
atoms A B C D
given A
offer B
rule ab: A B -> C
rule cd: C -> D
need D
'''

class FrontierTests(unittest.TestCase):
    def test_conditional_not_proved(self):
        p=parse(BASE); r=solve(p); check(p,r)
        self.assertEqual(r.status('D'),'conditional')
        self.assertEqual(set(r.frontier['D']),{frozenset({'B'})})
    def test_closed(self):
        p=parse(BASE.replace('given A\noffer B','given A B')); r=solve(p)
        self.assertEqual(r.status('D'),'closed_in_profile')
    def test_seedless_cycle(self):
        p=parse('profile C\natoms A B\nrule a: A -> B\nrule b: B -> A\nneed B')
        self.assertEqual(solve(p).status('B'),'no_route_in_profile')
    def test_seeded_cycle(self):
        p=parse('profile C\natoms A B\ngiven A\nrule a: A -> B\nrule b: B -> A\nneed B')
        r=solve(p); check(p,r); self.assertEqual(r.status('B'),'closed_in_profile')
    def test_nullary_rule(self):
        p=parse('profile C\natoms A\nrule a: -> A\nneed A')
        self.assertEqual(solve(p).status('A'),'closed_in_profile')
    def test_dominated_support_removed(self):
        p=parse('profile C\natoms A B C\noffer A B\nrule a: A B -> C\nrule b: A -> C\nneed C')
        r=solve(p); check(p,r); self.assertEqual(set(r.frontier['C']),{frozenset({'A'})})
    def test_incomparable_routes_retained(self):
        p=parse('profile C\natoms A B C\noffer A B\nrule a: A -> C\nrule b: B -> C\nneed C')
        self.assertEqual(len(solve(p).frontier['C']),2)
    def test_no_automatic_offer(self):
        p=parse(BASE.replace('offer B\n','')); self.assertFalse(solve(p).frontier['D'])
    def test_repeated_premise_is_not_linear(self):
        p=parse('profile C\natoms A B\noffer A\nrule a: A A -> B\nneed B')
        self.assertEqual(set(solve(p).frontier['B']),{frozenset({'A'})})
    def test_goal_as_explicit_offer_is_conditional(self):
        p=parse('profile C\natoms A\noffer A\nneed A')
        self.assertEqual(solve(p).status('A'),'conditional')
    def test_unused_display_stays_open(self):
        p=parse(BASE+'need B\n'); r=solve(p)
        self.assertEqual(r.status('B'),'conditional')
    def test_budget_zero(self):
        p=parse(BASE); r=solve(p,0); check(p,r)
        self.assertFalse(r.complete); self.assertEqual(r.status('D'),'budget_exhausted')
    def test_budget_retains_sound_partial_proof(self):
        p=parse(BASE); r=solve(p,2); check(p,r)
        self.assertEqual(r.status('D'),'conditional_incomplete')
    def test_negative_budget(self):
        with self.assertRaises(ValueError): solve(parse(BASE),-1)
    def test_changed_profile_rejected(self):
        p=parse(BASE); r=solve(p)
        with self.assertRaises(ValueError): check(replace(p,name='AnotherContext'),r)
    def test_removed_hypothesis_not_reused(self):
        p=parse(BASE); r=solve(p)
        with self.assertRaises(ValueError): check(replace(p,known=()),r)
        self.assertFalse(solve(replace(p,known=())).frontier['D'])
    def test_corrupted_support_rejected(self):
        p=parse(BASE); r=solve(p)
        r.nodes[-1]=replace(r.nodes[-1],support=frozenset())
        with self.assertRaises(ValueError): check(p,r)
    def test_self_reference_rejected(self):
        p=parse(BASE); r=solve(p)
        r.nodes[-1]=replace(r.nodes[-1],parents=(len(r.nodes)-1,))
        with self.assertRaises(ValueError): check(p,r)
    def test_wrong_rule_rejected(self):
        p=parse(BASE); r=solve(p); r.nodes[-1]=replace(r.nodes[-1],rule=0)
        with self.assertRaises(ValueError): check(p,r)
    def test_false_completeness_flag_rejected(self):
        p=parse(BASE); r=solve(p,0); r.complete=True
        with self.assertRaises(ValueError): check(p,r)
    def test_missing_given_frontier_rejected(self):
        p=parse(BASE); r=solve(p); r.frontier['A'].clear()
        with self.assertRaises(ValueError): check(p,r)
    def test_omitted_route_rejected(self):
        p=parse('profile C\natoms A B C\noffer A B\nrule a: A -> C\nrule b: B -> C\nneed C')
        r=solve(p); del r.frontier['C'][frozenset({'B'})]
        with self.assertRaises(ValueError): check(p,r)
    def test_unknown_directive(self):
        with self.assertRaises(ValueError): parse(BASE+'assume_magic D')
    def test_undeclared_atom(self):
        with self.assertRaises(ValueError): parse(BASE+'need Z')
    def test_duplicate_atom(self):
        with self.assertRaises(ValueError): parse(BASE+'atoms A')
    def test_duplicate_rule(self):
        with self.assertRaises(ValueError): parse(BASE+'rule ab: A -> C')
    def test_malformed_arrow(self):
        with self.assertRaises(ValueError): parse(BASE+'rule other: A -> B C')
    def test_overlap_given_offer(self):
        with self.assertRaises(ValueError): parse(BASE+'offer A')
    def test_missing_profile(self):
        with self.assertRaises(ValueError): parse(BASE.replace('profile Demo\n',''))
    def test_no_goals(self):
        with self.assertRaises(ValueError): parse(BASE.replace('need D\n',''))
    def test_export_generic_not_arithmetic(self):
        p=parse(BASE); text=export_lean(p,solve(p))
        self.assertIn('(A0 A1 A2 A3 : Prop)',text)
        self.assertIn('(r0 : A0 -> A1 -> A2)',text)
        self.assertNotIn('sorry',text)
        self.assertNotIn('\naxiom ',text)
    def test_oracle_for_example(self):
        p=parse((HERE/'example.jnp').read_text()); r=solve(p)
        self.assertEqual({a:set(v) for a,v in r.frontier.items()},oracle(p))


def experiments() -> dict:
    rng=random.Random(20260906)
    profiles=400
    n=7
    random_checks=0
    for i in range(profiles):
        atoms=tuple(f'A{j}' for j in range(n))
        offers=tuple(rng.sample(atoms,4))
        known=tuple(a for a in atoms if a not in offers and rng.random()<0.35)
        rules=tuple(Rule(f'r{j}',tuple(rng.choices(atoms,k=rng.randrange(4))),rng.choice(atoms))
                    for j in range(12))
        p=Profile(f'P{i}',atoms,known,offers,rules,atoms)
        r=solve(p); check(p,r)
        expected=oracle(p)
        assert {a:set(v) for a,v in r.frontier.items()} == expected
        rev=replace(p,rules=tuple(reversed(p.rules)))
        rr=solve(rev); check(rev,rr)
        assert {a:set(v) for a,v in rr.frontier.items()} == expected
        random_checks += n
    benchmarks=[]
    for k in range(1,9):
        offers=tuple(f'{s}{i}' for i in range(k) for s in ('A','B'))
        middle=tuple(f'C{i}' for i in range(k))
        rules=tuple(Rule(f'r{s}{i}',(f'{s}{i}',),f'C{i}')
                    for i in range(k) for s in ('A','B'))
        p=Profile(f'Exponential{k}',offers+middle+('G',),(),offers,
                  rules+(Rule('finish',middle,'G'),),('G',))
        start=time.perf_counter(); r=solve(p); elapsed=time.perf_counter()-start
        check(p,r); assert len(r.frontier['G'])==2**k
        benchmarks.append({'pairs':k,'offers':2*k,'routes':len(r.frontier['G']),
                           'nodes':len(r.nodes),'attempts':r.attempts,
                           'seconds_single_run':elapsed})
    # Arithmetic samples are validation of stated fixtures, not universal proofs.
    arithmetic=0
    for a in range(-13,14):
        for b in range(-8,9):
            for p in range(4,10):
                if p%2==1 and a%4==3 and b%2==0:
                    n2=b**p-1-a**p; n4=-a**p*b**p
                    assert n2%4==0 and n4%16==0
                    arithmetic+=1
    fixture={}
    for a,b,p in [(3,2,5),(3,2,4),(3,3,5),(3,2,3),(1,2,5)]:
        n2=b**p-1-a**p; n4=-a**p*b**p
        fixture[str((a,b,p))]={'a2_numerator_mod_4':n2%4,'a4_numerator_mod_16':n4%16}
    assert (2**5-1-3**5)//4==-53
    assert (-3**5*2**5)//16==-486
    return {'seed':20260906,'random_profiles':profiles,'atoms_per_profile':n,
            'offers_per_profile':4,'rules_per_profile':12,
            'exhaustive_support_assignments':profiles*16,
            'goal_frontiers_compared_to_oracle':random_checks,
            'reversed_schedule_profiles':profiles,
            'exponential_frontiers':benchmarks,'valid_Frey_arithmetic_triples':arithmetic,
            'Frey_boundary_fixtures':fixture,
            'limitations':['Finite Python tests, not proof of the Python implementation.',
                'Generic exported Lean was not compiled.',
                'No actual Lean term reification, grounding, tactic integration, or human study.']}

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(FrontierTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful(): sys.exit(1)
    report={'python':platform.python_version(),'platform':platform.platform(),
            'unit_tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'experiments':experiments()}
    (HERE/'test-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
