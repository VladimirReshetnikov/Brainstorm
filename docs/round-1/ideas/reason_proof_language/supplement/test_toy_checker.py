"""Regression tests for the small evidence model, not for Lean or Reason."""
import unittest
from toy_checker import (
    Atom, Arrow, Product, Var, Lam, App, Pair, Fst, Snd, CheckError,
    ResourceLimit, Query, Certificate, Claim, Status, check, certify,
    replay, select_candidate, assemble_plan,
)

A, B, C = Atom("A"), Atom("B"), Atom("C")
identity = Lam("x", A, Var("x"))


class EvidenceTests(unittest.TestCase):
    def test_01_identity(self):
        check(identity, Arrow(A, A))

    def test_02_structural_application(self):
        target = Arrow(Arrow(A, Arrow(B, C)),
                       Arrow(Arrow(A, B), Arrow(A, C)))
        term = Lam("f", Arrow(A, Arrow(B, C)),
                   Lam("g", Arrow(A, B), Lam("x", A,
                       App(App(Var("f"), Var("x")),
                           App(Var("g"), Var("x"))))))
        check(term, target)

    def test_03_product_swap(self):
        term = Lam("p", Product(A, B), Pair(Snd(Var("p")), Fst(Var("p"))))
        check(term, Arrow(Product(A, B), Product(B, A)))

    def test_04_wrong_target(self):
        with self.assertRaises(CheckError):
            check(identity, Arrow(A, B))

    def test_05_free_variable(self):
        with self.assertRaises(CheckError):
            check(Var("unavailable"), A)

    def test_06_apply_nonfunction(self):
        with self.assertRaises(CheckError):
            check(App(Var("x"), Var("x")), A, (("x", A),))

    def test_07_wrong_argument_type(self):
        with self.assertRaises(CheckError):
            check(App(Var("f"), Var("y")), B,
                  (("f", Arrow(A, B)), ("y", C)))

    def test_08_variable_does_not_escape_lambda(self):
        with self.assertRaises(CheckError):
            check(Pair(identity, Var("x")), Product(Arrow(A, A), A))

    def test_09_two_valid_proofs_same_target(self):
        target = Arrow(A, Arrow(A, A))
        check(Lam("x", A, Lam("y", A, Var("x"))), target)
        check(Lam("x", A, Lam("y", A, Var("y"))), target)

    def test_10_invalid_type_annotation(self):
        with self.assertRaises(CheckError):
            check(Lam("x", "not-a-type", Var("x")), Arrow(A, A))

    def test_11_lexical_shadowing(self):
        check(Lam("x", A, Lam("x", B, Var("x"))), Arrow(A, Arrow(B, B)))

    def test_12_duplicate_external_binding(self):
        with self.assertRaises(CheckError):
            check(Var("x"), A, (("x", A), ("x", B)))

    def test_13_replay_wrong_target(self):
        cert = certify(Query("worker-1", (), Arrow(A, A)), identity)
        with self.assertRaises(CheckError):
            replay(cert, Query("worker-1", (), Arrow(A, B)))

    def test_14_replay_stale_worker(self):
        cert = certify(Query("worker-1", (), Arrow(A, A)), identity)
        with self.assertRaises(CheckError):
            replay(cert, Query("worker-2", (), Arrow(A, A)))

    def test_15_replay_changed_context(self):
        cert = certify(Query("worker-1", (("x", A),), A), Var("x"))
        with self.assertRaises(CheckError):
            replay(cert, Query("worker-1", (("y", A),), A))

    def test_16_forged_certificate_rechecked(self):
        query = Query("worker-1", (), A)
        forged = Certificate(query, Var("not-in-scope"))
        with self.assertRaises(CheckError):
            replay(forged, query)

    def test_17_zero_budget_does_not_request_iterator(self):
        class MustNotIterate:
            def __iter__(self):
                raise AssertionError("candidate pool must not be inspected")
        result = select_candidate(Query("w", (), A), MustNotIterate(), 0)
        self.assertEqual(result.status, Status.BUDGET_EXHAUSTED)
        self.assertEqual(result.inspected, 0)
        self.assertIsNone(result.certificate)

    def test_18_budget_does_not_inspect_next_candidate(self):
        seen = []
        def stream():
            seen.append(1)
            yield Var("bad")
            seen.append(2)
            yield identity
        result = select_candidate(Query("w", (), Arrow(A, A)), stream(), 1)
        self.assertEqual(result.status, Status.BUDGET_EXHAUSTED)
        self.assertEqual(seen, [1])
        self.assertIsNone(result.certificate)

    def test_19_rejection_then_success(self):
        query = Query("w", (), Arrow(A, A))
        result = select_candidate(query, [Var("bad"), identity], 2)
        self.assertEqual(result.status, Status.CHECKED)
        self.assertEqual(result.inspected, 2)
        replay(result.certificate, query)

    def test_20_pool_end_is_not_negation(self):
        result = select_candidate(Query("w", (), A), [], 2)
        self.assertEqual(result.status, Status.POOL_ENDED)
        self.assertIsNone(result.certificate)

    def test_21_negative_budget_rejected(self):
        with self.assertRaises(CheckError):
            select_candidate(Query("w", (), A), [], -1)

    def test_22_checker_budget_exhaustion(self):
        with self.assertRaises(ResourceLimit):
            check(identity, Arrow(A, A), operation_limit=1)

    def test_23_valid_sequential_claims(self):
        query = Query("w", (), Arrow(A, A))
        claims = (Claim("id", Arrow(A, A), identity),
                  Claim("again", Arrow(A, A), Var("id")))
        cert = assemble_plan(query, claims, Var("again"))
        replay(cert, query)
        check(cert.term, query.target)  # discharged, empty original context

    def test_24_self_reference_rejected(self):
        with self.assertRaises(CheckError):
            assemble_plan(Query("w", (), A),
                          (Claim("h", A, Var("h")),), Var("h"))

    def test_25_forward_reference_rejected(self):
        with self.assertRaises(CheckError):
            assemble_plan(Query("w", (), Arrow(A, A)),
                          (Claim("first", Arrow(A, A), Var("later")),
                           Claim("later", Arrow(A, A), identity)), Var("first"))

    def test_26_duplicate_claim_name_rejected(self):
        with self.assertRaises(CheckError):
            assemble_plan(Query("w", (), Arrow(A, A)),
                          (Claim("id", Arrow(A, A), identity),
                           Claim("id", Arrow(A, A), identity)), Var("id"))

    def test_27_claim_cannot_shadow_external_hypothesis(self):
        with self.assertRaises(CheckError):
            assemble_plan(Query("w", (("x", A),), A),
                          (Claim("x", A, Var("x")),), Var("x"))

    def test_28_projection_requires_product(self):
        with self.assertRaises(CheckError):
            check(Fst(Var("x")), A, (("x", A),))

    def test_29_unknown_term_constructor_rejected(self):
        with self.assertRaises(CheckError):
            check({"pretend": "proof"}, A)

    def test_30_empty_type_name_rejected(self):
        with self.assertRaises(CheckError):
            check(Var("x"), Atom(""), (("x", Atom("")),))

    def test_31_exact_origin_accepts_valid_replay(self):
        query = Query("w", (), Arrow(A, A))
        replay(certify(query, identity), query)

    def test_32_empty_plan_checks_conclusion(self):
        query = Query("w", (), Arrow(A, A))
        replay(assemble_plan(query, (), identity), query)


if __name__ == "__main__":
    unittest.main(verbosity=2)
