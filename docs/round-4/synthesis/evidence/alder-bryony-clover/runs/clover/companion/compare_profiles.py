#!/usr/bin/env python3
"""Reproduce the two rule-profile operation counts in the Clover article."""
from dataclasses import replace
import json
from pathlib import Path
from clover_slice import elaborate, solve


def main() -> None:
    root = Path(__file__).resolve().parent
    source = (root / 'demo.clover').read_text(encoding='utf-8')
    request = elaborate(source)[0].request
    narrow = replace(request, allowed=('inj_from_left_inverse', 'inj_comp'))
    report = {
        'description': 'Algorithm operation counts, not Lean timings or usability data.',
        'full_registry': solve(request).as_dict(),
        'two_rule_profile': solve(narrow).as_dict(),
    }
    text = json.dumps(report, indent=2) + '\n'
    (root / 'profile-comparison.json').write_text(text, encoding='utf-8')
    print(text, end='')


if __name__ == '__main__':
    main()
