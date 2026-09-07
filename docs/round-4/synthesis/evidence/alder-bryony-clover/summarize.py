"""Read-only comparison of reproduced artifacts and editorial source anchors."""
from pathlib import Path
import hashlib
import json

LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[4]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
receipt = json.loads((LANE / "reproduction.json").read_text(encoding="utf-8"))
changes = []
for name, files in receipt["copied_files_before"].items():
    for rel, before in files.items():
        path = LANE / "runs" / name / rel
        after = sha(path)
        if before == after:
            continue
        original = ROOT / "docs/round-4/ideas" / name / rel
        row = {"report": name, "path": rel, "before_sha256": before,
               "after_sha256": after}
        old_text = original.read_text(encoding="utf-8")
        new_text = path.read_text(encoding="utf-8")
        if old_text == new_text:
            row["classification"] = "newline-only regeneration under Windows"
        elif rel.endswith(".json"):
            old, new = json.loads(old_text), json.loads(new_text)
            keys = sorted(k for k in old.keys() | new.keys() if old.get(k) != new.get(k))
            row["changed_top_level_keys"] = keys
            row["classification"] = ("runtime metadata only" if set(keys) <= {
                "python", "elapsed_seconds", "elapsed_seconds_including_oracles"}
                else "generated JSON difference; exact differing keys retained")
        else:
            row["classification"] = "generated textual difference"
        changes.append(row)
unchanged = all(sha(ROOT / p) == h for p, h in receipt["inputs_before"].items())
assert unchanged

