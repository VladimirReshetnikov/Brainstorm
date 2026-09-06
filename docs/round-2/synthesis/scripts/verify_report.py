"""Validate source provenance, document structure, build binding, and receipts.

This does not rerun Lean or the nine companions, prove mathematics, or replace
human visual inspection. Without a matching visual-review receipt it fails.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from pypdf import PdfReader
from verify_sources import validate as validate_sources

HERE = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def main():
    provenance = validate_sources()
    build = read(HERE / 'evidence/pdf-build-receipt.json')
    for path, digest in build['tex_inputs'].items():
        require(sha(HERE / path) == digest, f'Changed TeX input: {path}')
    pdf = HERE / 'unified-report.pdf'
    require(sha(pdf) == build['pdf_sha256'], 'PDF differs from build receipt')
    require(build['passes'] == 3, 'Three strict passes not recorded')
    log = (HERE / 'evidence/pdf-build-log.txt').read_text(encoding='utf-8', errors='replace')
    require(not re.search(r'Overfull|Missing character|undefined|Rerun to get|Label\(s\) may have changed|destination with the same identifier', log),
            'Final build log has unresolved output')
    require('Output written on ' in log, 'Build log has no completed PDF')
    tex = (HERE / 'unified-report.tex').read_text(encoding='utf-8')
    labels = re.findall(r'\\label\{([^}]+)\}', tex)
    require(len(labels) == len(set(labels)), 'Duplicate source label')
    refs = re.findall(r'\\(?:ref|pageref)\{([^}]+)\}', tex)
    require(set(refs) <= set(labels), 'Undefined source reference')
    bib = set(re.findall(r'\\bibitem\{([^}]+)\}', tex))
    cites = re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}', tex)
    require({key for group in cites for key in group.split(',')} <= bib, 'Missing bibliography entry')
    for target in re.findall(r'\\href\{([^}]+)\}', tex):
        if not target.startswith(('http:', 'https:')):
            require((HERE / target).is_file(), f'Broken local PDF link: {target}')
    reader = PdfReader(pdf)
    texts = [page.extract_text() or '' for page in reader.pages]
    text = re.sub(r'\s+', ' ', '\n'.join(texts))
    for phrase in ['Executive assessment', 'A common semantic model',
                   'A general residual-to-jet theorem', 'Questions for the next discussion',
                   'Earlier questions, restated and carried forward', 'Lean 4.32.0']:
        require(phrase in text, f'Expected PDF content missing: {phrase}')
    require(all(len(t.strip()) > 70 for t in texts), 'Unexpected nearly blank page')
    require('\ufffd' not in text, 'Replacement character in extracted PDF text')
    crosswalk = (HERE / 'crosswalk-table.tex').read_text(encoding='utf-8')
    require(len(re.findall(r'\\textbf\{[ROGVDLPE]\}', crosswalk)) == 72, 'Appendix table is incomplete')
    lean = read(HERE / 'evidence/lean/receipt.json')
    require(lean['exit_code'] == 0, 'Lean receipt does not show success')
    require(sha(HERE / 'evidence/lean/FocusedChecks.lean') == lean['source_sha256'].lower(), 'Lean source changed')
    require(sha(HERE / 'evidence/lean/FocusedChecks.log') == lean['log_sha256'].lower(), 'Lean output changed')
    lean_log = (HERE / 'evidence/lean/FocusedChecks.log').read_text(encoding='utf-8-sig')
    require(lean_log.count('depends on axioms:') == 8, 'Missing focused Lean axiom audits')
    for axioms in re.findall(r'depends on axioms: \[([^\]]*)\]', lean_log):
        require(set(axioms.split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}, 'Unexpected Lean axiom')
    math = read(HERE / 'evidence/math/synthesis-math-results.json')
    require(len(math['groups']) == 6 and all(g['status'] == 'passed' for g in math['groups']), 'Math sanity receipt failed')
    visual = read(HERE / 'evidence/visual-review.json')
    require(visual['pdf_sha256'] == sha(pdf), 'Visual review is for another PDF')
    require(visual['pages_reviewed'] == list(range(1, len(reader.pages) + 1)), 'Visual review does not cover all pages')
    require(visual['status'] == 'passed', 'Visual review not passed')
    artifacts = {}
    for path in sorted((HERE / 'evidence').rglob('*')):
        if path.is_file():
            artifacts[path.relative_to(HERE).as_posix()] = sha(path)
    result = {
        'status': 'passed', 'validated_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Document structure, pinned input sources, source/PDF build binding, visual-review receipt binding, and retained execution-receipt consistency. No generic mathematical proof or language implementation certified.',
        'source_validation': provenance, 'pdf_pages': len(reader.pages),
        'tex_inputs': build['tex_inputs'], 'pdf_sha256': sha(pdf),
        'pdf_passes': 3, 'all_pages_visually_reviewed': True,
        'focused_lean_declarations': 8, 'additional_finite_math_groups': 6,
        'nine_companion_reruns': 'See lane receipts and README; counts have different units and are not combined.',
        'evidence_sha256': artifacts,
    }
    (HERE / 'validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in {'source_validation', 'evidence_sha256'}}, indent=2))

if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        print(f'Report validation FAILED: {exc}', file=sys.stderr)
        sys.exit(1)
