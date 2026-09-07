-- Source query: target; remaining assumptions: []
-- UNCOMPILED HERE. Rules below are theorem parameters, not proved arithmetic.
set_option autoImplicit false
theorem fennel_0_0
    (P0 P1 : Prop)
    (h0 : P0)
    (r0 : P0 -> P1)
    : P1 := by
  have p0 : P0 := h0
  have p1 : P1 := r0 p0
  exact p1
