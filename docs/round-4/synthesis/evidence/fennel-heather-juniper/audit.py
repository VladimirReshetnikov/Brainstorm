"""Bounded independent lane probes; reads only original proposal inputs.

Uses already captured byte-identical runtime copies. No Lean/build/Git mutation.
All writes stay under this script's directory. Run: python -B audit.py
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os
import platform
import random
import subprocess
import sys

sys.dont_write_bytecode = True
LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[4]
OUT = LANE / "adversarial"
VOLATILE = {"python", "platform", "elapsed_seconds", "elapsed_seconds_single_run", "seconds_single_run"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, relative):
    path = LANE / "runs" / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def normalized(value):
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items() if k not in VOLATILE}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value


def refuse(call):
    try:
        call()
    except ValueError as exc:
        return str(exc)
    raise AssertionError("Expected refusal")


def main():
    receipt = json.loads((LANE / "reproduction.json").read_text())
    before = {p: sha(ROOT / p) for p in receipt["input_hashes_before"]}
    assert before == receipt["input_hashes_before"]
    for source in receipt["copied_sources"]:
        assert sha(LANE / source["copy"]) == source["sha256"]
    OUT.mkdir(exist_ok=True)
    f = load("fennel_lane_audit", "fennel/prototype/fennel.py")
    h = load("heather_lane_audit", "heather/companion/heather.py")
    j = load("juniper_lane_audit", "juniper/companion/juniper_frontier.py")
    result = {"pin": receipt["pin"], "scope": "bounded Python and artifact checks, no Lean execution",
              "command": [sys.executable, "-B", str(Path(__file__).resolve())],
              "python_version": platform.python_version(), "harness_sha256": sha(Path(__file__)),
              "seed": 2026090604, "comparisons": [], "probes": {}, "subprocesses": []}

    # Compare freshly emitted artifacts to author artifacts without confusing
    # a Windows newline difference with a changed theorem or certificate.
    for name in ("fennel", "heather", "juniper"):
        base = LANE / "runs" / name
        for fresh in sorted(base.rglob("*")):
            old = ROOT / "docs/round-4/ideas" / name.title() / fresh.relative_to(base)
            if fresh.is_file() and old.is_file() and fresh.suffix in {".json", ".lean"}:
                a, b = old.read_bytes(), fresh.read_bytes()
                mode = "JSON excluding explicitly listed runtime metadata" if fresh.suffix == ".json" else "UTF-8 text with CRLF normalized to LF only"
                equivalent = (normalized(json.loads(a)) == normalized(json.loads(b)) if fresh.suffix == ".json"
                              else a.decode("utf-8").replace("\r\n", "\n") == b.decode("utf-8").replace("\r\n", "\n"))
                result["comparisons"].append({"source": old.relative_to(ROOT).as_posix(),
                    "fresh": fresh.relative_to(LANE).as_posix(), "source_sha256": sha(old),
                    "fresh_sha256": sha(fresh), "byte_identical": a == b,
                    "comparison_mode": mode, "equivalent": equivalent})
                assert equivalent, str(fresh)
    result["ignored_JSON_runtime_keys"] = sorted(VOLATILE)

    # Directly compare the two separately authored algorithms on a shared
    # fragment. This is finite agreement, not proof or global equivalence.
    rng = random.Random(result["seed"])
    profiles, frontiers, route_checks = [], 0, 0
    atoms = tuple(f"A{i}" for i in range(6))
    for index in range(128):
        known = tuple(rng.sample(atoms, rng.randrange(3)))
        candidates = [a for a in atoms if a not in known]
        offers = tuple(rng.sample(candidates, rng.randrange(min(3, len(candidates))+1)))
        rules = tuple(j.Rule(f"r{i}", tuple(rng.choice(atoms) for _ in range(rng.randrange(4))), rng.choice(atoms))
                      for i in range(rng.randrange(11)))
        jp = j.Profile(f"Profile{index}", atoms, known, offers, rules, (atoms[-1],))
        jr = j.solve(jp, max_attempts=100000)
        j.check(jp, jr)
        fq = f.Query("target", atoms[-1])
        fp = f.Program(jp.name, atoms,
            tuple(f.Root("k"+a, a, False) for a in known)+tuple(f.Root("h"+a, a, True) for a in offers),
            tuple(f.Rule(r.name, r.premises, r.conclusion) for r in rules), (fq,))
        fr = f.plan(fp, fq, max_attempts=100000, max_nodes=10000)
        assert fr.complete and jr.complete
        for atom in atoms:
            actual = {frozenset(name[1:] for name in s) for s in fr.labels[atom]}
            assert actual == set(jr.frontier[atom])
            frontiers += 1
        for _, node in fr.routes():
            f.check(fp, fq, f.certificate(fr, node))
            route_checks += 1
        profiles.append({"name": jp.name, "known": known, "offers": offers,
                         "rules": [[r.name, r.premises, r.conclusion] for r in rules],
                         "frontiers": {a: sorted([sorted(s) for s in jr.frontier[a]]) for a in atoms}})
    (OUT / "cross-profiles.json").write_text(json.dumps(profiles, indent=2)+"\n", encoding="utf-8")
    result["probes"]["cross_implementation"] = {"profiles": 128, "atom_frontiers_compared": frontiers,
        "selected_Fennel_routes_checked": route_checks, "Juniper_results_checked": 128,
        "domain": "6 atoms; 0-2 known; 0-3 distinct offered atoms disjoint from known; 0-10 rules; 0-3 ordered premises, repetitions/cycles allowed",
        "limits": "100000 attempts and 10000 Fennel nodes; all completed; only one named Fennel pending root per offered atom"}

    # A deliberate language-model difference: proof-root provenance versus
    # offered propositions. This is not disagreement on the shared fragment.
    dup = f.parse("module Duplicate\natom P G\nask first : P\nask second : P\nrule go : P -> G\nshow target : G\n")
    dupplan = f.plan(dup, dup.queries[0])
    assert {s for s, _ in dupplan.routes()} == {frozenset({"first"}), frozenset({"second"})}
    result["probes"]["named_root_boundary"] = {"Fennel_supports": [sorted(s) for s, _ in dupplan.routes()],
        "Juniper_duplicate_offer_refusal": refuse(lambda: j.parse("profile Duplicate\natoms P G\noffer P P\nrule go: P -> G\nneed G\n"))}

    jp = j.parse("profile Coverage\natoms P Q G\noffer P Q\nrule left: P -> G\nrule right: Q -> G\nneed G\n")
    jr = j.solve(jp)
    omitted = copy.deepcopy(jr)
    del omitted.frontier["G"][frozenset({"Q"})]
    missing = refuse(lambda: j.check(jp, omitted))
    omitted.complete = False
    j.check(jp, omitted)
    truncated = j.solve(jp, max_attempts=1)
    j.check(jp, truncated)
    truncated.complete = True
    forged = refuse(lambda: j.check(jp, truncated))
    result["probes"]["coverage_boundary"] = {"omitted_complete_route": missing,
        "same_sound_subset_when_declared_incomplete": "accepted", "forged_truncation_complete": forged,
        "Fennel_limit": "Per-route checker has no complete-family input or coverage theorem; no whole-frontier completeness acceptance API to forge."}

    # Actual admitted input guards are part of both the request and the export.
    source = "heather guardprobe\ndomain diagonal\ninputs xs, ys\nclaim length(append(xs, ys)) == length(append(ys, ys))\n"
    diagonal = h.parse(source)
    free = h.parse(source.replace("domain diagonal", "domain free"))
    dc, fc = h.certificate(diagonal), h.certificate(free)
    assert dc["status"] == "model_proved" and fc["status"] == "counterexample"
    assert h.check_certificate(diagonal, dc) and h.check_certificate(free, fc)
    assert not h.check_certificate(free, dc)
    evensource = "heather evenprobe\ndomain even\ninputs xs\nclaim length(nil()) == length(xs)\n"
    er = h.parse(evensource)
    ec = h.certificate(er)
    assert tuple(ec["witness_lengths"]) == (2,) and h.check_certificate(er, ec)
    bad = copy.deepcopy(ec)
    bad["witness_lengths"], bad["witness_lists"] = (1,), ((0,),)
    assert not h.check_certificate(er, bad)
    result["probes"]["admissible_domains"] = {"diagonal_status": dc["status"], "free_status": fc["status"],
        "free_counterexample_lengths": fc["witness_lengths"], "cross_domain_receipt_rejected": True,
        "even_negative_lengths": ec["witness_lengths"], "odd_length_negative_rejected": True,
        "empty_singleton_refused": refuse(lambda: h.parse("heather bad\ndomain empty\ninputs xs\nclaim length(one()) == length(xs)\n"))}
    for name, req in (("diagonal", diagonal), ("free", free), ("even", er)):
        (OUT / f"{name}-certificate.json").write_text(json.dumps(h.certificate(req), indent=2)+"\n", encoding="utf-8")
    (OUT / "diagonal.lean").write_text(h.lean_export(diagonal, dc), encoding="utf-8")

    # Both domains span Q^k. Verify the implementation's same acceptance for
    # a fixed finite collection; the mathematical reason is stated in the memo.
    exprs = ["xs", "ys", "nil()", "one()", "reverse(xs)", "append(xs, ys)", "append(xs, xs)"]
    pairs = 0
    for left in exprs:
        for right in exprs:
            text = f"heather hull\ndomain free\ninputs xs, ys\nclaim length({left}) == length({right})\n"
            statuses = [h.certificate(h.parse(text.replace("domain free", "domain "+d)))["status"] for d in ("free", "even")]
            assert statuses[0] == statuses[1]
            pairs += 1
    result["probes"]["same_affine_hull"] = {"free_even_expression_pairs": pairs,
        "equality_acceptance_matches": True, "limit": "Finite implementation check; same rational affine hull is the paper argument, not a theorem proved by these samples."}

    # Reused output folders must not be treated as publication manifests:
    # fresh negative JSON can coexist with a previous positive .lean file.
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    for report, stages in {
        "fennel": ["module Stale\natom P G\ngiven hp : P\nrule go : P -> G\nshow target : G\n",
                   "module Stale\natom P G\ngiven hp : P\nshow target : G\n"],
        "heather": ["heather same\ndomain empty\ninputs xs\nclaim length(nil()) == length(xs)\n",
                    "heather same\ndomain free\ninputs xs\nclaim length(nil()) == length(xs)\n"]}.items():
        folder = OUT / (report+"-reuse")
        folder.mkdir(exist_ok=True)
        script = LANE / "runs" / report / ("prototype/fennel.py" if report == "fennel" else "companion/heather.py")
        captured = []
        for stage, content in enumerate(stages):
            inputpath = folder / f"stage{stage}.source"
            inputpath.write_text(content, encoding="utf-8")
            command = [sys.executable, "-B", str(script), str(inputpath), "--out" if report == "fennel" else "--output", str(folder / "output")]
            proc = subprocess.run(command, cwd=folder, env=env, capture_output=True, timeout=30)
            assert proc.returncode == 0
            for stream in ("stdout", "stderr"):
                (folder / f"stage{stage}.{stream}.txt").write_bytes(getattr(proc, stream))
            captured.append({"stage": stage, "stdout": proc.stdout.decode("utf-8").strip(),
                             "lean_hashes": {p.name: sha(p) for p in (folder / "output").glob("*.lean")}})
            result["subprocesses"].append({"command": command, "cwd": folder.relative_to(LANE).as_posix(), "exit_code": 0, "timeout_seconds": 30})
        assert captured[0]["lean_hashes"] and captured[0]["lean_hashes"] == captured[1]["lean_hashes"]
        result["probes"][report+"_stale_output"] = {"stages": captured,
            "interpretation": "Old positive Lean source remains beside fresh negative/no-route metadata; no source proof is accepted by this probe. Publication must use a fresh output directory or a checked request-bound manifest."}

    after = {p: sha(ROOT / p) for p in before}
    assert after == before
    result["source_file_count"] = len(before)
    result["inputs_unchanged"] = True
    result["bytecode_files"] = [p.relative_to(LANE).as_posix() for p in LANE.rglob("*.pyc")]
    assert not result["bytecode_files"]
    result["probe_artifacts"] = {p.relative_to(LANE).as_posix(): sha(p) for p in sorted(OUT.rglob("*")) if p.is_file()}
    (LANE / "audit.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"compared_artifacts": len(result["comparisons"]), "probes": result["probes"],
                      "input_files_unchanged": len(before)}, indent=2))


if __name__ == "__main__":
    main()
