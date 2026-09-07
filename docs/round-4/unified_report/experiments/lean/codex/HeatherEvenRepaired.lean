-- Synthesis repair: preserve the exact theorem; tolerate simp closing the goal.
-- GENERATED PROOF CANDIDATE; NOT COMPILED IN THIS DELIVERY.
-- Python acceptance does not establish Lean acceptance.
import Mathlib
set_option autoImplicit false

-- Source inputs: {'xs': 'v0'}
theorem heather_even_reverse_length (v0 : List Nat) (h_v0 : 2 ∣ v0.length) :
    ((v0).reverse).length = (v0).length := by
  simp only [List.length_append, List.length_reverse, List.length_nil, List.length_cons]
  all_goals omega
