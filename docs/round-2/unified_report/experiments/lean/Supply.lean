import Mathlib
-- Locality / derivative transfer
#check @HasDerivAt.congr_of_eventuallyEq
#check @Filter.EventuallyEq.deriv_eq
#check @IsOpen.mem_nhds
#check @HasDerivAt.comp
-- Formal power series: coefficients, truncation, substitution, derivative, extensionality
#check @PowerSeries.coeff_mul
#check @PowerSeries.trunc
#check @PowerSeries.coeff_trunc
#check @PowerSeries.HasSubst
#check @PowerSeries.subst
#check @PowerSeries.derivative
#check @PowerSeries.coeff_derivative
#check @PowerSeries.ext
#check @PowerSeries.exp
#check @PowerSeries.coeff_exp
#check @PowerSeries.X_pow_dvd_iff
#check @PowerSeries.order
-- Polynomials: noncomputable mathematical face
#check @Polynomial.eval
#check @Polynomial.derivative
#check @Polynomial.roots
#check @Polynomial.card_roots'
#check @Polynomial.rootMultiplicity
-- Radicals and branches
#check @Real.sqrt_eq_iff_mul_self_eq
#check @Real.sqrt_eq_iff'
#check @Real.sqrt_sq_eq_abs
#check @Real.sqrt_nonneg
-- Guarded casts (natural subtraction, exact division) and reflection
#check @Nat.cast_sub
#check @Nat.cast_div
#check @Nat.cast_injective
#check @Nat.cast_inj
-- Units versus nonzero
#check @IsUnit.mul_left_cancel
#check @IsUnit.mul_right_inj
#check @mul_right_cancel₀
-- Finite sums: reindexing, telescoping, interval/range bridges
#check @Finset.sum_bij
#check @Finset.sum_nbij'
#check @Finset.sum_range_sub
#check @Finset.sum_range_succ
#check @Finset.range_eq_Ico
-- Real roots: intermediate value, monotonicity
#check @intermediate_value_Icc
#check @StrictMonoOn.injOn
#check @exists_deriv_eq_slope
-- Scalar transport into a Q-algebra
#check @algebraMap
#check @map_natCast
#check @Rat.cast_injective
-- Native computation axiom constant historically blacklisted
#check @Lean.ofReduceBool
-- Is Mathlib's Polynomial executable? (expected: not computable)
#eval (Polynomial.X : Polynomial ℤ).natDegree
-- Does a Groebner-basis tactic exist at this pin?
example (x y : ℚ) (h : x - y = 0) : x^2 - y^2 = 0 := by grobner
-- Does polyrith still exist as a command at this pin?
example (x y : ℚ) (h : x - y = 0) : x^2 - y^2 = 0 := by polyrith
