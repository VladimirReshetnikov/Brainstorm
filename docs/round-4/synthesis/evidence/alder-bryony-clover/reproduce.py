"""Isolated round-4 Python reproduction; never invokes Lean or external repos."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time
from datetime import datetime,timezone

LANE=Path(__file__).resolve().parent
ROOT=LANE.parents[4]
PIN='58ced1ce667b3ba1ed162a0c6280959536c8bc5f'
NAMES=('alder','bryony','clover')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory():
    return {p.relative_to(ROOT).as_posix():sha(p) for n in NAMES
            for p in sorted((ROOT/'docs/round-4/ideas'/n).rglob('*')) if p.is_file()}

def main():
    before=inventory()
    runs=LANE/'runs'
    runs.mkdir(exist_ok=True)
    copied={}
    for name in NAMES:
        destination=runs/name
        if destination.exists(): raise RuntimeError('Refusing to overwrite previous run: '+str(destination))
        shutil.copytree(ROOT/'docs/round-4/ideas'/name,destination,
                        ignore=shutil.ignore_patterns('*.pdf','*.tex','*.log','build.sh'))
        copied[name]={p.relative_to(destination).as_posix():sha(p)
                      for p in sorted(destination.rglob('*')) if p.is_file()}
    commands=[
      ('alder','tests','.', ['companion/test_alder.py'],0),
      ('alder','demo','.', ['companion/alder_core.py','companion/examples/quotient.alder','--lean','companion/generated/Quotient.lean','--events','companion/generated/quotient.json'],0),
      ('alder','scope_negative','.', ['companion/alder_core.py','companion/examples/scope_rejected.alder','--lean','scope-refused.lean','--events','scope-refused.json'],1),
      ('alder','publication_negative','.', ['companion/alder_core.py','companion/examples/unused_claim_rejected.alder','--lean','publication-refused.lean','--events','publication-refused.json'],1),
      ('bryony','tests','.', ['prototype/test_bryony.py'],0),
      ('bryony','demo','.', ['prototype/bryony.py','prototype/frey4.bry','--output','evidence/frey4'],0),
      ('clover','tests','companion', ['-m','unittest','-v','test_clover_slice'],0),
      ('clover','demo','companion', ['clover_slice.py','demo.clover','--json','demo-result.json','--lean','GeneratedExamples.lean'],0),
      ('clover','affine','companion', ['affine_basis.py'],0),
      ('clover','profiles','companion', ['compare_profiles.py'],0),
    ]
    receipt={'pin':PIN,'started_utc':datetime.now(timezone.utc).isoformat(),
             'python':sys.version,'python_executable':sys.executable,
             'inspected_before_execution':True,'inputs_before':before,
             'copied_files_before':copied,'runs':[],
             'adaptations':['No source edits. Commands run from isolated package copies. Python -B and PYTHONDONTWRITEBYTECODE=1; PYTHONUTF8=1 for portable Windows text I/O. PDF/TeX/build scripts and historical .log files omitted from copies.'],
             'scope':'Fresh Python reference-model execution only; no Lean, Lake, PDF, external repository, authoring-productivity or universal implementation verification.'}
    env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
    for name,label,relative,args,expected in commands:
        cwd=runs/name/relative
        command=[sys.executable,'-B',*args]
        start=time.perf_counter()
        result=subprocess.run(command,cwd=cwd,env=env,capture_output=True,timeout=180)
        logs=LANE/'logs'/name
        logs.mkdir(parents=True,exist_ok=True)
        stdout=logs/(label+'.stdout.txt'); stderr=logs/(label+'.stderr.txt')
        stdout.write_bytes(result.stdout); stderr.write_bytes(result.stderr)
        row={'report':name,'case':label,'command':command,
             'cwd':cwd.relative_to(ROOT).as_posix(),'exit_code':result.returncode,
             'expected_exit_code':expected,'seconds':time.perf_counter()-start,
             'stdout':stdout.relative_to(LANE).as_posix(),'stdout_sha256':sha(stdout),
             'stderr':stderr.relative_to(LANE).as_posix(),'stderr_sha256':sha(stderr)}
        receipt['runs'].append(row)
        print(name,label,result.returncode,flush=True)
    receipt['inputs_unchanged']=before==inventory()
    receipt['source_copies_unchanged']=all(sha(runs/n/p)==h for n,m in copied.items()
        for p,h in m.items() if p.endswith(('.py','.alder','.bry','.clover')))
    receipt['negative_outputs_absent']=not any((runs/'alder'/p).exists() for p in
        ['scope-refused.lean','scope-refused.json','publication-refused.lean','publication-refused.json'])
    receipt['artifacts_after']={p.relative_to(LANE).as_posix():sha(p)
        for p in sorted(runs.rglob('*')) if p.is_file()}
    receipt['status']='passed' if (receipt['inputs_unchanged'] and receipt['source_copies_unchanged']
        and receipt['negative_outputs_absent'] and all(r['exit_code']==r['expected_exit_code'] for r in receipt['runs'])) else 'failed'
    (LANE/'reproduction.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(receipt['status'],flush=True)
    if receipt['status']!='passed': raise SystemExit(1)
if __name__=='__main__': main()
