"""Record the completed editorial read scope; this is not a product test."""
from pathlib import Path
import json

path = Path(__file__).resolve().parent / "source-register.json"
data = json.loads(path.read_text(encoding="utf-8"))
for record in data["files"]:
    record["read_scope"] = {"kind": "full", "line_start": 1, "line_end": record["lines"],
                            "method": "Static reading of the retained immutable git-show bytes; no execution."}
data["commands"] = [
    "python -B docs/round-3/synthesis/evidence/leant-review/capture.py",
    "python -B docs/round-3/synthesis/evidence/leant-review/capture.py BehavioralSelection/Internal.hs Length/PostVerification/Internal.hs Length/Handoff.hs",
    "python -B docs/round-3/synthesis/evidence/leant-review/capture-djex.py",
    "python -B docs/round-3/synthesis/evidence/leant-review/annotate-scope.py"
]
data["scope_notes"] = [
    "Six requested Leant modules and three direct implementation dependencies were read in full.",
    "The imported Djex product-contract API was checked only in the two ranges registered separately in djex-register.json, at the parent commit's immutable gitlink.",
    "The Djex historical report docs/reports/2026-08-14-finite-binary-product-spine-length-foundation.md was also read for navigation. Its historical integration-status statements were not used as current implementation evidence.",
    "No source contents from the live worktree were read. Git status and HEAD were captured as independently timestamped metadata. No Haskell, Lean, Lake, solver, synthesis, or tactic-suggestion execution occurred."
]
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
