import Mathlib

/-! The nine round-4 exporters emit generic implication theorems whose atoms are `Prop`
variables and whose rules are hypotheses.  Every report says the same thing about them:
compiling such a file checks proof assembly, not mathematics, because no registry links the
atom names to theorems.  This file supplies that link once, at the ProveIt pin: the generic
routes exported by Laurel (`frey_a4.lean`), Bryony (`Requirements.lean`) and Sorrel
(`SelectedPlan.lean`) are copied verbatim (modulo namespace) and then *instantiated* with the
kernel-checked Frey arithmetic of the round-3 review, so that the conditional route becomes an
unconditional theorem about the actual coefficients. -/
namespace FreyRoutes

/-! ### The arithmetic registry (round-3 `FreyExact.lean`, plus the `p ≥ 2` sharpening
that Clover, Juniper, Laurel and Rowan state for the first coefficient). -/

theorem sixteen_dvd_pow (b : ℤ) (p : ℕ) (hb : 2 ∣ b) (hp : 4 ≤ p) : 16 ∣ b ^ p := by
  obtain ⟨k, rfl⟩ := hb
  obtain ⟨q, rfl⟩ : ∃ q, p = q + 4 := ⟨p - 4, by omega⟩
  rw [mul_pow, pow_add]
  have h16 : (16 : ℤ) ∣ 2 ^ 4 := by norm_num
  exact (h16.mul_left (2 ^ q)).mul_right (k ^ (q + 4))

theorem four_dvd_pow (b : ℤ) (p : ℕ) (hb : 2 ∣ b) (hp : 2 ≤ p) : 4 ∣ b ^ p := by
  obtain ⟨k, rfl⟩ := hb
  obtain ⟨q, rfl⟩ : ∃ q, p = q + 2 := ⟨p - 2, by omega⟩
  rw [mul_pow, pow_add]
  have h4 : (4 : ℤ) ∣ 2 ^ 2 := by norm_num
  exact (h4.mul_left (2 ^ q)).mul_right (k ^ (q + 2))

theorem odd_pow_mod_four (a : ℤ) (p : ℕ) (hp : Odd p) (ha : a ≡ 3 [ZMOD 4]) :
    a ^ p ≡ 3 [ZMOD 4] := by
  have h1 : a ^ p ≡ 3 ^ p [ZMOD 4] := ha.pow p
  have h2 : (3 : ℤ) ^ p ≡ 3 [ZMOD 4] := by
    obtain ⟨m, rfl⟩ := hp
    rw [pow_succ, pow_mul]
    have h9 : (3 : ℤ) ^ 2 ≡ 1 [ZMOD 4] := by decide
    calc ((3 : ℤ) ^ 2) ^ m * 3 ≡ 1 ^ m * 3 [ZMOD 4] := (h9.pow m).mul_right 3
      _ = 3 := by simp
  exact h1.trans h2

/-- First numerator, with the sharpened bound `2 ≤ p` (the round-3 statement used `4 ≤ p`). -/
theorem four_dvd_a2 (a b : ℤ) (p : ℕ) (hp : Odd p) (hp2 : 2 ≤ p)
    (ha : a ≡ 3 [ZMOD 4]) (hb : 2 ∣ b) : 4 ∣ b ^ p - 1 - a ^ p := by
  have hb0 : b ^ p ≡ 0 [ZMOD 4] := Int.modEq_zero_iff_dvd.mpr (four_dvd_pow b p hb hp2)
  have h : b ^ p - 1 - a ^ p ≡ 0 - 1 - 3 [ZMOD 4] :=
    (hb0.sub_right 1).sub (odd_pow_mod_four a p hp ha)
  exact Int.modEq_zero_iff_dvd.mp (h.trans (by decide))

