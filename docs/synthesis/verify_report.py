"""Validate document references, evidence integrity, and extracted PDF content.

This is artifact validation, not proof verification or a substitute for visual QA.
Requires pypdf. Does not read or write C:\\Leant or C:\\ProveIt.
"""
from pathlib import Path
import hashlib
import json
import re
import zipfile
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def main():
    src = (HERE / 'unified-report.tex').read_text(encoding='utf-8')
    keys = re.findall(r'\\bibitem\{([^}]+)\}', src)
    assert len(keys) == len(set(keys)), 'Duplicate bibliography keys'
    for group in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}', src):
        assert set(group.split(',')) <= set(keys), f'Undefined citation: {group}'
    labels = re.findall(r'\\label\{([^}]+)\}', src)
    assert len(labels) == len(set(labels)), 'Duplicate labels'
    assert set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', src)) <= set(labels)
    for target in re.findall(r'\\source\{([^}]+)\}', src):
        if not target.startswith('https://'):
            assert (HERE / target).is_file(), f'Missing local reference: {target}'

    register = json.loads((HERE / 'source-register.json').read_text(encoding='utf-8'))
    crosswalk = json.loads((HERE / 'convergence.json').read_text(encoding='utf-8'))
    assert crosswalk == register['crosswalk'], 'Crosswalk/register drift'
    assert len(register['reports']) == 9
    for item in register['reports']:
        data = (ROOT / item['path']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    for row in crosswalk['reports']:
        lines = (ROOT / row['path']).read_text(encoding='utf-8').splitlines()
        assert set(crosswalk['features']) <= set(row)
        for feature in crosswalk['features']:
            for start, end in row[feature]['lines']:
                assert 1 <= start <= end <= len(lines)
                assert any(line.strip() for line in lines[start-1:end])
    evidence_count = 0
    for section in ['leant', 'protocol']:
        group = register[section]
        with zipfile.ZipFile(HERE / group['archive']) as z:
            assert z.testzip() is None
            assert set(z.namelist()) == {x['path'] for x in group['files']}
            for item in group['files']:
                data = z.read(item['path'])
                assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
                evidence_count += 1

    secondary = json.loads((HERE / 'secondary-source-register.json').read_text(encoding='utf-8'))
    secondary_count = 0
    for group in secondary['sources']:
        archive = HERE / group['archive']
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == group['archive_sha256']
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert set(z.namelist()) == {x['path'] for x in group['files']}
            for item in group['files']:
                data = z.read(item['path'])
                assert len(data) == item['bytes'], item['path']
                assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
                blob = f'blob {len(data)}\0'.encode() + data
                assert hashlib.sha1(blob).hexdigest() == item['git_blob'], item['path']
                secondary_count += 1

    pdf = HERE / 'unified-report.pdf'
    receipt = json.loads((HERE / '.build/build-receipt.json').read_text(encoding='utf-8-sig'))
    assert receipt['tex_sha256'] == hashlib.sha256((HERE / 'unified-report.tex').read_bytes()).hexdigest(), 'TeX changed since the last successful build'
    assert receipt['pdf_sha256'] == hashlib.sha256(pdf.read_bytes()).hexdigest(), 'PDF changed since the last successful build'
    assert receipt['passes'] == 3
    reader = PdfReader(pdf)
    pages = [p.extract_text() or '' for p in reader.pages]
    assert len(pages) >= 20
    assert all(len(text.strip()) > 350 for text in pages), 'Empty or nearly empty page'
    text = '\n'.join(pages)
    assert '\ufffd' not in text, 'Replacement glyph in PDF extraction'
    searchable_text = re.sub(r'\s+', ' ', text)
    for word in ['Contour', 'Loom', 'MathStep', 'Mosaic', 'Motive', 'Outline', 'Reason', 'Spine', 'Leant', 'proofStatus', 'X says Y', 'autoImplicit false', 'semantic notice', '90,637']:
        assert word in searchable_text, f'Missing expected topic: {word}'
    log = (HERE / '.build/unified-report.log').read_text(encoding='utf-8', errors='replace')
    assert not re.search(r'Overfull|Missing character|undefined|Rerun to get|Label\(s\) may have changed', log)
    result = {
        'kind': 'document_and_source_integrity_checks',
        'pages': len(pages), 'bibliography_entries': len(keys),
        'input_reports': 9, 'convergence_evidence_cells': 54,
        'archived_reference_files': evidence_count,
        'supplementary_archived_files': secondary_count,
        'secondary_review_revision': secondary['sources'][0]['revision'],
        'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
        'tex_sha256': hashlib.sha256(src.encode('utf-8')).hexdigest(),
        'result': 'passed',
        'source_pdf_build_receipt': 'matched',
        'limitations': 'Does not validate mathematical proofs, language implementation, Leant runtime behavior, or visual layout. Visual QA is recorded separately.'
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
