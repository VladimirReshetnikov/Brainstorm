"""Reproduce three reviewed companions in isolated copies; never mutate inputs."""
from pathlib import Path
import hashlib
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
NAMES = ("karst", "moraine", "obsidian")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory():
    return {p.relative_to(ROOT).as_posix(): digest(p)
            for name in NAMES for p in sorted((ROOT / "docs/round-3/ideas" / name).rglob("*"))
            if p.is_file()}


def main():
    before = inventory()
    for name, sha in before.items():
        blob = subprocess.run(["git", "show", f"{PIN}:{name}"], cwd=ROOT,
                              check=True, capture_output=True).stdout
        assert hashlib.sha256(blob).hexdigest() == sha, name
    results = []
    tasks = [
        ("karst", ("evidence/companion.py",), ["companion.py"], "evidence/results.json"),
        ("moraine", ("companion/length_contracts.py", "companion/test_length_contracts.py"),
         ["-m", "unittest", "-v", "test_length_contracts.py"], None),
        ("obsidian", ("experiments/checks.py",), ["checks.py"], "experiments/results.json"),
    ]
    for name, files, args, historical in tasks:
        destination = HERE / "runs" / name
        destination.mkdir(parents=True, exist_ok=True)
        copies = []
        for file in files:
            src = ROOT / "docs/round-3/ideas" / name / file
            dst = destination / src.name
            shutil.copyfile(src, dst)
            assert digest(src) == digest(dst)
            copies.append({"source": src.relative_to(ROOT).as_posix(),
                           "copy": dst.relative_to(HERE).as_posix(), "sha256": digest(src)})
        cmd = [sys.executable, "-B", *args]
        started = time.monotonic()
        run = subprocess.run(cmd, cwd=destination, capture_output=True, timeout=120)
        elapsed = time.monotonic() - started
        (destination / "stdout.txt").write_bytes(run.stdout)
        (destination / "stderr.txt").write_bytes(run.stderr)
        result = {"report": name, "command": cmd, "cwd": destination.relative_to(ROOT).as_posix(),
                  "exit_code": run.returncode, "elapsed_seconds": round(elapsed, 6), "copied_sources": copies,
                  "stdout_sha256": digest(destination / "stdout.txt"),
                  "stderr_sha256": digest(destination / "stderr.txt")}
        assert run.returncode == 0, result
        if historical:
            current = json.loads(run.stdout)
            old = json.loads((ROOT / "docs/round-3/ideas" / name / historical).read_text())
            result["parsed_result_matches_historical"] = current == old
            assert current == old
            if name == "karst":
                result["groups"] = [{"name": g["name"], "cases": g["cases"]} for g in current["groups"]]
                assert json.loads((destination / "results.json").read_text()) == current
            else:
                result["test_count"] = current["test_count"]
                result["counts_by_kind"] = current["counts_by_kind"]
        else:
            text = run.stderr.decode().replace("\r\n", "\n")
            result["tests"] = int(re.search(r"Ran (\d+) tests", text).group(1))
            result["passed_named_tests"] = re.findall(r"^(test_\w+).* \.\.\. ok$", text, re.M)
            old = (ROOT / "docs/round-3/ideas/moraine/companion/test-results.txt").read_text()
            result["named_passes_match_historical"] = result["passed_named_tests"] == re.findall(r"^(test_\w+).* \.\.\. ok$", old, re.M)
            assert result["tests"] == 32 and result["named_passes_match_historical"] and text.rstrip().endswith("OK")
        results.append(result)
    assert inventory() == before, "Input changed during reproduction"
    receipt = {"pinned_source_commit": PIN, "python_version": sys.version,
               "platform": platform.platform(), "input_files": before, "input_files_unchanged": True,
               "source_bytes_match_pin": True, "runs": results,
               "limits": "Fresh Python reproduction only; no Lean execution, frontend verification, performance comparison, or foreign repository build."}
    (HERE / "reproduction.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"input_files": len(before), "all_inputs_unchanged": True,
                      "runs": [{k: v for k, v in r.items() if k in ("report", "exit_code", "elapsed_seconds", "test_count", "tests", "groups", "counts_by_kind", "parsed_result_matches_historical", "named_passes_match_historical")} for r in results]}, indent=2))


if __name__ == "__main__":
    main()
