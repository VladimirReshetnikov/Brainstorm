#!/usr/bin/env python3
"""Resolve two operation requirements and export their ordinary-Lean proof candidate."""
import json
from dataclasses import asdict
from pathlib import Path
from heather import Context, Fact

c = Context('use-site-snapshot-1', ('n','d'))
c.assume('hdpos',Fact('positive',('d',)))
c.assume('hdiv',Fact('divides',('d','n')))
nonzero, divisible = c.exact_quotient_requirements('n','d')
assert nonzero is not None and divisible is not None
assert c.check(nonzero) and c.check(divisible)
out = Path('generated'); out.mkdir(exist_ok=True)
(out/'use_site.json').write_text(json.dumps({
    'status':'requirements_resolved_in_reference_model',
    'consumer':'exact_quotient(n,d)', 'rule_firings':c.firings,
    'evidence':[asdict(e) for e in c.evidence],
    'limitations':['No quotient value is constructed here.',
                   'No Lean compiler was run.',
                   'This is not an integration with Leant.']},indent=2)+'\n')
(out/'UseSite.lean').write_text(
    '-- GENERATED PROOF CANDIDATE; NOT COMPILED IN THIS DELIVERY.\n'
    '-- This proves readiness premises, not an exact-division implementation.\n'
    'import Mathlib\nset_option autoImplicit false\n\n'
    'theorem quotient_requirements (n d : Nat)\n'
    '    (hdpos : 0 < d) (hdiv : d ∣ n) : d ≠ 0 ∧ d ∣ n := by\n'
    f'  exact ⟨{nonzero.lean}, {divisible.lean}⟩\n')
print('Two requirements resolved; one implication rule fired; Lean export uncompiled.')
