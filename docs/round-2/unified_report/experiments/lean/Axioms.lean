-- Probe: which axioms does native_decide introduce on the toolchain ProveIt pins?
theorem byDecide : (2 ^ 20) % 7 = 4 := by decide
theorem byNative : (2 ^ 20) % 7 = 4 := by native_decide
#print axioms byDecide
#print axioms byNative
