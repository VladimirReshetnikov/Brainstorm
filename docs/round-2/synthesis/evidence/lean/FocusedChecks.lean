import Mathlib.Data.Real.Basic
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
Focused round-2 synthesis checks. These are ordinary Lean theorems using existing
mathlib, not an implementation of any proposed proof language, provider protocol,
or certificate checker. No sorry, native_decide, or new axioms are used.

1. Totalized real division refutes unguarded cancellation at x = 1.
2. One forward binomial row is insufficient for the inverse row: the forward
   equations for all relevant lower indices are essential.
-/

namespace Round2Synthesis

theorem cancellation_at_one_fails :
    (((1 : ℝ) ^ 2 - 1) / ((1 : ℝ) - 1)) ≠ (1 : ℝ) + 1 := by
  norm_num

theorem guarded_cancellation (x : ℝ) (hx : x ≠ 1) :
    (x ^ 2 - 1) / (x - 1) = x + 1 := by
  apply (div_eq_iff (sub_ne_zero.mpr hx)).2
  ring

theorem unguarded_cancellation_is_false :
    ¬ (∀ x : ℝ, (x ^ 2 - 1) / (x - 1) = x + 1) := by
  intro h
  exact cancellation_at_one_fails (h 1)

def zeroSequence : ℕ → ℤ := fun _ => 0

def deltaSequence : ℕ → ℤ := fun k => if k = 0 then 1 else 0

def forwardRow (a : ℕ → ℤ) (n : ℕ) : ℤ :=
  ∑ k ∈ Finset.range (n + 1), (Nat.choose n k : ℤ) * a k

def inverseRow (b : ℕ → ℤ) (n : ℕ) : ℤ :=
  ∑ k ∈ Finset.range (n + 1),
    (-1 : ℤ) ^ (n - k) * (Nat.choose n k : ℤ) * b k

theorem one_forward_row_holds :
    deltaSequence 1 = forwardRow zeroSequence 1 := by
  norm_num [forwardRow, zeroSequence, deltaSequence, Finset.sum_range_succ]

theorem inverse_row_value :
    inverseRow deltaSequence 1 = -1 := by
  norm_num [inverseRow, deltaSequence, Finset.sum_range_succ]

theorem corresponding_inverse_row_fails :
    zeroSequence 1 ≠ inverseRow deltaSequence 1 := by
  rw [inverse_row_value]
  norm_num [zeroSequence]

theorem pointwise_binomial_implication_is_false :
    ¬ (∀ a b : ℕ → ℤ,
      b 1 = forwardRow a 1 → a 1 = inverseRow b 1) := by
  intro h
  exact corresponding_inverse_row_fails
    (h zeroSequence deltaSequence one_forward_row_holds)

theorem pointwise_binomial_iff_is_false :
    ¬ (∀ a b : ℕ → ℤ,
      b 1 = forwardRow a 1 ↔ a 1 = inverseRow b 1) := by
  intro h
  exact corresponding_inverse_row_fails
    ((h zeroSequence deltaSequence).mp one_forward_row_holds)

#print axioms cancellation_at_one_fails
#print axioms guarded_cancellation
#print axioms unguarded_cancellation_is_false
#print axioms one_forward_row_holds
#print axioms inverse_row_value
#print axioms corresponding_inverse_row_fails
#print axioms pointwise_binomial_implication_is_false
#print axioms pointwise_binomial_iff_is_false

end Round2Synthesis

