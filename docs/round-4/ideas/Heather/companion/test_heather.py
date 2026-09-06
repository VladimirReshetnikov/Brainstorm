#!/usr/bin/env python3
"""Deterministic executable tests; none of these runs a Lean kernel."""
from __future__ import annotations
import copy
import itertools
import json
import platform
import random
import sys
import time
import unittest
from dataclasses import replace
from pathlib import Path
from heather import (Affine, Context, Evidence, Expr, Fact, HeatherError, Request,
                     admissible, certificate, check_certificate, evaluate, frame,
                     lean_export, model, parse)

COUNTS = {'model_evaluation_comparisons': 0, 'domain_law_comparisons': 0,
          'concrete_negative_witnesses': 0, 'certificate_mutations_refused': 0}


def source(domain: str, left: str, right: str, inputs: str = 'xs, ys') -> str:
    return f'heather example_law\ndomain {domain}\ninputs {inputs}\nclaim length({left}) == length({right})\n'


class HeatherTests(unittest.TestCase):
    def test_01_actual_source_to_export(self):
        for f in sorted(Path('examples').glob('*.hthr')):
            req = parse(f.read_text())
            cert = certificate(req)
            self.assertTrue(check_certificate(req, cert))
            if cert['status'] == 'model_proved':
                out = lean_export(req, cert)
                self.assertIn('NOT COMPILED', out)
                self.assertIn('theorem heather_'+req.name, out)

    def test_02_empty_is_not_a_positive_length_domain(self):
        req = parse(source('empty','nil()','xs','xs'))
        cert = certificate(req)
        self.assertEqual(cert['status'], 'model_proved')
        self.assertNotEqual(cert['lhs'], cert['rhs'])
        self.assertEqual(frame('empty',1), ((0,),))

    def test_03_diagonal_correlation(self):
        req = parse(source('diagonal','append(xs,ys)','append(ys,ys)'))
        cert = certificate(req)
        self.assertEqual(cert['status'],'model_proved')
        self.assertNotEqual(cert['lhs'],cert['rhs'])
        raw = replace(req,domain='free')
        bad = certificate(raw)
        self.assertEqual(bad['status'],'counterexample')
        self.assertTrue(check_certificate(raw,bad))
        self.assertFalse(check_certificate(req,bad))

    def test_04_even_witness_really_even(self):
        req = parse(source('even','nil()','xs','xs'))
        cert = certificate(req)
        self.assertEqual(cert['witness_lengths'],(2,))
        self.assertTrue(check_certificate(req,cert))

    def test_05_ill_typed_empty_constructor(self):
        with self.assertRaises(HeatherError):
            parse(source('empty','one()','xs','xs'))

    def test_06_syntax_and_arity_refusals(self):
        bads = ['xs.reverse()', 'append(xs)', '__import__("os")',
                'reverse(unknown)', 'append(xs,ys,ys)', '[0]']
        for bad in bads:
            with self.assertRaises(HeatherError): parse(source('free',bad,'xs'))
        with self.assertRaises(HeatherError): parse(source('diagonal','xs','xs','xs'))
        with self.assertRaises(HeatherError): parse(source('unknown','xs','xs','xs'))

    def test_07_positive_certificate_mutations(self):
        req = parse(source('free','reverse(xs)','xs','xs'))
        cert = canonical_copy(certificate(req))
        mutations = []
        for key, value in [('request','wrong'),('schema',99),('status','kernel_verified'),
                           ('frame',[[0]]),('lean_status','compiled'),('witness_lengths',[0])]:
            x=copy.deepcopy(cert); x[key]=value; mutations.append(x)
        x=copy.deepcopy(cert); x['lhs']['constant']=1; mutations.append(x)
        x=copy.deepcopy(cert); x['rhs']['coefficients']=[1,0]; mutations.append(x)
        x=copy.deepcopy(cert); x['lhs']['coefficients']=[True]; mutations.append(x)
        x=copy.deepcopy(cert); x['schema']=True; mutations.append(x)
        for x in mutations:
            self.assertFalse(check_certificate(req,x)); COUNTS['certificate_mutations_refused']+=1

    def test_08_negative_witness_mutations(self):
        req=parse(source('free','nil()','xs','xs'))
        cert=canonical_copy(certificate(req))
        mutations=[]
        for key,value in [('witness_lengths',[0]),('witness_lists',[[]]),
                          ('witness_lengths',[-1]),('witness_lists',[[False]])]:
            x=copy.deepcopy(cert); x[key]=value; mutations.append(x)
        for x in mutations:
            self.assertFalse(check_certificate(req,x)); COUNTS['certificate_mutations_refused']+=1
        with self.assertRaises(HeatherError): lean_export(req,cert)

    def test_09_generated_model_semantics(self):
        rng=random.Random(20260906)
        for _ in range(300):
            e=random_expr(rng,4,2,allow_one=True)
            a=model(e,2)
            for n,m in itertools.product(range(5),repeat=2):
                env=(tuple(range(n)),tuple(range(m)))
                self.assertEqual(len(evaluate(e,env)),a.at((n,m)))
                COUNTS['model_evaluation_comparisons']+=1

    def test_10_generated_domain_decisions(self):
        rng=random.Random(617)
        for domain in ['free','empty','diagonal','even']:
            for j in range(180):
                a=random_expr(rng,3,2,domain!='empty')
                b=random_expr(rng,3,2,domain!='empty')
                req=Request(f'case_{j}',domain,('xs','ys'),a,b)
                cert=certificate(req)
                self.assertTrue(check_certificate(req,cert))
                if cert['status']=='counterexample':
                    env=tuple(tuple(v) for v in cert['witness_lists'])
                    self.assertNotEqual(len(evaluate(a,env)),len(evaluate(b,env)))
                    COUNTS['concrete_negative_witnesses']+=1
                for ns in itertools.product(range(5),repeat=2):
                    if admissible(domain,ns):
                        env=tuple(tuple(range(n)) for n in ns)
                        actual=len(evaluate(a,env))==len(evaluate(b,env))
                        if cert['status']=='model_proved': self.assertTrue(actual)
                        COUNTS['domain_law_comparisons']+=1

    def test_11_use_site_inserts_nonzero_proof(self):
        c=Context('epoch-1',('n','d'))
        c.assume('hdpos',Fact('positive',('d',)))
        c.assume('hdiv',Fact('divides',('d','n')))
        a,b=c.exact_quotient_requirements('n','d')
        self.assertIsNotNone(a); self.assertIsNotNone(b)
        self.assertEqual(a.lean,'(Nat.ne_of_gt hdpos)')
        self.assertEqual(c.firings,1)
        self.assertTrue(c.check(a))

    def test_12_missing_divisibility_stays_open(self):
        c=Context('e',('n','d'))
        c.assume('hp',Fact('positive',('d',)))
        a,b=c.exact_quotient_requirements('n','d')
        self.assertIsNotNone(a); self.assertIsNone(b)

    def test_13_unseeded_cycle(self):
        c=Context('e',('d',))
        self.assertIsNone(c.require(Fact('positive',('d',))))
        self.assertIsNone(c.require(Fact('nonzero',('d',))))
        self.assertEqual(len(c.evidence),0)

    def test_14_wrong_object_and_sibling_branch(self):
        c=Context('left',('d','e'))
        c.assume('hp',Fact('positive',('d',)))
        self.assertIsNone(c.require(Fact('nonzero',('e',))))
        proof=c.require(Fact('nonzero',('d',)))
        other=Context('right',('d','e'))
        self.assertFalse(other.check(proof))
        self.assertIsNone(other.require(Fact('nonzero',('d',))))

    def test_15_rebuild_and_structure_refusal(self):
        old=Context('old',('d',)); old.assume('hp',Fact('positive',('d',)))
        proof=old.require(Fact('nonzero',('d',)))
        new=Context('new',('d',)); new.assume('hp',Fact('positive',('d',)))
        self.assertFalse(new.check(proof))
        self.assertIsNotNone(new.require(Fact('nonzero',('d',))))
        with self.assertRaises(HeatherError): Context('e',('d',),'Int')

    def test_16_evidence_corruption(self):
        c=Context('e',('d',)); c.assume('hp',Fact('positive',('d',)))
        proof=c.require(Fact('nonzero',('d',)))
        self.assertFalse(c.check(replace(proof,lean='False.elim bogus')))
        c.evidence.append(Evidence('e',Fact('positive',('d',)), 'Nat.pos_of_ne_zero',(999,),'bogus'))
        self.assertFalse(c.check(c.evidence[-1]))

    def test_17_no_implicit_equality_transport(self):
        # The executable prototype handles exact anchors only. General checked
        # rewriting is specified in the article but intentionally not simulated.
        c=Context('e',('d','e')); c.assume('hp',Fact('positive',('d',)))
        self.assertIsNone(c.require(Fact('nonzero',('e',))))

    def test_18_bounded_source_size(self):
        expr='xs'
        for _ in range(40): expr='reverse('+expr+')'
        with self.assertRaises(HeatherError): parse(source('free',expr,'xs','xs'))


def canonical_copy(x): return json.loads(json.dumps(x))

def random_expr(rng,depth,arity,allow_one):
    leaves=[Expr('nil')]+[Expr('input',index=i) for i in range(arity)]
    if allow_one: leaves.append(Expr('one'))
    if depth==0 or rng.randrange(3)==0: return rng.choice(leaves)
    if rng.randrange(2)==0: return Expr('reverse',(random_expr(rng,depth-1,arity,allow_one),))
    return Expr('append',tuple(random_expr(rng,depth-1,arity,allow_one) for _ in range(2)))

if __name__=='__main__':
    start=time.perf_counter()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(HeatherTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'status':'passed' if result.wasSuccessful() else 'failed',
            'test_methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'counters':COUNTS,'python':platform.python_version(),
            'elapsed_seconds':round(time.perf_counter()-start,6),
            'lean_compiled':False, 'scope':'finite executable Python model, not kernel verification'}
    Path('test_results.json').write_text(json.dumps(report,indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() else 1)
