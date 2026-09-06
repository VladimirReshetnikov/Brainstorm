/-
BASALT: illustrative conservative core.
STATUS: not compiled in the preparation environment.
No claim of kernel acceptance accompanies this file.
No Mathlib dependency is intended. Requires Lean 4.
-/
set_option autoImplicit false
universe u v w
namespace Basalt

variable {A : Type u} {B : Type v} {C : Type w}

def weaken {P Q : A -> Prop} (h : forall x, P x -> Q x)
    (z : Subtype P) : Subtype Q :=
  ⟨z.val, h z.val z.property⟩

def meet {P Q : A -> Prop} (x : A) (hp : P x) (hq : Q x) :
    {a : A // P a ∧ Q a} :=
  ⟨x, ⟨hp, hq⟩⟩

theorem weaken_value {P Q : A -> Prop}
    (h : forall x, P x -> Q x) (z : Subtype P) :
    (weaken h z).val = z.val := rfl

structure LawfulFn (A : Type u) (B : Type v)
    (pre : A -> Prop) (post : A -> B -> Prop) where
  run : A -> B
  law : forall x, pre x -> post x (run x)

def composeLaw
    (f : A -> B) (g : B -> C)
    (P : A -> Prop) (Q : A -> B -> Prop)
    (R : A -> B -> C -> Prop)
    (hf : forall x, P x -> Q x (f x))
    (hg : forall x y, Q x y -> R x y (g y)) :
    forall x, P x -> R x (f x) (g (f x)) :=
  fun x hx => hg x (f x) (hf x hx)

def consequence
    (f : A -> B) (P P' : A -> Prop) (Q Q' : A -> B -> Prop)
    (hf : forall x, P x -> Q x (f x))
    (hp : forall x, P' x -> P x)
    (hq : forall x y, P' x -> Q x y -> Q' x y) :
    forall x, P' x -> Q' x (f x) :=
  fun x hx => hq x (f x) hx (hf x (hp x hx))

def composeInvariant
    (P : A -> Prop) (Q : B -> Prop) (R : C -> Prop)
    (f : LawfulFn A B P (fun _ y => Q y))
    (g : LawfulFn B C Q (fun _ z => R z)) :
    LawfulFn A C P (fun _ z => R z) where
  run := fun x => g.run (f.run x)
  law := fun x hx => g.law (f.run x) (f.law x hx)

theorem observationCongruence
    (obs : A -> B) (f : A -> C) (abstractFn : B -> C)
    (adequate : forall x, f x = abstractFn (obs x))
    (x y : A) (same : obs x = obs y) : f x = f y :=
  Eq.trans (adequate x)
    (Eq.trans (congrArg abstractFn same) (Eq.symm (adequate y)))

def precisionCompose
    (EA : Nat -> A -> A -> Prop)
    (EB : Nat -> B -> B -> Prop)
    (EC : Nat -> C -> C -> Prop)
    (f : A -> B) (g : B -> C) (df dg : Nat -> Nat)
    (hf : forall n x y, EA (df n) x y -> EB n (f x) (f y))
    (hg : forall n x y, EB (dg n) x y -> EC n (g x) (g y)) :
    forall n x y, EA (df (dg n)) x y -> EC n (g (f x)) (g (f y)) :=
  fun n x y h => hg n (f x) (f y) (hf (dg n) x y h)

#print axioms Basalt.weaken_value
#print axioms Basalt.observationCongruence
end Basalt
