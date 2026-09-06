"""Check only the two synthesis interface theorems, serially after other Lean."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / 'evidence/lean'
LEAN = Path.home() / '.elan/toolchains/leanprover--lean4---v4.32.0/bin/lean.exe'
source = OUT / 'SynthesisChecks.lean'
env = dict(os.environ, LEAN_NUM_THREADS='0')
env.pop('LEAN_PATH', None)
command = [str(LEAN), str(source)]
started = time.perf_counter()
run = subprocess.run(command, cwd=OUT, env=env, capture_output=True, timeout=120)
log = OUT / 'SynthesisChecks.log'
log.write_bytes(run.stdout + run.stderr)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
receipt = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'command': command,
           'version': subprocess.check_output([str(LEAN), '--version'], env=env, text=True).strip(),
           'LEAN_NUM_THREADS': '0', 'LEAN_PATH': 'unset; bundled Init only',
           'exit_code': run.returncode, 'seconds': time.perf_counter() - started,
           'source_sha256': sha(source), 'log_sha256': sha(log), 'theorems': 2,
           'scope': 'Two generic interface implications with their premises explicit; no frontend or matrix implementation.'}
(OUT / 'synthesis-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(log.read_text(encoding='utf-8'))
raise SystemExit(run.returncode)
