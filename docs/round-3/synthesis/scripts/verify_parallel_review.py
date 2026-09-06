"""Validate retained parallel-review evidence without executing any experiment.

Only Git read operations and local file reads occur. ``validate()`` returns a
JSON-compatible result; it neither writes a receipt nor refreshes stale evidence.
The Git/PDF bindings attest byte identity, not the peer's editorial conclusions.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path, PureWindowsPath
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
OUT = HERE / "evidence/parallel-review"
PEER = "docs/round-3/unified_report"
PIN = "8ddc6abb07df3906949f8f1a55b88288987fabe5"
REPORTS = ("Basalt", "Fiber", "Gneiss", "Karst", "Moraine", "Obsidian",
           "Schist", "Tephra", "Trellis")
FREY_NAMES = ("sixteen_dvd_pow", "odd_pow_mod_four", "four_dvd_a2",
              "sixteen_dvd_a4", "cast_a2", "cast_a4")
FREY_AXIOMS = {
    "FreyExact.four_dvd_a2": ["propext", "Classical.choice", "Quot.sound"],
    "FreyExact.sixteen_dvd_a4": ["propext", "Quot.sound"],
    "FreyExact.cast_a2": ["propext", "Classical.choice", "Quot.sound"],
    "FreyExact.cast_a4": ["propext", "Classical.choice", "Quot.sound"],
}
ADEQUACY_NAMES = ("empty_models_agree", "empty_coefficients_differ",
                  "coefficient_test_not_complete")
CASE_COUNTS = {"FreyExact.lean": (6, 7, 4), "SupplyChecked.lean": (0, 4, 0),
               "AdequacyChecks.lean": (3, 0, 3)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def local(base, relative):
    require(isinstance(relative, str) and relative, "Empty evidence path")
    require(not PureWindowsPath(relative).is_absolute() and not Path(relative).is_absolute(),
            f"Expected relative evidence path: {relative}")
    target = (base / relative).resolve()
    require(target.is_relative_to(base.resolve()), f"Evidence path escapes its root: {relative}")
    require(target.is_file(), f"Missing evidence: {target}")
    return target


def bound(base, relative, expected):
    require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected),
            f"Invalid SHA-256 for {relative}")
    path = local(base, relative)
    require(digest(path.read_bytes()) == expected, f"Evidence hash differs: {relative}")
    return path


def git(*args, data=None):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], input=data)


def validate_sources():
    register = read(OUT / "source-register.json")
    require(register["source_commit"] == PIN, "Parallel-review input pin differs")
    rows = register["files"]
    require(len(rows) == len({row["path"] for row in rows}) == 28,
            "Expected 28 distinct registered peer artifacts")
    tree = {}
    for line in git("ls-tree", "-r", PIN, "--", PEER).decode().splitlines():
        metadata, path = line.split("\t", 1)
        _, kind, blob = metadata.split()
        require(kind == "blob", f"Unexpected non-blob peer artifact: {path}")
        tree[path] = blob
    require(set(tree) == {row["path"] for row in rows}, "Peer inventory differs from immutable tree")
    blob_ids = list(dict.fromkeys(tree.values()))
    raw_batch = git("cat-file", "--batch", data=("\n".join(blob_ids) + "\n").encode())
    offset, canonical = 0, {}
    for blob in blob_ids:
        end = raw_batch.index(b"\n", offset)
        header = raw_batch[offset:end].decode().split()
        require(len(header) == 3 and header[:2] == [blob, "blob"], "Unexpected Git batch header")
        size = int(header[2])
        body = raw_batch[end + 1:end + 1 + size]
        require(len(body) == size and raw_batch[end + 1 + size:end + 2 + size] == b"\n",
                "Truncated Git blob batch")
        canonical[blob] = body
        offset = end + 2 + size
    require(offset == len(raw_batch), "Unexpected trailing Git batch bytes")
    sources = {}
    for row in rows:
        relative = row["path"]
        require(tree[relative] == row["git_blob"], f"Immutable Git identity differs: {relative}")
        raw = canonical[row["git_blob"]]
        require(digest(raw) == row["git_bytes_sha256"], f"Canonical Git bytes differ: {relative}")
        path = bound(ROOT, relative, row["checkout_sha256"])
        require(path.stat().st_size == row["bytes"], f"Checkout size differs: {relative}")
        # This particular capture contains no checkout newline conversions.
        require(path.read_bytes() == raw, f"Peer checkout is not the captured Git byte sequence: {relative}")
        sources[relative] = raw
    return sources


def lean_code(text):
    """Remove nested block and line comments for this small, string-free corpus.

    This helper inventories declarations; it is not a Lean parser or proof check.
    """
    out, index, depth = [], 0, 0
    while index < len(text):
        if text.startswith("/-", index):
            depth += 1
            out.append(" ")
            index += 2
        elif depth and text.startswith("-/", index):
            depth -= 1
            out.append(" ")
            index += 2
        elif not depth and text.startswith("--", index):
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
        else:
            if not depth or text[index] == "\n":
                out.append(text[index])
            index += 1
    require(depth == 0, "Unclosed Lean source comment")
    return "".join(out)


def axiom_inventory(log):
    inventory = {}
    pattern = r"^'([^']+)' (does not depend on any axioms|depends on axioms: \[([^\]]*)\])\s*$"
    for match in re.finditer(pattern, log, re.M):
        name = match[1]
        axioms = [] if match[3] is None else [part.strip() for part in match[3].split(",") if part.strip()]
        require(name not in inventory, f"Duplicate axiom inventory: {name}")
        inventory[name] = axioms
    return inventory


def validate_execution(sources):
    receipt = read(OUT / "execution-receipt.json")
    require("version 4.32.0," in receipt["version"], "Unexpected Lean version")
    require(receipt["LEAN_NUM_THREADS"] == "0", "Unexpected Lean thread setting")
    require(PureWindowsPath(receipt["executable"]).name.lower() in {"lean", "lean.exe"},
            "Recorded checker is not a direct Lean command")
    require(re.fullmatch(r"[0-9a-f]{64}", receipt["manifest_sha256"]), "Malformed manifest digest")
    require(re.fullmatch(r"[0-9a-f]{40}", receipt["proveit_head"]), "Malformed ProveIt revision")
    dependencies = receipt["dependencies"]
    require(dependencies and len(dependencies) == len({d["name"] for d in dependencies}),
            "Missing or duplicate dependency metadata")
    for dependency in dependencies:
        require(dependency["manifest_revision"] == dependency["actual_revision"],
                f"Recorded dependency revision mismatch: {dependency['name']}")
        require(not dependency["tracked_source_status"],
                f"Recorded dependency source was modified: {dependency['name']}")
        require(isinstance(dependency["library_present"], bool), "Malformed dependency library status")
    require(receipt["LEAN_PATH"] == [d["library_path"] for d in dependencies if d["library_present"]],
            "LEAN_PATH differs from the recorded dependency library inventory")
    rows = receipt["cases"]
    require(len(rows) == 3 and {row["source"] for row in rows} == set(CASE_COUNTS),
            "Fresh parallel-review receipt must contain all three completed checks")
    results = {}
    for row in rows:
        name = row["source"]
        require(row["exit_code"] == row["expected_exit_code"] == 0, f"Lean check did not succeed: {name}")
        require(isinstance(row["seconds"], (float, int)) and row["seconds"] >= 0,
                f"Malformed execution duration: {name}")
        source = bound(OUT, name, row["source_sha256"])
        require(row["log"] == source.with_suffix(".log").name, f"Unexpected log path: {name}")
        log = bound(OUT, row["log"], row["log_sha256"]).read_text(encoding="utf-8-sig")
        command = row["command"]
        require(len(command) == 2 and command[0] == receipt["executable"]
                and PureWindowsPath(command[1]).parts[-6:] ==
                ("docs", "round-3", "synthesis", "evidence", "parallel-review", name),
                f"Unexpected Lean invocation: {name}")
        require(not re.search(r"\berror:|declaration uses ['`]sorry['`]|\bsorryAx\b", log),
                f"Retained Lean output contains a failure or placeholder: {name}")
        code = lean_code(source.read_text(encoding="utf-8-sig"))
        declarations = re.findall(r"^\s*theorem\s+([\w.]+)", code, re.M)
        examples = len(re.findall(r"^\s*example\b", code, re.M))
        queries = re.findall(r"^\s*#print axioms ([\w.]+)\s*$", code, re.M)
        require((len(declarations), examples, len(queries)) == CASE_COUNTS[name],
                f"Source declaration/example/query inventory differs: {name}")
        require((row["named_theorems"], row["examples"]) == CASE_COUNTS[name][:2],
                f"Receipt/source count mismatch: {name}")
        require(not re.search(r"\b(?:sorry|admit|native_decide)\b|^\s*axiom\b", code, re.M),
                f"Unexpected placeholder or native proof execution in source: {name}")
        axioms = axiom_inventory(log)
        if name == "FreyExact.lean":
            require(source.read_bytes() == sources[f"{PEER}/experiments/lean/FreyExact.lean"],
                    "Fresh Frey source differs from the immutable peer source")
            require(tuple(declarations) == FREY_NAMES, "Frey declaration names differ")
            require(queries == [target.split(".")[-1] for target in FREY_AXIOMS], "Frey axiom queries differ")
            require(axioms == FREY_AXIOMS, "Frey axiom dependencies differ")
        elif name == "SupplyChecked.lean":
            peer = sources[f"{PEER}/experiments/lean/Supply3.lean"].decode("utf-8")
            expected = lean_code(peer).replace("Matrix.mul_eq_one_comm", "mul_eq_one_comm")
            expected = expected.replace("example : True := by mvcgen",
                "example : Odd (5 : ℕ) ∧ 4 ≤ (5 : ℕ) ∧ (3 : ℤ) ≡ 3 [ZMOD 4] ∧ 2 ∣ (2 : ℤ) := by decide")
            require(re.sub(r"\s+", " ", code).strip() == re.sub(r"\s+", " ", expected).strip(),
                    "Positive supply probe differs from its identified source adaptation")
            require(len(re.findall(r"^\s*#check\b", code, re.M)) == 16 and not axioms,
                    "Supply query/output inventory differs")
        else:
            require(tuple(declarations) == ADEQUACY_NAMES and tuple(queries) == ADEQUACY_NAMES,
                    "Adequacy theorem or axiom-query names differ")
            require(axioms == {f"ObservationAdequacy.{target}": [] for target in ADEQUACY_NAMES},
                    "Adequacy checks must have three empty axiom inventories")
            require(not re.search(r"^\s*import\b", code, re.M), "Adequacy source no longer uses only implicit Init")
        results[name] = {"named_theorems": len(declarations), "examples": examples,
                         "axiom_queries": len(queries), "axioms": axioms,
                         "source_sha256": row["source_sha256"], "log_sha256": row["log_sha256"],
                         "recorded_exit_code": row["exit_code"], "scope": row["scope"]}
    return {"version": receipt["version"], "cases": results,
            "successful_retained_checks": 3, "named_theorems": 9, "examples": 11,
            "queried_declarations": 7, "recorded_dependency_count": len(dependencies),
            "execution_receipt_sha256": digest((OUT / "execution-receipt.json").read_bytes())}


def editorial_counts(sources):
    def rows(name):
        return list(csv.DictReader(io.StringIO(sources[f"{PEER}/{name}"].decode("utf-8-sig"))))

    negative = rows("negative_suite.csv")
    incidence_counts = [sum(bool(row[name]) for name in REPORTS) for row in negative]
    require(len(negative) == len({row["id"] for row in negative}) == 48, "Negative-family CSV inventory differs")
    require(incidence_counts == [int(row["reports"]) for row in negative], "Negative-family CSV incidence totals differ")
    require(sum(incidence_counts) == 142, "Expected 142 report-family incidences")
    matrix, questions, cores = rows("feature_matrix.csv"), rows("question_tally.csv"), rows("lean_cores.csv")
    require(len(matrix) == 76 and len(questions) == 20 and len(cores) == 7, "Editorial CSV row counts differ")
    for row in matrix + questions:
        require(all(row[name] in {"Y", "P", "N"} for name in REPORTS), "Unknown editorial reading mark")
    unanimous = [row for row in matrix if all(row[name] == "Y" for name in REPORTS)]
    for row in questions:
        require(int(row["explicit"]) == sum(row[name] == "Y" for name in REPORTS)
                and int(row["implicit"]) == sum(row[name] == "P" for name in REPORTS),
                "Question tally arithmetic differs")
    core_files = {"Basalt": "Basalt.lean", "Fiber": "FiberAx.lean", "Gneiss": "Gneiss.lean",
                  "Karst": "Karst.lean", "Moraine": "MoraineAx.lean", "Schist": "Schist.lean",
                  "Tephra": "TephraAx.lean"}
    core_counts = {}
    for name, filename in core_files.items():
        code = lean_code(sources[f"{PEER}/experiments/lean/{filename}"].decode("utf-8"))
        core_counts[name] = len(re.findall(r"^\s*theorem\s+", code, re.M))
    require(core_counts == {"Basalt": 2, "Fiber": 3, "Gneiss": 2, "Karst": 12,
                            "Moraine": 16, "Schist": 8, "Tephra": 6},
            "Imported core source declaration inventory differs")
    require({row["report"]: int(row["theorems"]) for row in cores}
            == dict(core_counts, Karst=11), "Peer core CSV discrepancy changed")
    return {"classification": "Editorial classifications of the same nine proposals; their semantic scoring is not validated.",
            "commitment_rows": len(matrix), "unanimous_marked_rows": len(unanimous),
            "inherited_commitment_rows": sum(row["stated_in_round2_syntheses"] == "yes" for row in matrix),
            "fresh_unanimous_marked_rows": sum(row["stated_in_round2_syntheses"] == "no" for row in unanimous),
            "negative_families": len(negative), "report_family_incidences": sum(incidence_counts),
            "families_marked_inherited": sum(bool(row["inherits_round2"]) for row in negative),
            "families_with_one_report": incidence_counts.count(1),
            "families_with_at_least_five_reports": sum(count >= 5 for count in incidence_counts),
            "question_rows": len(questions),
            "questions_marked_explicit_in_all_reports": sum(int(row["explicit"]) == 9 for row in questions),
            "peer_core_csv_reported_theorem_total": sum(int(row["theorems"]) for row in cores),
            "core_source_named_theorems": core_counts,
            "core_source_named_theorem_total": sum(core_counts.values()),
            "core_count_qualification": "The peer CSV reports 48, counting Karst's 11 axiom queries instead of its 12 named theorem declarations. The seven original cores have 49 named theorem declarations; this CSV does not supersede the separate source inventory.",
            "negative_suite_qualification": "142 counts populated report-family cells, not 142 unique source rows or 142 executable tests. Multiple source labels can occupy one cell."}


def validate():
    sources = validate_sources()
    execution = validate_execution(sources)
    return {"status": "passed", "source_commit": PIN, "peer_artifacts_bound": len(sources),
            "secondary_syntheses_counted_as_proposals": 0,
            "source_register_sha256": digest((OUT / "source-register.json").read_bytes()),
            "fresh_execution_evidence": execution, "editorial_metadata": editorial_counts(sources),
            "limitations": [
                "This validator performs only read-only Git and artifact-consistency checks. It reruns no Lean, Lake, solver, Python companion, or PDF build.",
                "Successful exit codes and axiom inventories describe retained fresh executions; validation does not independently recheck their proof terms.",
                "The runs used existing ProveIt dependency library artifacts. Recorded manifest revisions and clean tracked-source statuses are consistent, but this validator neither rebuilds nor hashes or audits every imported .olean or compares live external repositories.",
                "FreyExact.lean is unchanged peer source. SupplyChecked.lean is an explicitly adapted positive probe, replacing the deprecated matrix name and deliberate mvcgen misuse with an admissible Frey tuple. It does not validate an effectful mvcgen workflow or claim the original Supply3 file succeeded.",
                "AdequacyChecks.lean is a new small counterexample to unrestricted coefficient-test completeness over List Empty, not a verified Leant adapter or arbitrary abstraction theorem.",
                "Byte-bound peer PDFs and CSVs receive no source/PDF parity or semantic editorial-scoring validation here. The parallel synthesis remains a secondary review of the same nine proposals."
            ]}


if __name__ == "__main__":
    try:
        print(json.dumps(validate(), indent=2))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"Parallel-review evidence validation FAILED: {error}", file=sys.stderr)
        sys.exit(1)
