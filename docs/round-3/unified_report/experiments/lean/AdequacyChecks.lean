/-! Raw affine coefficient equality is not complete for source semantics over
List Empty: the only realizable length is zero. This file uses bundled Init. -/
namespace ObservationAdequacy

def affine (c a n : Nat) : Nat := c + a * n

theorem empty_models_agree :
    ∀ xs : List Empty, affine 0 1 xs.length = affine 0 0 xs.length := by
  intro xs
  cases xs with
  | nil => rfl
  | cons x _ => exact nomatch x

theorem empty_coefficients_differ : (0, 1) ≠ ((0, 0) : Nat × Nat) := by
  decide

theorem coefficient_test_not_complete :
    ¬ (∀ c a d b : Nat,
      (∀ xs : List Empty, affine c a xs.length = affine d b xs.length) →
      (c, a) = (d, b)) := by
  intro h
  exact empty_coefficients_differ (h 0 1 0 0 empty_models_agree)

#print axioms empty_models_agree
#print axioms empty_coefficients_differ
#print axioms coefficient_test_not_complete
end ObservationAdequacy
