import Mathlib

/- Round-four synthesis follow-up: Juniper's sharper p >= 2 a2 interface.
The modular-power proof and transport pattern adapt the prior FreyExact
specimen at Brainstorm 58ced1c, docs/round-3/synthesis/evidence/parallel-review.
These are coefficient helper facts, with no Fermat equation or curve claim. -/
namespace FreySharper

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

theorem four_dvd_a2_sharper (a b : ℤ) (p : ℕ) (hp : Odd p) (hp2 : 2 ≤ p)
    (ha : a ≡ 3 [ZMOD 4]) (hb : 2 ∣ b) : 4 ∣ b ^ p - 1 - a ^ p := by
  have hb0 : b ^ p ≡ 0 [ZMOD 4] := Int.modEq_zero_iff_dvd.mpr (four_dvd_pow b p hb hp2)
  have h : b ^ p - 1 - a ^ p ≡ 0 - 1 - 3 [ZMOD 4] :=
    (hb0.sub_right 1).sub (odd_pow_mod_four a p hp ha)
  exact Int.modEq_zero_iff_dvd.mp (h.trans (by decide))

theorem cast_a2_sharper (a b : ℤ) (p : ℕ) (hp : Odd p) (hp2 : 2 ≤ p)
    (ha : a ≡ 3 [ZMOD 4]) (hb : 2 ∣ b) :
    (((b ^ p - 1 - a ^ p) / 4 : ℤ) : ℚ) = ((b ^ p - 1 - a ^ p : ℤ) : ℚ) / 4 :=
  Int.cast_div (four_dvd_a2_sharper a b p hp hp2 ha hb) (by norm_num)

example : (4 : ℤ) ∣ 2 ^ 3 - 1 - 3 ^ 3 := by decide
example : ¬ (16 : ℤ) ∣ -((3 : ℤ) ^ 3 * 2 ^ 3) := by decide

#print axioms four_dvd_pow
#print axioms odd_pow_mod_four
#print axioms four_dvd_a2_sharper
#print axioms cast_a2_sharper
end FreySharper
