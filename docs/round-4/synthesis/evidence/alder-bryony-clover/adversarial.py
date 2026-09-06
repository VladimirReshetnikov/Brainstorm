"""Review probes, run only against the preserved isolated Clover copy.

No Lean execution. Accepted symbolic plans plus exported text test the export
boundary; a separate root-owned Lean run determines compilability.
"""
from pathlib import Path
import dataclasses
import hashlib
import importlib.util
import json
import os
import sys

LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[4]
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
module_path = LANE / "runs/clover/companion/clover_slice.py"
spec = importlib.util.spec_from_file_location("review_clover", module_path)
c = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = c
spec.loader.exec_module(c)

cases = {
    "KeywordClaim": "fix f : End\nclaim theorem : same f f\n",
    "ShadowCompose": "fix f : End\nclaim compose : same f f\nclaim composed : same (f . f) (f . f)\n",
    "ShadowRule": "fix f g r : End\nassume retract : left_inverse r f\nassume outer : injective g\nclaim inj_comp : same f f\nclaim composite : injective (g . f)\n",
}
out = LANE / "adversarial"
out.mkdir(exist_ok=True)
results = []
for name, source in cases.items():
    source_path = out / (name + ".clover")
    source_path.write_text(source, encoding="utf-8")
    claims = c.elaborate(source)
    statuses = [claim.result.status for claim in claims]
    assert all(status == "plan_checked" for status in statuses)
    generated = c.export_document(claims)
    lean_path = out / (name + ".lean")
    lean_path.write_text(generated, encoding="utf-8")
    results.append({"name": name, "source": source_path.relative_to(LANE).as_posix(),
                    "generated": lean_path.relative_to(LANE).as_posix(),
                    "statuses": statuses,
                    "scope": "Python plan accepted and Lean source exported; Lean execution owned separately by root."})

# Root-rule fidelity is a declared syntactic policy, not method indispensability.
claim = c.elaborate("fix f : End\nassume already : injective f\nclaim goal : injective f\n")[0]
req = dataclasses.replace(claim.request, required_root="inj_transport")
result = c.solve(req)
assert result.status == "plan_checked"
assert result.plan.proof.name == "inj_transport"
assert result.support == ["already_2"]
nodes = c.proof_order(result.plan.proof)
results.append({"name": "RequiredTransportMayBeIdentity",
                "status": result.status, "root": result.plan.proof.name,
                "support": result.support,
                "nodes": [{"kind": p.kind, "name": p.name, "conclusion": str(p.conclusion)} for p in nodes],
                "scope": "A demanded transport root is satisfied using reflexive same f f and the goal as an existing assumption. This meets the stated root policy, but does not establish the method was indispensable."})

receipt_path = LANE / "reproduction.json"
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
unchanged = all(sha(ROOT / path) == digest for path, digest in receipt["inputs_before"].items())
assert unchanged
report = {
    "status": "passed", "python": sys.version, "command": [sys.executable, "-B", str(Path(__file__).resolve())],
    "module": module_path.relative_to(LANE).as_posix(), "module_sha256": sha(module_path),
    "inputs_unchanged": unchanged, "results": results,
    "artifacts": {p.relative_to(LANE).as_posix(): sha(p) for p in sorted(out.iterdir()) if p.is_file()},
    "scope": "Review-authored adversarial inputs with unmodified imported parser/exporter. No Lean compilation, source edits, or behavioral integration."
}
(LANE / "adversarial.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
