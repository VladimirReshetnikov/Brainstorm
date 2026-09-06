"""Validate the editorial index and all three native round-four matrices.

Default execution is read-only. Explicit --create builds the initial index and
normalizes only the Alder/Bryony/Clover matrix's source-anchor path spelling.
The source register supplies canonical case-sensitive paths and byte hashes.
No reproduction receipt, execution output, imported source, or Git state changes.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import sys

SYNTHESIS = Path(__file__).resolve().parents[1]
ROOT = SYNTHESIS.parents[2]
REGISTER = SYNTHESIS / "source-register.json"
INDEX = SYNTHESIS / "convergence.json"
PIN = "58ced1ce667b3ba1ed162a0c6280959536c8bc5f"
LANES = {
    "alder-bryony-clover": ("evidence/alder-bryony-clover/convergence.json", ("Alder", "Bryony", "Clover")),
    "fennel-heather-juniper": ("evidence/fennel-heather-juniper/convergence.json", ("Fennel", "Heather", "Juniper")),
    "laurel-rowan-sorrel": ("evidence/laurel-rowan-sorrel/laneconvergence.json", ("Laurel", "Rowan", "Sorrel")),
}
REPORTS = {name for _, names in LANES.values() for name in names}
ANTICHAINS = {"Alder", "Bryony", "Fennel", "Juniper", "Laurel", "Sorrel"}
CATEGORIES = {name: "support_antichain" for name in ANTICHAINS}
CATEGORIES.update(Clover="concrete_grounding", Heather="behavioral_frontend", Rowan="diagnostic_and_semilinear")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canonical_register():
    register = read_json(REGISTER)
    require(register.get("input_commit") == PIN, "Source-register pin mismatch")
    entries = {row["path"]: row for row in register["files"]}
    require(len(entries) == len(register["files"]), "Duplicate source-register paths")
    primary = {p: row for p, row in entries.items() if row["role"] == "round4-primary-input"}
    require({p["name"] for p in register["packages"]} == REPORTS, "Source register must name exactly nine reports")
    folded = {p.casefold(): p for p in primary}
    require(len(folded) == len(primary), "Ambiguous case-insensitive source paths")
    return primary, folded


def parse_anchor(anchor):
    if isinstance(anchor, str):
        path, separator, number = anchor.rpartition(":")
        require(separator and number.isdigit(), f"Malformed source anchor: {anchor!r}")
        return path, int(number), None
    require(isinstance(anchor, dict), f"Unsupported anchor representation: {anchor!r}")
    path, number = anchor.get("path"), anchor.get("line")
    require(isinstance(path, str) and type(number) is int, f"Malformed source anchor: {anchor!r}")
    excerpt = anchor.get("excerpt", anchor.get("source_line"))
    require(excerpt is None or isinstance(excerpt, str), f"Non-text excerpt: {anchor!r}")
    return path, number, excerpt


def validate_data(index):
    primary, folded = canonical_register()
    require(index.get("schema") == "round4-native-convergence-index-1", "Unknown convergence index schema")
    require(index.get("input_commit") == PIN, "Convergence index pin mismatch")
    require(index.get("source_register") == {"path": "source-register.json", "sha256": digest(REGISTER)},
            "Source-register identity mismatch")
    require(set(index.get("native_matrices", {})) == set(LANES), "Index must contain exactly three native matrices")
    require(set(index.get("reports", {})) == REPORTS, "Index must classify exactly nine reports")
    source_cache = {}
    seen_anchors = set()
    observed_reports = set()
    matrix_stats = {}
    anchor_occurrences = 0

    def check_anchor(anchor, label):
        nonlocal anchor_occurrences
        path, number, excerpt = parse_anchor(anchor)
        require(path in primary,
                f"{label}: path is not canonical and case-sensitive in source-register.json: {path!r}; "
                f"canonical spelling: {folded.get(path.casefold(), 'not registered')!r}")
        require(not PurePosixPath(path).is_absolute() and ".." not in PurePosixPath(path).parts and "\\" not in path,
                f"{label}: invalid repository-relative path")
        if path not in source_cache:
            source = ROOT / path
            require(source.is_file(), f"Missing source: {path}")
            require(digest(source) == primary[path]["sha256"], f"Changed source bytes: {path}")
            source_cache[path] = source.read_text(encoding="utf-8-sig").splitlines()
        lines = source_cache[path]
        require(1 <= number <= len(lines), f"{label}: line outside source: {path}:{number}")
        text = lines[number - 1].strip()
        require(bool(text), f"{label}: blank source anchor: {path}:{number}")
        if excerpt is not None:
            require(excerpt.strip() == text, f"{label}: excerpt mismatch at {path}:{number}")
        seen_anchors.add((path, number))
        anchor_occurrences += 1

    for lane_id, (expected_path, expected_names) in LANES.items():
        entry = index["native_matrices"][lane_id]
        require(entry.get("path") == expected_path, f"Wrong path for matrix {lane_id}")
        native_path = SYNTHESIS / expected_path
        require(entry.get("sha256") == digest(native_path), f"Native matrix changed: {expected_path}")
        matrix = read_json(native_path)
        pin = matrix.get("input_pin", matrix.get("input_commit", matrix.get("pin")))
        require(pin == PIN, f"Native matrix pin mismatch: {lane_id}")
        names = set(matrix.get("reports", {}))
        require(names == set(expected_names), f"Unexpected reports in {lane_id}")
        require(set(entry.get("reports", [])) == names and len(entry["reports"]) == len(names),
                f"Report index mismatch in {lane_id}")
        require(not observed_reports.intersection(names), "A report appears in more than one native lane")
        observed_reports.update(names)
        dimensions = matrix.get("dimensions")
        require(isinstance(dimensions, (dict, list)) and bool(dimensions), f"Missing dimensions in {lane_id}")
        require(entry.get("native_dimensions") == dimensions, f"Native dimensions flattened or changed in {lane_id}")
        dimension_keys = list(dimensions)
        require(len(set(dimension_keys)) == len(dimension_keys), f"Duplicate dimensions in {lane_id}")
        before_anchors = anchor_occurrences
        cell_count = 0
        for name, readings in matrix["reports"].items():
            for dimension in dimension_keys:
                cell = readings.get(dimension)
                require(isinstance(cell, dict), f"Missing native cell: {name}/{dimension}")
                mark = cell.get("idea", cell.get("status", cell.get("mark")))
                require(mark in {"explicit", "partial", "absent"}, f"Unknown editorial mark: {name}/{dimension}")
                require(isinstance(cell.get("qualification"), str) and bool(cell["qualification"].strip()),
                        f"Missing qualification: {name}/{dimension}")
                anchors = cell.get("anchors")
                require(isinstance(anchors, list) and bool(anchors), f"Missing anchors: {name}/{dimension}")
                for anchor in anchors:
                    check_anchor(anchor, f"{name}/{dimension}")
                cell_count += 1
        matrix_stats[lane_id] = {"reports": len(names), "native_dimensions": len(dimension_keys),
                                 "native_cells": cell_count, "anchor_occurrences": anchor_occurrences - before_anchors}
    require(observed_reports == REPORTS, "Native matrices do not cover all nine reports")
    native_occurrences = anchor_occurrences
    for name, classification in index["reports"].items():
        require(classification.get("implementation_class") == CATEGORIES[name], f"Wrong implementation class: {name}")
        lane_id = classification.get("native_matrix")
        require(lane_id in LANES and name in LANES[lane_id][1], f"Wrong native matrix for {name}")
        require(isinstance(classification.get("qualification"), str) and bool(classification["qualification"].strip()),
                f"Missing implementation qualification: {name}")
        anchors = classification.get("anchors")
        require(isinstance(anchors, list) and bool(anchors), f"Missing implementation anchors: {name}")
        for anchor in anchors:
            check_anchor(anchor, f"{name}/implementation")
    return {"status": "passed", "reports": len(REPORTS), "native_matrices": len(LANES),
            "per_matrix": matrix_stats,
            "native_cells": sum(x["native_cells"] for x in matrix_stats.values()),
            "native_anchor_occurrences": native_occurrences,
            "implementation_anchor_occurrences": anchor_occurrences - native_occurrences,
            "unique_source_anchors": len(seen_anchors), "anchored_source_files": len(source_cache),
            "boundary": "Editorial inventory and source/hash consistency only. Native dimensions differ; counts are not votes, novelty scores, independent confirmations, proof correctness, or usability measurements."}


def validate():
    """Read-only entry point for the package-level validator."""
    result = validate_data(read_json(INDEX))
    result["index_sha256"] = digest(INDEX)
    return result


def create():
    """Explicit initial index construction; preserves all native semantics."""
    require(not INDEX.exists(), "Existing convergence index is never refreshed implicitly")
    primary, folded = canonical_register()
    owned_path = SYNTHESIS / LANES["alder-bryony-clover"][0]
    owned = read_json(owned_path)
    corrections = {}
    for readings in owned["reports"].values():
        for cell in readings.values():
            for anchor in cell["anchors"]:
                old = anchor["path"]
                require(old.casefold() in folded, f"Unknown owned source path: {old}")
                canonical = folded[old.casefold()]
                if old != canonical:
                    anchor["path"] = canonical
                    corrections[old] = canonical
    if corrections:
        owned["path_case_normalization"] = {
            "reason": "Canonical TitleCase report folders from source-register.json; editorial marks, qualifications, line numbers and excerpts are unchanged. No reproduction outputs or receipts were modified.",
            "paths": corrections,
        }
        owned_path.write_text(json.dumps(owned, indent=2) + "\n", encoding="utf-8")
    matrices = {}
    index = {"schema": "round4-native-convergence-index-1", "input_commit": PIN,
             "nature": "Editorial index of three native matrices. Their differing dimensions and qualifications are preserved; no common voting grid, vote counts, novelty score, or empirical independence is inferred.",
             "source_register": {"path": "source-register.json", "sha256": digest(REGISTER)},
             "implementation_classes": {
                 "support_antichain": "Finite propositional sufficient-support antichains; mathematical interpretations and real Lean grounding remain separate.",
                 "concrete_grounding": "Restricted interpreted term grammar with actual finite grounding and first-proof closure.",
                 "behavioral_frontend": "Restricted list-source interpretation and admissible observation-domain certificates with concrete Lean exports.",
                 "diagnostic_and_semilinear": "Finite typed grounding, first-proof closure, diagnostic leaves, and supplied semilinear observation images.",
             }, "native_matrices": {}, "reports": {}}
    for lane_id, (relative, names) in LANES.items():
        path = SYNTHESIS / relative
        native = read_json(path)
        matrices[lane_id] = native
        index["native_matrices"][lane_id] = {"path": relative, "sha256": digest(path),
                "reports": list(names), "native_dimensions": native["dimensions"]}
    specs = {
        "Alder": ("support_antichain", ["support_antichain", "semantic_binding"],
                  "Inclusion-minimal offered supports with immutable proof DAGs, lexical scope, separate replay, and conditional propositional export. Starts from ground opaque atoms; it does not bind arithmetic or analytic rules to Lean semantics."),
        "Bryony": ("support_antichain", ["support_antichain", "semantic_binding"],
                   "Inclusion-minimal offered supports and exact full-snapshot proof-tree replay with conditional propositional export. First proof retained per equal support; general dependent grounding and mathematical registration are proposed."),
        "Clover": ("concrete_grounding", ["grounding", "semantic_binding"],
                   "Source-derived endomorphism arena and goal-triggered grounding over seven concrete semantic rules. Retains one proof per atom and immediate unresolved routes, not minimal support families. Export/Lean acceptance and complete-document status remain separate."),
        "Fennel": ("support_antichain", ["frontier", "bounded"],
                   "Named proof-root support antichains with implemented rule allowlists, proof replay, and capped partial outcomes. Registry atoms are opaque and Lean exports have explicit implication hypotheses; no real Lean grounding."),
        "Heather": ("behavioral_frontend", ["admissibility", "checker"],
                    "Restricted list language, affine interpretation, admissible-domain certificates and concrete negative witnesses/Lean goals. Its small readiness resolver is not a general antichain engine, and exported source correctness is distinct from model acceptance."),
        "Juniper": ("support_antichain", ["frontier", "bounded"],
                    "Offered-support antichains with distinct conditional-derivation and finite-coverage checking; interrupted runs retain sound routes without claiming complete globally minimal inventories. Supplied Lean export is generic implication assembly."),
        "Laurel": ("support_antichain", ["alternative_minimality", "bounded_grounding"],
                   "Minimal residual-support frontiers over ground opaque atoms, independent replay and honest partial-result limits. No general Lean theorem grounding; an empty export carries no theorem evidence."),
        "Rowan": ("diagnostic_and_semilinear", ["residual_contract", "admissible_observations"],
                  "Finite typed generation and first-proof closure plus diagnostic leaf frontiers and semilinear image checks. A diagnostic leaf list need not be a sufficient support; supplied image/candidate models are not a verified source bridge. No Lean file supplied."),
        "Sorrel": ("support_antichain", ["alternative_minimality", "residual_contract"],
                   "Total-assumption support antichains and replayable conditional plans, with missing premises computed relative to available facts. CLI route selection and budgeted-family wording require the scoped corrections documented by the review."),
    }
    for name, (category, selected_dimensions, qualification) in specs.items():
        lane_id = next(k for k, (_, names) in LANES.items() if name in names)
        readings = matrices[lane_id]["reports"][name]
        anchors = []
        for dimension in selected_dimensions:
            path, line, _ = parse_anchor(readings[dimension]["anchors"][0])
            text = (ROOT / path).read_text(encoding="utf-8-sig").splitlines()[line - 1].strip()
            anchors.append({"path": path, "line": line, "excerpt": text})
        index["reports"][name] = {"implementation_class": category, "native_matrix": lane_id,
                                 "anchors": anchors, "qualification": qualification}
    validate_data(index)
    INDEX.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create", action="store_true", help="Create the initial index; refuses to overwrite it")
    args = parser.parse_args()
    if args.create:
        create()
    print(json.dumps(validate(), indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as error:
        print(f"Convergence validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
