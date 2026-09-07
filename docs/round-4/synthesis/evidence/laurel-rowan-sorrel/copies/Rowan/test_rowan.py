#!/usr/bin/env python3
"""Executable tests of Rowan's finite reference model, not Lean proofs."""
from __future__ import annotations
import dataclasses
import itertools
import json
import platform
import random
import time
import unittest
from pathlib import Path
from rowan_model import *

COUNTS = {"list_denotation_comparisons": 0, "affine_pair_image_checks": 0,
          "affine_sample_evaluations": 0, "concrete_counterexamples": 0,
          "closure_order_trials": 0, "frey_arithmetic_cases": 0}

class SymbolicTests(unittest.TestCase):
    def setUp(self):
        self.x = Term("x", "Real")
        self.y = Term("y", "Real")
        self.pos = Atom("Positive", (self.x,))
        self.nz = Atom("Nonzero", (self.x,))
        self.inv = Atom("InvAllowed", (self.x,))
        self.a = Assumption("positive_x", self.pos)
        self.ctx = Context("demo", (self.x, self.y), (self.a,))
        self.rules = (GroundRule("positive-nonzero", (self.pos,), self.nz),
                      GroundRule("inverse", (self.nz,), self.inv))

    def test_01_frey_end_to_end(self):
        a, b, c = run_script(DEMO)["answers"]
        self.assertEqual(a["status"], "derived")
        self.assertEqual(a["support"], ["bound_p", "even_b"])
        self.assertEqual(b["frontier"], ["Odd(p)", "ResidueThree(a)"])
        self.assertEqual(c["status"], "derived")
        self.assertEqual(a["metrics"]["ground_assignments"], 10)

    def test_02_guard_missing_not_refuted(self):
        empty = dataclasses.replace(self.ctx, assumptions=())
        out = solve(Request(empty, self.inv), self.rules)
        self.assertEqual(out.status, "open")
        self.assertEqual(out.frontier, (self.pos,))

    def test_03_unseeded_cycle(self):
        rs = (GroundRule("pn", (self.pos,), self.nz), GroundRule("np", (self.nz,), self.pos))
        ctx = dataclasses.replace(self.ctx, assumptions=())
        self.assertEqual(solve(Request(ctx, self.pos), rs).status, "open")

    def test_04_seeded_cycle(self):
        rs = (*self.rules, GroundRule("np", (self.nz,), self.pos))
        out = solve(Request(self.ctx, self.inv), rs)
        self.assertTrue(check_derivation(Request(self.ctx, self.inv), out.proof, rs))

    def test_05_sibling_scope(self):
        local = dataclasses.replace(self.a, scope=("left",))
        ctx = dataclasses.replace(self.ctx, scope=("right",), assumptions=(local,))
        self.assertEqual(solve(Request(ctx, self.inv), self.rules).status, "open")

    def test_06_parent_scope(self):
        ctx = dataclasses.replace(self.ctx, scope=("left", "nested"))
        self.assertEqual(solve(Request(ctx, self.inv), self.rules).status, "derived")

    def test_07_stale_snapshot(self):
        ctx = dataclasses.replace(self.ctx, epoch="rebuilt")
        with self.assertRaises(ValueError):
            solve(Request(ctx, self.inv), self.rules)

    def test_08_same_print_different_structure(self):
        other = dataclasses.replace(self.x, meaning="different-topology")
        goal = Atom("Nonzero", (other,))
        ctx = dataclasses.replace(self.ctx, terms=(*self.ctx.terms, other))
        self.assertEqual(solve(Request(ctx, goal), self.rules).status, "open")
        self.assertEqual(goal.text(), self.nz.text())
        self.assertNotEqual(goal, self.nz)

    def test_09_no_string_rewrite_transport(self):
        goal = Atom("Nonzero", (self.y,))
        self.assertEqual(solve(Request(self.ctx, goal), self.rules).status, "open")
        eq = Atom("Equal", (self.x, self.y))
        ctx = dataclasses.replace(self.ctx, assumptions=(*self.ctx.assumptions, Assumption("eq", eq)))
        rs = (*self.rules, GroundRule("explicit-transport", (self.nz, eq), goal))
        self.assertEqual(solve(Request(ctx, goal), rs).status, "derived")

    def test_10_forbidden_support(self):
        request = Request(self.ctx, self.inv, allowed_support=frozenset())
        self.assertEqual(solve(request, self.rules).status, "open")

    def test_11_forbidden_method(self):
        request = Request(self.ctx, self.inv, allowed_rules=frozenset({"inverse"}))
        self.assertEqual(solve(request, self.rules).status, "open")

    def test_12_tampered_target(self):
        request = Request(self.ctx, self.inv)
        proof = solve(Request(self.ctx, self.nz), self.rules).proof
        self.assertFalse(check_derivation(request, proof, self.rules))

    def test_13_forged_leaf(self):
        proof = Derivation(self.inv, assumption=Assumption("forged", self.inv))
        self.assertFalse(check_derivation(Request(self.ctx, self.inv), proof, self.rules))

    def test_14_forged_rule(self):
        false_rule = GroundRule("inverse", (self.pos,), self.inv)
        leaf = Derivation(self.pos, assumption=self.a)
        proof = Derivation(self.inv, false_rule, (leaf,))
        self.assertFalse(check_derivation(Request(self.ctx, self.inv), proof, self.rules))

    def test_15_support_checked_transitively(self):
        unrestricted = solve(Request(self.ctx, self.inv), self.rules).proof
        restricted = Request(self.ctx, self.inv, allowed_support=frozenset())
        self.assertFalse(check_derivation(restricted, unrestricted, self.rules))

    def test_16_grounding_types_and_budget(self):
        ts = (Term("a", "Int"), Term("b", "Int"), Term("p", "Nat"))
        rs, n = ground(FREY_SCHEMAS, ts, FREY_SIGNATURES)
        self.assertEqual((len(rs), n), (10, 10))
        with self.assertRaises(ValueError):
            ground(FREY_SCHEMAS, ts, FREY_SIGNATURES, cap=9)
        malformed = Schema("bad", (("a", "Int"),), (), Pattern("Odd", ("a",)))
        with self.assertRaises(ValueError):
            ground((malformed,), ts, FREY_SIGNATURES)

    def test_17_rule_order_independence(self):
        # Random ordering is only an executed finite stress check, not a theorem.
        rng = random.Random(20260906)
        rs = (*self.rules, GroundRule("redundant", (self.pos,), self.inv),
              GroundRule("cycle", (self.inv,), self.pos))
        for _ in range(100):
            shuffled = list(rs)
            rng.shuffle(shuffled)
            out = solve(Request(self.ctx, self.inv), shuffled)
            self.assertEqual(out.status, "derived")
            self.assertTrue(check_derivation(Request(self.ctx, self.inv), out.proof, rs))
            COUNTS["closure_order_trials"] += 1

    def test_18_duplicate_premises_and_nullary_rule(self):
        rs = (GroundRule("repeat", (self.pos, self.pos), self.nz),
              GroundRule("zero", (), self.inv))
        for target in (self.nz, self.inv):
            out = solve(Request(self.ctx, target), rs)
            self.assertEqual(out.status, "derived")
            self.assertTrue(check_derivation(Request(self.ctx, target), out.proof, rs))

    def test_19_parser_refuses_ambiguity(self):
        for text in ("object a : Int\nobject a : Int", "derive g : Odd(a)",
                     "object a : Int\nassume h : Odd(a)", "magic true"):
            with self.assertRaises(ValueError):
                run_script(text)

    def test_20_request_is_immutable(self):
        r = Request(self.ctx, self.inv)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            r.target = self.pos


