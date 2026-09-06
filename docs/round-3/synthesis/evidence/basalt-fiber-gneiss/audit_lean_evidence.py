"""Read-only cross-check of the root-owned Lean receipts, not a Lean run."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
SYNTHESIS = HERE.parents[1]
ROOT = HERE.parents[4]
LEAN = SYNTHESIS / "evidence/lean"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


receipt = json.loads((LEAN / "receipt.json").read_text())
results = []
for case in receipt["cases"]:
    original = ROOT / case["source"]
    copy = SYNTHESIS / case["copied_source"]
    assert digest(original) == digest(copy) == case["source_sha256"]
    assert digest(SYNTHESIS / case["log"]) == case["log_sha256"]
    assert case["exit_code"] == 0 and case["audit"]["exit_code"] == 0
    audit = case["audit"]
    assert digest(SYNTHESIS / audit["source"]) == audit["source_sha256"]
    assert digest(SYNTHESIS / audit["log"]) == audit["log_sha256"]
    names = re.findall(r"^theorem\s+(\S+)", original.read_text(encoding="utf-8"), re.M)
    log = (SYNTHESIS / audit["log"]).read_text(encoding="utf-8")
    axioms = {}
    for name, dependencies in re.findall(r"^'([^']+)' (does not depend on any axioms|depends on axioms:.*)$", log, re.M):
        dependencies = dependencies.strip()
        if name in axioms:
            assert axioms[name] == dependencies
        axioms[name] = dependencies
    results.append({"proposal": case["proposal"], "source": case["source"],
                    "named_theorem_declarations": names,
                    "named_theorem_count": len(names),
                    "audited_unique_declarations": axioms})

synthesis_receipt = json.loads((LEAN / "synthesis-receipt.json").read_text())
assert digest(LEAN / "SynthesisChecks.lean") == synthesis_receipt["source_sha256"]
assert digest(LEAN / "SynthesisChecks.log") == synthesis_receipt["log_sha256"]
assert synthesis_receipt["exit_code"] == 0
output = {"scope": "Independent read-only source/log hash and count audit; no Lean execution in this lane.",
          "version": receipt["version"], "results": results,
          "original_named_theorems": sum(r["named_theorem_count"] for r in results),
          "unique_audited_original_declarations": sum(len(r["audited_unique_declarations"]) for r in results),
          "additional_synthesis_theorems": 2}
(HERE / "lean-evidence-review.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in output.items() if k != "results"}, indent=2))
for item in results:
    print(item["proposal"], item["named_theorem_count"], len(item["audited_unique_declarations"]))
