"""Create (explicit --create) or verify immutable round-four source provenance."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess
from pypdf import PdfReader

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
PIN = '58ced1ce667b3ba1ed162a0c6280959536c8bc5f'
NAMES = ['Alder','Bryony','Clover','Fennel','Heather','Juniper','Laurel','Rowan','Sorrel']
REGISTER = HERE / 'source-register.json'

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def digest(b):
    return hashlib.sha256(b).hexdigest()

def files_at(prefix):
    return git('ls-tree','-r','--name-only',PIN,'--',prefix).decode().splitlines()

def entry(path, role):
    blob = git('rev-parse', f'{PIN}:{path}').decode().strip()
    raw = git('cat-file','blob',blob)
    assert (ROOT/path).read_bytes() == raw, path
    return {'path': path, 'role': role, 'git_blob': blob,
            'sha256': digest(raw), 'bytes': len(raw)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create', action='store_true')
    args = parser.parse_args()
    if args.create:
        if REGISTER.exists():
            raise SystemExit('Existing provenance is not refreshed implicitly.')
        paths = files_at('docs/round-4/ideas')
        assert len(paths) == 159
        rows = [entry(p, 'round4-primary-input') for p in paths]
        secondary = ['docs/round-3/synthesis/unified-report.tex',
                     'docs/round-3/synthesis/unified-report.pdf',
                     'docs/round-3/unified_report/unified_report.tex',
                     'docs/round-3/unified_report/unified_report.pdf']
        rows += [entry(p,'round3-secondary-synthesis') for p in secondary]
        packages = []
        for name in NAMES:
            own = [p for p in paths if p.split('/')[3] == name]
            pdf = next(p for p in own if p.endswith('.pdf'))
            packages.append({'name':name,'artifacts':len(own),'pdf':pdf,
                             'pdf_pages':len(PdfReader(ROOT/pdf).pages),
                             'lean_sources':len([p for p in own if p.endswith('.lean')])})
        data = {'created_utc':datetime.now(timezone.utc).isoformat(),
                'input_commit':PIN, 'packages':packages, 'files':rows,
                'scope':'Input bytes and PDF metadata verified; input PDFs were not rebuilt. Prior syntheses are secondary context, not additional independent proposals.'}
        REGISTER.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    data = json.loads(REGISTER.read_text(encoding='utf-8'))
    assert data['input_commit'] == PIN
    for item in data['files']:
        raw = (ROOT/item['path']).read_bytes()
        assert digest(raw) == item['sha256'], item['path']
        assert digest(git('cat-file','blob',item['git_blob'])) == item['sha256']
        assert git('rev-parse', f"{PIN}:{item['path']}").decode().strip() == item['git_blob']
    assert sum(p['artifacts'] for p in data['packages']) == 159
    assert sum(p['pdf_pages'] for p in data['packages']) == 325
    assert sum(p['lean_sources'] for p in data['packages']) == 20
    print('Verified 159 round-four inputs and four secondary synthesis files; 325 source PDF pages, 20 supplied Lean files.')

if __name__ == '__main__':
    main()