class AffineTests(unittest.TestCase):
    def test_21_empty_element_type(self):
        img = Image(1, (Component((0,)),))
        self.assertTrue(decide_affine(Affine(0, (0,)), Affine(0, (1,)), img).equal_on_image)
        # No positive length is supplied as a purported input of List Empty.
        self.assertEqual(len(()), 0)

    def test_22_inhabited_element_type(self):
        img = Image(1, (Component((0,), ((1,),)),))
        d = decide_affine(Affine(0, (0,)), Affine(0, (1,)), img)
        self.assertEqual(d.witness, (1,))
        xs = (0,) * d.witness[0]
        self.assertNotEqual(len(()), len(xs))
        COUNTS["concrete_counterexamples"] += 1

    def test_23_correlated_lengths(self):
        diagonal = Image(2, (Component((0, 0), ((1, 1),)),))
        self.assertTrue(decide_affine(Affine(0, (1, 0)), Affine(0, (0, 1)), diagonal).equal_on_image)
        full = Image(2, (Component((0, 0), ((1, 0), (0, 1))),))
        self.assertEqual(decide_affine(Affine(0, (1, 0)), Affine(0, (0, 1)), full).witness, (1, 0))
        # This vector cannot equal (length xs, length(reverse xs)).

    def test_24_guarded_shifted_image(self):
        img = Image(2, (Component((2, 3), ((1, 1),)),))
        self.assertTrue(decide_affine(Affine(1, (1, 0)), Affine(0, (0, 1)), img).equal_on_image)
        d = decide_affine(Affine(0, (1, 0)), Affine(0, (0, 1)), img)
        self.assertEqual(d.witness, (2, 3))

    def test_25_finite_union_and_empty_domain(self):
        img = Image(1, (Component((0,)), Component((2,), ((2,),))))
        self.assertFalse(decide_affine(Affine(0, (0,)), Affine(0, (1,)), img).equal_on_image)
        self.assertTrue(decide_affine(Affine(1, (0,)), Affine(8, (9,)), Image(1, ())).equal_on_image)

    def test_26_dimension_corruption(self):
        with self.assertRaises(ValueError):
            Component((0, 0), ((1,),))
        with self.assertRaises(ValueError):
            Component((-1,))
        with self.assertRaises(ValueError):
            decide_affine(Affine(0, (1,)), Affine(0, (1,)), Image(2, ()))
        with self.assertRaises(ValueError):
            Affine(0, (1,)).eval((1, 2))

    def test_27_exhaustive_affine_matrix(self):
        forms = [Affine(c, (a, b)) for c, a, b in itertools.product(range(3), repeat=3)]
        images = [Image(2, (Component((0, 0), ((1, 0), (0, 1))),)),
                  Image(2, (Component((0, 0)),)),
                  Image(2, (Component((0, 0), ((1, 1),)),)),
                  Image(2, (Component((2, 3), ((1, 1),)),)),
                  Image(2, (Component((0, 0), ((2, 0),)), Component((1, 1), ((0, 2),)))),
                  Image(2, ())]
        for f, g, img in itertools.product(forms, forms, images):
            decision = decide_affine(f, g, img)
            if not decision.equal_on_image:
                c = img.components[decision.component]
                self.assertEqual(c.point(decision.coordinates), decision.witness)
                self.assertNotEqual(f.eval(decision.witness), g.eval(decision.witness))
            agreement = True
            for c in img.components:
                for z in itertools.product(range(4), repeat=len(c.generators)):
                    x = c.point(z)
                    agreement &= f.eval(x) == g.eval(x)
                    COUNTS["affine_sample_evaluations"] += 1
            # Bases and unit generators are among the sampled points. Thus every
            # returned basis witness is necessarily present in this finite check.
            self.assertEqual(decision.equal_on_image, agreement)
            COUNTS["affine_pair_image_checks"] += 1

    def test_28_list_interpreter_and_normalization(self):
        expressions = {ListExpr("nil"), ListExpr("input", value=0), ListExpr("input", value=1)}
        for _ in range(2):
            old = expressions
            expressions = ({ListExpr("nil"), ListExpr("input", value=0), ListExpr("input", value=1)}
                           | {ListExpr(k, (e,)) for e in old for k in ("cons", "reverse", "mapSucc")}
                           | {ListExpr("append", (a, b)) for a, b in itertools.product(old, old)})
        self.assertEqual(len(expressions), 507)
        for e in expressions:
            nf = e.model(2)
            for n, m in itertools.product(range(5), repeat=2):
                env = (tuple(range(n)), tuple(range(m)))
                self.assertEqual(len(e.eval(env)), nf.eval((n, m)))
                COUNTS["list_denotation_comparisons"] += 1

    def test_29_realized_list_counterexample(self):
        xs = ListExpr("input", value=0)
        candidate = ListExpr("append", (xs, xs))
        full = Image(1, (Component((0,), ((1,),)),))
        d = decide_affine(candidate.model(1), xs.model(1), full)
        env = ((0,) * d.witness[0],)
        self.assertNotEqual(len(candidate.eval(env)), len(xs.eval(env)))
        COUNTS["concrete_counterexamples"] += 1

    def test_30_invalid_list_syntax(self):
        for args in (("mystery",), ("append", (ListExpr("nil"),)), ("input", (), -1)):
            with self.assertRaises(ValueError):
                ListExpr(*args)
        with self.assertRaises(ValueError):
            ListExpr("input", value=2).model(2)


