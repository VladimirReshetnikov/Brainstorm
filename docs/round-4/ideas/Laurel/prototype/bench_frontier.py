#!/usr/bin/env python3
"""Illustrate exponential frontier width; not a Lean performance benchmark."""
import json
from pathlib import Path
import time
from laurel_core import Profile, Rule, infer

rows = []
for k in (2, 4, 6, 8, 10):
    left = tuple(f'a{i}' for i in range(k))
    right = tuple(f'b{i}' for i in range(k))
    middle = tuple(f'p{i}' for i in range(k))
    rules = tuple(Rule(f'ra{i}', (left[i],), middle[i]) for i in range(k))
    rules += tuple(Rule(f'rb{i}', (right[i],), middle[i]) for i in range(k))
    rules += (Rule('finish', middle, 'goal'),)
    p = Profile('wide', left + right + middle + ('goal',), frozenset(),
                frozenset(left + right), rules)
    start = time.perf_counter()
    r = infer(p)
    elapsed = time.perf_counter() - start
    width = len(r.frontiers['goal'])
    assert width == 2 ** k and r.complete
    rows.append({'k': k, 'offers': 2*k, 'frontier_width': width,
                 'seconds_one_run': round(elapsed, 6),
                 'premise_combinations': r.combinations})
obj = {'scope': 'Python symbolic implementation; one run per case; no kernel timing',
       'family': 'one of ai or bi required for each i', 'rows': rows}
out = Path(__file__).resolve().parents[1] / 'evidence' / 'width_experiment.json'
out.write_text(json.dumps(obj, indent=2) + '\n')
print(json.dumps(obj, indent=2))
