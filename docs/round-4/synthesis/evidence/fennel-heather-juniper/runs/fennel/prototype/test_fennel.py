#!/usr/bin/env python3
"""Executed checks for the finite Horn prototype, not Lean-kernel tests."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import replace
from itertools import combinations
import json
import platform
import random
import time
import unittest
from pathlib import Path
from fennel import (FennelError, Program, Root, Rule, Query, parse, plan,
                    certificate, check, export_lean)

HERE = Path(__file__).resolve().parent

def subsets(items):
    return [frozenset(c) for k in range(len(items)+1) for c in combinations(items, k)]

def ordinary_closure(program, query, enabled):
    # Deliberately independent reference: run ordinary forward closure for one
    # chosen assignment of available assumption roots, with no provenance labels.
    facts = {r.atom for r in program.roots if not r.pending or r.name in enabled}
    while True:
        old = set(facts)
        for rule in program.rules:
            if query.only is not None and rule.name not in query.only:
                continue
            if set(rule.premises) <= facts:
                facts.add(rule.conclusion)
        if facts == old:
            return facts

class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.p = parse((HERE / 'quotients.fnl').read_text())
        self.q = self.p.queries[1]
        self.result = plan(self.p, self.q)
        self.cert = certificate(self.result, self.result.routes()[1][1])

    def reject(self, cert, program=None, query=None):
        with self.assertRaises(FennelError):
            check(program or self.p, query or self.q, cert)

    def test_expected_frontiers(self):
        got = [{s for s, _ in plan(self.p, q).routes()} for q in self.p.queries]
        self.assertEqual(got, [{frozenset()}, {frozenset(['cached']), frozenset(['odd','residue'])},
                              {frozenset(['odd','residue'])}, set()])

    def test_cycle_without_seed(self):
        p = parse('module Cycle\natom P Q\nrule r : P -> Q\nrule s : Q -> P\nshow out : Q')
        self.assertEqual(plan(p,p.queries[0]).routes(), [])

    def test_seeded_cycle(self):
        p = parse('module Cycle\natom P Q\nask hp : P\nrule r : P -> Q\nrule s : Q -> P\nshow out : Q')
        result = plan(p,p.queries[0])
        self.assertEqual([s for s,_ in result.routes()], [frozenset(['hp'])])
        check(p,p.queries[0],certificate(result,result.routes()[0][1]))

    def test_duplicate_premise_is_not_consumed(self):
        p = parse('module Duplicate\natom P Q\ngiven hp : P\nrule r : P & P -> Q\nshow out : Q')
        result = plan(p,p.queries[0])
        self.assertEqual(check(p,p.queries[0],certificate(result,result.routes()[0][1])), frozenset())

    def test_empty_premise_rule(self):
        p = parse('module Empty\natom P\nrule r : -> P\nshow out : P')
        self.assertEqual([s for s,_ in plan(p,p.queries[0]).routes()], [frozenset()])

    def test_target_metadata_tamper(self):
        c=deepcopy(self.cert); c['target']='Unrelated'; self.reject(c)

    def test_proof_target_tamper(self):
        c=deepcopy(self.cert); c['root']=0; self.reject(c)

    def test_support_tamper(self):
        c=deepcopy(self.cert); c['nodes'][-1]['support']=[]; self.reject(c)

    def test_wrong_arity(self):
        c=deepcopy(self.cert); c['nodes'][-1]['children']=[]; self.reject(c)

    def test_wrong_premise_order(self):
        c=deepcopy(self.cert); c['nodes'][-1]['children'].reverse(); self.reject(c)

    def test_unknown_rule(self):
        c=deepcopy(self.cert); c['nodes'][-1]['name']='forged'; self.reject(c)

    def test_forward_reference(self):
        c=deepcopy(self.cert); c['nodes'][-1]['children']=[len(c['nodes'])-1]; self.reject(c)

    def test_unknown_root(self):
        c=deepcopy(self.cert); c['nodes'][0]['name']='notInContext'; self.reject(c)

    def test_changed_request(self):
        self.reject(self.cert, query=self.p.queries[3])

    def test_changed_rule(self):
        bad=replace(self.p, rules=(replace(self.p.rules[0],conclusion='Unrelated'),)+self.p.rules[1:])
        self.reject(self.cert, program=bad)

    def test_removed_assumption(self):
        bad=replace(self.p, roots=tuple(r for r in self.p.roots if r.name!='odd'))
        self.reject(self.cert, program=bad)

    def test_changed_method_policy(self):
        self.reject(self.cert, query=replace(self.q,only=('reuse',)))

    def test_unused_bad_node(self):
        c=deepcopy(self.cert)
        c['nodes'].append({'kind':'root','atom':'Div4','name':'bad','children':[],'support':[]})
        self.reject(c)

    def test_malformed_certificate(self):
        c=deepcopy(self.cert); c['nodes'][-1].pop('children'); self.reject(c)

    def test_source_injection_refused(self):
        with self.assertRaises(FennelError):
            parse('module Bad\natom P\naxiom unsound : P')

    def test_duplicate_name_refused(self):
        with self.assertRaises(FennelError):
            parse('module Bad\natom P\ngiven h : P\nask h : P')

    def test_undeclared_atom_refused(self):
        with self.assertRaises(FennelError):
            parse('module Bad\natom P\nshow q : Q')

    def test_missing_module_refused(self):
        with self.assertRaises(FennelError):
            parse('atom P')

    def test_unknown_method_refused(self):
        with self.assertRaises(FennelError):
            parse('module Bad\natom P\nshow q : P using only missing')

    def test_node_quota_marks_incomplete(self):
        r=plan(self.p,self.q,max_nodes=2)
        self.assertFalse(r.complete)
        for _, i in r.routes(): check(self.p,self.q,certificate(r,i))

    def test_attempt_quota_keeps_sound_routes(self):
        r=plan(self.p,self.q,max_attempts=3)
        self.assertFalse(r.complete)
        for _, i in r.routes(): check(self.p,self.q,certificate(r,i))

    def test_export_is_conditional_and_explicit(self):
        text=export_lean(self.p,self.q,self.cert,'testTheorem')
        self.assertNotIn('sorry',text)
        self.assertNotIn('axiom ',text)
        self.assertIn('(h3 : P2)',text) # pending odd premise explicitly bound
        self.assertIn('(h4 : P3)',text) # pending residue premise explicitly bound
        self.assertIn('UNCOMPILED HERE',text)


def exhaustive_comparison(seed=20260906, cases=2000):
    rng=random.Random(seed)
    assignment_comparisons=0
    certificate_checks=0
    max_nodes=0
    for _ in range(cases):
        n=rng.randint(1,6)
        atoms=tuple(f'A{i}' for i in range(n))
        roots=[]
        for i in range(rng.randint(0,4)):
            roots.append(Root(f'h{i}',rng.choice(atoms),True))
        if rng.random()<0.5:
            roots.append(Root('given',rng.choice(atoms),False))
        rules=[]
        for i in range(rng.randint(0,12)):
            rules.append(Rule(f'r{i}',tuple(rng.choice(atoms) for _ in range(rng.randint(0,3))),rng.choice(atoms)))
        query=Query('out',rng.choice(atoms),None)
        p=Program('Random',atoms,tuple(roots),tuple(rules),(query,))
        result=plan(p,query)
        assert result.complete
        max_nodes=max(max_nodes,len(result.nodes))
        for enabled in subsets([r.name for r in roots if r.pending]):
            reference=ordinary_closure(p,query,enabled)
            inferred={a for a,bucket in result.labels.items() if any(s<=enabled for s in bucket)}
            assert reference==inferred, (p,enabled,reference,inferred)
            assignment_comparisons+=1
        for atom,bucket in result.labels.items():
            # Export/check at the original query only; compare all labels above.
            keys=list(bucket)
            assert all(not s<t for s in keys for t in keys)
        for _,i in result.routes():
            check(p,query,certificate(result,i))
            certificate_checks+=1
    return {'seed':seed,'graphs':cases,'subset_closure_comparisons':assignment_comparisons,
            'selected_target_certificate_checks':certificate_checks,
            'max_stored_nodes_in_random_suite':max_nodes}


def arithmetic_neighbors():
    # Exact host-integer arithmetic; these are finite examples, not universal proofs.
    fixtures=[(3,2,5),(3,2,4),(3,3,5),(3,2,3),(1,2,5)]
    out=[]
    for a,b,p in fixtures:
        u=b**p-1-a**p; v=-(a**p)*(b**p)
        out.append({'a':a,'b':b,'p':p,'div4':u%4==0,'div16':v%16==0})
    assert out[0]['div4'] and out[0]['div16']
    assert not out[1]['div4'] and not out[2]['div4']
    assert not out[3]['div16'] and not out[4]['div4']
    return out

if __name__=='__main__':
    start=time.perf_counter()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BoundaryTests)
    run=unittest.TextTestRunner(verbosity=2).run(suite)
    if not run.wasSuccessful(): raise SystemExit(1)
    report={'python':platform.python_version(),'boundary_tests':run.testsRun,
            'boundary_success':run.wasSuccessful(),
            'finite_comparison':exhaustive_comparison(),
            'arithmetic_fixtures':arithmetic_neighbors(),
            'lean_compilation':'not run; no Lean executable available',
            'scope':'finite Horn prototype; no dependent Lean elaboration, no user study'}
    report['elapsed_seconds_single_run']=round(time.perf_counter()-start,6)
    (HERE.parent/'evidence'/'test_results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
