"""Check retained adversarial exports, one identified repair, and sharper Frey lemmas.

Run only after check_lean.py completes. All Lean executions are serial and use
its existing dependency paths; writes stay in the synthesis package.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import time

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / 'evidence/lean/followups'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    base = json.loads((HERE/'evidence/lean/execution-receipt.json').read_text())
    assert len(base['cases']) == 20, 'The original-source campaign must finish first.'
    OUT.mkdir(exist_ok=True)
    source = HERE/'evidence/lean/originals/Heather/companion/generated/even_reverse_length.lean'
    repaired = source.read_text(encoding='utf-8')
    assert repaired.count('\n  omega') == 1
    repaired = repaired.replace('\n  omega', '\n  all_goals omega')
    (OUT/'HeatherEvenRepaired.lean').write_text(
        '-- Synthesis repair: preserve the exact theorem; tolerate simp closing the goal.\n'+repaired,
        encoding='utf-8')
    cases = []
    for name in ['KeywordClaim','ShadowCompose','ShadowRule']:
        original = HERE/'evidence/alder-bryony-clover/adversarial'/f'{name}.lean'
        (OUT/f'{name}.lean').write_bytes(original.read_bytes())
        cases.append((name+'.lean', 'clover', 'Adversarial output from unchanged Clover parser/checker/exporter', str(original.relative_to(HERE))))
    original = HERE/'evidence/laurel-rowan-sorrel/SorrelSelectionProbe.lean'
    if not original.exists():
        matches = list((HERE/'evidence/laurel-rowan-sorrel').rglob('SorrelSelectionProbe.lean'))
        assert len(matches)==1
        original=matches[0]
    (OUT/original.name).write_bytes(original.read_bytes())
    cases.append((original.name,'core','Valid conditional route chosen despite another already-available route',str(original.relative_to(HERE))))
    cases += [('HeatherEvenRepaired.lean','mathlib','Single tactic sequencing repair; original theorem statement preserved',str(source.relative_to(HERE))),
              ('FreySharper.lean','mathlib','Four named helper theorems, two examples, four axiom queries; Juniper p >= 2 improvement',None)]
    receipt = {'checked_utc':datetime.now(timezone.utc).isoformat(),
               'version':base['version'],'executable':base['executable'],
               'base_receipt_sha256':sha(HERE/'evidence/lean/execution-receipt.json'),
               'scope':'Follow-ups are separate from the 20 byte-identical originals. No external writes or full dependency audit.',
               'cases':[]}
    for name,mode,scope,origin in cases:
        env=dict(os.environ,LEAN_NUM_THREADS='0')
        env.pop('LEAN_PATH',None)
        if mode=='clover': env['LEAN_PATH']=str(HERE/'.build/lean')
        if mode=='mathlib': env['LEAN_PATH']=os.pathsep.join(d['library_path'] for d in base['dependencies'] if d['library_present'])
        command=[base['executable'],name]
        print('Checking follow-up '+name,flush=True)
        start=time.perf_counter()
        result=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=900)
        log=OUT/Path(name).with_suffix('.log')
        log.write_bytes(result.stdout+result.stderr)
        row={'source':name,'source_sha256':sha(OUT/name),'origin':origin,
             'command':command,'cwd':str(OUT),'LEAN_PATH':env.get('LEAN_PATH'),
             'exit_code':result.returncode,'seconds':time.perf_counter()-start,
             'log':log.name,'log_sha256':sha(log),'scope':scope}
        receipt['cases'].append(row)
        (OUT/'execution-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
        print(f'{name}: exit {result.returncode}',flush=True)

if __name__=='__main__':
    main()
