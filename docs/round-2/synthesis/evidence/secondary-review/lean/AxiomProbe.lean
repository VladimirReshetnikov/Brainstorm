/-! Same arithmetic proposition as the imported Axioms.lean probe, with no imports.
This tests the exact axiom inventory separately from the Mathlib-importing target checks. -/
namespace SecondaryReviewNoImports

theorem pureDecide : ((2 : Nat) ^ 20) % 7 = 4 := by decide
theorem nativeDecide : ((2 : Nat) ^ 20) % 7 = 4 := by native_decide

#print axioms pureDecide
#print axioms nativeDecide

end SecondaryReviewNoImports

