-- Source query: second_coefficient; remaining assumptions: ['cached']
-- UNCOMPILED HERE. Rules below are theorem parameters, not proved arithmetic.
set_option autoImplicit false
theorem fennel_1_0
    (P0 P1 P2 P3 P4 P5 P6 P7 P8 P9 : Prop)
    (h5 : P8)
    (r3 : P8 -> P7)
    : P7 := by
  have p0 : P8 := h5
  have p1 : P7 := r3 p0
  exact p1
