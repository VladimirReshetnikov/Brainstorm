# Opaque proposition skeleton, NOT an arithmetic formalization.
module QuotientRequirements
atom EvenB LargeP OddP ResidueA Div16 Div4 Nonzero4 Cast4
atom PrecomputedCast Unrelated

given even : EvenB
given large : LargeP
given denom : Nonzero4
ask odd : OddP
ask residue : ResidueA
ask cached : PrecomputedCast

rule pow16 : EvenB & LargeP -> Div16
rule congr4 : EvenB & LargeP & OddP & ResidueA -> Div4
rule cast : Div4 & Nonzero4 -> Cast4
rule reuse : PrecomputedCast -> Cast4

show fourth_coefficient : Div16
show second_coefficient : Cast4
show arithmetic_route : Cast4 using only pow16 congr4 cast
show unrelated_target : Unrelated
