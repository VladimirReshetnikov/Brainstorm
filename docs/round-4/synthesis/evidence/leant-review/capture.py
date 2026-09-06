"""Read immutable Leant Git objects; write review evidence only in Brainstorm."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OLD = ROOT / 'docs/round-3/synthesis/evidence/leant-review'
REPO = Path('C:/Leant')
PIN = '823259f7e3c6d24e990d3f48f78c4f1c4f88059e'

def git(*args, repo=REPO):
    result = subprocess.run(['git', *args], cwd=repo, capture_output=True, check=True, timeout=60)
    return result.stdout

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    previous = json.loads((OLD / 'source-register.json').read_text())
    records = []
    for item in previous['files']:
        path = item['source_path']
        blob = git('show', PIN + ':' + path)
        retained = OLD / item['retained_copy']
        assert blob == retained.read_bytes()
        assert sha(blob) == item['sha256']
        records.append({'source_path': path, 'git_blob': git('rev-parse', PIN + ':' + path).decode().strip(),
                        'sha256': sha(blob), 'bytes': len(blob), 'lines': len(blob.decode().splitlines()),
                        'retained_copy': retained.relative_to(ROOT).as_posix(),
                        'prior_copy_freshly_byte_reverified': True,
                        'read_scope_this_pass': 'Hash reverified only; exact fresh read ranges annotated after review.'})
    path = 'src/Main.hs'
    blob = git('show', PIN + ':' + path)
    ranges = [[4050, 4300], [4930, 4990], [5130, 5290]]
    lines = blob.decode().splitlines()
    excerpt = '\n\n'.join('\n'.join(f'{i}: {lines[i-1]}' for i in range(a, b+1)) for a, b in ranges) + '\n'
    destination = HERE / 'main-excerpts.txt'
    destination.write_text(excerpt, encoding='utf-8')
    records.append({'source_path': path, 'git_blob': git('rev-parse', PIN + ':' + path).decode().strip(),
                    'sha256': sha(blob), 'bytes': len(blob), 'lines': len(lines), 'retained_excerpt': destination.name,
                    'excerpt_sha256': sha(destination.read_bytes()), 'read_scope_this_pass': {'ranges': ranges, 'kind': 'selected ranges only'}})
    old_djex = json.loads((OLD / 'djex-register.json').read_text())
    gitlink = git('ls-tree', PIN, 'lib/Djex').decode().strip()
    assert gitlink == old_djex['parent_gitlink']
    djex_repo = REPO / 'lib/Djex'
    djex_blob = git('show', old_djex['pinned_commit'] + ':' + old_djex['source_path'], repo=djex_repo)
    assert sha(djex_blob) == old_djex['full_blob_sha256']
    assert sha((OLD / old_djex['retained_excerpt']).read_bytes()) == old_djex['excerpt_sha256']
    output = {'pinned_commit': PIN, 'snapshot_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'live_head_at_snapshot': git('rev-parse', 'HEAD').decode().strip(),
              'live_status_at_snapshot': git('status', '--short').decode().splitlines(),
              'scope': 'Immutable git-show source only; live HEAD/status are metadata. No dirty source reads, builds, service execution, or external writes.',
              'commands': ['git show <pin>:<registered path>', 'git rev-parse <pin>:<registered path>', 'git rev-parse HEAD', 'git status --short', 'git ls-tree <pin> lib/Djex'],
              'capture_script_sha256': sha(Path(__file__).read_bytes()), 'files': records,
              'djex': dict(old_djex, parent_gitlink_freshly_reverified=gitlink,
                           full_blob_freshly_reverified=True, excerpt_freshly_hash_reverified=True,
                           retained_excerpt=(OLD / old_djex['retained_excerpt']).relative_to(ROOT).as_posix()),
              'validation': {'all_nine_prior_source_copies_match_pinned_git_show_bytes': True}}
    (HERE / 'source-register.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'sources': len(records), 'live_head': output['live_head_at_snapshot'], 'live_status': output['live_status_at_snapshot'], 'prior_copies_match': True}, indent=2))

if __name__ == '__main__':
    main()
