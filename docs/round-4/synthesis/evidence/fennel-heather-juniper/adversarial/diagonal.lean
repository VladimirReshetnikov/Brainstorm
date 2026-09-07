-- GENERATED PROOF CANDIDATE; NOT COMPILED IN THIS DELIVERY.
-- Python acceptance does not establish Lean acceptance.
import Mathlib
set_option autoImplicit false

-- Source inputs: {'xs': 'v0', 'ys': 'v1'}
theorem heather_guardprobe (v0 v1 : List Nat) (h : v0.length = v1.length) :
    ((v0 ++ v1)).length = ((v1 ++ v1)).length := by
  simp only [List.length_append, List.length_reverse, List.length_nil, List.length_cons]
  omega
