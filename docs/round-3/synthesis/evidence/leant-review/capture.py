"""Read immutable Leant blobs. Never read worktree file contents or invoke builds."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = Path("C:/Leant")
PIN = "823259f7e3c6d24e990d3f48f78c4f1c4f88059e"
FILES = ["Verification.hs", "Behavioral.hs", "BehavioralSelection.hs", "Length/Contract.hs", "Length/Adapter.hs", "Length/PostVerification.hs"]

def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, check=True).stdout

def main():
    receipt = ROOT / "source-register.json"
    if receipt.exists():
        data = json.loads(receipt.read_text())
    else:
        data = {"pinned_commit": PIN, "snapshot_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "live_head_at_snapshot": git("rev-parse", "HEAD").decode().strip(),
                "live_status_at_snapshot": git("status", "--short").decode().splitlines(),
                "scope": "Immutable git show blobs only. Live dirty paths are status metadata, not attributed source contents. No builds or service executions.", "files": []}
    for short in sys.argv[1:] or FILES:
        path = "src/Leant/Synth/" + short
        blob = git("show", PIN + ":" + path)
        dst = ROOT / "source" / short
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(blob)
        record = {"source_path": path, "retained_copy": dst.relative_to(ROOT).as_posix(),
                  "git_blob": git("rev-parse", PIN + ":" + path).decode().strip(),
                  "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob), "lines": len(blob.decode().splitlines()),
                  "url": f"https://github.com/VladimirReshetnikov/Leant/blob/{PIN}/{path}"}
        old = next((r for r in data["files"] if r["source_path"] == path), None)
        if old and "read_scope" in old:
            record["read_scope"] = old["read_scope"]
        data["files"] = [r for r in data["files"] if r["source_path"] != path] + [record]
        print(short, record["lines"])
    receipt.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
