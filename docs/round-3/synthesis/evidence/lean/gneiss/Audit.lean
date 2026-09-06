/-
GNEISS: a small ordinary-Lean encoding of the proposed contracts.
This file is a design specimen. It was NOT compiled in the preparation
session: no Lean executable was available. It uses no `sorry` or new axioms,
but that fact is not a substitute for compilation and an axiom audit.
Suggested validation: lean GneissCore.lean (with a recorded toolchain).
-/
import Init

namespace Gneiss
universe u v w

variable {A : Type u} {B : Type v} {C : Type w}

/-- Evidence about the same value, rather than a replacement value. -/
structure Has (a : A) (P : A → Prop) : Prop where
  proof : P a

def Has.weaken {a : A} {P Q : A → Prop}
    (h : Has a P) (bridge : ∀ x, P x → Q x) : Has a Q :=
  ⟨bridge a h.proof⟩

def Has.inter {a : A} {P Q : A → Prop}
    (hp : Has a P) (hq : Has a Q) : Has a (fun x => P x ∧ Q x) :=
  ⟨⟨hp.proof, hq.proof⟩⟩

/-- A specification of an already selected total function. -/
structure Contract (f : A → B) (P : A → Prop)
    (Q : A → B → Prop) : Prop where
  holds : ∀ x, P x → Q x (f x)

/-- The intermediate value is bound before its next precondition. -/
def Contract.comp {f : A → B} {g : B → C}
    {P : A → Prop} {Q : A → B → Prop}
    {P' : B → Prop} {Q' : B → C → Prop}
    (hf : Contract f P Q) (hg : Contract g P' Q')
    (next : ∀ x, P x → Q x (f x) → P' (f x)) :
    Contract (fun x => g (f x)) P
      (fun x z => ∃ y, Q x y ∧ Q' y z) :=
  ⟨fun x hx =>
    ⟨f x, hf.holds x hx, hg.holds (f x) (next x hx (hf.holds x hx))⟩⟩

/-- Strengthening the precondition and weakening the postcondition. -/
def Contract.consequence {f : A → B}
    {P P' : A → Prop} {Q Q' : A → B → Prop}
    (h : Contract f P Q)
    (pre : ∀ x, P' x → P x)
    (post : ∀ x y, P' x → Q x y → Q' x y) : Contract f P' Q' :=
  ⟨fun x hx => post x (f x) hx (h.holds x (pre x hx))⟩

/-- A checked result can still have an undischarged guard. -/
structure Conditional (G : Prop) (Q : B → Prop) where
  value : B
  correct : G → Q value

def Conditional.discharge {G : Prop} {Q : B → Prop}
    (r : Conditional G Q) (h : G) : {y : B // Q y} :=
  ⟨r.value, r.correct h⟩

/-- Preserving an observation is an explicit theorem about an operation. -/
def Respects (R : A → A → Prop) (S : B → B → Prop) (f : A → B) : Prop :=
  ∀ x y, R x y → S (f x) (f y)

theorem respects_comp {R : A → A → Prop} {S : B → B → Prop}
    {T : C → C → Prop} {f : A → B} {g : B → C}
    (hf : Respects R S f) (hg : Respects S T g) :
    Respects R T (fun x => g (f x)) :=
  fun x y h => hg (f x) (f y) (hf x y h)

/-- A solution predicate requires both directions. -/
structure Complete (P S : A → Prop) : Prop where
  sound : ∀ x, S x → P x
  covers : ∀ x, P x → S x

theorem complete_iff {P S : A → Prop} (h : Complete P S) :
    ∀ x, P x ↔ S x :=
  fun x => ⟨h.covers x, h.sound x⟩

#print axioms respects_comp
#print axioms complete_iff
end Gneiss


-- Review-only axiom queries.
#print axioms Gneiss.respects_comp
#print axioms Gneiss.complete_iff
