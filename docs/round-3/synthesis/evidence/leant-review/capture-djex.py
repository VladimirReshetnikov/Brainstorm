"""Retain bounded excerpts of the immutable submodule API imported by Leant."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
PARENT_PIN = "823259f7e3c6d24e990d3f48f78c4f1c4f88059e"
PIN = "22da13fd69ce54dd1e47db9faba28eb2869629d1"
SOURCE = "synthesis/internal/Language/Haskell/Synthesis/Internal/Semantic/Length.hs"
RANGES = [(321, 390), (1341, 1480)]


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout


def main():
    gitlink = git("C:/Leant", "ls-tree", PARENT_PIN, "lib/Djex").decode().strip()
    assert gitlink.split()[1:3] == ["commit", PIN], gitlink
    blob = git("C:/Leant/lib/Djex", "show", PIN + ":" + SOURCE)
    lines = blob.decode().splitlines()
    excerpt = "\n\n".join("\n".join(f"{i}: {lines[i-1]}" for i in range(a, b+1)) for a, b in RANGES) + "\n"
    target = ROOT / "djex-length-excerpts.txt"
    target.write_text(excerpt, encoding="utf-8")
    record = {"parent_pin": PARENT_PIN, "parent_gitlink": gitlink, "pinned_commit": PIN,
              "source_path": SOURCE, "git_blob": git("C:/Leant/lib/Djex", "rev-parse", PIN + ":" + SOURCE).decode().strip(),
              "full_blob_sha256": hashlib.sha256(blob).hexdigest(), "full_blob_bytes": len(blob), "full_blob_lines": len(lines),
              "read_scope": "Only the two recorded source ranges were reviewed, not the complete implementation.",
              "ranges": RANGES, "retained_excerpt": target.name,
              "excerpt_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
              "url": f"https://github.com/VladimirReshetnikov/Djex/blob/{PIN}/{SOURCE}"}
    (ROOT / "djex-register.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
