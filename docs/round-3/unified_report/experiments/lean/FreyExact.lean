import Mathlib

/-! The Frey exact-division proposition stated on paper by five round-3 reports,
checked in Lean at the ProveIt pin (Lean v4.32.0, Mathlib as pinned).
Admissibility: p odd, 4 ≤ p, a ≡ 3 (mod 4), b even. No Fermat equation, primality,
nonzeroness, or coprimality is used. -/
namespace FreyExact

theorem sixteen_dvd_pow (b : ℤ) (p : ℕ) (hb : 2 ∣ b) (hp : 4 ≤ p) : 16 ∣ b ^ p := by
  obtain ⟨k, rfl⟩ := hb
  obtain ⟨q, rfl⟩ : ∃ q, p = q + 4 := ⟨p - 4, by omega⟩
  rw [mul_pow, pow_add]
  have h16 : (16 : ℤ) ∣ 2 ^ 4 := by norm_num
  exact (h16.mul_left (2 ^ q)).mul_right (k ^ (q + 4))

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

/-- First Frey numerator is divisible by 4. -/
theorem four_dvd_a2 (a b : ℤ) (p : ℕ) (hp : Odd p) (hp4 : 4 ≤ p)
    (ha : a ≡ 3 [ZMOD 4]) (hb : 2 ∣ b) : 4 ∣ b ^ p - 1 - a ^ p := by
  have hb4 : 4 ∣ b ^ p := (by norm_num : (4 : ℤ) ∣ 16).trans (sixteen_dvd_pow b p hb hp4)
  have hb0 : b ^ p ≡ 0 [ZMOD 4] := Int.modEq_zero_iff_dvd.mpr hb4
  have h : b ^ p - 1 - a ^ p ≡ 0 - 1 - 3 [ZMOD 4] :=
    (hb0.sub_right 1).sub (odd_pow_mod_four a p hp ha)
  exact Int.modEq_zero_iff_dvd.mp (h.trans (by decide))

/-- Second Frey numerator is divisible by 16. -/
theorem sixteen_dvd_a4 (a b : ℤ) (p : ℕ) (hp4 : 4 ≤ p) (hb : 2 ∣ b) :
    16 ∣ -(a ^ p * b ^ p) :=
  (dvd_neg).mpr ((sixteen_dvd_pow b p hb hp4).mul_left (a ^ p))

/-- Exact-quotient transport: the integer quotients cast to the rational quotients. -/
theorem cast_a2 (a b : ℤ) (p : ℕ) (hp : Odd p) (hp4 : 4 ≤ p)
    (ha : a ≡ 3 [ZMOD 4]) (hb : 2 ∣ b) :
    (((b ^ p - 1 - a ^ p) / 4 : ℤ) : ℚ) = ((b ^ p - 1 - a ^ p : ℤ) : ℚ) / 4 :=
  Int.cast_div (four_dvd_a2 a b p hp hp4 ha hb) (by norm_num)

theorem cast_a4 (a b : ℤ) (p : ℕ) (hp4 : 4 ≤ p) (hb : 2 ∣ b) :
    ((-(a ^ p * b ^ p) / 16 : ℤ) : ℚ) = ((-(a ^ p * b ^ p) : ℤ) : ℚ) / 16 :=
  Int.cast_div (sixteen_dvd_a4 a b p hp4 hb) (by norm_num)

/-- The interface is inhabited: (3, 2, 5) gives a2 = -53 and a4 = -486. -/
example : ((2 : ℤ) ^ 5 - 1 - 3 ^ 5) / 4 = -53 := by decide
example : (-((3 : ℤ) ^ 5 * 2 ^ 5)) / 16 = -486 := by decide

/-- Negative neighbours: each dropped premise admits a concrete failure. -/
example : ¬ (4 : ℤ) ∣ (2 : ℤ) ^ 4 - 1 - 3 ^ 4 := by decide      -- p = 4 even
example : ¬ (4 : ℤ) ∣ (3 : ℤ) ^ 5 - 1 - 3 ^ 5 := by decide      -- b odd
example : ¬ (16 : ℤ) ∣ -((3 : ℤ) ^ 3 * 2 ^ 3) := by decide     -- p = 3 < 4
example : ¬ (4 : ℤ) ∣ (2 : ℤ) ^ 5 - 1 - 1 ^ 5 := by decide      -- a ≡ 1 (mod 4)
/-- Inexact integer division does not cast: 1 / 4 = 0 in ℤ. -/
example : (((1 : ℤ) / 4 : ℤ) : ℚ) ≠ ((1 : ℤ) : ℚ) / 4 := by norm_num

#print axioms four_dvd_a2
#print axioms sixteen_dvd_a4
#print axioms cast_a2
#print axioms cast_a4
end FreyExact
