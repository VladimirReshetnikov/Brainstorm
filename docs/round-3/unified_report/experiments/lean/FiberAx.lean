/-
FIBER reference encoding in ordinary Lean 4.

This file was NOT compiler-checked in the authoring environment. It gives
small explicit encodings, not a FIBER compiler or a polynomial checker.
No sorry, axiom declaration, or native-evaluation proof is used.
-/

universe u v w
namespace Fiber

abbrev Refined (A : Type u) (P : A → Prop) : Type u :=
  { x : A // P x }

def introduce {A : Type u} {P : A → Prop}
    (x : A) (h : P x) : Refined A P := ⟨x, h⟩

def weaken {A : Type u} {P Q : A → Prop}
    (h : ∀ x, P x → Q x) (x : Refined A P) : Refined A Q :=
  ⟨x.val, h x.val x.property⟩

theorem weaken_preserves_value {A : Type u} {P Q : A → Prop}
    (h : ∀ x, P x → Q x) (x : Refined A P) :
    (weaken h x).val = x.val := rfl

def conjoin {A : Type u} {P Q : A → Prop}
    (x : A) (hp : P x) (hq : Q x) :
    Refined A (fun y => P y ∧ Q y) :=
  ⟨x, ⟨hp, hq⟩⟩

def Behavior {A : Type u} {B : Type v}
    (f : A → B) (P : A → Prop) (Q : A → B → Prop) : Prop :=
  ∀ x, P x → Q x (f x)

theorem compose_behavior {A : Type u} {B : Type v} {C : Type w}
    (f : A → B) (g : B → C)
    (P : A → Prop) (Q : A → B → Prop)
    (H : B → C → Prop) (S : A → C → Prop)
    (hf : Behavior f P Q)
    (hg : ∀ x y, P x → Q x y → H y (g y))
    (hs : ∀ x y z, P x → Q x y → H y z → S x z) :
    Behavior (fun x => g (f x)) P S :=
  fun x hx => hs x (f x) (g (f x)) hx (hf x hx)
    (hg x (f x) hx (hf x hx))

structure Observation {A : Type u} {B : Type v}
    (anchor : A) (relation : A → B → Prop) where
  value : B
  evidence : relation anchor value

def weaken_observation {A : Type u} {B : Type v} {a : A}
    {R S : A → B → Prop}
    (h : ∀ b, R a b → S a b) (o : Observation a R) :
    Observation a S :=
  ⟨o.value, h o.value o.evidence⟩

-- This composition theorem ASSUMES the real checker soundness theorem.
-- It is not a proof of polynomial-checker soundness or of native execution.
theorem certificate_bridge {A : Type u} {B : Type v} {C : Type w}
    (input : A) (output : B) (certificate : C)
    (check : A → B → C → Bool) (spec : A → B → Prop)
    (sound : ∀ i o c, check i o c = true → spec i o)
    (execution : check input output certificate = true) :
    spec input output :=
  sound input output certificate execution

end Fiber
#print axioms Fiber.weaken_preserves_value
#print axioms Fiber.compose_behavior
#print axioms Fiber.certificate_bridge
