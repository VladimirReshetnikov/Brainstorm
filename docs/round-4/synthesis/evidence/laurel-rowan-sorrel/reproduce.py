"""Isolated, bytecode-disabled reproduction of three round-4 Python packages.

The author source directories are read-only. This runner copies their complete
packages, runs only inspected Python programs in those copies, and records
exact arguments, standard streams, source/result hashes, and input immutability.
It invokes no Lean, Lake, TeX, Git, network, or external repository command.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
IDEAS = ROOT / "docs/round-4/ideas"
NAMES = ("Laurel", "Rowan", "Sorrel")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(directory):
    return {p.relative_to(directory).as_posix(): sha(p)
            for p in sorted(directory.rglob("*")) if p.is_file()}

def main():
    original = {name: inventory(IDEAS / name) for name in NAMES}
    copied = {}
    for name in NAMES:
        destination = HERE / "copies" / name
        if destination.exists():
            raise SystemExit(f"Refusing to overwrite existing reproduction copy: {destination}")
        shutil.copytree(IDEAS / name, destination)
        copied[name] = inventory(destination)
        assert copied[name] == original[name]
    jobs = [
        ("laurel-tests", "Laurel/prototype", ["test_core.py"]),
        ("laurel-width", "Laurel/prototype", ["bench_frontier.py"]),
        *[(f"laurel-{name}", "Laurel/prototype", ["laurel_core.py", f"examples/{name}.laurel", "--json", f"generated/{name}.json", "--lean", f"generated/{name}.lean"])
          for name in ("quotient", "frey_a4", "alternatives", "cycle")],
        ("laurel-budget-zero", "Laurel/prototype", ["laurel_core.py", "examples/quotient.laurel", "--budget", "0"]),
        ("rowan-demo", "Rowan", ["rowan_model.py"]),
        ("rowan-tests", "Rowan", ["test_rowan.py"]),
        ("sorrel-tests", "Sorrel", ["sorrel_model.py", "--test", "--json", "test_results.json"]),
        ("sorrel-quotient", "Sorrel", ["sorrel_model.py", "examples/quotient.sorrel", "--json", "examples/quotient_result.json", "--export-lean", "SelectedPlan.lean"]),
        ("sorrel-cauchy", "Sorrel", ["sorrel_model.py", "examples/cauchy.sorrel", "--json", "examples/cauchy_result.json"]),
    ]
    receipts = []
    (HERE / "logs").mkdir(exist_ok=True)
    for label, relative_cwd, args in jobs:
        cwd = HERE / "copies" / relative_cwd
        command = [sys.executable, "-B", *args]
        started = time.time()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
        outcome = subprocess.run(command, cwd=cwd, env=env, capture_output=True, timeout=180)
        stdout = HERE / "logs" / f"{label}.stdout.txt"
        stderr = HERE / "logs" / f"{label}.stderr.txt"
        stdout.write_bytes(outcome.stdout)
        stderr.write_bytes(outcome.stderr)
        receipts.append({"label": label, "command": command,
                         "cwd": str(cwd), "exit_code": outcome.returncode,
                         "elapsed_seconds": round(time.time() - started, 6),
                         "stdout": stdout.relative_to(HERE).as_posix(),
                         "stdout_sha256": sha(stdout),
                         "stderr": stderr.relative_to(HERE).as_posix(),
                         "stderr_sha256": sha(stderr)})
        print(f"{label}: exit {outcome.returncode}", flush=True)
    final_original = {name: inventory(IDEAS / name) for name in NAMES}
    outputs = {name: inventory(HERE / "copies" / name) for name in NAMES}
    unchanged = original == final_original
    no_bytecode = not any((HERE / "copies").rglob("*.pyc"))
    receipt = {
        "input_pin": "58ced1ce667b3ba1ed162a0c6280959536c8bc5f",
        "scope": "Fresh Python execution only; no Lean/Lake/PDF/Git or external-repository mutations.",
        "python": sys.version, "runner_sha256": sha(Path(__file__)),
        "input_sha256_before": original, "copied_sha256_before": copied,
        "runs": receipts, "output_sha256": outputs,
        "input_sha256_after": final_original,
        "all_inputs_unchanged": unchanged, "no_bytecode": no_bytecode,
    }
    (HERE / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    assert unchanged and no_bytecode
    assert all(r["exit_code"] == 0 for r in receipts)

if __name__ == "__main__":
    main()
