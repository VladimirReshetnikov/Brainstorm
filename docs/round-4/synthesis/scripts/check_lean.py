"""Check all 20 supplied Lean files serially, without modifying inputs.

Only CloverCore needs an isolated compiled module. Mathlib imports use existing
ProveIt dependencies read-only; no Lake, dependency builds, or cache updates.
Nonzero original results are evidence, not an excuse to rewrite the inputs.
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
INPUT = HERE.parent / 'ideas'
OUT = HERE / 'evidence/lean'
PROVEIT = Path('C:/ProveIt')
LEAN = Path.home() / '.elan/toolchains/leanprover--lean4---v4.32.0/bin/lean.exe'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    library = HERE / '.build/lean'
    library.mkdir(parents=True, exist_ok=True)
    manifest = PROVEIT / 'lake-manifest.json'
    data = json.loads(manifest.read_text())
    deps, paths = [], []
    for p in data['packages']:
        root = PROVEIT / data['packagesDir'] / p['name']
        lib = root / '.lake/build/lib/lean'
        if lib.is_dir():
            paths.append(str(lib.resolve()))
        deps.append({'name': p['name'], 'manifest_revision': p['rev'],
                     'actual_revision': git(root, 'rev-parse', 'HEAD'),
                     'tracked_source_status': git(root, 'status', '--porcelain', '-uno'),
                     'library_path': str(lib.resolve()), 'library_present': lib.is_dir()})
    assert all(d['manifest_revision'] == d['actual_revision'] and not d['tracked_source_status'] for d in deps)
    env = dict(os.environ, LEAN_NUM_THREADS='0')
    env.pop('LEAN_PATH', None)
    receipt = {'checked_utc': datetime.now(timezone.utc).isoformat(),
               'input_commit': git(ROOT, 'rev-parse', 'HEAD'),
               'executable': str(LEAN), 'version': subprocess.check_output([str(LEAN), '--version'], text=True).strip(),
               'LEAN_NUM_THREADS': '0', 'proveit_head': git(PROVEIT, 'rev-parse', 'HEAD'),
               'manifest_sha256': sha(manifest), 'dependencies': deps,
               'scope': 'Fresh acceptance attempts of byte-identical copies of all supplied Lean sources. Existing dependency artifacts are used, not rebuilt or fully audited. A successful opaque-Prop template proves conditional implication assembly only.',
               'cases': []}
    originals = sorted(INPUT.rglob('*.lean'))
    assert len(originals) == 20
    for source in originals:
        relative = source.relative_to(INPUT)
        copy = OUT / 'originals' / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(source.read_bytes())
        caseenv = env.copy()
        command = [str(LEAN), copy.name]
        if relative.parts[0] == 'Heather':
            caseenv['LEAN_PATH'] = os.pathsep.join(paths)
        if relative.parts[0] == 'Clover':
            caseenv['LEAN_PATH'] = str(library)
            if copy.name == 'CloverCore.lean':
                command += ['-o', str(library / 'CloverCore.olean')]
        print('Checking ' + relative.as_posix(), flush=True)
        start = time.perf_counter()
        try:
            result = subprocess.run(command, cwd=copy.parent, env=caseenv, capture_output=True, timeout=900)
            code, output = result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired as exc:
            code, output = 'timeout', (exc.stdout or b'') + (exc.stderr or b'')
        log = copy.with_suffix('.log')
        log.write_bytes(output)
        receipt['cases'].append({'input': source.relative_to(ROOT).as_posix(),
            'copy': copy.relative_to(HERE).as_posix(), 'source_sha256': sha(copy),
            'command': command, 'cwd': str(copy.parent), 'LEAN_PATH': caseenv.get('LEAN_PATH'),
            'exit_code': code, 'seconds': time.perf_counter()-start,
            'log': log.relative_to(HERE).as_posix(), 'log_sha256': sha(log)})
        assert sha(source) == sha(copy)
        (OUT / 'execution-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
        print(str(code) + ': ' + relative.as_posix(), flush=True)
    assert sha(manifest) == receipt['manifest_sha256']
    print('Completed all 20 original-source attempts.', flush=True)

if __name__ == '__main__':
    main()