theorem sixteen_dvd_a4 (a b : ℤ) (p : ℕ) (hp4 : 4 ≤ p) (hb : 2 ∣ b) :
    16 ∣ -(a ^ p * b ^ p) :=
  (dvd_neg).mpr ((sixteen_dvd_pow b p hb hp4).mul_left (a ^ p))

/-! ### The generic routes, as exported by the round-4 companions. -/

/-- Laurel `frey_a4.lean`, `route_0`: residual support `div16`. -/
theorem laurel_route_0 (P0 P1 P2 P3 P4 : Prop)
    (r1 : P2 -> P3 -> P4) (k0 : P3) (h0 : P2) : P4 := by
  have d0 : P4 := r1 h0 k0
  exact d0

/-- Laurel `frey_a4.lean`, `route_1`: residual support `even_b`. -/
theorem laurel_route_1 (P0 P1 P2 P3 P4 : Prop)
    (r0 : P0 -> P1 -> P2) (r1 : P2 -> P3 -> P4) (k0 : P3) (k1 : P1) (h0 : P0) : P4 := by
  have d0 : P2 := r0 h0 k1
  have d1 : P4 := r1 d0 k0
  exact d1

/-- Bryony `Requirements.lean`, `route_1`: prospective premises `EvenB, LargeP`. -/
theorem bryony_route_1 (p0 p1 p2 p3 p4 p5 : Prop)
    (r0 : p0 -> p1 -> p2) (r1 : p2 -> p3) (r2 : p3 -> p4 -> p5)
    (k0 : p4) (h0 : p0) (h1 : p1) : p5 :=
  r2 (r1 (r0 (h0) (h1))) (k0)

/-- Sorrel `SelectedPlan.lean`: the support `{EvenB, LargeP, Direct4}` for `Dvd4 ∧ Dvd16`. -/
theorem sorrel_selectedPlan (A0 A1 A2 A3 A4 A5 A6 A7 : Prop)
    (r0 : A4 -> A5 -> A2) (r2 : A1 -> A3) (r3 : A3 -> A2 -> A0)
    (hA1 : A1) (hA4 : A4) (hA5 : A5) : A0 := (r3 (r2 hA1) (r0 hA4 hA5))

/-! ### Instantiation: the routes applied to the registry give the coefficient identities. -/

/-- Laurel's evenness route, instantiated: `P0 := 2 ∣ b`, `P1 := 4 ≤ p`,
`P2 := 16 ∣ N₄`, `P3 := (16 : ℚ) ≠ 0`, `P4 :=` the cast identity. -/
theorem a4_cast_by_laurel_route_1 (a b : ℤ) (p : ℕ) (hp4 : 4 ≤ p) (hb : 2 ∣ b) :
    ((-(a ^ p * b ^ p) / 16 : ℤ) : ℚ) = ((-(a ^ p * b ^ p) : ℤ) : ℚ) / 16 :=
  laurel_route_1 (2 ∣ b) (4 ≤ p) (16 ∣ -(a ^ p * b ^ p)) ((16 : ℚ) ≠ 0)
    (((-(a ^ p * b ^ p) / 16 : ℤ) : ℚ) = ((-(a ^ p * b ^ p) : ℤ) : ℚ) / 16)
    (fun he hp => sixteen_dvd_a4 a b p hp he)
    (fun hd hz => Int.cast_div hd hz)
    (by norm_num) hp4 hb

/-- Laurel's direct route: the consumer's own guard `16 ∣ N₄` offered as the residual. -/
theorem a4_cast_by_laurel_route_0 (a b : ℤ) (p : ℕ) (hd : 16 ∣ -(a ^ p * b ^ p)) :
    ((-(a ^ p * b ^ p) / 16 : ℤ) : ℚ) = ((-(a ^ p * b ^ p) : ℤ) : ℚ) / 16 :=
  laurel_route_0 (2 ∣ b) (4 ≤ p) (16 ∣ -(a ^ p * b ^ p)) ((16 : ℚ) ≠ 0)
    (((-(a ^ p * b ^ p) / 16 : ℤ) : ℚ) = ((-(a ^ p * b ^ p) : ℤ) : ℚ) / 16)
    (fun hd hz => Int.cast_div hd hz) (by norm_num) hd

