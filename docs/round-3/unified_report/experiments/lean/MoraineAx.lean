/-
Moraine: ordinary-Lean reference semantics.

STATUS: Written as a reference encoding; NOT compiler-tested in the environment
used to produce the article. No `sorry`, `admit`, or new axiom declarations occur.
This is not a Moraine parser, elaborator, or completed reflective checker.

The last section covers only the denotational/structural half of the length
checker. Affine coefficient normalization and its correctness must still be
ported and proved before any Python result can become a Lean proof.

Suggested validation: `lean Contracts.lean` in a pinned Lean installation.
-/
import Std

namespace MoraineReference

universe u v w

structure Certified (A : Type u) (P : A → Prop) where
  value : A
  property : P value

def Refines {A : Type u} (P Q : A → Prop) : Prop :=
  ∀ x, P x → Q x

namespace Certified

variable {A : Type u} {P Q : A → Prop}

def weaken (h : Refines P Q) (x : Certified A P) : Certified A Q :=
  ⟨x.value, h x.value x.property⟩

theorem weaken_preserves_value (h : Refines P Q) (x : Certified A P) :
    (weaken h x).value = x.value := rfl

def strengthen (x : Certified A P) (h : Q x.value) :
    Certified A (fun a => P a ∧ Q a) :=
  ⟨x.value, ⟨x.property, h⟩⟩

theorem strengthen_preserves_value (x : Certified A P) (h : Q x.value) :
    (strengthen x h).value = x.value := rfl

end Certified

theorem refinement_refl {A : Type u} (P : A → Prop) : Refines P P :=
  fun _ h => h

theorem refinement_trans {A : Type u} {P Q R : A → Prop}
    (hPQ : Refines P Q) (hQR : Refines Q R) : Refines P R :=
  fun x h => hQR x (hPQ x h)

theorem evidence_transport {A : Type u} {a b : A} {P : A → Prop}
    (h : a = b) (p : P a) : P b := h ▸ p

/-- A row may be stored as individual proofs, without nesting carrier wrappers. -/
def RowHolds {A : Type u} {I : Type v} (row : I → A → Prop) (a : A) : Prop :=
  ∀ i, row i a

theorem row_project {A : Type u} {I : Type v} {row : I → A → Prop} {a : A}
    (h : RowHolds row a) (i : I) : row i a := h i

/-- A specification of an existing total function, not a restricted-domain type. -/
def MapSpec {A : Type u} {B : Type v}
    (P : A → Prop) (Q : A → B → Prop) (f : A → B) : Prop :=
  ∀ x, P x → Q x (f x)

theorem mapSpec_apply {A : Type u} {B : Type v}
    {P : A → Prop} {Q : A → B → Prop} {f : A → B}
    (h : MapSpec P Q f) (x : A) (hx : P x) : Q x (f x) := h x hx

theorem mapSpec_weaken {A : Type u} {B : Type v}
    {P₁ P₂ : A → Prop} {Q₁ Q₂ : A → B → Prop} {f : A → B}
    (h : MapSpec P₁ Q₁ f)
    (pre : ∀ x, P₂ x → P₁ x)
    (post : ∀ x y, P₂ x → Q₁ x y → Q₂ x y) : MapSpec P₂ Q₂ f :=
  fun x hx => post x (f x) hx (h x (pre x hx))

theorem mapSpec_compose {A : Type u} {B : Type v} {C : Type w}
    {P : A → Prop} {Q : A → B → Prop}
    {R : B → Prop} {S : B → C → Prop}
    {f : A → B} {g : B → C}
    (hf : MapSpec P Q f) (hg : MapSpec R S g)
    (bridge : ∀ x y, P x → Q x y → R y) :
    MapSpec P (fun x z => ∃ y, Q x y ∧ S y z) (fun x => g (f x)) := by
  intro x hx
  have hq : Q x (f x) := hf x hx
  exact ⟨f x, hq, hg (f x) (bridge x (f x) hx hq)⟩

/-- Two-input relational behavior. -/
def RelSpec {A : Type u} {B : Type v}
    (R : A → A → Prop) (S : B → B → Prop) (f : A → B) : Prop :=
  ∀ x y, R x y → S (f x) (f y)

theorem relSpec_compose {A : Type u} {B : Type v} {C : Type w}
    {R : A → A → Prop} {S : B → B → Prop} {T : C → C → Prop}
    {f : A → B} {g : B → C}
    (hf : RelSpec R S f) (hg : RelSpec S T g) :
    RelSpec R T (fun x => g (f x)) :=
  fun x y h => hg (f x) (f y) (hf x y h)

def InversePair {A : Type u} {B : Type v} (f : A → B) (g : B → A) : Prop :=
  (∀ x, g (f x) = x) ∧ (∀ y, f (g y) = y)

