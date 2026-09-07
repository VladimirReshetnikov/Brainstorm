"""Verify the delivered report, retained execution evidence, and visual receipt.

--seal explicitly creates a final artifact manifest after editing and visual
review. Default verification never refreshes that manifest or execution data.
It checks recorded executions and hashes; it does not rerun Lean or Python tests.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pypdf import PdfReader

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]
MANIFEST=HERE/'artifact-manifest.json'
EXCLUDE={'artifact-manifest.json','validation.json'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def inventory():
    result={}
    for p in sorted(HERE.rglob('*')):
        rel=p.relative_to(HERE)
        if p.is_file() and rel.as_posix() not in EXCLUDE and not any(x in {'.build','.qa','__pycache__'} for x in rel.parts):
            result[rel.as_posix()]={'sha256':sha(p),'bytes':p.stat().st_size}
    return result

def check_lean():
    base=read(HERE/'evidence/lean/execution-receipt.json')
    assert len(base['cases'])==20
    inputs=read(HERE/'source-register.json')
    required={r['path'] for r in inputs['files'] if r['role']=='round4-primary-input' and r['path'].endswith('.lean')}
    assert {r['input'] for r in base['cases']}==required
    for r in base['cases']:
        assert sha(HERE/r['copy'])==r['source_sha256']==sha(ROOT/r['input'])
        assert sha(HERE/r['log'])==r['log_sha256']
        expected=1 if r['input'].endswith('/even_reverse_length.lean') else 0
        assert r['exit_code']==expected, r['input']
    follow=read(HERE/'evidence/lean/followups/execution-receipt.json')
    assert follow['base_receipt_sha256']==sha(HERE/'evidence/lean/execution-receipt.json')
    expected={'KeywordClaim.lean':1,'ShadowCompose.lean':1,'ShadowRule.lean':1,
              'SorrelSelectionProbe.lean':0,'HeatherEvenRepaired.lean':0,'FreySharper.lean':0}
    assert {r['source'] for r in follow['cases']}==set(expected)
    for r in follow['cases']:
        directory=HERE/'evidence/lean/followups'
        assert sha(directory/r['source'])==r['source_sha256']
        assert sha(directory/r['log'])==r['log_sha256']
        assert r['exit_code']==expected[r['source']]
    return {'original_files':20,'original_accepted_files':19,'original_rejected_files':1,
            'followup_accepted_files':3,'followup_expected_rejections':3,
            'original_receipt_sha256':sha(HERE/'evidence/lean/execution-receipt.json'),
            'followup_receipt_sha256':sha(HERE/'evidence/lean/followups/execution-receipt.json')}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seal',action='store_true')
    args=parser.parse_args()
    for name in ['verify_sources.py','verify_convergence.py','verify_python_evidence.py']:
        run=subprocess.run([sys.executable,'-B',str(HERE/'scripts'/name)],cwd=ROOT,capture_output=True)
        print(run.stdout.decode('utf-8',errors='replace').strip())
        if run.returncode:
            raise RuntimeError(run.stderr.decode('utf-8',errors='replace'))
    lean=check_lean()
    tex=HERE/'unified-report.tex'
    pdf=HERE/'unified-report.pdf'
    build=read(HERE/'evidence/build-receipt.json')
    assert build['passes']==3 and build['tex_sha256']==sha(tex) and build['pdf_sha256']==sha(pdf)
    assert build['tex_inputs']=={'unified-report.tex':sha(tex)}
    log=(HERE/'evidence/build.log').read_text(encoding='utf-8',errors='replace')
    assert not re.search(r'Overfull|Missing character|undefined|Rerun to get|Label\(s\) may have changed|destination with the same identifier',log)
    assert 'Output written on' in log
    source=tex.read_text(encoding='utf-8')
    assert 'Final compiler results are recorded' not in source
    for target in re.findall(r'\\href\{([^}]+)\}',source):
        if not target.startswith(('http://','https://')):
            assert (HERE/target).is_file(), target
    reader=PdfReader(pdf)
    page_text=[p.extract_text() or '' for p in reader.pages]
    assert all(len(t.strip())>30 for t in page_text)
    combined='\n'.join(page_text)
    for token in ['Alder','Bryony','Clover','Fennel','Heather','Juniper','Laurel','Rowan','Sorrel',
                  'Questions for the next iteration','Nineteen of the twenty original files']:
        assert token in combined,token
    visual=read(HERE/'evidence/visual-review.json')
    assert visual['pdf_sha256']==sha(pdf)
    assert visual['page_count']==len(reader.pages)
    assert visual['reviewed_pages']==list(range(1,len(reader.pages)+1))
    assert visual['status']=='passed'
    current=inventory()
    if args.seal:
        MANIFEST.write_text(json.dumps({'sealed_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'All committed-package candidates except this manifest and regenerable final validation; intermediate build/render directories excluded.',
            'files':current},indent=2)+'\n',encoding='utf-8')
    manifest=read(MANIFEST)
    assert manifest['files']==current,'Artifacts changed since seal; inspect before explicitly resealing.'
    result={'verified_utc':datetime.now(timezone.utc).isoformat(),'status':'passed',
            'source_sha256':sha(tex),'pdf_sha256':sha(pdf),'pdf_pages':len(reader.pages),
            'artifact_manifest_sha256':sha(MANIFEST),'artifact_files':len(current),
            'lean':lean,'python_validation_sha256':sha(HERE/'evidence/python-validation.json'),
            'visual_review_sha256':sha(HERE/'evidence/visual-review.json'),
            'scope':'Source/receipt integrity, completed recorded executions, PDF build/text checks, and hash-bound human visual review. No new Lean/Python experiment or usability measurement.'}
    (HERE/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f"Verified {len(current)} package artifacts; {len(reader.pages)}-page source/PDF pair; original and follow-up Lean outcomes; Python receipts; visual review.")

if __name__=='__main__':
    main()
