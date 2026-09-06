-- GENERATED PROOF CANDIDATE; NOT COMPILED IN THIS DELIVERY.
-- Python acceptance does not establish Lean acceptance.
import Mathlib
set_option autoImplicit false

-- Source inputs: {'xs': 'v0'}
theorem heather_empty_preserves (v0 : List Empty) :
    (([] : List Empty)).length = (v0).length := by
  have hx_v0 : v0 = [] := by
    cases v0 with
    | nil => rfl
    | cons a _ => exact nomatch a
  subst_vars
  simp
