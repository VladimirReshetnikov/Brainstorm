"""Check convergence locators against the read-only report/code inputs."""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
data = json.loads((here / 'laneconvergence.json').read_text())
records = []
for name, dimensions in data['reports'].items():
    for dimension, cell in dimensions.items():
        for anchor in cell['anchors']:
            relative, line = anchor.rsplit(':', 1)
            lines = (root / relative).read_text(encoding='utf-8').splitlines()
            number = int(line)
            text = lines[number - 1] if 0 < number <= len(lines) else None
            records.append({'report': name, 'dimension': dimension, 'anchor': anchor,
                            'source_line': text, 'valid_nonblank': bool(text and text.strip())})
(here / 'convergence-anchor-check.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
bad = [r for r in records if not r['valid_nonblank']]
print(json.dumps({'anchors': len(records), 'invalid_or_blank': bad}, indent=2))
assert not bad
