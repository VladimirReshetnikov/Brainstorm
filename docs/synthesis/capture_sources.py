"""Capture the explicitly reviewed source set without writing to reference repos.

Run deliberately to refresh provenance. PDF builds do not refresh this snapshot.
The archive contains sources only, not dependencies or executable build artifacts.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True, encoding='utf-8').strip()


def record(repo, name):
    data = (repo / name).read_bytes()
    result = {'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
              'lines': len(data.splitlines())}
    tracked = subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', f'HEAD:{name}'], capture_output=True).returncode == 0
    if tracked:
        old = subprocess.check_output(['git', '-C', str(repo), 'show', f'HEAD:{name}'])
        # Track both exact bytes and newline-normalized equality for Windows source files.
        result.update(head_blob=git(repo, 'rev-parse', f'HEAD:{name}'),
                      matches_head_ignoring_crlf=data.replace(b'\r\n', b'\n') == old.replace(b'\r\n', b'\n'))
    else:
        result['matches_head_ignoring_crlf'] = False
        result['untracked_at_capture'] = True
    return result, data


def main():
    leant = Path('C:/Leant')
    proveit = Path('C:/ProveIt')
    selected = [
        'LICENSE', 'README.md', 'leant.cabal',
        'src/Main.hs', 'src/Leant/Backend.hs', 'src/Leant/Synth/Engine.hs',
        'src/Leant/Synth/Fragment.hs', 'src/Leant/Synth/Verification.hs',
        'src/Leant/Synth/Replay.hs', 'src/Leant/Synth/Behavioral.hs',
        'src/Leant/Synth/PostVerification.hs',
        'src/Leant/Synth/Length/Selection/Generic.hs', 'src/Leant/Synth/Length/Integration.hs',
        'docs/candidate-quality.md', 'docs/length-ranking.md', 'docs/behavioral-synthesis.md',
        'test/prove-suggest.txt', 'test/prove-suggest.golden', 'test/run-tests.sh',
        'test/synth-basic.txt', 'test/synth-basic.golden',
        'test/synth-behavior.txt', 'test/synth-behavior.golden', 'test-unit/Spec.hs',
    ]
    reports = []
    for p in sorted((ROOT / 'docs/ideas').rglob('*.tex')):
        rec, _ = record(ROOT, p.relative_to(ROOT).as_posix())
        reports.append(rec)
    files = []
    archive = HERE / 'evidence/leant-reviewed-source.zip'
    archive.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in selected:
            rec, data = record(leant, name)
            files.append(rec)
            info = zipfile.ZipInfo(name, (2026, 9, 6, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    psources = []
    for name in [
        'Analysis/FabiusFunction/Lean/FabiusFunction/BinomialInversion.lean',
        'Analysis/FabiusFunction/Lean/FabiusFunction/AutonomousIteratedDeriv.lean',
        'NumberTheory/IntegerSums/Lean/IntegerSums/FloorSqrtSum.lean',
    ]:
        rec, _ = record(proveit, name)
        assert rec['matches_head_ignoring_crlf'], f'ProveIt source drift: {name}'
        psources.append(rec)
    cached = Path('C:/Users/vresh/AppData/Local/Python/pythoncore-3.14-64/Lib/site-packages/lean_interact/cache/augustepoiroux/repl/repl_v1.3.18_lean-toolchain-v4.32.0')
    protocol = []
    protocol_archive = HERE / 'evidence/repl-protocol-source.zip'
    with zipfile.ZipFile(protocol_archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in ['LICENSE', 'REPL/Main.lean', 'REPL/JSON.lean', 'REPL/Snapshots.lean']:
            data = (cached / name).read_bytes()
            protocol.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
            info = zipfile.ZipInfo(name, (2026, 9, 6, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    reg = {
        'scope': 'Source inspection only; no Lean or Leant build/test/replay receipts. Original reports read without mutation.',
        'review_date_pacific': '2026-09-05',
        'brainstorm_corpus_commit': 'ddbc1d4', 'reports': reports,
        'leant': {'path': str(leant), 'head': git(leant, 'rev-parse', 'HEAD'),
                  'status_at_capture': git(leant, '--no-optional-locks', 'status', '--short'),
                  'djex_gitlink': git(leant, 'rev-parse', 'HEAD:lib/Djex'),
                  'djex_checked_out': git(leant / 'lib/Djex', 'rev-parse', 'HEAD'),
                  'archive': archive.relative_to(HERE).as_posix(), 'files': files},
        'proveit': {'path': str(proveit), 'head': git(proveit, 'rev-parse', 'HEAD'), 'files': psources},
        'protocol': {'path': str(cached), 'scope': 'Available cached source, not a verified active Leant backend binary',
                     'archive': protocol_archive.relative_to(HERE).as_posix(), 'files': protocol},
        'crosswalk': json.loads((HERE / 'convergence.json').read_text(encoding='utf-8')),
        'external_documentation': [
            'https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/',
            'https://lean-lang.org/doc/reference/latest/ValidatingProofs/',
            'https://isabelle.in.tum.de/dist/library/Doc/Prog_Prove/Isar.html',
        ],
    }
    (HERE / 'source-register.json').write_text(json.dumps(reg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Captured {len(reports)} reports, {len(files)} Leant files, and {len(psources)} unchanged ProveIt sources.')


if __name__ == '__main__':
    main()
