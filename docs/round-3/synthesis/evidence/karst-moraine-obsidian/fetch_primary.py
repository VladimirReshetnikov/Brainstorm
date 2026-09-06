"""Retain the pinned primary source used to check Moraine's tensor assumptions."""
from pathlib import Path
import hashlib
import json
import urllib.request

base = Path(__file__).resolve().parent
url = "https://raw.githubusercontent.com/anthropics/fermats-last-theorem/aa2d8b34692b16c70f699536de0d8e75b9a3e9ef/P2M/Sol/S_Algebra_exists_algHom_equiv_pi.lean"
data = urllib.request.urlopen(url, timeout=30).read()
target = base / "primary" / "S_Algebra_exists_algHom_equiv_pi.lean"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(data)
assert b"[\xe2\x88\x80 i, Module.Finite A (H i)] [\xe2\x88\x80 i, Module.Free A (H i)]" in data
record = {"url": url, "retrieved_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
          "sha256": hashlib.sha256(data).hexdigest(),
          "git_blob_sha1": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
          "source_lines": len(data.decode().splitlines()),
          "critical_line": next(i for i, line in enumerate(data.decode().splitlines(), 1) if "[∀ i, Module.Finite" in line),
          "status": "Pinned primary source retrieved and read; not compiled or repository-audited."}
(base / "primary" / "receipt.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, indent=2))