# Entries describe readings, not novelty, scientific independence, or scores.
dimensions = {
    "scoped_evidence": "Same-object evidence and exact scoped/contextual identity",
    "obligation_telescope": "Unfinished work is conditional evidence with dependent order",
    "support_antichain": "Alternative inclusion-minimal sufficient premise families",
    "grounding": "Finite term arena and theorem-instance generation separate from closure",
    "behavioral_composition": "Relational contracts preserve actual intermediate values",
    "observation_adequacy": "Positive transfer, coverage, and realized negative evidence are separate",
    "semantic_binding": "Source correspondence and actual theorem semantics at the final target",
    "method_policy": "Required derivation policy is separate from theorem truth and search hints",
    "conservative_kernel": "Richer authoring discipline first, ordinary Lean kernel conversion",
    "matched_evaluation": "Matched library/service/renderer controls and stopping rules",
}
# tuple: idea, implementation, TeX anchors, code anchors, qualification
readings = {
 "alder": {
  "scoped_evidence": ("explicit", "partial_in_slice", [248, 905, 922], [("companion/alder_core.py",66)], "Opaque atom and assumption identities with lexical restoration are implemented; actual Lean expressions, structures, and typed context migration are proposed."),
  "obligation_telescope": ("explicit", "partial_in_slice", [227, 274, 1003], [("companion/alder_core.py",234)], "The report gives dependent telescope semantics; the parser implements only finite nondependent residual supports and conditional exports."),
  "support_antichain": ("explicit", "implemented_in_slice", [384, 397, 1049], [("companion/alder_core.py",113)], "Executed inclusion-minimal supports in a fixed grounded Horn system; no globally weakest conditions or cost-optimal proofs."),
  "grounding": ("explicit", "proposed_only", [474, 479, 1153], [("companion/alder_core.py",52)], "Typed finite-arena generation is specified; executable inputs already declare ground opaque atoms and rules."),
  "behavioral_composition": ("explicit", "proposed_only", [314, 341, 1140], [], "Pure total-function laws and dependent composition are specified; the frontend has no behavioral Lean elaboration."),
  "observation_adequacy": ("explicit", "partial_in_slice", [724, 762, 812], [("companion/observations.py",31)], "Integer affine frames into abelian groups are justified on paper; finite arithmetic/list-grammar checks are executed, without a Lean source bridge."),
  "semantic_binding": ("explicit", "partial_in_slice", [703, 1012, 1021], [("companion/alder_core.py",179)], "Independent Python proof replay and generic propositional Lean exports are implemented; rule meanings remain explicit theorem assumptions."),
  "method_policy": ("explicit", "proposed_only", [450, 470, 1139], [], "Policy must precede destructive support minimization; a finite derivation-policy automaton is proposed, not implemented."),
  "conservative_kernel": ("explicit", "proposed_only", [939, 960, 984], [], "Recommend Lean elaboration first; primitive refinements and definitional functoriality require separate measured/metatheoretic justification."),
  "matched_evaluation": ("explicit", "partial_in_slice", [1060, 1065, 1105], [], "L0-L4 and renderer controls with stopping rules are specified; only finite Python model telemetry is measured."),
 },
 "bryony": {
  "scoped_evidence": ("explicit", "partial_in_slice", [203, 718, 753], [("prototype/bryony.py",175)], "Certificate replay checks the full exact snapshot, including opaque context/candidate/policy labels; this is not Lean context embedding."),
  "obligation_telescope": ("explicit", "partial_in_slice", [212, 218, 727], [("prototype/bryony.py",170)], "Dependent interpretation is specified, while executable requirements are finite sets of independent proposition names."),
  "support_antichain": ("explicit", "implemented_in_slice", [253, 269, 309], [("prototype/bryony.py",123)], "Paper soundness/termination/relative completeness plus finite differential execution; first proof retained per equal support, no cost optimization."),
  "grounding": ("explicit", "proposed_only", [341, 346, 355], [], "Separate generation and closure budgets/completeness are proposed; executable registry is already ground."),
  "behavioral_composition": ("explicit", "proposed_only", [173, 225, 244], [], "Guarded total functions, refined domains, dependent witness functions and actual-intermediate composition are distinguished in the semantics."),
  "observation_adequacy": ("explicit", "partial_in_slice", [571, 592, 774], [], "Positive abstraction and realized refutation have separate theorems; only tiny opaque observation-consumer and arithmetic fixtures execute."),
  "semantic_binding": ("explicit", "partial_in_slice", [246, 621, 748], [("prototype/bryony.py",227)], "Generic propositional Lean templates retain rule assumptions; actual arithmetic/analysis denotation binding is an unimplemented gate."),
  "method_policy": ("explicit", "partial_in_slice", [736, 741, 755], [("prototype/bryony.py",55)], "Changed policy labels invalidate certificates; a label does not filter rules. Production must prefilter or index supports by policy."),
  "conservative_kernel": ("explicit", "proposed_only", [649, 668, 707], [], "Proof-explicit native refinements are a separate optimization experiment; entailment stays outside conversion."),
  "matched_evaluation": ("explicit", "partial_in_slice", [796, 812, 817], [], "Matched L0-L4/LR controls and stopping thresholds after pilot are proposed; no authoring or real-file index measurements."),
 },
 "clover": {
  "scoped_evidence": ("explicit", "partial_in_slice", [548, 1261, 1278], [("companion/clover_slice.py",392)], "Parser creates fresh binder/assumption identities and lexical scopes; actual dependent Lean context and import changes are not implemented."),
  "obligation_telescope": ("explicit", "partial_in_slice", [699, 733, 828], [("companion/clover_slice.py",328)], "Dependent telescopes are specified; the executable returns unresolved immediate routes and excludes unresolved claims from known facts."),
  "support_antichain": ("partial", "not_implemented", [828, 1164, 1940], [("companion/clover_slice.py",314)], "Explicitly does not promise minimal frontiers: one proof per atom, actual support reported, up to eight immediate routes. This is a different scope from Alder/Bryony."),
  "grounding": ("explicit", "implemented_in_slice", [1080, 1102, 1202], [("companion/clover_slice.py",225)], "Goal-triggered grounding over written/subterm endomorphism syntax is executed; no fresh-term closure or general dependent Lean theorem matching."),
  "behavioral_composition": ("explicit", "partial_in_slice", [620, 645, 1917], [("companion/CloverCore.lean",26)], "Full behavioral composition is proposed; the seven concrete endomorphism laws and generated proofs include injective composition."),
  "observation_adequacy": ("explicit", "partial_in_slice", [1327, 1366, 1473], [("companion/affine_basis.py",1)], "Field-affine coverage and realizers give a paper equivalence; exact finite checks execute without a Leant candidate denotation bridge."),
  "semantic_binding": ("explicit", "partial_in_slice", [1668, 1917, 2025], [("companion/clover_slice.py",460)], "Fixed registry has concrete Lean meanings; source parse/plan/export execute. Review probes expose declaration-name export hygiene gaps; generated-source compilation is separately owned by root."),
  "method_policy": ("explicit", "partial_in_slice", [514, 1947, 2200], [("companion/clover_slice.py",213)], "Allowed rules and required root are checked through the API. Required root is a syntactic policy, not indispensability; reflexive transport can satisfy it."),
  "conservative_kernel": ("explicit", "proposed_only", [1752, 1814, 1878], [], "Ordinary Lean is first implementation; compare library rewriting, proof-producing canonicalization, and kernel conversion on identical workload."),
  "matched_evaluation": ("explicit", "partial_in_slice", [1967, 2093, 2163], [], "211 versus 16 ground instances is an executed model profile comparison, not Lean speed or author benefit; full matched evaluation is proposed."),
 },
}
reports = {}
invalid = []
for name, values in readings.items():
    tex = "docs/round-4/ideas/" + name.capitalize() + "/" + name.capitalize() + ".tex"
    entries = {}
    for key, (idea, implementation, tex_lines, code, qualification) in values.items():
        anchors = [{"path": tex, "line": n} for n in tex_lines]
        anchors.extend({"path": "docs/round-4/ideas/" + name.capitalize() + "/" + p, "line": n} for p, n in code)
        for anchor in anchors:
            lines = (ROOT / anchor["path"]).read_text(encoding="utf-8").splitlines()
            n = anchor["line"]
            if not (0 < n <= len(lines) and lines[n-1].strip()):
                invalid.append(anchor.copy())
            anchor["excerpt"] = lines[n-1].strip()
        entries[key] = {"idea": idea, "implementation": implementation,
                        "anchors": anchors, "qualification": qualification}
    reports[name.capitalize()] = entries
assert not invalid, invalid
crosswalk = {"schema": 1, "input_pin": receipt["pin"],
             "nature": "Editorial source reading: neither novelty scoring nor independent empirical confirmation. Idea and implementation classifications are deliberately separate.",
             "idea_values": ["explicit", "partial", "absent"],
             "implementation_values": ["implemented_in_slice", "partial_in_slice", "proposed_only", "not_implemented"],
             "dimensions": dimensions, "reports": reports}
(LANE / "convergence.json").write_text(json.dumps(crosswalk, indent=2) + "\n", encoding="utf-8")
summary = {"status": "passed", "inputs_unchanged_at_review": unchanged,
           "changed_reproduced_files": changes, "cell_count": sum(map(len, reports.values())),
           "anchors_validated": True,
           "historical_label_caveat": "Copied/generated files retain their authors' no-Lean and kernel_checked:false strings. No program source was edited to change those labels. In particular Alder's no-Lean-executable statement is hard-coded, not current environment detection. The central root-owned Lean receipt governs fresh compilation claims.",
           "runtime_scope": "All source packages preserved. Only Python reference models and exact finite arithmetic rerun. Root separately owns Lean compilation and adversarial export checks."}
(LANE / "review-results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
