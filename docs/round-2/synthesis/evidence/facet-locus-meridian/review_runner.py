"""Read-only companion reruns for the Facet/Locus/Meridian synthesis review.

All generated files stay beside this script. No Lean, PDF, or Git mutation.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
PACKAGES = {
    "facet": ("facet", "facet.tex", "math_checks.py", "math-check-results.json"),
    "locus": ("Locus_Proof_Language_Proposal", "locus.tex", "certificate_demo.py", "test-results.json"),
    "meridian": ("meridian", "meridian.tex", "check_examples.py", "example_checks.json"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    record = {
        "review_time_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "executable": sys.executable,
        "workspace_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "scope": "Finite exact-arithmetic Python reruns only; no Lean, Leant, PDF build, or language implementation validation.",
        "runs": {},
    }
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for name, (directory, tex, script, shipped_result) in PACKAGES.items():
        source = ROOT / "docs/round-2/ideas" / directory
        before = {p.name: digest(p) for p in sorted(source.iterdir()) if p.is_file()}
        receipt = OUT / f"{name}-results.json"
        command = [sys.executable, "-B", str(source / script)]
        if name != "facet":
            command += ["--json", str(receipt)]
        run = subprocess.run(command, cwd=OUT, env=env, text=True,
                             capture_output=True, timeout=60, check=False)
        (OUT / f"{name}-stdout.txt").write_text(run.stdout, encoding="utf-8")
        (OUT / f"{name}-stderr.txt").write_text(run.stderr, encoding="utf-8")
        if name == "facet":
            receipt.write_text(run.stdout, encoding="utf-8")
        after = {p.name: digest(p) for p in sorted(source.iterdir()) if p.is_file()}
        sections, section, subsection, appendix = [], 0, 0, False
        for line_number, line in enumerate((source / tex).read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith(r"\appendix"):
                appendix, section, subsection = True, 0, 0
            match = re.match(r"\\(section|subsection)\{(.*)\}", line)
            if match:
                if match[1] == "section":
                    section, subsection = section + 1, 0
                else:
                    subsection += 1
                number = chr(64 + section) if appendix else str(section)
                if match[1] == "subsection":
                    number += f".{subsection}"
                sections.append({"number": number, "line": line_number, "heading": match[2]})
        (OUT / f"{name}-sections.json").write_text(json.dumps(sections, indent=2) + "\n", encoding="utf-8")
        rerun = json.loads(receipt.read_text(encoding="utf-8"))
        shipped = json.loads((source / shipped_result).read_text(encoding="utf-8"))
        comparable = {key: rerun.get(key) == shipped.get(key) for key in (
            ("total_checks", "checks_by_family") if name == "facet" else
            ("tests_run", "failures", "errors", "jet_mod_q6", "cubic_bracket_48") if name == "locus" else
            ("passed", "total", "tests", "lambert_polynomials_lowest_coefficient_first")
        )}
        record["runs"][name] = {
            "command": command, "cwd": str(OUT), "exit_code": run.returncode,
            "source_files_unchanged": before == after, "source_sha256": before,
            "shipped_receipt_agreement": comparable,
            "missing_readme_artifacts": [p for p in ("SHA256SUMS", "SHA256SUMS.txt")
                                         if f"`{p}`" in (source / "README.md").read_text(encoding="utf-8")
                                         and not (source / p).exists()],
        }
        if run.returncode or before != after or not all(comparable.values()):
            raise RuntimeError(f"Review check failed: {name}")
        print(f"{name}: exit 0; receipt agrees; original files unchanged")
    (OUT / "review-receipt.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
