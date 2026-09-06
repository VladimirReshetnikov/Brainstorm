"""Reproduce three read-only source companions in this evidence directory.

Run from any directory using Python 3.10+ with -B. No Lean, Lake, TeX, network,
or writes in docs/round-3/ideas are used. Original scripts were inspected before
execution; they use only the Python standard library.
"""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import platform
import re
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PIN = "58bb54219f494b29310ff77384732129411da887"
REPORTS = ("schist", "tephra", "trellis")
SCRIPTS = {
    "schist": "check_examples.py",
    "tephra": "tephra_checks.py",
    "trellis": "companions/trellis_reference.py",
}


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def snapshot():
    return {p.relative_to(ROOT).as_posix(): digest(p)
            for report in REPORTS
            for p in sorted((ROOT / "docs/round-3/ideas" / report).rglob("*"))
            if p.is_file()}


def main():
    before = snapshot()
    runs = []
    for report in REPORTS:
        original = ROOT / "docs/round-3/ideas" / report / SCRIPTS[report]
        out = HERE / report
        out.mkdir(parents=True, exist_ok=True)
        copied = out / original.name
        shutil.copyfile(original, copied)
        command = [sys.executable, "-B", copied.name]
        if report == "trellis":
            command.extend(["--output", "results.json"])
        start = time.perf_counter()
        proc = subprocess.run(command, cwd=out, capture_output=True, timeout=60)
        elapsed = time.perf_counter() - start
        (out / "stdout.txt").write_bytes(proc.stdout)
        (out / "stderr.txt").write_bytes(proc.stderr)
        audit = (proc.stdout + proc.stderr).decode("utf-8", errors="replace")
        count = int(re.search(r"(?:Ran (\d+) tests|(\d+) tests passed)", audit).group(1 if report != "trellis" else 2))
        entry = {
            "report": report,
            "command": command,
            "working_directory": out.relative_to(ROOT).as_posix(),
            "exit_code": proc.returncode,
            "seconds": elapsed,
            "tests": count,
            "source": original.relative_to(ROOT).as_posix(),
            "source_sha256": digest(original),
            "copied_source_sha256": digest(copied),
            "artifacts": {p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file()},
        }
        if report == "trellis":
            fresh = json.loads((out / "results.json").read_text())
            old = json.loads((original.parent / "results.json").read_text())
            entry["result_json_equal"] = fresh == old
        elif report == "tephra":
            fresh = json.loads((out / "check_results.json").read_text())
            old = json.loads((original.parent / "check_results.json").read_text())
            entry["result_json_equal_except_python_version"] = {
                k: v for k, v in fresh.items() if k != "python"
            } == {k: v for k, v in old.items() if k != "python"}
        runs.append(entry)
        if proc.returncode != 0 or count != {"schist": 10, "tephra": 23, "trellis": 31}[report]:
            raise RuntimeError(f"Unexpected result: {entry}")
    after = snapshot()
    if before != after:
        raise RuntimeError("Source inputs changed")
    receipt = {
        "pin": PIN,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "scope": "Fresh finite companion reruns only; no Lean, frontend, repository build, or productivity validation.",
        "scripts_inspected_before_execution": True,
        "sources_unchanged": before == after,
        "source_hashes_before_and_after": before,
        "runs": runs,
    }
    (HERE / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tests": {r["report"]: r["tests"] for r in runs},
                      "source_files_unchanged": len(before), "python": platform.python_version()}))


if __name__ == "__main__":
    main()
