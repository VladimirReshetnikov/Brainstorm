"""Executed regression tests for the restricted model, not a Lean test suite."""
import itertools
import json
import unittest
from dataclasses import replace
from pathlib import Path
from clover_slice import (Atom, Term, Proof, Plan, Request, PlanError, RULES, atom, comp,
                         parse_atom, elaborate, solve, check_plan, export_document,
                         arena_for, ground, subst_atom, well_formed_atom)

F, G, R, K = (Term(x) for x in ('f', 'g', 'r', 'k'))

def req(goal, hypotheses=(), binders=(F, G, R, K), **kwargs):
    return Request('test-snapshot', binders, tuple(hypotheses), goal, **kwargs)

class CloverTests(unittest.TestCase):
    def test_01_direct_assumption(self):
        a = atom('injective', F)
        self.assertEqual(solve(req(a, [('h', a)])).status, 'plan_checked')

    def test_02_inverse_implies_injective(self):
        out = solve(req(atom('injective', F), [('h', atom('left_inverse', R, F))]))
        self.assertEqual(out.support, ['h'])

    def test_03_composition(self):
        q = req(atom('injective', comp(G, F)),
                [('hf', atom('injective', F)), ('hg', atom('injective', G))])
        self.assertEqual(solve(q).status, 'plan_checked')

    def test_04_involution_chain(self):
        q = req(atom('injective', F), [('h', atom('involutive', F))])
        self.assertEqual(solve(q).metrics['proof_nodes'], 3)

    def test_05_no_injectivity_from_nothing(self):
        self.assertEqual(solve(req(atom('injective', F))).status, 'unresolved')

    def test_06_seedless_cycles(self):
        out = solve(req(atom('same', F, G)))
        self.assertEqual(out.status, 'unresolved')
        self.assertIn('not a refutation', out.detail)

    def test_07_equality_transport(self):
        q = req(atom('injective', G), [('e', atom('same', F, G)), ('h', atom('injective', F))])
        self.assertEqual(solve(q).status, 'plan_checked')

    def test_08_wrong_function_no_transport(self):
        q = req(atom('injective', G), [('h', atom('injective', F))])
        self.assertEqual(solve(q).status, 'unresolved')

    def test_09_wrong_composition_factor(self):
        q = req(atom('injective', comp(G, F)), [('h', atom('injective', F))])
        self.assertEqual(solve(q).status, 'unresolved')

    def test_10_budget_is_not_false(self):
        q = req(atom('injective', F), [('h', atom('involutive', F))])
        self.assertEqual(solve(q, max_attempts=0).status, 'resource_limit')

    def test_11_snapshot_mismatch(self):
        q = req(atom('injective', F), [('h', atom('involutive', F))])
        p = solve(q).plan
        with self.assertRaises(PlanError):
            check_plan(replace(q, source_id='different'), p)

    def test_12_target_tampering(self):
        q = req(atom('injective', F), [('h', atom('involutive', F))])
        p = solve(q).plan
        with self.assertRaises(PlanError):
            check_plan(q, replace(p, goal=atom('injective', G)))

    def test_13_forged_root(self):
        q = req(atom('injective', F), [('h', atom('involutive', F))])
        p = solve(q).plan
        with self.assertRaises(PlanError):
            check_plan(q, replace(p, proof=replace(p.proof, conclusion=atom('injective', G))))

    def test_14_missing_assumption(self):
        q = req(atom('injective', F), [('h', atom('injective', F))])
        p = solve(q).plan
        q2 = replace(q, assumptions=())
        with self.assertRaises(PlanError):
            check_plan(q2, replace(p, request_id=q2.identity))

    def test_15_wrong_substitution(self):
        q = req(atom('injective', F), [('h', atom('left_inverse', R, F))])
        p = solve(q).plan
        bad = replace(p.proof, substitution=(('f', G), ('g', R)))
        with self.assertRaises(PlanError):
            check_plan(q, replace(p, proof=bad))

    def test_16_forbidden_rule(self):
        q = req(atom('injective', F), [('h', atom('involutive', F))])
        p = solve(q).plan
        q2 = replace(q, allowed=('inj_comp',))
        with self.assertRaises(PlanError):
            check_plan(q2, replace(p, request_id=q2.identity))

    def test_17_required_root(self):
        q = req(atom('injective', comp(G, F)),
                [('f', atom('injective', F)), ('g', atom('injective', G))],
                required_root='inj_comp')
        out = solve(q)
        self.assertEqual(out.status, 'plan_checked')
        self.assertEqual(out.plan.proof.name, 'inj_comp')

    def test_18_impossible_required_root(self):
        q = req(atom('injective', F), [('h', atom('injective', F))], required_root='inj_comp')
        self.assertEqual(solve(q).status, 'unresolved')

    def test_19_sibling_scope_isolation(self):
        source = '''fix f : End
scope
assume h : injective f
claim yes : injective f
end
scope
claim no : injective f
end'''
        self.assertEqual([c.result.status for c in elaborate(source)], ['plan_checked', 'unresolved'])

    def test_20_shadowed_name_identity(self):
        source = '''fix f : End
assume h : injective f
scope
fix f : End
claim inner : injective f
end
claim outer : injective f'''
        self.assertEqual([c.result.status for c in elaborate(source)], ['unresolved', 'plan_checked'])

    def test_21_unfinished_claim_is_not_seed(self):
        source = '''fix f : End
claim first : involutive f
claim second : injective f'''
        self.assertTrue(all(c.result.status == 'unresolved' for c in elaborate(source)))

    def test_22_unused_bad_claim_blocks_complete_document(self):
        cs = elaborate('fix f : End\nclaim bad : involutive f\nclaim true : same f f')
        self.assertEqual([c.result.status for c in cs], ['unresolved', 'plan_checked'])
        self.assertFalse(all(c.result.status == 'plan_checked' for c in cs))

    def test_23_bad_arity(self):
        with self.assertRaises(ValueError):
            parse_atom('same f', {'f': F})

    def test_24_unknown_symbol(self):
        with self.assertRaises(ValueError):
            parse_atom('injective absent', {'f': F})

    def test_25_unclosed_scope(self):
        with self.assertRaises(ValueError):
            elaborate('fix f : End\nscope')

    def test_26_duplicate_claim(self):
        with self.assertRaises(ValueError):
            elaborate('fix f : End\nclaim a : same f f\nclaim a : same f f')

    def test_27_schedule_independence_status(self):
        # Exhaust all 32 subsets of these five seeds; proofs may differ.
        pool = [atom('injective', F), atom('injective', G), atom('involutive', F),
                atom('same', F, G), atom('left_inverse', R, F)]
        for mask in range(32):
            hs = [(f'h{i}', a) for i, a in enumerate(pool) if mask & (1 << i)]
            q = req(atom('injective', comp(G, F)), hs)
            a, b = solve(q), solve(q, reverse_schedule=True)
            self.assertEqual(a.status, b.status)
            if a.plan:
                check_plan(q, a.plan)
                check_plan(q, b.plan)

    def test_28_no_arena_invention(self):
        q = req(atom('injective', comp(G, F)), [('h', atom('involutive', F))])
        arena = set(arena_for(q))
        m = dict(instance_attempts=0)
        for r in ground(q, 50000, m):
            for a in r.premises + (r.conclusion,):
                for t in a.args:
                    self.assertTrue(t.subterms() <= arena)

    def test_29_profile_reduces_instantiations(self):
        q = req(atom('injective', comp(G, F)),
                [('h', atom('left_inverse', R, F)), ('j', atom('injective', G))])
        full = solve(q)
        narrow = solve(replace(q, allowed=('inj_comp', 'inj_from_left_inverse')))
        self.assertEqual(narrow.status, full.status)
        self.assertLess(narrow.metrics['instance_attempts'], full.metrics['instance_attempts'])

    def test_30_export_no_hole_or_postulated_rule(self):
        cs = elaborate('fix f : End\nassume h : involutive f\nclaim a : injective f')
        text = export_document(cs)
        self.assertIn('inj_from_left_inverse', text)
        self.assertNotIn('sorry', text)
        self.assertNotIn('axiom ', text)

    def test_31_nested_composition(self):
        q = req(atom('injective', comp(K, comp(G, F))),
                [('f', atom('injective', F)), ('g', atom('injective', G)), ('k', atom('injective', K))])
        self.assertEqual(solve(q).status, 'plan_checked')

    def test_32_same_transitivity(self):
        q = req(atom('same', F, K), [('a', atom('same', F, G)), ('b', atom('same', G, K))])
        self.assertEqual(solve(q).status, 'plan_checked')

    def test_33_out_of_scope_binder(self):
        q = req(atom('injective', F), binders=(G,))
        with self.assertRaises(ValueError):
            solve(q)

    def test_34_no_name_based_inverse_guess(self):
        cs = elaborate('fix f inverse : End\nclaim c : injective f')
        self.assertEqual(cs[0].result.status, 'unresolved')

    def test_35_rules_on_all_two_element_endomorphisms(self):
        # Exhaustive finite semantic check, NOT a universal soundness proof.
        functions = list(itertools.product(range(2), repeat=2))
        def ev(t, rho):
            if t.head == 'compose':
                g, f = (ev(a, rho) for a in t.args)
                return tuple(g[f[x]] for x in range(2))
            return rho[t.head]
        def holds(a, rho):
            args = [ev(t, rho) for t in a.args]
            if a.pred == 'injective':
                return len(set(args[0])) == 2
            if a.pred == 'involutive':
                return all(args[0][args[0][x]] == x for x in range(2))
            if a.pred == 'left_inverse':
                return all(args[0][args[1][x]] == x for x in range(2))
            return args[0] == args[1]
        checked = 0
        for r in RULES:
            for values in itertools.product(functions, repeat=len(r.variables)):
                rho = {'$' + k: v for k, v in zip(r.variables, values)}
                if all(holds(a, rho) for a in r.premises):
                    self.assertTrue(holds(r.conclusion, rho))
                checked += 1
        self.assertEqual(checked, 136)

if __name__ == '__main__':
    unittest.main(verbosity=2)
