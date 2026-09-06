/-
Schist logical reference core, 6 September 2026.

STATUS: This source was authored but NOT compiled in the preparation environment.
It has no authored axioms, sorry placeholders, or native_decide invocations.
No claim about successful elaboration or the transitive axiom inventory is made.
Run: lean SchistCore.lean
The #print commands at the end are intended to create an actual future receipt.

This is a library-level reference, not the proposed frontend or an implementation
of property inference, provider integration, or editor replay.
-/
import Lean

universe u v w
namespace Schist

section Refinements
variable {A : Type u} {B : Type v} {C : Type w}

/-- An explicit, proof-backed change of a refinement, retaining its value. -/
def weaken {P Q : A → Prop} (h : ∀ a, P a → Q a)
    (x : {a : A // P a}) : {a : A // Q a} :=
  ⟨x.val, h x.val x.property⟩

theorem weaken_value {P Q : A → Prop} (h : ∀ a, P a → Q a)
    (x : {a : A // P a}) : (weaken h x).val = x.val := rfl

/-- A law of a total base function. It is not a partial-function encoding. -/
def Contract (f : A → B) (pre : A → Prop) (post : A → B → Prop) : Prop :=
  ∀ a, pre a → post a (f a)

theorem contract_consequence {f : A → B} {P P' : A → Prop}
    {Q Q' : A → B → Prop} (h : Contract f P Q)
    (hin : ∀ a, P' a → P a)
    (hout : ∀ a b, P' a → Q a b → Q' a b) :
    Contract f P' Q' :=
  fun a ha => hout a (f a) ha (h a (hin a ha))

theorem contract_compose {f : A → B} {g : B → C}
    {P : A → Prop} {Q : A → B → Prop} {R : A → C → Prop}
    (hf : Contract f P Q) (hg : ∀ a b, Q a b → R a (g b)) :
    Contract (fun a => g (f a)) P R :=
  fun a ha => hg a (f a) (hf a ha)

/-- Each observation is explicitly indexed by its original anchor. -/
structure Observation (R : A → B → Prop) (anchor : A) where
  value : B
  sound : R anchor value

/-- Ordered composition retains the actual intermediate value and its proof. -/
def composeObservations (R : A → B → Prop) (S : A → B → C → Prop)
    (T : A → C → Prop)
    (first : (a : A) → Observation R a)
    (second : (a : A) → (b : B) → R a b → {c : C // S a b c})
    (bridge : ∀ a b c, R a b → S a b c → T a c)
    (a : A) : Observation T a :=
  let b := first a
  let c := second a b.value b.sound
  ⟨c.val, bridge a b.value c.val b.sound c.property⟩

/-- Sufficient, not necessarily weakest, requirement transformation. -/
def ReqSound (f : A → B) (req : (B → Prop) → A → Prop) : Prop :=
  ∀ Q a, req Q a → Q (f a)

theorem req_compose {f : A → B} {g : B → C}
    {rf : (B → Prop) → A → Prop} {rg : (C → Prop) → B → Prop}
    (hf : ReqSound f rf) (hg : ReqSound g rg) :
    ReqSound (fun a => g (f a)) (fun Q => rf (rg Q)) :=
  fun Q a h => hg Q (f a) (hf (rg Q) a h)

end Refinements

/- A deliberately small certificate example. Unlike a universal CAS, this
   language expresses only affine natural-number expressions in one variable. -/
namespace AffineCertificate

inductive Expr where
  | lit : Nat → Expr
  | var : Expr
  | add : Expr → Expr → Expr
  | scale : Nat → Expr → Expr
  deriving DecidableEq, Repr

def eval : Expr → Nat → Nat
  | .lit n, _ => n
  | .var, x => x
  | .add a b, x => eval a x + eval b x
  | .scale n a, x => n * eval a x

/-- A pair (slope, intercept), with no bounded-integer arithmetic. -/
def nf : Expr → Nat × Nat
  | .lit n => (0, n)
  | .var => (1, 0)
  | .add a b => ((nf a).1 + (nf b).1, (nf a).2 + (nf b).2)
  | .scale n a => (n * (nf a).1, n * (nf a).2)

theorem eval_nf (e : Expr) (x : Nat) :
    eval e x = (nf e).1 * x + (nf e).2 := by
  induction e with
  | lit n => simp [eval, nf]
  | var => simp [eval, nf]
  | add a b ha hb =>
      simp [eval, nf, ha, hb, Nat.add_mul,
        Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]
  | scale n a ha =>
      simp [eval, nf, ha, Nat.mul_add, Nat.mul_assoc]

def check (e f : Expr) : Bool := decide (nf e = nf f)

theorem check_sound (e f : Expr) (h : check e f = true) :
    ∀ x : Nat, eval e x = eval f x := by
  have heq : nf e = nf f := of_decide_eq_true h
  intro x
  calc
    eval e x = (nf e).1 * x + (nf e).2 := eval_nf e x
    _ = (nf f).1 * x + (nf f).2 := by rw [heq]
    _ = eval f x := (eval_nf f x).symm

def lhs : Expr := .scale 3 (.add .var (.lit 2))
def rhs : Expr := .add (.scale 3 .var) (.lit 6)
def corrupted : Expr := .add (.scale 3 .var) (.lit 7)

/-- Original-target reconstruction; source reification is definitional here. -/
theorem original_target (x : Nat) : 3 * (x + 2) = 3 * x + 6 := by
  simpa [lhs, rhs, eval] using (check_sound lhs rhs (by decide) x)

theorem corrupted_rejected : check lhs corrupted = false := by decide

end AffineCertificate
end Schist

#print axioms Schist.weaken_value
#print axioms Schist.contract_consequence
#print axioms Schist.contract_compose
#print axioms Schist.req_compose
#print axioms Schist.AffineCertificate.eval_nf
#print axioms Schist.AffineCertificate.check_sound
#print axioms Schist.AffineCertificate.original_target
#print axioms Schist.AffineCertificate.corrupted_rejected
