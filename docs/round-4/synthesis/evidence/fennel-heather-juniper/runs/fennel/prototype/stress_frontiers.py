#!/usr/bin/env python3
"""Demonstrate exponential frontier output; no Lean performance claim."""
from pathlib import Path
import json
from fennel import Program, Root, Rule, Query, plan

def family(k):
    atoms=tuple([f'P{i}' for i in range(k)]+['Goal'])
    roots=tuple(Root(f'{c}{i}',f'P{i}',True) for i in range(k) for c in 'ab')
    rule=Rule('join',atoms[:-1],'Goal')
    query=Query('out','Goal')
    return Program('Exponential',atoms,roots,(rule,),(query,)),query

rows=[]
for k in (2,4,6,8,10):
    p,q=family(k)
    result=plan(p,q)
    count=len(result.routes())
    assert result.complete and count==2**k
    rows.append({'pairs':k,'minimal_routes':count,'stored_nodes':len(result.nodes),
                 'complete':result.complete})
p,q=family(10)
r=plan(p,q,max_nodes=128)
assert not r.complete
report={'exact_runs':rows,'capped_run':{'pairs':10,'max_nodes':128,
        'routes_retained':len(r.routes()),'complete':r.complete}}
Path(__file__).resolve().parents[1].joinpath('evidence/stress_results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
