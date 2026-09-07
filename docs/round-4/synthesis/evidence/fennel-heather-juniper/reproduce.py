"""Read-only input capture and isolated reproduction of three round-four packages.

Product code was inspected before execution. No Lean/Lake/LaTeX or network call
is made. Original files are never written; all runtime paths stay in this lane.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[4]
PIN = "58ced1ce667b3ba1ed162a0c6280959536c8bc5f"
NAMES = ("fennel", "heather", "juniper")
RUNTIME_SUFFIXES = {".py", ".fnl", ".hthr", ".jnp"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory():
    return {p.relative_to(ROOT).as_posix(): sha(p) for name in NAMES
            for p in sorted((ROOT / f"docs/round-4/ideas/{name.title()}").rglob("*")) if p.is_file()}


def git(*args, data=None):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], input=data)


def main():
    before = inventory()
    tree = {}
    for line in git("ls-tree", "-r", PIN, "--", *[f"docs/round-4/ideas/{n.title()}" for n in NAMES]).decode().splitlines():
        meta, relative = line.split("\t", 1)
        tree[relative] = meta.split()[2]
    assert set(tree) == set(before)
    ids = list(dict.fromkeys(tree.values()))
    batch = git("cat-file", "--batch", data=("\n".join(ids)+"\n").encode())
    offset, canonical = 0, {}
    for blob in ids:
        end = batch.index(b"\n", offset)
        header = batch[offset:end].decode().split()
        assert header[:2] == [blob, "blob"]
        size = int(header[2])
        raw = batch[end+1:end+1+size]
        canonical[blob] = hashlib.sha256(raw).hexdigest()
        offset = end+size+2
    assert offset == len(batch)
    assert all(canonical[tree[p]] == h for p, h in before.items())
    receipt = {"pin": PIN, "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "python_executable": sys.executable, "python_version": platform.python_version(),
               "input_hashes_before": before, "input_git_blobs": tree,
               "input_bytes_match_pin": True, "scripts_read_before_execution": True,
               "adaptations": ["Runtime copies only; original scripts are byte-identical.",
                 "-B and PYTHONDONTWRITEBYTECODE=1 prevent bytecode writes.",
                 "PYTHONUTF8=1 and PYTHONIOENCODING=utf-8 make Windows text output explicit.",
                 "Each documented working directory is reproduced inside this evidence lane; no source edits.",
                 "Initial capture stopped before copies or executions because lowercase Windows paths did not match case-sensitive Git paths; corrected harness uses canonical title-case input names."],
               "copied_sources": [], "runs": []}
    for name in NAMES:
        source = ROOT / f"docs/round-4/ideas/{name.title()}"
        destination = LANE / "runs" / name
        destination.mkdir(parents=True, exist_ok=True)
        if name == "fennel":
            (destination / "evidence").mkdir(exist_ok=True)
        for path in sorted(source.rglob("*")):
            if path.is_file() and path.suffix in RUNTIME_SUFFIXES:
                target = destination / path.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())
                receipt["copied_sources"].append({"source": path.relative_to(ROOT).as_posix(),
                    "copy": target.relative_to(LANE).as_posix(), "sha256": sha(target)})
    specs = [
        ("fennel", "demo", "", ["prototype/fennel.py", "prototype/quotients.fnl", "--out", "prototype/generated"]),
        ("fennel", "tests", "", ["prototype/test_fennel.py"]),
        ("fennel", "stress", "", ["prototype/stress_frontiers.py"]),
        ("heather", "tests", "companion", ["test_heather.py"]),
        ("heather", "use-site", "companion", ["use_site_demo.py"]),
        *[("heather", "demo-"+name, "companion", ["heather.py", "examples/"+name+".hthr", "--output", "generated"])
          for name in ("diagonal", "empty", "free", "even", "refuted")],
        ("juniper", "tests", "companion", ["test_frontier.py"]),
        ("juniper", "inverse", "companion", ["inverse_polynomials.py"]),
        ("juniper", "demo", "companion", ["juniper_frontier.py", "example.jnp", "--json", "example-result.json", "--lean", "Generated.lean"]),
        ("juniper", "capped", "companion", ["juniper_frontier.py", "example.jnp", "--max-attempts", "2"]),
    ]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        for name, label, suffix, arguments in specs:
            cwd = LANE / "runs" / name / suffix
            command = [sys.executable, "-B", *arguments]
            started = time.perf_counter()
            result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, timeout=180)
            logs = LANE / "logs" / name
            logs.mkdir(parents=True, exist_ok=True)
            streams = {}
            for stream in ("stdout", "stderr"):
                path = logs / f"{label}.{stream}.txt"
                path.write_bytes(getattr(result, stream))
                streams[stream] = {"path": path.relative_to(LANE).as_posix(), "sha256": sha(path)}
            receipt["runs"].append({"report": name, "label": label, "cwd": cwd.relative_to(ROOT).as_posix(),
                "command": command, "exit_code": result.returncode, "seconds": time.perf_counter()-started,
                "timeout_seconds": 180, "logs": streams})
            print(name, label, result.returncode, flush=True)
            assert result.returncode == 0, result.stderr.decode("utf-8")
    finally:
        after = inventory()
        receipt["input_hashes_after"] = after
        receipt["inputs_unchanged"] = after == before
        receipt["runtime_artifacts"] = {p.relative_to(LANE).as_posix(): sha(p)
            for p in sorted((LANE / "runs").rglob("*")) if p.is_file() and p.suffix not in RUNTIME_SUFFIXES}
        receipt["bytecode_files"] = [p.relative_to(LANE).as_posix() for p in (LANE / "runs").rglob("*.pyc")]
        (LANE / "reproduction.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
        assert receipt["inputs_unchanged"] and not receipt["bytecode_files"]


if __name__ == "__main__":
    main()
