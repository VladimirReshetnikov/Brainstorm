import Mathlib.Tactic.LinearCombination

/-! Focused audit of the secondary synthesis. These are original-target
theorems, not a new checker or a performance benchmark. -/
namespace SecondaryReview

theorem grobnerRat (x y : ℚ) (h : x - y = 0) : x ^ 2 - y ^ 2 = 0 := by
  grobner

theorem linearCombinationRat (x y : ℚ) (h : x - y = 0) :
    x ^ 2 - y ^ 2 = 0 := by
  linear_combination (x + y) * h

theorem pureDecide : ((2 : Nat) ^ 20) % 7 = 4 := by decide
theorem nativeDecide : ((2 : Nat) ^ 20) % 7 = 4 := by native_decide

#print axioms grobnerRat
#print axioms linearCombinationRat
#print axioms pureDecide
#print axioms nativeDecide

end SecondaryReview

