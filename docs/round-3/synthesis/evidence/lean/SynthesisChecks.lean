/-
Two small synthesis-level interface theorems. These do not formalize a new
frontend, a solver, or the commutative-ring matrix theorem used in the report.
-/
import Init

set_option autoImplicit false
namespace Round3Synthesis
universe u v w z

/-- Negative abstract evidence needs a realized, admissible source input.
The preservation premise says a true source specification would imply the
abstract specification; no global surjectivity of the observation is required.
-/
theorem refute_via_realization
    {A : Type u} {B : Type v} {U : Type w} {V : Type z}
    (f : A → B) (model : U → V) (observeIn : A → U) (observeOut : B → V)
    (allowed : A → Prop) (spec : A → B → Prop) (abstractSpec : U → V → Prop)
    (commutes : ∀ x, allowed x → observeOut (f x) = model (observeIn x))
    (preserves : ∀ x y, allowed x → spec x y → abstractSpec (observeIn x) (observeOut y))
    (a : U) (x : A) (hx : allowed x) (realizes : observeIn x = a)
    (bad : ¬ abstractSpec a (model a)) :
    ¬ (∀ y, allowed y → spec y (f y)) := by
  intro all
  have h := preserves x (f x) hx (all x hx)
  rw [commutes x hx, realizes] at h
  exact bad h

/-- A family of observations can transport local reversal of one-sided
inverses back to the original object. Local reversal and observation coverage
are explicit hypotheses; this is not itself a finite-matrix proof.
-/
theorem reverse_via_observations
    {A : Type u} {I : Type v} {O : I → Type w}
    (observe : (i : I) → A → O i)
    (onto : ∀ i y, ∃ x, observe i x = y)
    (separates : ∀ x y, (∀ i, observe i x = observe i y) → x = y)
    (f g : A → A) (fo go : (i : I) → O i → O i)
    (cf : ∀ i x, observe i (f x) = fo i (observe i x))
    (cg : ∀ i x, observe i (g x) = go i (observe i x))
    (localReverse : ∀ i, (∀ y, fo i (go i y) = y) → ∀ y, go i (fo i y) = y)
    (left : ∀ x, f (g x) = x) : ∀ x, g (f x) = x := by
  have hi (i : I) : ∀ y, fo i (go i y) = y := by
    intro y
    obtain ⟨x, hx⟩ := onto i y
    rw [← hx, ← cg i x, ← cf i (g x), left x]
  intro x
  apply separates
  intro i
  rw [cg i (f x), cf i x]
  exact localReverse i (hi i) (observe i x)

end Round3Synthesis

#print axioms Round3Synthesis.refute_via_realization
#print axioms Round3Synthesis.reverse_via_observations
