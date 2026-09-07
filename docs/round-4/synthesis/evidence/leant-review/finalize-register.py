"""Capture narrow direct acceptance helpers and annotate actual static read scopes."""
from pathlib import Path
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
REPO = Path('C:/Leant')
PIN = '823259f7e3c6d24e990d3f48f78c4f1c4f88059e'

def git(*args):
    return subprocess.run(['git', *args], cwd=REPO, capture_output=True, check=True, timeout=60).stdout

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    register = HERE / 'source-register.json'
    data = json.loads(register.read_text())
    fresh_full = {'src/Leant/Synth/Verification.hs', 'src/Leant/Synth/Behavioral.hs',
                  'src/Leant/Synth/Length/Contract.hs', 'src/Leant/Synth/Length/Adapter.hs',
                  'src/Leant/Synth/Length/Handoff.hs'}
    for record in data['files']:
        if record['source_path'] in fresh_full:
            record['read_scope_this_pass'] = {'kind': 'full static reading', 'ranges': [[1, record['lines']]]}
        elif record['source_path'] != 'src/Main.hs':
            record['read_scope_this_pass'] = {'kind': 'hash reverified only; not reread this pass'}
    for path, ranges, output in [
            ('src/Main.hs', [[760, 782], [2380, 2475]], 'main-helper-excerpts.txt'),
            ('src/Leant/Synth/Fragment.hs', [[1555, 1590]], 'fragment-excerpts.txt')]:
        blob = git('show', PIN + ':' + path)
        lines = blob.decode().splitlines()
        excerpt = '\n\n'.join('\n'.join(f'{i}: {lines[i-1]}' for i in range(a,b+1)) for a,b in ranges) + '\n'
        target = HERE / output
        target.write_text(excerpt, encoding='utf-8')
        existing = next((r for r in data['files'] if r['source_path'] == path), None)
        if existing:
            existing['additional_read_ranges'] = ranges
            existing['additional_retained_excerpt'] = output
            existing['additional_excerpt_sha256'] = sha(target.read_bytes())
        else:
            data['files'].append({'source_path': path, 'git_blob': git('rev-parse', PIN + ':' + path).decode().strip(),
                                  'sha256': sha(blob), 'bytes': len(blob), 'lines': len(lines),
                                  'read_scope_this_pass': {'kind': 'selected ranges only', 'ranges': ranges},
                                  'retained_excerpt': output, 'excerpt_sha256': sha(target.read_bytes())})
    data['djex']['read_scope_this_pass'] = 'Both retained ranges 321-390 and 1341-1480 reread in full; remainder not read.'
    data['audit_commands'] = ['python -B docs/round-4/synthesis/evidence/leant-review/capture.py',
                              'python -B docs/round-4/synthesis/evidence/leant-review/finalize-register.py']
    data['scope_notes'] = [
        'Five small Leant modules reread fully; four further previous source copies freshly byte-reverified only.',
        'Main.hs read only in explicitly registered ranges; Fragment.hs read only in the candidate-verification helper range.',
        'Djex inspected at the parent pin gitlink, not its live branch. Its full blob hash and preserved excerpt hash match prior evidence.',
        'No claim is made about current HEAD implementation, dirty contents, backend protocol correctness, or fresh runtime behavior.']
    register.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print('Registered direct helpers and explicit fresh read scopes.')

if __name__ == '__main__':
    main()
