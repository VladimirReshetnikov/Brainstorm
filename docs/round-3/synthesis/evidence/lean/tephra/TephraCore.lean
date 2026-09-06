/-
Tephra: a small reference encoding of the proposed semantic interfaces.

Status: supplied as Lean 4 source, NOT compiled in the preparation environment.
This file is not the Tephra elaborator, a polynomial checker, or a formalization
of the article's prefix-local inverse theorem. It uses no sorry or added axiom.
-/
import Init

set_option autoImplicit false

namespace Tephra

universe u v w z r s

/-- A first-class value with an ordinary proposition-valued refinement. -/
structure Refined (A : Type u) (P : A → Prop) where
  value : A
  evidence : P value

def Refined.weaken {A : Type u} {P Q : A → Prop}
    (r : Refined A P) (h : ∀ x, P x → Q x) : Refined A Q :=
  ⟨r.value, h r.value r.evidence⟩

/-- A contract about an already fixed total function. -/
def Contract {A : Type u} {B : Type v}
    (pre : A → Prop) (post : A → B → Prop) (f : A → B) : Prop :=
  ∀ x, pre x → post x (f x)

theorem Contract.weaken {A : Type u} {B : Type v}
    {P P' : A → Prop} {Q Q' : A → B → Prop} {f : A → B}
    (hf : Contract P Q f)
    (hpre : ∀ x, P' x → P x)
    (hpost : ∀ x y, P' x → Q x y → Q' x y) : Contract P' Q' f :=
  fun x hx => hpost x (f x) hx (hf x (hpre x hx))

theorem Contract.comp {A : Type u} {B : Type v} {C : Type w}
    {P : A → Prop} {Q : A → B → Prop}
    {U : B → Prop} {V : B → C → Prop} {W : A → C → Prop}
    {f : A → B} {g : B → C}
    (hf : Contract P Q f) (hg : Contract U V g)
    (bridge : ∀ x y, P x → Q x y → U y)
    (finish : ∀ x y c, P x → Q x y → V y c → W x c) :
    Contract P W (fun x => g (f x)) := by
  intro x hx
  have hq : Q x (f x) := hf x hx
  have hv : V (f x) (g (f x)) := hg (f x) (bridge x (f x) hx hq)
  exact finish x (f x) (g (f x)) hx hq hv

/-- The semantic object is an index, not an unvalidated string field. -/
structure Result {A : Type u} {B : Type v} (R : A → B → Prop) (x : A) where
  value : B
  sound : R x value

def Result.adapt {A : Type u} {B : Type v} {R S : A → B → Prop} {x : A}
    (r : Result R x) (h : ∀ y, R x y → S x y) : Result S x :=
  ⟨r.value, h r.value r.sound⟩

def Result.discharge {A : Type u} {B : Type v}
    {R : A → B → Prop} {x : A} {G : Prop}
    (r : Result (fun a b => G → R a b) x) (hg : G) : Result R x :=
  ⟨r.value, r.sound hg⟩

/-- A dependent output may be chosen only in the scope of its guard proof. -/
structure Guarded {A : Type u} (G : A → Prop)
    (B : (a : A) → G a → Type v)
    (Q : (a : A) → (h : G a) → B a h → Prop) (a : A) where
  produce : (h : G a) → {b : B a h // Q a h b}

/-- A complete solution predicate stores both directions. -/
structure CompleteSolutions {A : Type u} (P : A → Prop) where
  member : A → Prop
  sound : ∀ x, member x → P x
  complete : ∀ x, P x → member x

/-- A map on observations with a proved commuting square. -/
structure ObsMap {A : Type u} {B : Type v} {U : Type w} {V : Type z}
    (observeA : A → U) (observeB : B → V) (f : A → B) where
  map : U → V
  commutes : ∀ x, observeB (f x) = map (observeA x)

def ObsMap.comp {A : Type u} {B : Type v} {C : Type w}
    {U : Type z} {V : Type r} {W : Type s}
    {oa : A → U} {ob : B → V} {oc : C → W}
    {f : A → B} {g : B → C}
    (mf : ObsMap oa ob f) (mg : ObsMap ob oc g) :
    ObsMap oa oc (fun x => g (f x)) where
  map := fun a => mg.map (mf.map a)
  commutes := by
    intro x
    calc
      oc (g (f x)) = mg.map (ob (f x)) := mg.commutes (f x)
      _ = mg.map (mf.map (oa x)) := congrArg mg.map (mf.commutes x)

/-- Preserving a predicate permits restriction; the ambient map stays fixed. -/
def restrict {A : Type u} (P : A → Prop) (f : A → A)
    (hf : ∀ x, P x → P (f x)) : {x : A // P x} → {x : A // P x} :=
  fun x => ⟨f x.val, hf x.val x.property⟩

theorem restrict_value {A : Type u} (P : A → Prop) (f : A → A)
    (hf : ∀ x, P x → P (f x)) (x : {x : A // P x}) :
    (restrict P f hf x).val = f x.val := rfl

theorem restrict_comp {A : Type u} (P : A → Prop) (f g : A → A)
    (hf : ∀ x, P x → P (f x)) (hg : ∀ x, P x → P (g x))
    (x : {x : A // P x}) :
    restrict P (fun a => f (g a)) (fun a ha => hf (g a) (hg a ha)) x =
      restrict P f hf (restrict P g hg x) := rfl

/-- Refinement entailment is witnessed; it is not a new conversion rule. -/
theorem refinement_intersection {A : Type u} {P Q : A → Prop}
    (x : A) (hp : P x) (hq : Q x) : P x ∧ Q x := ⟨hp, hq⟩

/-- One realized counterexample refutes a universal specification. -/
theorem refute_universal {A : Type u} {P : A → Prop}
    (x : A) (bad : ¬ P x) : ¬ (∀ y, P y) :=
  fun all => bad (all x)

end Tephra