/-- Bryony's route through `NumeratorExact` (here read as `16 ∣ N₄`, so `r1` is the identity). -/
theorem a4_cast_by_bryony_route_1 (a b : ℤ) (p : ℕ) (hp4 : 4 ≤ p) (hb : 2 ∣ b) :
    ((-(a ^ p * b ^ p) / 16 : ℤ) : ℚ) = ((-(a ^ p * b ^ p) : ℤ) : ℚ) / 16 :=
  bryony_route_1 (2 ∣ b) (4 ≤ p) (16 ∣ -(a ^ p * b ^ p)) (16 ∣ -(a ^ p * b ^ p))
    ((16 : ℚ) ≠ 0)
    (((-(a ^ p * b ^ p) / 16 : ℤ) : ℚ) = ((-(a ^ p * b ^ p) : ℤ) : ℚ) / 16)
    (fun he hp => sixteen_dvd_a4 a b p hp he) id (fun hd hz => Int.cast_div hd hz)
    (by norm_num) hb hp4

/-- Sorrel's plan, instantiated with the direct first-coefficient proof as `Direct4`:
both divisibilities from `{EvenB, LargeP, Direct4}`. -/
theorem both_dvd_by_sorrel_plan (a b : ℤ) (p : ℕ) (hp : Odd p) (hp4 : 4 ≤ p)
    (ha : a ≡ 3 [ZMOD 4]) (hb : 2 ∣ b) :
    4 ∣ b ^ p - 1 - a ^ p ∧ 16 ∣ -(a ^ p * b ^ p) :=
  sorrel_selectedPlan (4 ∣ b ^ p - 1 - a ^ p ∧ 16 ∣ -(a ^ p * b ^ p))
    (4 ∣ b ^ p - 1 - a ^ p) (16 ∣ -(a ^ p * b ^ p)) (4 ∣ b ^ p - 1 - a ^ p)
    (2 ∣ b) (4 ≤ p) (Odd p) (a ≡ 3 [ZMOD 4])
    (fun he hp => sixteen_dvd_a4 a b p hp he) id (fun h4 h16 => ⟨h4, h16⟩)
    (four_dvd_a2 a b p hp (by omega) ha hb) hb hp4

/-- The satisfiable fixture and the four neighbours, as in every report. -/
example : ((2 : ℤ) ^ 5 - 1 - 3 ^ 5) / 4 = -53 := by decide
example : (-((3 : ℤ) ^ 5 * 2 ^ 5)) / 16 = -486 := by decide
example : ¬ (4 : ℤ) ∣ (2 : ℤ) ^ 4 - 1 - 3 ^ 4 := by decide      -- (3,2,4): p even
example : ¬ (4 : ℤ) ∣ (3 : ℤ) ^ 5 - 1 - 3 ^ 5 := by decide      -- (3,3,5): b odd
example : ¬ (16 : ℤ) ∣ -((3 : ℤ) ^ 3 * 2 ^ 3) := by decide     -- (3,2,3): p < 4
example : ¬ (4 : ℤ) ∣ (2 : ℤ) ^ 5 - 1 - 1 ^ 5 := by decide      -- (1,2,5): a ≡ 1
/-- The sharpened bound is witnessed: `(3,2,3)` satisfies the first-coefficient interface. -/
example : (4 : ℤ) ∣ (2 : ℤ) ^ 3 - 1 - 3 ^ 3 := by decide

#print axioms four_dvd_a2
#print axioms a4_cast_by_laurel_route_1
#print axioms a4_cast_by_laurel_route_0
#print axioms a4_cast_by_bryony_route_1
#print axioms both_dvd_by_sorrel_plan
end FreyRoutes
