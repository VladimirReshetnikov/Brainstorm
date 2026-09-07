-- Generated finite-model implication; NOT compiled in this study.
-- Atom meanings and rule truth remain theorem parameters.
import Init
set_option autoImplicit false
theorem selectedPlan
    (A0 A1 A2 A3 : Prop)
    (r0 : A0 -> A3)
    (hA0 : A0)
    : A3 := (r0 hA0)

-- Atom key (lexical names, not Lean expressions):
-- A0 = Selection.A
-- A1 = Selection.B
-- A2 = Selection.C
-- A3 = Selection.Goal
