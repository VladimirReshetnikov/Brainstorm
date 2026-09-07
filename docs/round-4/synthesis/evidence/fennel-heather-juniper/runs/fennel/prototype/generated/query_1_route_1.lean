-- Source query: second_coefficient; remaining assumptions: ['odd', 'residue']
-- UNCOMPILED HERE. Rules below are theorem parameters, not proved arithmetic.
set_option autoImplicit false
theorem fennel_1_1
    (P0 P1 P2 P3 P4 P5 P6 P7 P8 P9 : Prop)
    (h0 : P0)
    (h1 : P1)
    (h2 : P6)
    (h3 : P2)
    (h4 : P3)
    (r1 : P0 -> P1 -> P2 -> P3 -> P5)
    (r2 : P5 -> P6 -> P7)
    : P7 := by
  have p0 : P0 := h0
  have p1 : P1 := h1
  have p2 : P6 := h2
  have p3 : P2 := h3
  have p4 : P3 := h4
  have p5 : P5 := r1 p0 p1 p3 p4
  have p6 : P7 := r2 p5 p2
  exact p6