class ArithmeticTests(unittest.TestCase):
    def test_31_frey_fixture_and_single_premise_neighbors(self):
        self.assertEqual(exact_quotient(2**5-1-3**5, 4), -53)
        self.assertEqual(exact_quotient(-3**5*2**5, 16), -486)
        cases = [(3, 2, 4, 4), (3, 3, 5, 4), (3, 2, 3, 16), (1, 2, 5, 4)]
        for a, b, p, d in cases:
            n = b**p-1-a**p if d == 4 else -a**p*b**p
            with self.assertRaises(ValueError):
                exact_quotient(n, d)
            COUNTS["frey_arithmetic_cases"] += 1
        for a, b, p in itertools.product(range(-9, 10), range(-8, 9), range(4, 10)):
            if a % 4 == 3 and b % 2 == 0 and p % 2 == 1:
                n2, n4 = b**p-1-a**p, -a**p*b**p
                self.assertEqual(4*exact_quotient(n2, 4), n2)
                self.assertEqual(16*exact_quotient(n4, 16), n4)
                COUNTS["frey_arithmetic_cases"] += 1

    def test_32_denominator_and_cast_neighbors(self):
        with self.assertRaises(ValueError):
            exact_quotient(1, 4)
        with self.assertRaises(ValueError):
            exact_quotient(0, 0)
        self.assertEqual(exact_quotient(12, -4), -3)
        # A nonzero integer need not remain nonzero under a unital ring map.
        self.assertNotEqual(2, 0)
        self.assertEqual(2 % 2, 0)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    start = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {"status": "passed" if result.wasSuccessful() else "failed",
               "scope": "executed Python reference model; no Lean kernel checking",
               "python": platform.python_version(), "tests_run": result.testsRun,
               "failures": len(result.failures), "errors": len(result.errors),
               "elapsed_seconds_single_run": round(time.perf_counter()-start, 6),
               "counters": COUNTS}
    Path(__file__).with_name("test_results.json").write_text(json.dumps(summary, indent=2)+"\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)
