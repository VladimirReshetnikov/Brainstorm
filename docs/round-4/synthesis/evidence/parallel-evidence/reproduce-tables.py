"""Reproduce an inspected editorial table generator in an isolated copy only."""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = ROOT / 'docs/round-4/unified_report'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(path):
    return {p.relative_to(path).as_posix(): sha(p) for p in sorted(path.rglob('*')) if p.is_file()}

def main():
    before = inventory(SOURCE)
    copy = HERE / 'copy'
    if copy.exists():
        raise SystemExit('Refusing to overwrite previous isolated generator copy')
    (copy / 'tools').mkdir(parents=True)
    shutil.copyfile(SOURCE / 'tools/make_tables.py', copy / 'tools/make_tables.py')
    command = [sys.executable, '-B', 'tools/make_tables.py']
    run = subprocess.run(command, cwd=copy, capture_output=True, timeout=60,
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8'))
    (HERE / 'generator.stdout.txt').write_bytes(run.stdout)
    (HERE / 'generator.stderr.txt').write_bytes(run.stderr)
    comparisons = []
    for generated in sorted(copy.iterdir()):
        if generated.is_file():
            original = SOURCE / generated.name
            comparisons.append({'file': generated.name, 'sha256': sha(generated),
                                'original_sha256': sha(original),
                                'byte_identical': generated.read_bytes() == original.read_bytes(),
                                'newline_normalized_text_identical': generated.read_text(encoding='utf-8') == original.read_text(encoding='utf-8')})
    reports = ['Alder','Bryony','Clover','Fennel','Heather','Juniper','Laurel','Rowan','Sorrel']
    def rows(name):
        with (copy / name).open(encoding='utf-8', newline='') as handle:
            return list(csv.DictReader(handle))
    matrix, suite, questions = map(rows, ['feature_matrix.csv','negative_suite.csv','question_tally.csv'])
    counts = {'matrix_rows': len(matrix),
              'unanimous_rows': sum(all(r[n] == 'Y' for n in reports) for r in matrix),
              'unanimous_new_rows': sum(all(r[n] == 'Y' for n in reports) and r['stated_in_round3_syntheses']=='no' for r in matrix),
              'negative_families': len(suite),
              'negative_new_families': sum(not r['inherits_round3'] for r in suite),
              'negative_with_E_somewhere': sum(any(r[n]=='E' for n in reports) for r in suite),
              'negative_in_at_least_five': sum(int(r['reports']) >= 5 for r in suite),
              'question_rows': len(questions),
              'questions_explicit_all': sum(r['explicit']=='9' for r in questions),
              'question_rows_not_explicit_all': [r['id'] for r in questions if r['explicit']!='9'],
              'affine_theorem_I2_Y_count': next(sum(r[n]=='Y' for n in reports) for r in matrix if r['id']=='I2')}
    record = {'source_pin': 'c92ef058979fcb8f6c11030ac9ed80c64186e0f8',
              'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Editorial table-generator reproduction and CSV arithmetic only; no report-semantic or test-execution validation follows from count parity.',
              'command': command, 'cwd': str(copy), 'python': sys.version, 'exit_code': run.returncode,
              'generator_source_sha256': sha(copy / 'tools/make_tables.py'),
              'stdout_sha256': sha(HERE / 'generator.stdout.txt'), 'stderr_sha256': sha(HERE / 'generator.stderr.txt'),
              'input_inventory_before': before, 'inputs_unchanged': before == inventory(SOURCE),
              'no_bytecode': not any(HERE.rglob('*.pyc')), 'generated_comparisons': comparisons,
              'independently_counted_CSV_rows': counts}
    (HERE / 'table-receipt.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    assert run.returncode == 0 and record['inputs_unchanged'] and record['no_bytecode']
    assert all(r['newline_normalized_text_identical'] for r in comparisons)
    print(json.dumps(counts, indent=2))

if __name__ == '__main__':
    main()
