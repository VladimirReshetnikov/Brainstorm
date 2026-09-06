"""Serial, isolated checks of supplied Lean specimens; no Lake or output olean.

The source packages are read-only. A separate audited copy adds only #print
commands. Receipt success is compiler acceptance, not frontend implementation.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
OUT = HERE / 'evidence/lean'
LEAN = Path.home() / '.elan/toolchains/leanprover--lean4---v4.32.0/bin/lean.exe'
CASES = [
 ('basalt', 'companions/ContractCore.lean', ['Basalt.weaken_value', 'Basalt.observationCongruence']),
 ('fiber', 'CoreEncoding.lean', ['Fiber.weaken_preserves_value', 'Fiber.compose_behavior', 'Fiber.certificate_bridge']),
 ('gneiss', 'GneissCore.lean', ['Gneiss.respects_comp', 'Gneiss.complete_iff']),
 ('karst', 'examples/KarstCore.lean', ['KarstCore.behCompose', 'KarstCore.dropAllLengthOnEmpty']),
 ('moraine', 'companion/Contracts.lean', ['MoraineReference.mapSpec_compose', 'MoraineReference.LengthExpr.model_sound', 'MoraineReference.LengthExpr.promote_model_spec']),
 ('schist', 'SchistCore.lean', ['Schist.AffineCertificate.eval_nf', 'Schist.AffineCertificate.check_sound', 'Schist.AffineCertificate.original_target', 'Schist.AffineCertificate.corrupted_rejected']),
 ('tephra', 'TephraCore.lean', ['Tephra.Contract.comp', 'Tephra.restrict_comp', 'Tephra.refute_universal']),
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, LEAN_NUM_THREADS='0')
    env.pop('LEAN_PATH', None)
    version = subprocess.check_output([str(LEAN), '--version'], text=True, env=env).strip()
    receipt = {'started_utc': datetime.now(timezone.utc).isoformat(),
               'executable': str(LEAN), 'version': version, 'LEAN_NUM_THREADS': '0',
               'scope': 'Serial standalone source and axiom audit; no Lake, external repository build, or dependency download.',
               'cases': []}
    for name, relative, audits in CASES:
        source = ROOT / 'docs/round-3/ideas' / name / relative
        folder = OUT / name
        folder.mkdir(exist_ok=True)
        copied = folder / source.name
        copied.write_bytes(source.read_bytes())
        command = [str(LEAN), str(copied)]
        started = time.perf_counter()
        run = subprocess.run(command, cwd=folder, env=env, capture_output=True, timeout=120)
        log = folder / 'original.log'
        log.write_bytes(run.stdout + run.stderr)
        result = {'proposal': name, 'source': source.relative_to(ROOT).as_posix(),
                  'copied_source': copied.relative_to(HERE).as_posix(),
                  'source_sha256': sha(source), 'command': command, 'cwd': str(folder),
                  'exit_code': run.returncode, 'seconds': time.perf_counter() - started,
                  'log': log.relative_to(HERE).as_posix(), 'log_sha256': sha(log)}
        print(f'{name}: original exit {run.returncode}', flush=True)
        if run.returncode == 0:
            audited = folder / 'Audit.lean'
            audited.write_bytes(source.read_bytes() + ('\n\n-- Review-only axiom queries.\n' +
                                '\n'.join('#print axioms ' + target for target in audits) + '\n').encode('utf-8'))
            audit_run = subprocess.run([str(LEAN), str(audited)], cwd=folder, env=env,
                                       capture_output=True, timeout=120)
            audit_log = folder / 'audit.log'
            audit_log.write_bytes(audit_run.stdout + audit_run.stderr)
            result['audit'] = {'targets': audits, 'exit_code': audit_run.returncode,
                              'source': audited.relative_to(HERE).as_posix(), 'source_sha256': sha(audited),
                              'log': audit_log.relative_to(HERE).as_posix(), 'log_sha256': sha(audit_log)}
            print(f'{name}: audit exit {audit_run.returncode}', flush=True)
        if sha(source) != result['source_sha256']:
            raise RuntimeError('Read-only input changed: ' + str(source))
        receipt['cases'].append(result)
        (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    receipt['completed_utc'] = datetime.now(timezone.utc).isoformat()
    (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()
