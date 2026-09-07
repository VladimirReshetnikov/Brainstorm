"""Focused semantic probes against isolated original copies; no Lean execution."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, HERE / "copies" / relative)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value

def main():
    rowan = module("lane_rowan", "Rowan/rowan_model.py")
    sorrel = module("lane_sorrel", "Sorrel/sorrel_model.py")
    laurel = module("lane_laurel", "Laurel/prototype/laurel_core.py")
    atom = lambda name: rowan.Atom(name, ())
    a, b, goal = map(atom, ("A", "B", "Goal"))
    rules = (rowan.GroundRule("unseeded", (a,), a),
             rowan.GroundRule("finish", (a, b), goal))
    ctx = rowan.Context("demo", (), ())
    first = rowan.solve(rowan.Request(ctx, goal), rules)
    supplemented = rowan.Context("demo", (), tuple(rowan.Assumption(f"h{i}", item)
                                                  for i, item in enumerate(first.frontier)))
    second = rowan.solve(rowan.Request(supplemented, goal), rules)
    assert first.frontier == (b,) and second.status == "open"
    records = [{"id": "rowan-cycle-plus-leaf-frontier",
                "rules": ["A -> A", "A & B -> Goal"],
                "known": [], "reported_frontier": [x.text() for x in first.frontier],
                "after_assuming_entire_reported_frontier": second.status,
                "remaining_frontier": [x.text() for x in second.frontier],
                "conclusion": "The explanatory frontier is not necessarily a sufficient residual contract; derived-proof checking remains intact."}]
    problem = sorrel.parse("""context Selection
atom A B C Goal
assumption A B C
available B C
rule short: A -> Goal
rule ready: B & C -> Goal
goal Goal
""")
    result = sorrel.solve(problem)
    view = sorrel.report(problem, result)
    chosen = sorrel.ordered_sets(result.labels[problem.goal])[0]
    proof = result.labels[problem.goal][chosen]
    exported = sorrel.export_lean(problem, proof)
    (HERE / "SorrelSelectionProbe.lean").write_text(exported, encoding="utf-8")
    assert view["status"] == "supported_in_model"
    assert view["residual_frontier"] == [[]]
    assert {x.name for x in chosen} == {"A"}
    records.append({"id": "sorrel-export-selection-vs-available-route",
                    "available": ["B", "C"], "result": view,
                    "cli_selected_support": sorted(x.name for x in chosen),
                    "selected_residual": sorted(x.name for x in chosen - problem.available),
                    "conclusion": "CLI chooses the smallest total support, even when another route is already available; export is still a valid conditional theorem, not a false closed proof."})
    atoms = ("A", "B", "Goal")
    lp = laurel.Profile("CycleLeaf", atoms, frozenset(), frozenset({"B"}),
                        (laurel.Rule("cycle", ("A",), "A"), laurel.Rule("finish", ("A", "B"), "Goal")))
    lr = laurel.infer(lp)
    assert lr.complete and not lr.frontiers["Goal"]
    records.append({"id": "laurel-rejects-insufficient-offer-under-cycle",
                    "result": laurel.summary(lp, lr, "Goal"),
                    "conclusion": "No offered subset is falsely returned as a sufficient route."})
    # Budgeted antichains need not be globally inclusion-minimal: the B route
    # appears before the known A -> Goal route that eventually removes it.
    bp = laurel.Profile("Budget", atoms, frozenset({"A"}), frozenset({"B"}),
                        (laurel.Rule("offered", ("B",), "Goal"), laurel.Rule("known", ("A",), "Goal")))
    partial = laurel.infer(bp, 1)
    complete = laurel.infer(bp)
    assert not partial.complete and set(partial.frontiers["Goal"]) == {frozenset({"B"})}
    assert set(complete.frontiers["Goal"]) == {frozenset()}
    laurel.check_proof(bp, partial.frontiers["Goal"][frozenset({"B"})], "Goal", frozenset({"B"}))
    records.append({"id": "partial-minimality-is-relative-to-discovered-routes",
                    "partial": laurel.summary(bp, partial, "Goal"),
                    "complete": laurel.summary(bp, complete, "Goal"),
                    "conclusion": "The partial conditional proof is sound while its support is dominated by a later route; the report correctly qualifies this."})
    output = {"scope": "Fresh Python semantic probes; no Lean compilation, frontend implementation, or source-registry truth established.",
              "probes": records}
    (HERE / "semantic-probes.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
