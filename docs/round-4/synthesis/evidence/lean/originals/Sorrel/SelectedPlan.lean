-- Generated finite-model implication; NOT compiled in this study.
-- Atom meanings and rule truth remain theorem parameters.
import Init
set_option autoImplicit false
theorem selectedPlan
    (A0 A1 A2 A3 A4 A5 A6 A7 : Prop)
    (r0 : A4 -> A5 -> A2)
    (r2 : A1 -> A3)
    (r3 : A3 -> A2 -> A0)
    (hA1 : A1)
    (hA4 : A4)
    (hA5 : A5)
    : A0 := (r3 (r2 hA1) (r0 hA4 hA5))

-- Atom key (lexical names, not Lean expressions):
-- A0 = ExactQuotient.Both
-- A1 = ExactQuotient.Direct4
-- A2 = ExactQuotient.Dvd16
-- A3 = ExactQuotient.Dvd4
-- A4 = ExactQuotient.EvenB
-- A5 = ExactQuotient.LargeP
-- A6 = ExactQuotient.OddP
-- A7 = ExactQuotient.ResidueA