theorem inversePair_injective {A : Type u} {B : Type v}
    {f : A → B} {g : B → A} (h : InversePair f g) :
    ∀ x y, f x = f y → x = y := by
  intro x y hxy
  calc
    x = g (f x) := (h.1 x).symm
    _ = g (f y) := congrArg g hxy
    _ = y := h.1 y

theorem inversePair_surjective {A : Type u} {B : Type v}
    {f : A → B} {g : B → A} (h : InversePair f g) :
    ∀ y, ∃ x, f x = y :=
  fun y => ⟨g y, h.2 y⟩

/-- Set-wise evidence, with a set represented as a predicate. -/
def On {A : Type u} (U P : A → Prop) : Prop := ∀ x, U x → P x

/-- A neighborhood-witness presentation, not a new topology or filter theory. -/
def WitnessedLocal {A : Type u} (neighborhood : (A → Prop) → Prop)
    (P : A → Prop) : Prop :=
  ∃ U, neighborhood U ∧ On U P

theorem on_to_witnessedLocal {A : Type u}
    {neighborhood : (A → Prop) → Prop} {U P : A → Prop}
    (hU : neighborhood U) (h : On U P) : WitnessedLocal neighborhood P :=
  ⟨U, hU, h⟩

theorem join_cases {P Q R : Prop} (hCases : P ∨ Q)
    (hLeft : P → R) (hRight : Q → R) : R :=
  Or.elim hCases hLeft hRight

/-- The fixed list-expression grammar used by the Python reference checker. -/
inductive LengthExpr (k : Nat) where
  | input : Fin k → LengthExpr k
  | nil : LengthExpr k
  | cons : Nat → LengthExpr k → LengthExpr k
  | append : LengthExpr k → LengthExpr k → LengthExpr k
  | reverse : LengthExpr k → LengthExpr k
  | mapSucc : LengthExpr k → LengthExpr k

namespace LengthExpr

variable {k : Nat}

def eval : LengthExpr k → (Fin k → List Nat) → List Nat
  | .input i, env => env i
  | .nil, _ => []
  | .cons head tail, env => head :: eval tail env
  | .append left right, env => eval left env ++ eval right env
  | .reverse body, env => (eval body env).reverse
  | .mapSucc body, env => (eval body env).map Nat.succ

/-- Structural arithmetic model; not yet a normalized coefficient vector. -/
def model : LengthExpr k → (Fin k → Nat) → Nat
  | .input i, env => env i
  | .nil, _ => 0
  | .cons _ tail, env => model tail env + 1
  | .append left right, env => model left env + model right env
  | .reverse body, env => model body env
  | .mapSucc body, env => model body env

theorem model_sound (e : LengthExpr k) (env : Fin k → List Nat) :
    (eval e env).length = model e (fun i => (env i).length) := by
  induction e with
  | input i => rfl
  | nil => rfl
  | cons head tail ih => simp [eval, model, ih]
  | append left right ihLeft ihRight => simp [eval, model, ihLeft, ihRight]
  | reverse body ih => simp [eval, model, ih]
  | mapSucc body ih => simp [eval, model, ih]

/-- Promotion needs the universal model theorem, not just several test values. -/
theorem promote_model_spec (e : LengthExpr k) (required : (Fin k → Nat) → Nat)
    (h : ∀ lengths, model e lengths = required lengths) :
    ∀ env : Fin k → List Nat,
      (eval e env).length = required (fun i => (env i).length) := by
  intro env
  calc
    (eval e env).length = model e (fun i => (env i).length) := model_sound e env
    _ = required (fun i => (env i).length) := h _

example (i : Fin k) :
    MapSpec (fun _ : Fin k → List Nat => True)
      (fun (env : Fin k → List Nat) (out : List Nat) => out.length = (env i).length)
      (fun env => eval (.reverse (.input i)) env) := by
  intro env _
  simp [eval]

end LengthExpr
end MoraineReference
#print axioms MoraineReference.Certified.weaken_preserves_value
#print axioms MoraineReference.Certified.strengthen_preserves_value
#print axioms MoraineReference.refinement_refl
#print axioms MoraineReference.refinement_trans
#print axioms MoraineReference.evidence_transport
#print axioms MoraineReference.row_project
#print axioms MoraineReference.mapSpec_apply
#print axioms MoraineReference.mapSpec_weaken
#print axioms MoraineReference.mapSpec_compose
#print axioms MoraineReference.relSpec_compose
#print axioms MoraineReference.inversePair_injective
#print axioms MoraineReference.inversePair_surjective
#print axioms MoraineReference.on_to_witnessedLocal
#print axioms MoraineReference.join_cases
#print axioms MoraineReference.LengthExpr.model_sound
#print axioms MoraineReference.LengthExpr.promote_model_spec
