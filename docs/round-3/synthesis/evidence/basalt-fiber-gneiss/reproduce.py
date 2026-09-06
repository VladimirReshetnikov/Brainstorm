"""Reproduce the three reviewed Python companions without changing inputs."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
INPUT = ROOT / "docs/round-3/ideas"
PIN = "58bb54219f494b29310ff77384732129411da887"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def inventory() -> dict:
    return {p.relative_to(ROOT).as_posix(): digest(p)
            for name in ("basalt", "fiber", "gneiss")
            for p in sorted((INPUT / name).rglob("*")) if p.is_file()}


def main() -> None:
    before = inventory()
    runs = []
    for name, source, receipt in (
        ("basalt", "companions/certificate_demo.py", "companions/test_results.json"),
        ("fiber", "tools/check_examples.py", "evidence/checks.json"),
        ("gneiss", "contract_model.py", "test_results.json"),
    ):
        original = INPUT / name / source
        destination = HERE / "runs" / name / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, destination)
        assert digest(original) == digest(destination)
        command = [sys.executable, "-B", str(destination)]
        started = datetime.now(timezone.utc).isoformat()
        clock = time.perf_counter()
        completed = subprocess.run(command, cwd=HERE / "runs" / name,
                                   capture_output=True, timeout=90)
        elapsed = time.perf_counter() - clock
        run_dir = HERE / "runs" / name
        (run_dir / "stdout.txt").write_bytes(completed.stdout)
        (run_dir / "stderr.txt").write_bytes(completed.stderr)
        generated = run_dir / receipt
        result = json.loads(generated.read_text(encoding="utf-8"))
        runs.append({"report": name, "command": command,
                     "cwd": str(run_dir), "started_utc": started,
                     "elapsed_seconds": elapsed, "exit_code": completed.returncode,
                     "source": original.relative_to(ROOT).as_posix(),
                     "source_sha256": digest(original),
                     "copied_source_sha256": digest(destination),
                     "receipt": generated.relative_to(HERE).as_posix(),
                     "receipt_sha256": digest(generated), "result": result,
                     "stdout_sha256": digest(run_dir / "stdout.txt"),
                     "stderr_sha256": digest(run_dir / "stderr.txt")})
        assert completed.returncode == 0 and result["status"] == "passed"
    after = inventory()
    assert before == after, "Source package changed during reproduction"
    receipt = {"input_pin": PIN, "python": sys.version,
               "source_files": before, "source_files_unchanged": before == after,
               "runs": runs,
               "scope": "Fresh finite Python execution only. Not Lean compilation,"
                        " universal implementation verification, or an integrated frontend test."}
    (HERE / "reproduction.json").write_text(json.dumps(receipt, indent=2) + "\n",
                                             encoding="utf-8")
    print(json.dumps({"unchanged_input_files": len(before),
                      "runs": [{"report": r["report"], "exit_code": r["exit_code"],
                                "result": r["result"]} for r in runs]}, indent=2))


if __name__ == "__main__":
    main()
