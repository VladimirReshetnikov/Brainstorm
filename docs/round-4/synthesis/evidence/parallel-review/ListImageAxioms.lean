/-! Realizable observation frames for list lengths, kernel-checked with core Lean only
(no Mathlib).  The four domain instances are the ones six round-4 reports prove on paper:
independent lists over an inhabited type, lists over an empty type, a list observed
together with its reverse (the diagonal), and the image characterisation of `length`. -/
set_option autoImplicit false
namespace ListImage

/-- The image of `List.length` on `List α` is `{0} ∪ ℕ` according to whether `α` is inhabited
(Juniper, Proposition "image of list length"; Rowan, equation (list-image); Bryony §11.4). -/
theorem length_image (α : Type) (n : Nat) :
    (∃ xs : List α, xs.length = n) ↔ n = 0 ∨ Nonempty α := by
  constructor
  · rintro ⟨xs, rfl⟩
    cases xs with
    | nil => exact Or.inl rfl
    | cons a _ => exact Or.inr ⟨a⟩
  · rintro (rfl | h)
    · exact ⟨[], rfl⟩
    · exact h.elim fun a => ⟨List.replicate n a, List.length_replicate⟩

/-- Over an empty element type the one-point frame decides every affine length law:
constant-empty output and the identity have models 0 and n, yet agree on every input. -/
theorem empty_one_point_frame (a b c d : Int) (h0 : b = d) :
    ∀ xs : List Empty, a * xs.length + b = c * xs.length + d := by
  intro xs
  cases xs with
  | nil => simp [h0]
  | cons x _ => exact nomatch x

/-- Over an inhabited type two realized points (the empty list and a singleton) decide
equality of two affine length laws; the frame points are actual lists. -/
theorem inhabited_two_point_frame (a b c d : Int) (h0 : b = d) (h1 : a + b = c + d) :
    ∀ n : Nat, a * n + b = c * n + d := by
  have hac : a = c := by omega
  subst hac; subst h0; intro n; rfl

/-- A list and its reverse are observed on the diagonal; the affine difference
`c + a n₁ + b n₂` vanishes there exactly when `c = 0` and `a + b = 0`, not when `a = b = 0`
(Alder §10.6, Clover §12.4, Heather §8.4, Laurel §9.4, Rowan §11.5). -/
theorem diagonal_frame (a b c : Int) :
    (∀ xs : List Nat, c + a * xs.length + b * xs.reverse.length = 0) ↔ c = 0 ∧ a + b = 0 := by
  constructor
  · intro h
    have h0 := h []
    have h1 := h [0]
    simp at h0 h1
    omega
  · rintro ⟨rfl, hab⟩ xs
    rw [List.length_reverse]
    have : a * (xs.length : Int) + b * xs.length = (a + b) * xs.length := (Int.add_mul a b _).symm
    rw [Int.zero_add, this, hab, Int.zero_mul]

/-- The ambient witness (1, 0) is not realizable on the diagonal, but on two independent
inputs it is: `([0], [])` separates `n₁` from `n₂`. -/
example : ∃ xs ys : List Nat, xs.length ≠ ys.length := ⟨[0], [], by decide⟩
/-- The same two forms `n₁ + n₂` and `2 n₂` (Heather's example) agree on the diagonal ... -/
example : ∀ xs : List Nat, (xs ++ xs).length = (xs ++ xs).length := fun _ => rfl
/-- ... but not on independent inputs. -/
example : ¬ ∀ xs ys : List Nat, (xs ++ ys).length = (ys ++ ys).length := by
  intro h; have := h [0] []; simp at this

end ListImage

-- Review-only appended axiom queries; original source above is unchanged.
#print axioms ListImage.length_image
#print axioms ListImage.empty_one_point_frame
#print axioms ListImage.inhabited_two_point_frame
#print axioms ListImage.diagonal_frame
