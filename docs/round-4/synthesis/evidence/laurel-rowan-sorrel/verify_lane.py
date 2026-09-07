"""Retain focused-probe receipts and compare isolated outputs with author inputs."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(path):
    return {p.relative_to(path).as_posix(): sha(p)
            for p in sorted(path.rglob('*')) if p.is_file()}

def main():
    receipt = json.loads((HERE / 'receipt.json').read_text())
    command = [sys.executable, '-B', 'semantic_probes.py']
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0', PYTHONIOENCODING='utf-8')
    run = subprocess.run(command, cwd=HERE, env=env, capture_output=True, timeout=60)
    streams = {}
    for name, contents in [('stdout', run.stdout), ('stderr', run.stderr)]:
        path = HERE / 'logs' / f'semantic-probes.{name}.txt'
        path.write_bytes(contents)
        streams[name] = {'path': path.relative_to(HERE).as_posix(), 'sha256': sha(path)}
    current = {name: inventory(ROOT / 'docs/round-4/ideas' / name)
               for name in ('Laurel', 'Rowan', 'Sorrel')}
    comparisons = []
    for name, files in receipt['input_sha256_before'].items():
        for relative, expected in files.items():
            copy = HERE / 'copies' / name / relative
            if relative.endswith('.lean') or relative.endswith('_result.json') or '/generated/' in relative:
                original = ROOT / 'docs/round-4/ideas' / name / relative
                comparisons.append({'package': name, 'path': relative,
                                    'byte_identical_to_author_input': sha(copy) == expected,
                                    'text_identical_after_universal_newlines': copy.read_text(encoding='utf-8') == original.read_text(encoding='utf-8'),
                                    'original_sha256': expected, 'fresh_sha256': sha(copy)})
    record = {'scope': 'Fresh Python probes and file comparison only; no Lean compilation.',
              'command': command, 'cwd': str(HERE), 'exit_code': run.returncode,
              'python': sys.version, 'streams': streams,
              'source_sha256': sha(HERE / 'semantic_probes.py'),
              'result_sha256': sha(HERE / 'semantic-probes.json'),
              'generated_lean_sha256': sha(HERE / 'SorrelSelectionProbe.lean'),
              'input_file_counts': {name: len(files) for name, files in current.items()},
              'all_inputs_unchanged_since_reproduction': current == receipt['input_sha256_before'],
              'no_bytecode_in_lane': not any(HERE.rglob('*.pyc')),
              'generated_artifact_comparison': comparisons}
    (HERE / 'probe-receipt.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    assert run.returncode == 0
    assert record['all_inputs_unchanged_since_reproduction'] and record['no_bytecode_in_lane']
    assert all(item['text_identical_after_universal_newlines'] for item in comparisons)
    print(json.dumps(record, indent=2))

if __name__ == '__main__':
    main()
