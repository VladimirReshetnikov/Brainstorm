"""Recheck the parallel review's two new Lean files, then query list theorem axioms.

Run serially, with no other Lean job active. Sources and outputs stay here;
pre-existing ProveIt dependency artifacts are read only. No Lake invocation.
The appended-query file is explicitly distinct from the unchanged source.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import time

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
OUT = HERE / 'evidence/parallel-review'
PIN = 'c92ef058979fcb8f6c11030ac9ed80c64186e0f8'
PREFIX = 'docs/round-4/unified_report/'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd)

def write(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows=[]
    for line in git('ls-tree','-r',PIN,'--',PREFIX).decode().splitlines():
        meta, path=line.split('\t',1)
        mode, kind, blob=meta.split()
        assert kind=='blob'
        data=git('cat-file','blob',blob)
        assert data==(ROOT/path).read_bytes(), path
        rows.append({'path':path,'git_blob':blob,'sha256':sha(ROOT/path),'bytes':len(data)})
    register={'snapshot_utc':datetime.now(timezone.utc).isoformat(),'pinned_commit':PIN,
              'role':'Parallel round-four synthesis; secondary interpretation and new experiments, not a tenth independent report.',
              'files':rows}
    write('source-register.json',register)
    base=json.loads((HERE/'evidence/lean/execution-receipt.json').read_text())
    env=dict(os.environ,LEAN_NUM_THREADS='0')
    env.pop('LEAN_PATH',None)
    version=subprocess.check_output([base['executable'],'--version'],env=env).decode().strip()
    assert version==base['version']
    deps=[]
    for d in base['dependencies']:
        if not d['library_present']: continue
        library=Path(d['library_path'])
        assert library.is_dir()
        package=library.parents[3]
        deps.append({'library_path':str(library),'package_head':git('rev-parse','HEAD',cwd=package).decode().strip(),
                     'package_status':git('status','--short',cwd=package).decode().splitlines()})
    for name in ['FreyRoutes.lean','ListImage.lean']:
        (OUT/name).write_bytes((ROOT/PREFIX/'experiments/lean'/name).read_bytes())
    original=(OUT/'ListImage.lean').read_bytes()
    queries=['length_image','empty_one_point_frame','inhabited_two_point_frame','diagonal_frame']
    (OUT/'ListImageAxioms.lean').write_bytes(original+b'\n-- Review-only appended axiom queries; original source above is unchanged.\n'+
        ''.join(f'#print axioms ListImage.{q}\n' for q in queries).encode())
    receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'version':version,
             'executable':base['executable'],'source_register_sha256':sha(OUT/'source-register.json'),
             'runner_sha256':sha(Path(__file__)),'dependencies':deps,
             'dependency_scope':'Existing library artifacts, package HEAD/status recorded; no rebuild or dependency compilation audit.',
             'scope':'Two unchanged peer sources and one separately identified appended-query audit; serial direct Lean, no external writes.',
             'cases':[]}
    write('execution-receipt.json',receipt)
    for name,mode,origin in [('FreyRoutes.lean','mathlib',PREFIX+'experiments/lean/FreyRoutes.lean'),
                             ('ListImage.lean','core',PREFIX+'experiments/lean/ListImage.lean'),
                             ('ListImageAxioms.lean','core',None)]:
        runenv=dict(env)
        if mode=='mathlib': runenv['LEAN_PATH']=os.pathsep.join(d['library_path'] for d in deps)
        command=[base['executable'],name]
        print('Checking parallel review '+name,flush=True)
        start=time.perf_counter()
        result=subprocess.run(command,cwd=OUT,env=runenv,capture_output=True,timeout=900)
        log=OUT/Path(name).with_suffix('.log')
        log.write_bytes(result.stdout+result.stderr)
        row={'source':name,'source_sha256':sha(OUT/name),'input':origin,'command':command,
             'cwd':str(OUT),'LEAN_PATH':runenv.get('LEAN_PATH'),'LEAN_NUM_THREADS':'0',
             'exit_code':result.returncode,'seconds':time.perf_counter()-start,
             'log':log.name,'log_sha256':sha(log)}
        receipt['cases'].append(row)
        write('execution-receipt.json',receipt)
        print(f'{name}: exit {result.returncode}',flush=True)
        assert result.returncode==0, log.read_text(encoding='utf-8',errors='replace')

if __name__=='__main__':
    main()
