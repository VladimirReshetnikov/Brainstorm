"""Paired regression tests; run: python -m unittest -v test_length_contracts.py."""
import itertools
import random
import unittest
from dataclasses import replace
from length_contracts import (Expr, Affine, Request, Certificate, Refusal,
    normal_form, propose, verify, evaluate, distinguishing_lengths)

X = Expr('input', index=0)
NIL = Expr('nil')
ID = Affine(0, (1,))

def req(e=X, spec=ID, k=1, epoch='local-17'):
    return Request(epoch, k, e, spec)

class Contracts(unittest.TestCase):
    def test_01_identity(self):
        r = req(); self.assertEqual(verify(r, propose(r)).normal_form, ID)
    def test_02_reverse(self):
        r = req(Expr('reverse', (X,))); verify(r, propose(r))
    def test_03_map_succ(self):
        r = req(Expr('map_succ', (X,))); verify(r, propose(r))
    def test_04_append(self):
        r = req(Expr('append', (X, X)), Affine(0, (2,))); verify(r, propose(r))
    def test_05_cons(self):
        r = req(Expr('cons', (X,), value=5), Affine(1, (1,))); verify(r, propose(r))
    def test_06_zero_input_closed(self):
        r = req(NIL, Affine(0, ()), 0); verify(r, propose(r))
    def test_07_two_inputs(self):
        e = Expr('append', (X, Expr('input', index=1)))
        r = req(e, Affine(0, (1, 1)), 2); verify(r, propose(r))
    def test_08_wrong_coefficient(self):
        r = req(); c = replace(propose(r), normal_form=Affine(0, (2,)))
        with self.assertRaises(Refusal): verify(r, c)
    def test_09_wrong_constant(self):
        r = req(); c = replace(propose(r), normal_form=Affine(1, (1,)))
        with self.assertRaises(Refusal): verify(r, c)
    def test_10_false_spec(self):
        r = req(NIL)
        with self.assertRaises(Refusal): verify(r, propose(r))
    def test_11_same_law_wrong_source(self):
        r = req(); c = propose(req(Expr('reverse', (X,))))
        with self.assertRaises(Refusal): verify(r, c)
    def test_12_wrong_scope(self):
        r = req(); c = replace(propose(r), epoch='sibling-17')
        with self.assertRaises(Refusal): verify(r, c)
    def test_13_missing_epoch(self):
        r = req(epoch='')
        with self.assertRaises(Refusal): verify(r, propose(r))
    def test_14_truncated_coefficients(self):
        r = req(); c = replace(propose(r), normal_form=Affine(0, ()))
        with self.assertRaises(Refusal): verify(r, c)
    def test_15_extra_coefficients(self):
        r = req(); c = replace(propose(r), normal_form=Affine(0, (1, 0)))
        with self.assertRaises(Refusal): verify(r, c)
    def test_16_wrong_request_arity(self):
        r = req(); c = Certificate(r.epoch, 2, X, Affine(0, (1, 0)))
        with self.assertRaises(Refusal): verify(r, c)
    def test_17_unknown_filter(self):
        with self.assertRaises(Refusal): normal_form(Expr('filter', (X,)), 1)
    def test_18_missing_child(self):
        with self.assertRaises(Refusal): normal_form(Expr('append', (X,)), 1)
    def test_19_extra_child(self):
        with self.assertRaises(Refusal): normal_form(Expr('nil', (X,)), 1)
    def test_20_input_out_of_range(self):
        with self.assertRaises(Refusal): normal_form(Expr('input', index=1), 1)
    def test_21_negative_coefficient(self):
        r = req(spec=Affine(0, (-1,)))
        with self.assertRaises(Refusal): verify(r, propose(r))
    def test_22_boolean_not_natural(self):
        r = req(spec=Affine(0, (True,)))
        with self.assertRaises(Refusal): verify(r, propose(r))
    def test_23_unexpected_field(self):
        with self.assertRaises(Refusal): normal_form(Expr('nil', value=3), 1)
    def test_24_depth_budget(self):
        e = X
        for _ in range(66): e = Expr('reverse', (e,))
        with self.assertRaises(Refusal): normal_form(e, 1)
    def test_25_unsupported_arity(self):
        with self.assertRaises(Refusal): normal_form(NIL, 65)
    def test_26_counterexample_constant(self):
        a,b=Affine(1,(2,)),Affine(0,(2,))
        n=distinguishing_lengths(a,b)
        self.assertIsNotNone(n); self.assertNotEqual(a.at(n),b.at(n))
    def test_27_counterexample_coefficient(self):
        a,b=Affine(3,(0,2)),Affine(3,(0,1))
        n=distinguishing_lengths(a,b)
        self.assertIsNotNone(n); self.assertNotEqual(a.at(n),b.at(n))
    def test_28_equal_forms(self):
        self.assertIsNone(distinguishing_lengths(ID, ID))
    def test_29_length_does_not_imply_identity(self):
        e=Expr('map_succ',(X,)); r=req(e); verify(r,propose(r))
        self.assertNotEqual(evaluate(e,[(0,1)]), (0,1))
    def test_30_concrete_regression(self):
        rng=random.Random(20260906)
        def gen(d):
            if d == 0:
                return NIL if rng.randrange(4)==0 else Expr('input',index=rng.randrange(3))
            op=rng.choice(['nil','input','cons','append','reverse','map_succ'])
            if op=='nil': return NIL
            if op=='input': return Expr('input',index=rng.randrange(3))
            if op=='cons': return Expr(op,(gen(d-1),),value=rng.randrange(10))
            return Expr(op,tuple(gen(d-1) for _ in range(2 if op=='append' else 1)))
        for _ in range(400):
            e=gen(4); a=normal_form(e,3)
            for ns in itertools.product(range(4),repeat=3):
                inputs=[list(range(n)) for n in ns]
                self.assertEqual(len(evaluate(e,inputs)),a.at(ns))
    def test_31_basis_complete_finite_regression(self):
        forms=[Affine(c,(a,b)) for c,a,b in itertools.product(range(3),repeat=3)]
        for a in forms:
            for b in forms:
                n=distinguishing_lengths(a,b)
                if a==b: self.assertIsNone(n)
                else: self.assertNotEqual(a.at(n),b.at(n))
    def test_32_wrong_length_vector(self):
        with self.assertRaises(Refusal): ID.at(())

if __name__=='__main__': unittest.main(verbosity=2)
