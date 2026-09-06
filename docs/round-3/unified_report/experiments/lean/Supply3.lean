import Mathlib

-- Names and tactics the round-3 reports lean on, probed at the ProveIt pin.
#check @Set.EqOn.eventuallyEq_of_mem
#check @IsOpen.mem_nhds
#check @HasDerivAt.congr_of_eventuallyEq
#check @Filter.EventuallyEq.deriv_eq
#check @Matrix.mul_eq_one_comm
#check @Finite.injective_iff_surjective
#check @Int.cast_div
#check @Int.ModEq.pow
#check @MeasureTheory.tendsto_integral_of_dominated_convergence
#check @MeasureTheory.integral_tsum_of_summable_integral_norm
#check @lipschitzWith_of_nnnorm_deriv_le
#check @Squarefree
#check @Function.Injective.comp
#check @Subtype.ext
#check @MulAction
#check @Std.Do.Triple

example : Continuous (fun x : ℝ => Real.exp (x ^ 2) + 1) := by fun_prop
example (f g : ℝ → ℝ) (U : Set ℝ) (hU : IsOpen U) (x : ℝ) (hx : x ∈ U)
    (h : Set.EqOn f g U) : deriv f x = deriv g x :=
  (h.eventuallyEq_of_mem (hU.mem_nhds hx)).deriv_eq
example (n : ℕ) (A B : Matrix (Fin n) (Fin n) ℤ) (h : A * B = 1) : B * A = 1 :=
  Matrix.mul_eq_one_comm.mp h
example : True := by mvcgen
