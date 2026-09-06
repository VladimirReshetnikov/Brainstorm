"""Create explicitly, or verify, the immutable round-3 input register.

Canonical Git identity and checkout byte identity are separate. This checks
provenance, not the truth of input reports or source/PDF parity of their builds.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pypdf import PdfReader

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
PIN = '58bb54219f494b29310ff77384732129411da887'
NAMES = ['basalt', 'fiber', 'gneiss', 'karst', 'moraine', 'obsidian', 'schist', 'tephra', 'trellis']

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def inventory():
    return git('ls-tree', '-r', '--name-only', PIN, '--', 'docs/round-3/ideas').decode().splitlines()

def create():
    files = []
    for relative in inventory():
        path = ROOT / relative
        blob = git('rev-parse', f'{PIN}:{relative}').decode().strip()
        canonical = git('cat-file', 'blob', blob)
        checkout = path.read_bytes()
        row = {'path': relative, 'proposal': relative.split('/')[3], 'git_blob': blob,
               'git_bytes_sha256': digest(canonical), 'checkout_sha256': digest(checkout),
               'bytes': len(checkout)}
        if path.suffix == '.pdf':
            row['pdf_pages'] = len(PdfReader(path).pages)
        else:
            row['text_lines'] = len(checkout.decode('utf-8-sig').splitlines())
        files.append(row)
    inherited = []
    for relative in ['docs/round-2/synthesis/unified-report.tex', 'docs/round-2/unified_report/unified_report.tex']:
        inherited.append({'path': relative, 'classification': 'prior synthesis, not an independent round-3 proposal',
                          'git_blob': git('rev-parse', f'{PIN}:{relative}').decode().strip(),
                          'checkout_sha256': digest((ROOT / relative).read_bytes())})
    result = {'source_commit': PIN, 'created_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'All tracked files of nine round-3 packages; prior syntheses classified separately. Input PDF pages are metadata, not fresh PDF/TeX parity checks.',
              'proposals': NAMES, 'files': files, 'prior_syntheses': inherited}
    (HERE / 'source-register.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

def validate():
    data = json.loads((HERE / 'source-register.json').read_text(encoding='utf-8'))
    subprocess.run(['git', 'merge-base', '--is-ancestor', PIN, 'HEAD'], cwd=ROOT, check=True)
    assert data['source_commit'] == PIN and data['proposals'] == NAMES
    assert sorted(row['path'] for row in data['files']) == sorted(inventory())
    # Batch Git queries to avoid hundreds of process launches on Windows.
    head_rows = git('ls-tree', '-r', 'HEAD', '--', 'docs/round-3/ideas').decode().splitlines()
    head_blobs = {line.split('\t', 1)[1]: line.split('\t', 1)[0].split()[2] for line in head_rows}
    index_rows = git('ls-files', '-s', '--', 'docs/round-3/ideas').decode().splitlines()
    index_blobs = {line.split('\t', 1)[1]: line.split('\t', 1)[0].split()[1] for line in index_rows
                   if line.split('\t', 1)[0].split()[2] == '0'}
    blob_ids = list(dict.fromkeys(row['git_blob'] for row in data['files']))
    batch = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT,
                                    input=('\n'.join(blob_ids) + '\n').encode())
    offset, canonical_hashes = 0, {}
    for blob in blob_ids:
        end = batch.index(b'\n', offset)
        header = batch[offset:end].decode().split()
        assert header[0] == blob and header[1] == 'blob'
        size = int(header[2])
        contents = batch[end + 1:end + 1 + size]
        assert len(contents) == size and batch[end + 1 + size:end + 2 + size] == b'\n'
        canonical_hashes[blob] = digest(contents)
        offset = end + 2 + size
    assert offset == len(batch)
    pages = {}
    for row in data['files']:
        path = ROOT / row['path']
        actual = path.read_bytes()
        assert digest(actual) == row['checkout_sha256'], f'Changed input checkout: {path}'
        assert head_blobs.get(row['path']) == row['git_blob'], f'Changed input in HEAD: {path}'
        assert index_blobs.get(row['path']) == row['git_blob'], f'Changed input in index: {path}'
        assert canonical_hashes[row['git_blob']] == row['git_bytes_sha256']
        if 'pdf_pages' in row:
            assert len(PdfReader(path).pages) == row['pdf_pages']
            pages[row['proposal']] = row['pdf_pages']
        else:
            assert len(actual.decode('utf-8-sig').splitlines()) == row['text_lines']
    for row in data['prior_syntheses']:
        assert digest((ROOT / row['path']).read_bytes()) == row['checkout_sha256']
    return {'status': 'passed', 'source_commit': PIN, 'proposal_count': len(NAMES),
            'input_files': len(data['files']), 'input_pdf_pages': pages,
            'prior_syntheses_counted_as_proposals': 0}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--create', action='store_true')
    args = parser.parse_args()
    if args.create:
        create()
    print(json.dumps(validate(), indent=2))
