/-
Clover's ordinary-Lean semantic reference for the executable Python slice.
Written and manually reviewed, but NOT compiled in the preparation environment.
No Mathlib import, no added axioms, no sorry, and no native evaluation are used
in this source. These are source observations, not a kernel-acceptance claim.
-/
set_option autoImplicit false
universe u
namespace CloverCore

def compose {A : Type u} (g f : A -> A) : A -> A := fun x => g (f x)
def Injective {A : Type u} (f : A -> A) : Prop :=
  ∀ x y, f x = f y -> x = y
def LeftInverse {A : Type u} (g f : A -> A) : Prop := ∀ x, g (f x) = x
def Involutive {A : Type u} (f : A -> A) : Prop := ∀ x, f (f x) = x
def Same {A : Type u} (f g : A -> A) : Prop := ∀ x, f x = g x

theorem inv_from_involution {A : Type u} (f : A -> A)
    (h : Involutive f) : LeftInverse f f := h

theorem inj_from_left_inverse {A : Type u} (f g : A -> A)
    (h : LeftInverse g f) : Injective f := by
  intro x y hxy
  exact (h x).symm.trans ((congrArg g hxy).trans (h y))

theorem inj_comp {A : Type u} (f g : A -> A)
    (hf : Injective f) (hg : Injective g) : Injective (compose g f) := by
  intro x y hxy
  exact hf x y (hg (f x) (f y) hxy)

theorem same_symm {A : Type u} (f g : A -> A)
    (h : Same f g) : Same g f := fun x => (h x).symm

theorem same_trans {A : Type u} (f g k : A -> A)
    (hfg : Same f g) (hgk : Same g k) : Same f k :=
  fun x => (hfg x).trans (hgk x)

theorem inj_transport {A : Type u} (f g : A -> A)
    (hfg : Same f g) (hf : Injective f) : Injective g := by
  intro x y hxy
  exact hf x y ((hfg x).trans (hxy.trans (hfg y).symm))

theorem same_refl {A : Type u} (f : A -> A) : Same f f := fun _ => rfl

#print axioms inv_from_involution
#print axioms inj_from_left_inverse
#print axioms inj_comp
#print axioms same_symm
#print axioms same_trans
#print axioms inj_transport
#print axioms same_refl
end CloverCore
