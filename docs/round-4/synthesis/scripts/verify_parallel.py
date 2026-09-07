"""Check pinned parallel-review inputs and retained new receipts, without reruns."""
from pathlib import Path
import hashlib
import json
import subprocess

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]
OUT=HERE/'evidence/parallel-review'
PEER=ROOT/'docs/round-4/unified_report'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def validate():
    reg=read(OUT/'source-register.json')
    assert reg['pinned_commit']=='c92ef058979fcb8f6c11030ac9ed80c64186e0f8'
    tree=subprocess.check_output(['git','ls-tree','-r',reg['pinned_commit'],'--',
                                  'docs/round-4/unified_report/'],cwd=ROOT).decode()
    expected={line.split('\t',1)[1]:line.split('\t',1)[0].split()[2] for line in tree.splitlines()}
    assert len(reg['files'])==94 and {r['path']:r['git_blob'] for r in reg['files']}==expected
    for r in reg['files']:
        data=(ROOT/r['path']).read_bytes()
        assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
        assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==r['git_blob']
    run=read(OUT/'execution-receipt.json')
    assert run['source_register_sha256']==sha(OUT/'source-register.json')
    assert run['runner_sha256']==sha(HERE/'scripts/check_parallel_lean.py')
    assert [r['source'] for r in run['cases']]==['FreyRoutes.lean','ListImage.lean','ListImageAxioms.lean']
    for r in run['cases']:
        assert r['exit_code']==0
        assert r['source_sha256']==sha(OUT/r['source'])
        assert r['log_sha256']==sha(OUT/r['log'])
        if r['input']:
            assert (OUT/r['source']).read_bytes()==(ROOT/r['input']).read_bytes()
    original=(OUT/'ListImage.lean').read_bytes()
    audited=(OUT/'ListImageAxioms.lean').read_bytes()
    assert audited.startswith(original)
    queries=['length_image','empty_one_point_frame','inhabited_two_point_frame','diagonal_frame']
    suffix=(b'\n-- Review-only appended axiom queries; original source above is unchanged.\n'+
        ''.join(f'#print axioms ListImage.{q}\n' for q in queries).encode())
    assert audited==original+suffix
    axiom_log=(OUT/'ListImageAxioms.log').read_text(encoding='utf-8')
    assert all(f"'ListImage.{q}'" in axiom_log for q in queries)
    tables=HERE/'evidence/parallel-evidence'
    tr=read(tables/'table-receipt.json')
    assert tr['source_pin']==reg['pinned_commit'] and tr['exit_code']==0 and tr['inputs_unchanged']
    assert tr['generator_source_sha256']==sha(PEER/'tools/make_tables.py')==sha(tables/'copy/tools/make_tables.py')
    for name in ['stdout','stderr']:
        assert tr[f'{name}_sha256']==sha(tables/f'generator.{name}.txt')
    assert len(tr['input_inventory_before'])==94
    for path,digest in tr['input_inventory_before'].items(): assert sha(PEER/path)==digest
    assert len(tr['generated_comparisons'])==11
    for r in tr['generated_comparisons']:
        generated=tables/'copy'/r['file']; original=PEER/r['file']
        assert sha(generated)==r['sha256'] and sha(original)==r['original_sha256']
        assert r['byte_identical']==(generated.read_bytes()==original.read_bytes())
        assert r['newline_normalized_text_identical'] and generated.read_text(encoding='utf-8')==original.read_text(encoding='utf-8')
    return {'pinned_secondary_files':94,'unchanged_new_lean_files_accepted':2,'appended_query_audits_accepted':1,
            'table_generator_invocations':1,'generated_tables_text_equal':11,
            'source_register_sha256':sha(OUT/'source-register.json'),
            'lean_receipt_sha256':sha(OUT/'execution-receipt.json'),
            'table_receipt_sha256':sha(tables/'table-receipt.json')}

if __name__=='__main__':
    print(json.dumps(validate(),indent=2))
