-- Source query: fourth_coefficient; remaining assumptions: []
-- UNCOMPILED HERE. Rules below are theorem parameters, not proved arithmetic.
set_option autoImplicit false
theorem fennel_0_0
    (P0 P1 P2 P3 P4 P5 P6 P7 P8 P9 : Prop)
    (h0 : P0)
    (h1 : P1)
    (r0 : P0 -> P1 -> P4)
    : P4 := by
  have p0 : P0 := h0
  have p1 : P1 := h1
  have p2 : P4 := r0 p0 p1
  exact p2
