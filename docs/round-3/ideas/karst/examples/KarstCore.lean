/-
Karst: ordinary-Lean semantic model of selected proposed rules.

STATUS: Written for this article, but NOT COMPILED in this session.
No proposed Karst syntax is used here. This file is not a frontend or a
verified polynomial checker. Run `lean KarstCore.lean` with a pinned Lean 4
installation and retain the actual output before making verification claims.
-/
import Init

namespace KarstCore
universe u v w

-- A local view is just a proposition about the original value.
def View {A : Type u} (x : A) (P : A → Prop) : Prop := P x

theorem viewIntro {A : Type u} (x : A) {P : A → Prop}
    (h : P x) : View x P := h

theorem viewConsequence {A : Type u} (x : A) {P Q : A → Prop}
    (h : View x P) (step : P x → Q x) : View x Q := step h

theorem viewIntersection {A : Type u} (x : A) {P Q : A → Prop}
    (hp : View x P) (hq : View x Q) : View x (fun a => P a ∧ Q a) :=
  And.intro hp hq

def packView {A : Type u} (x : A) {P : A → Prop}
    (h : View x P) : {a : A // P a} := ⟨x, h⟩

theorem packView_val {A : Type u} (x : A) {P : A → Prop}
    (h : View x P) : (packView x h).val = x := rfl

theorem transportView {A : Type u} {x y : A} {P : A → Prop}
    (same : x = y) (h : View x P) : View y P := same ▸ h

-- Refinement of behavior, not just inhabitance of the arrow type.
def Beh {A : Type u} {B : Type v}
    (pre : A → Prop) (post : A → B → Prop) (f : A → B) : Prop :=
  ∀ x, pre x → post x (f x)

theorem behConsequence {A : Type u} {B : Type v}
    {pre pre' : A → Prop} {post post' : A → B → Prop}
    {f : A → B} (h : Beh pre post f)
    (weakenPre : ∀ x, pre' x → pre x)
    (weakenPost : ∀ x y, pre' x → post x y → post' x y) :
    Beh pre' post' f :=
  fun x hx => weakenPost x (f x) hx (h x (weakenPre x hx))

theorem behCompose {A : Type u} {B : Type v} {C : Type w}
    {pre : A → Prop} {post : A → B → Prop}
    {nextPre : B → Prop} {nextPost : B → C → Prop}
    {f : A → B} {g : B → C}
    (hf : Beh pre post f) (hg : Beh nextPre nextPost g)
    (bridge : ∀ x y, pre x → post x y → nextPre y) :
    Beh pre (fun x z => ∃ y, post x y ∧ nextPost y z)
      (fun x => g (f x)) := by
  intro x hx
  have hy : post x (f x) := hf x hx
  have hp : nextPre (f x) := bridge x (f x) hx hy
  exact ⟨f x, hy, hg (f x) hp⟩

-- Separate local predicates avoid any dependency on a property-instance API.
def Inj {A : Type u} {B : Type v} (f : A → B) : Prop :=
  ∀ x y, f x = f y → x = y

def Surj {A : Type u} {B : Type v} (f : A → B) : Prop :=
  ∀ y, ∃ x, f x = y

theorem injCompose {A : Type u} {B : Type v} {C : Type w}
    {f : A → B} {g : B → C} (hf : Inj f) (hg : Inj g) :
    Inj (fun x => g (f x)) :=
  fun x y h => hf x y (hg (f x) (f y) h)

theorem involutionInj {A : Type u} (f : A → A)
    (hff : ∀ x, f (f x) = x) : Inj f := by
  intro x y h
  calc
    x = f (f x) := (hff x).symm
    _ = f (f y) := congrArg f h
    _ = y := hff y

theorem fixesPointPreservesComplement {A : Type u}
    {f : A → A} (hf : Inj f) (z : A) (hz : f z = z) :
    ∀ x, x ≠ z → f x ≠ z := by
  intro x hx hfx
  exact hx (hf x z (hfx.trans hz.symm))

theorem surjectiveCannotOmit {A : Type u} {f : A → A}
    (hf : Surj f) (z : A) (omits : ∀ x, f x ≠ z) : False := by
  obtain ⟨x, hx⟩ := hf z
  exact omits x hx

-- An abstract length counterexample need not correspond to a typed input.
def dropAll {A : Type u} : List A → List A := fun _ => []

theorem dropAllLengthOnEmpty (xs : List Empty) :
    (dropAll xs).length = xs.length := by
  cases xs with
  | nil => rfl
  | cons impossible rest => exact Empty.elim impossible

-- These commands are a requested audit, not an audit already performed.
#print axioms viewConsequence
#print axioms viewIntersection
#print axioms packView_val
#print axioms transportView
#print axioms behConsequence
#print axioms behCompose
#print axioms injCompose
#print axioms involutionInj
#print axioms fixesPointPreservesComplement
#print axioms surjectiveCannotOmit
#print axioms dropAllLengthOnEmpty
end KarstCore
