"""Reproduce the peer's Frey proof and two explicitly identified follow-up probes.

Serial Lean only. Uses existing ProveIt dependency artifacts read-only through
LEAN_PATH; invokes neither Lake nor a dependency build and requests no .olean.
The source register is created separately and is never refreshed by this script.
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
PEER = ROOT / 'docs/round-3/unified_report/experiments/lean'
OUT = HERE / 'evidence/parallel-review'
PROVEIT = Path('C:/ProveIt')
LEAN = Path.home() / '.elan/toolchains/leanprover--lean4---v4.32.0/bin/lean.exe'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def main():
    OUT.mkdir(exist_ok=True)
    manifest = PROVEIT / 'lake-manifest.json'
    data = json.loads(manifest.read_text())
    dependencies = []
    paths = []
    for package in data['packages']:
        path = PROVEIT / data['packagesDir'] / package['name']
        library = path / '.lake/build/lib/lean'
        if library.is_dir():
            paths.append(str(library.resolve()))
        dependencies.append({'name': package['name'], 'manifest_revision': package['rev'],
                             'actual_revision': git(path, 'rev-parse', 'HEAD'),
                             'tracked_source_status': git(path, 'status', '--porcelain', '-uno'),
                             'library_path': str(library.resolve()),
                             'library_present': library.is_dir()})
    assert all(p['manifest_revision'] == p['actual_revision'] for p in dependencies)
    assert all(not p['tracked_source_status'] for p in dependencies)
    env = dict(os.environ, LEAN_NUM_THREADS='0', LEAN_PATH=os.pathsep.join(paths))
    version = subprocess.check_output([str(LEAN), '--version'], env=env, text=True).strip()
    assert 'version 4.32.0,' in version
    (OUT / 'FreyExact.lean').write_bytes((PEER / 'FreyExact.lean').read_bytes())
    receipt = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'version': version,
               'executable': str(LEAN), 'LEAN_NUM_THREADS': '0', 'LEAN_PATH': paths,
               'proveit_head': git(PROVEIT, 'rev-parse', 'HEAD'),
               'manifest_sha256': sha(manifest), 'dependencies': dependencies,
               'scope': 'Fresh serial acceptance of an unchanged imported Frey proof and two identified local probes, using existing dependency artifacts. No external writes, Lake, dependency build, cache refresh, or complete audit of imported library artifacts.',
               'cases': []}
    specs = [('FreyExact.lean', 0, 6, 7, 'Unchanged peer source: six named theorems, seven examples, four axiom queries.'),
             ('SupplyChecked.lean', 0, 0, 4, 'Adapted positive supply probe: removes the deliberate mvcgen misuse, uses the replacement matrix lemma, and checks an admissible Frey premise tuple.'),
             ('AdequacyChecks.lean', 0, 3, 0, 'New bundled-core counterexample to coefficient-test completeness on List Empty.')]
    for name, expected, theorems, examples, scope in specs:
        source = OUT / name
        command = [str(LEAN), str(source)]
        print(f'Checking {name} serially...', flush=True)
        start = time.perf_counter()
        run = subprocess.run(command, cwd=OUT, env=env, capture_output=True, timeout=900)
        log = OUT / source.with_suffix('.log').name
        log.write_bytes(run.stdout + run.stderr)
        receipt['cases'].append({'source': name, 'source_sha256': sha(source),
                                 'command': command, 'exit_code': run.returncode,
                                 'expected_exit_code': expected,
                                 'seconds': time.perf_counter() - start,
                                 'log': log.name, 'log_sha256': sha(log),
                                 'named_theorems': theorems, 'examples': examples,
                                 'scope': scope})
        (OUT / 'execution-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        print(f'{name}: exit {run.returncode}, {receipt["cases"][-1]["seconds"]:.2f}s', flush=True)
        if run.returncode != expected:
            print(log.read_text(encoding='utf-8'), flush=True)
            raise SystemExit(run.returncode or 1)
    assert sha(manifest) == receipt['manifest_sha256']
    print('All three focused checks accepted.', flush=True)


if __name__ == '__main__':
    main()
