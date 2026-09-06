"""Validate retained Python evidence without executing any experiment.

validate() is read-only. The CLI writes only evidence/python-validation.json,
and only when --write-summary is supplied. No subprocesses or proposal imports.
Git-object provenance and all Lean/PDF checks belong to separate validators.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
EVIDENCE = HERE / "evidence"
PIN = "58ced1ce667b3ba1ed162a0c6280959536c8bc5f"
RUNTIME = {".py", ".alder", ".bry", ".clover", ".fnl", ".hthr", ".jnp", ".laurel", ".sorrel"}
VOLATILE = {"python", "platform", "elapsed_seconds", "elapsed_seconds_single_run", "seconds_single_run"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    need(path.is_file(), f"Missing retained file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def relative(base, value):
    """Accept a receipt-relative path only inside its declared directory."""
    need(isinstance(value, str), "Expected string path")
    path = (base / value.replace("\\", "/")).resolve()
    need(path.is_relative_to(base.resolve()), f"Path leaves declared root: {value}")
    return path


def recorded_path(value):
    """Relocate a historical absolute workspace path without accessing it."""
    value = value.replace("\\", "/")
    marker = "docs/round-4/synthesis/"
    position = value.find(marker)
    need(position >= 0, f"Not a synthesis workspace path: {value}")
    return relative(ROOT, value[position:])


def checked_hash(path, expected):
    need(isinstance(expected, str) and len(expected) == 64, f"Malformed SHA256 for {path}")
    need(sha(path) == expected, f"Changed retained file: {path}")


def check_map(base, mapping, exact=False):
    need(isinstance(mapping, dict), f"Expected hash map under {base}")
    paths = set()
    for name, expected in mapping.items():
        path = relative(base, name)
        need(path not in paths, f"Duplicate resolved path: {path}")
        paths.add(path)
        checked_hash(path, expected)
    if exact:
        actual = {p.resolve() for p in base.rglob("*") if p.is_file()}
        need(paths == actual, f"Retained inventory changed under {base}: {paths ^ actual}")
    return len(paths)


def normalized(value):
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items() if k not in VOLATILE}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value


def flatten(packages, prefix):
    return {f"{prefix}/{name}/{path}": digest
            for name, files in packages.items() for path, digest in files.items()}


def source_key(value):
    return value.replace("\\", "/").casefold()


def registry():
    data = read(HERE / "source-register.json")
    need(data["input_commit"] == PIN, "Source-register pin changed")
    rows = [r for r in data["files"] if r["role"] == "round4-primary-input"]
    need(len(rows) == 159, "Expected 159 primary inputs")
    index = {source_key(r["path"]): r for r in rows}
    need(len(index) == len(rows), "Case-colliding source-register entries")
    for item in rows:
        checked_hash(relative(ROOT, item["path"]), item["sha256"])
        need((ROOT / item["path"]).stat().st_size == item["bytes"], f"Input size changed: {item['path']}")
    return index


def input_scope(index, names, captured):
    expected = {key: row["sha256"] for key, row in index.items()
                if row["path"].split("/")[3].casefold() in names}
    actual = {source_key(path): digest for path, digest in captured.items()}
    need(len(actual) == len(captured) and actual == expected, f"Input scope/hash mismatch for {names}")
    return len(expected)


def copies(index, lane, names, before, copy_prefix):
    """Check every initial copy against the register; source code stays exact.

    Generated outputs may change after execution and are validated separately
    against their post-run hash inventory. The before inventory cannot omit a
    Python program or source-language fixture from any covered package.
    """
    count = 0
    for name in names:
        files = before[name]
        package = name.casefold()
        expected_runtime = {row["path"].split("/", 4)[4]: row["sha256"]
                            for row in index.values()
                            if row["path"].split("/")[3].casefold() == package
                            and Path(row["path"]).suffix in RUNTIME}
        copied_runtime = {path: digest for path, digest in files.items() if Path(path).suffix in RUNTIME}
        need(copied_runtime == expected_runtime, f"Missing/changed copied source inventory for {name}")
        copyroot = relative(lane, f"{copy_prefix}/{name}")
        for path, digest in files.items():
            key = source_key(f"docs/round-4/ideas/{name}/{path}")
            need(key in index and index[key]["sha256"] == digest, f"Initial copy differs from source register: {key}")
            if Path(path).suffix in RUNTIME:
                checked_hash(relative(copyroot, path), digest)
                count += 1
        actual_runtime = {p.relative_to(copyroot).as_posix() for p in copyroot.rglob("*")
                          if p.is_file() and p.suffix in RUNTIME}
        need(actual_runtime == set(expected_runtime), f"Unexpected or missing runtime source for {name}")
    return count


def command(run, lane, expected_cwd, args, exit_code, nested_logs=False):
    cmd = run["command"]
    need(len(cmd) >= 3 and Path(cmd[0].replace("\\", "/")).name.casefold().startswith("python"), "Not a Python command")
    need(cmd[1:] == ["-B", *args], f"Unexpected retained command: {cmd}")
    cwd = recorded_path(run["cwd"])
    need(cwd == relative(lane, expected_cwd), f"Command working directory mismatch: {run['cwd']}")
    need(type(run["exit_code"]) is int and run["exit_code"] == exit_code, f"Unexpected command outcome: {cmd}")
    if "expected_exit_code" in run:
        need(run["expected_exit_code"] == exit_code, f"Changed expected exit: {cmd}")
    streams = {}
    for stream in ("stdout", "stderr"):
        item = run["logs"][stream] if nested_logs else {"path": run[stream], "sha256": run[stream+"_sha256"]}
        checked_hash(relative(lane, item["path"]), item["sha256"])
        streams[stream] = item
    return {"command": cmd, "cwd": cwd.relative_to(ROOT).as_posix(), "exit_code": exit_code,
            "expected_outcome": "intentional rejection" if exit_code else "successful command",
            "streams": streams}


def abc(index):
    lane = EVIDENCE / "alder-bryony-clover"
    d = read(lane / "reproduction.json")
    need(d["pin"] == PIN and d["status"] == "passed", "ABC reproduction status/pin")
    need(all(d[k] is True for k in ("inspected_before_execution", "inputs_unchanged", "source_copies_unchanged", "negative_outputs_absent")), "ABC receipt flags")
    inputs = input_scope(index, {"alder", "bryony", "clover"}, d["inputs_before"])
    programs = copies(index, lane, ("alder", "bryony", "clover"), d["copied_files_before"], "runs")
    outputs = {key.removeprefix("runs/"): value for key, value in d["artifacts_after"].items()}
    need(all(k.startswith("runs/") for k in d["artifacts_after"]), "Unexpected ABC artifact scope")
    artifacts = check_map(lane / "runs", outputs, exact=True)
    specs = [
        ("alder", "tests", "runs/alder", ["companion/test_alder.py"], 0),
        ("alder", "demo", "runs/alder", ["companion/alder_core.py", "companion/examples/quotient.alder", "--lean", "companion/generated/Quotient.lean", "--events", "companion/generated/quotient.json"], 0),
        ("alder", "scope_negative", "runs/alder", ["companion/alder_core.py", "companion/examples/scope_rejected.alder", "--lean", "scope-refused.lean", "--events", "scope-refused.json"], 1),
        ("alder", "publication_negative", "runs/alder", ["companion/alder_core.py", "companion/examples/unused_claim_rejected.alder", "--lean", "publication-refused.lean", "--events", "publication-refused.json"], 1),
        ("bryony", "tests", "runs/bryony", ["prototype/test_bryony.py"], 0),
        ("bryony", "demo", "runs/bryony", ["prototype/bryony.py", "prototype/frey4.bry", "--output", "evidence/frey4"], 0),
        ("clover", "tests", "runs/clover/companion", ["-m", "unittest", "-v", "test_clover_slice"], 0),
        ("clover", "demo", "runs/clover/companion", ["clover_slice.py", "demo.clover", "--json", "demo-result.json", "--lean", "GeneratedExamples.lean"], 0),
        ("clover", "affine", "runs/clover/companion", ["affine_basis.py"], 0),
        ("clover", "profiles", "runs/clover/companion", ["compare_profiles.py"], 0),
    ]
    need(len(d["runs"]) == 10, "Expected 10 ABC base jobs")
    jobs = []
    for run, (report, label, cwd, args, code) in zip(d["runs"], specs):
        need((run["report"], run["case"]) == (report, label), "ABC job inventory changed")
        jobs.append({"label": f"{report}-{label}", **command(run, lane, cwd, args, code)})
    for name in ("scope-refused", "publication-refused"):
        for suffix in (".lean", ".json"):
            need(not (lane / "runs/alder" / (name+suffix)).exists(), "Negative Alder output unexpectedly exists")
    adv = read(lane / "adversarial.json")
    need(adv["status"] == "passed" and adv["inputs_unchanged"] is True, "ABC adversarial completion")
    need(recorded_path(adv["command"][2]) == lane / "adversarial.py" and adv["command"][1] == "-B", "ABC adversarial command")
    checked_hash(relative(lane, adv["module"]), adv["module_sha256"])
    need(adv["module_sha256"] == index[source_key("docs/round-4/ideas/Clover/companion/clover_slice.py")]["sha256"], "ABC adversarial imported source changed")
    need(len(adv["results"]) == 4 and len(adv["artifacts"]) == 6, "ABC adversarial inventory changed")
    need([r["name"] for r in adv["results"]] == ["KeywordClaim", "ShadowCompose", "ShadowRule", "RequiredTransportMayBeIdentity"], "ABC adversarial case identities")
    for row, size in zip(adv["results"][:3], (1, 2, 2)):
        need(row["statuses"] == ["plan_checked"] * size, "ABC adversarial expected plan outcome")
    method = adv["results"][3]
    need(method["status"] == "plan_checked" and method["root"] == "inj_transport" and method["support"] == ["already_2"], "ABC method-policy observation changed")
    need(all(k.startswith("adversarial/") for k in adv["artifacts"]), "ABC adversarial artifact root")
    check_map(lane / "adversarial", {k.removeprefix("adversarial/"): v for k, v in adv["artifacts"].items()}, exact=True)
    need(read(lane / "logs/adversarial.stdout.txt") == adv, "ABC adversarial stdout disagrees")
    need((lane / "logs/adversarial.stderr.txt").read_bytes() == b"", "ABC adversarial stderr not empty")
    return {"lane": lane.name, "status": "passed", "input_files": inputs, "copied_runtime_sources": programs,
            "post_run_files_verified": artifacts, "base_jobs": jobs, "base_jobs_count": 10,
            "additional": {"case_count": 4, "artifact_count": 6, "command": adv["command"],
                "completion_evidence": "passed receipt matches retained stdout; no top-level exit code retained",
                "scope": adv["scope"]},
            "receipt_paths": [lane / "reproduction.json", lane / "adversarial.json"],
            "other_bound_paths": [lane / "reproduce.py", lane / "adversarial.py", lane / "logs/adversarial.stdout.txt", lane / "logs/adversarial.stderr.txt"]}


def fhj(index):
    lane = EVIDENCE / "fennel-heather-juniper"
    d = read(lane / "reproduction.json")
    need(d["pin"] == PIN and d["input_bytes_match_pin"] is True and d["inputs_unchanged"] is True, "FHJ input status")
    need(d["input_hashes_before"] == d["input_hashes_after"] and d["bytecode_files"] == [], "FHJ input/bytecode flags")
    inputs = input_scope(index, {"fennel", "heather", "juniper"}, d["input_hashes_before"])
    need(set(d["input_git_blobs"]) == set(d["input_hashes_before"]), "FHJ blob inventory")
    for path, blob in d["input_git_blobs"].items():
        need(index[source_key(path)]["git_blob"] == blob, f"FHJ blob differs from register: {path}")
    before = {n: {} for n in ("fennel", "heather", "juniper")}
    copied_hashes = {}
    for row in d["copied_sources"]:
        parts = row["source"].split("/", 4)
        name, path = parts[3].casefold(), parts[4]
        need(row["copy"] == f"runs/{name}/{path}", "FHJ source/copy path mismatch")
        need(path not in before[name], "Duplicate FHJ copied source")
        before[name][path] = row["sha256"]
        copied_hashes[row["copy"]] = row["sha256"]
    programs = copies(index, lane, tuple(before), before, "runs")
    allfiles = {**copied_hashes, **d["runtime_artifacts"]}
    need(not (set(copied_hashes) & set(d["runtime_artifacts"])), "FHJ source/output inventory overlap")
    need(all(k.startswith("runs/") for k in allfiles), "Unexpected FHJ artifact root")
    artifacts = check_map(lane / "runs", {k.removeprefix("runs/"): v for k, v in allfiles.items()}, exact=True)
    specs = [
        ("fennel", "demo", "", ["prototype/fennel.py", "prototype/quotients.fnl", "--out", "prototype/generated"]),
        ("fennel", "tests", "", ["prototype/test_fennel.py"]),
        ("fennel", "stress", "", ["prototype/stress_frontiers.py"]),
        ("heather", "tests", "companion", ["test_heather.py"]),
        ("heather", "use-site", "companion", ["use_site_demo.py"]),
        *[("heather", "demo-"+n, "companion", ["heather.py", "examples/"+n+".hthr", "--output", "generated"]) for n in ("diagonal", "empty", "free", "even", "refuted")],
        ("juniper", "tests", "companion", ["test_frontier.py"]),
        ("juniper", "inverse", "companion", ["inverse_polynomials.py"]),
        ("juniper", "demo", "companion", ["juniper_frontier.py", "example.jnp", "--json", "example-result.json", "--lean", "Generated.lean"]),
        ("juniper", "capped", "companion", ["juniper_frontier.py", "example.jnp", "--max-attempts", "2"]),
    ]
    need(len(d["runs"]) == 14, "Expected 14 FHJ base jobs")
    jobs = []
    for run, (report, label, suffix, args) in zip(d["runs"], specs):
        need((run["report"], run["label"]) == (report, label), "FHJ job inventory")
        need(run["timeout_seconds"] == 180, "FHJ timeout metadata changed")
        jobs.append({"label": report+"-"+label, **command(run, lane, f"runs/{report}/{suffix}", args, 0, True)})
    a = read(lane / "audit.json")
    need(a["pin"] == PIN and a["inputs_unchanged"] is True and a["source_file_count"] == inputs and a["bytecode_files"] == [], "FHJ audit flags")
    checked_hash(lane / "audit.py", a["harness_sha256"])
    need(recorded_path(a["command"][2]) == lane / "audit.py" and a["command"][1] == "-B", "FHJ audit command")
    need(len(a["comparisons"]) == 27 and set(a["ignored_JSON_runtime_keys"]) == VOLATILE, "FHJ comparison inventory")
    for row in a["comparisons"]:
        original, fresh = relative(ROOT, row["source"]), relative(lane, row["fresh"])
        need(index[source_key(row["source"])]["sha256"] == row["source_sha256"], "FHJ comparison source binding")
        checked_hash(original, row["source_sha256"])
        checked_hash(fresh, row["fresh_sha256"])
        equal = (normalized(read(original)) == normalized(read(fresh)) if fresh.suffix == ".json"
                 else original.read_text(encoding="utf-8") == fresh.read_text(encoding="utf-8"))
        need(equal and row["equivalent"] is True, f"FHJ generated parity changed: {fresh}")
        need(row["byte_identical"] == (original.read_bytes() == fresh.read_bytes()), "FHJ byte parity claim changed")
    need(all(k.startswith("adversarial/") for k in a["probe_artifacts"]), "FHJ probe artifact root")
    check_map(lane / "adversarial", {k.removeprefix("adversarial/"): v for k, v in a["probe_artifacts"].items()}, exact=True)
    need(set(a["probes"]) == {"cross_implementation", "named_root_boundary", "coverage_boundary", "admissible_domains", "same_affine_hull", "fennel_stale_output", "heather_stale_output"}, "FHJ probe inventory")
    x = a["probes"]["cross_implementation"]
    need([x[k] for k in ("profiles", "atom_frontiers_compared", "selected_Fennel_routes_checked", "Juniper_results_checked")] == [128, 768, 89, 128], "FHJ cross-comparison counts")
    need(len(read(lane / "adversarial/cross-profiles.json")) == 128, "FHJ retained profile count")
    need(a["probes"]["same_affine_hull"]["free_even_expression_pairs"] == 49, "FHJ hull comparison count")
    need(a["probes"]["same_affine_hull"]["equality_acceptance_matches"] is True, "FHJ hull comparison outcome")
    coverage = a["probes"]["coverage_boundary"]
    need(coverage["same_sound_subset_when_declared_incomplete"] == "accepted"
         and coverage["omitted_complete_route"] == coverage["forged_truncation_complete"] == "complete frontier is not rule-closed", "FHJ coverage outcomes")
    domains = a["probes"]["admissible_domains"]
    need(domains["diagonal_status"] == "model_proved" and domains["free_status"] == "counterexample"
         and domains["free_counterexample_lengths"] == [1, 0] and domains["even_negative_lengths"] == [2]
         and domains["cross_domain_receipt_rejected"] is True and domains["odd_length_negative_rejected"] is True,
         "FHJ domain outcomes")
    need(len(a["subprocesses"]) == 4, "FHJ stale-output command count")
    for i, run in enumerate(a["subprocesses"]):
        report, stage = ("fennel" if i < 2 else "heather"), i % 2
        folder = lane / "adversarial" / (report+"-reuse")
        cmd = run["command"]
        script = lane / "runs" / report / ("prototype/fennel.py" if report == "fennel" else "companion/heather.py")
        need(run["exit_code"] == 0 and run["timeout_seconds"] == 30, "FHJ stale-output command outcome")
        need(relative(lane, run["cwd"]) == folder and cmd[1] == "-B", "FHJ stale-output working directory")
        need(recorded_path(cmd[2]) == script and recorded_path(cmd[3]) == folder / f"stage{stage}.source", "FHJ stale-output source command")
        need(cmd[4] == ("--out" if report == "fennel" else "--output") and recorded_path(cmd[5]) == folder / "output", "FHJ stale-output destination")
    for report in ("fennel", "heather"):
        stages = a["probes"][report+"_stale_output"]["stages"]
        need(len(stages) == 2 and stages[0]["lean_hashes"]
             and stages[0]["lean_hashes"] == stages[1]["lean_hashes"], "FHJ retained stale-output observation")
        check_map(lane / "adversarial" / (report+"-reuse") / "output", stages[1]["lean_hashes"])
    expected_stdout = {"compared_artifacts": 27, "probes": a["probes"], "input_files_unchanged": inputs}
    need(read(lane / "audit.stdout.txt") == expected_stdout, "FHJ audit stdout changed")
    need((lane / "audit.stderr.txt").read_bytes() == b"", "FHJ audit stderr not empty")
    return {"lane": lane.name, "status": "passed", "input_files": inputs, "copied_runtime_sources": programs,
            "post_run_files_verified": artifacts, "base_jobs": jobs, "base_jobs_count": 14,
            "additional": {"scope": a["scope"], "command": a["command"],
                "completion_evidence": "completed hash-bound audit and matching stdout; no top-level exit code retained",
                "cross_implementation": x, "free_even_pairs": 49, "comparison_artifacts": 27,
                "probe_groups": sorted(a["probes"]), "stale_output_subprocesses": a["subprocesses"]},
            "receipt_paths": [lane / "reproduction.json", lane / "audit.json"],
            "other_bound_paths": [lane / "reproduce.py", lane / "audit.py", lane / "audit.stdout.txt", lane / "audit.stderr.txt"]}


def lrs(index):
    lane = EVIDENCE / "laurel-rowan-sorrel"
    d = read(lane / "receipt.json")
    need(d["input_pin"] == PIN and d["all_inputs_unchanged"] is True and d["no_bytecode"] is True, "LRS reproduction flags")
    need(d["input_sha256_before"] == d["input_sha256_after"] == d["copied_sha256_before"], "LRS initial/after input binding")
    checked_hash(lane / "reproduce.py", d["runner_sha256"])
    inputs = input_scope(index, {"laurel", "rowan", "sorrel"}, flatten(d["input_sha256_before"], "docs/round-4/ideas"))
    programs = copies(index, lane, ("Laurel", "Rowan", "Sorrel"), d["copied_sha256_before"], "copies")
    artifacts = check_map(lane / "copies",
                          {f"{n}/{p}": h for n, files in d["output_sha256"].items() for p, h in files.items()}, exact=True)
    specs = [
        ("laurel-tests", "Laurel/prototype", ["test_core.py"]),
        ("laurel-width", "Laurel/prototype", ["bench_frontier.py"]),
        *[("laurel-"+n, "Laurel/prototype", ["laurel_core.py", "examples/"+n+".laurel", "--json", "generated/"+n+".json", "--lean", "generated/"+n+".lean"]) for n in ("quotient", "frey_a4", "alternatives", "cycle")],
        ("laurel-budget-zero", "Laurel/prototype", ["laurel_core.py", "examples/quotient.laurel", "--budget", "0"]),
        ("rowan-demo", "Rowan", ["rowan_model.py"]),
        ("rowan-tests", "Rowan", ["test_rowan.py"]),
        ("sorrel-tests", "Sorrel", ["sorrel_model.py", "--test", "--json", "test_results.json"]),
        ("sorrel-quotient", "Sorrel", ["sorrel_model.py", "examples/quotient.sorrel", "--json", "examples/quotient_result.json", "--export-lean", "SelectedPlan.lean"]),
        ("sorrel-cauchy", "Sorrel", ["sorrel_model.py", "examples/cauchy.sorrel", "--json", "examples/cauchy_result.json"]),
    ]
    need(len(d["runs"]) == 12, "Expected 12 LRS base jobs")
    jobs = []
    for run, (label, suffix, args) in zip(d["runs"], specs):
        need(run["label"] == label, "LRS job inventory changed")
        jobs.append({"label": label, **command(run, lane, "copies/"+suffix, args, 0)})
    p = read(lane / "probe-receipt.json")
    need(p["command"][1:] == ["-B", "semantic_probes.py"] and recorded_path(p["cwd"]) == lane, "LRS probe command")
    need(p["exit_code"] == 0 and p["all_inputs_unchanged_since_reproduction"] is True and p["no_bytecode_in_lane"] is True, "LRS probe status")
    checked_hash(lane / "semantic_probes.py", p["source_sha256"])
    checked_hash(lane / "semantic-probes.json", p["result_sha256"])
    checked_hash(lane / "SorrelSelectionProbe.lean", p["generated_lean_sha256"])
    for stream in p["streams"].values():
        checked_hash(relative(lane, stream["path"]), stream["sha256"])
    probes = read(lane / "semantic-probes.json")
    need(read(relative(lane, p["streams"]["stdout"]["path"])) == probes, "LRS probe stdout/result mismatch")
    need(len(probes["probes"]) == 4 and p["input_file_counts"] == {"Laurel": 25, "Rowan": 9, "Sorrel": 11}, "LRS probe counts")
    need([r["id"] for r in probes["probes"]] == ["rowan-cycle-plus-leaf-frontier", "sorrel-export-selection-vs-available-route", "laurel-rejects-insufficient-offer-under-cycle", "partial-minimality-is-relative-to-discovered-routes"], "LRS semantic probe identities")
    need(len(p["generated_artifact_comparison"]) == 11, "LRS parity inventory")
    for row in p["generated_artifact_comparison"]:
        original = relative(ROOT, f"docs/round-4/ideas/{row['package']}/{row['path']}")
        fresh = relative(lane, f"copies/{row['package']}/{row['path']}")
        checked_hash(original, row["original_sha256"])
        checked_hash(fresh, row["fresh_sha256"])
        need(row["byte_identical_to_author_input"] == (original.read_bytes() == fresh.read_bytes()), "LRS byte parity claim changed")
        need(row["text_identical_after_universal_newlines"] == (original.read_text(encoding="utf-8") == fresh.read_text(encoding="utf-8")), "LRS text parity claim changed")
    return {"lane": lane.name, "status": "passed", "input_files": inputs, "copied_runtime_sources": programs,
            "post_run_files_verified": artifacts, "base_jobs": jobs, "base_jobs_count": 12,
            "additional": {"scope": p["scope"], "command": p["command"], "exit_code": 0,
                "case_count": 4, "probe_ids": [x["id"] for x in probes["probes"]], "comparison_artifacts": 11},
            "receipt_paths": [lane / "receipt.json", lane / "probe-receipt.json"],
            "other_bound_paths": [lane / "reproduce.py", lane / "semantic_probes.py", lane / "semantic-probes.json", lane / "SorrelSelectionProbe.lean"]}


def validate():
    """Read-only receipt and hash validation; returns a serializable summary."""
    index = registry()
    lanes = [abc(index), fhj(index), lrs(index)]
    bound, receipt_hashes = {}, {}
    for lane in lanes:
        directory = EVIDENCE / lane["lane"]
        need(not list(directory.rglob("*.pyc")), f"Bytecode files appeared in {directory}")
        for path in lane.pop("receipt_paths"):
            receipt_hashes[path.relative_to(HERE).as_posix()] = sha(path)
        for path in lane.pop("other_bound_paths"):
            bound[path.relative_to(HERE).as_posix()] = sha(path)
    need([x["base_jobs_count"] for x in lanes] == [10, 14, 12], "Base job totals changed")
    need(sum(x["input_files"] for x in lanes) == 159, "Lane input coverage is not 159")
    return {"status": "passed", "validated_utc": datetime.now(timezone.utc).isoformat(),
            "input_pin": PIN, "validator": "scripts/verify_python_evidence.py", "validator_sha256": sha(Path(__file__)),
            "source_register_sha256": sha(HERE / "source-register.json"), "verified_receipt_sha256": receipt_hashes,
            "additional_retained_file_sha256": bound, "base_jobs": 36, "base_zero_exits": 34,
            "base_expected_rejection_exits": 2, "input_files_verified": 159, "lanes": lanes,
            "scope": "Fresh validation of retained Python execution evidence, exact expected command outcomes, original/copy hashes and post-run artifacts. No experiments rerun.",
            "limitations": [
                "Receipt validation is consistency/provenance evidence, not a proof of Python semantics, a new benchmark run, Lean acceptance, or visual QA.",
                "Source bytes and lane records are bound to source-register; immutable Git object verification is performed separately by verify_sources.py.",
                "Generated files are checked against recorded post-run hashes. Author/fresh equality is required only for explicitly described parity comparisons; intentional generated differences remain legitimate.",
                "ABC adversarial and FHJ audit receipts omit a top-level process exit code. Their complete output/receipt agreement is checked; no missing exit code is fabricated.",
                "ABC reproduction/adversarial and FHJ reproduction do not hash-bind their original runner source. Current runner hashes are retained as packaging evidence, not retroactive proof of historical runner bytes.",
                "Some copies retain historical PDF/build/Lean-status metadata. Hash validation of those files does not repeat their claimed builds or imply the same status in this environment."
            ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-summary", action="store_true")
    args = parser.parse_args()
    summary = validate()
    if args.write_summary:
        (EVIDENCE / "python-validation.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print("Verified Python evidence: 10 + 14 + 12 base jobs; 34 zero exits and 2 expected rejections; 159 original files; all copied runtime sources and retained post-run artifacts unchanged.")
    print("Additional coverage: ABC 4 adversarial cases; FHJ 128 shared profiles/768 frontiers plus domain, coverage and stale-output probes; LRS 4 semantic probes. No tests, Lean or PDF tools were run.")


if __name__ == "__main__":
    main()
