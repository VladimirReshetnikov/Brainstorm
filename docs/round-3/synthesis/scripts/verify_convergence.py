"""Consolidate editorial source readings and verify their table and locators.

Default operation is read-only. --write regenerates only convergence.json and
crosswalk-table.tex. This does not re-code the reports or validate their claims.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
PIN = "58bb54219f494b29310ff77384732129411da887"
REPORTS = ["basalt", "fiber", "gneiss", "karst", "moraine", "obsidian",
           "schist", "tephra", "trellis"]
LANES = ["basalt-fiber-gneiss", "karst-moraine-obsidian", "schist-tephra-trellis"]
DIMENSIONS = {
    "core": "Conservative Lean elaboration",
    "anchor": "Same-object scoped evidence",
    "structures": "Structure data separated from proof properties",
    "behavior": "Dependent behavioral composition and consequence",
    "bounded": "Bounded property inference",
    "observation": "Explicit observation and transport guarantees",
    "leant": "Proof-linked behavioral synthesis",
    "checker": "Denotation, checker soundness, and original-target bridge",
    "fidelity": "Statement, method, and kernel truth distinguished",
    "evaluation": "Matched Lean baselines and stopping rules",
}
STATUSES = ("explicit", "partial", "absent")
MARKS = {"explicit": "E", "partial": "P", "absent": "A"}
# Routine review corrections made in the lane registers before consolidation.
# Preserve their history without silently repairing future invalid locators.
ANCHOR_CORRECTIONS = {
    "docs/round-3/ideas/gneiss/gneiss.tex:1521":
        "docs/round-3/ideas/gneiss/gneiss.tex:1522",
    "docs/round-3/ideas/schist/schist.tex:1565":
        "docs/round-3/ideas/schist/schist.tex:1579",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def consolidate() -> dict:
    register = json.loads((HERE / "source-register.json").read_text(encoding="utf-8"))
    assert register["source_commit"] == PIN
    registered = {row["path"]: row for row in register["files"]}
    reports = {}
    lanes = []
    for lane in LANES:
        path = HERE / "evidence" / lane / "convergence.json"
        raw = path.read_bytes()
        source = json.loads(raw)
        pin = source.get("input_pin", source.get("pinned_source_commit", source.get("pin")))
        assert pin == PIN, (lane, pin)
        path_relative = path.relative_to(ROOT).as_posix()
        lanes.append({"path": path_relative, "sha256": digest(raw),
                      "method": source.get("method", source.get("interpretation"))})
        source_reports = source["reports"]
        if isinstance(source_reports, list):
            source_reports = {row["report"]: row["dimensions"] for row in source_reports}
        for report, dimensions in source_reports.items():
            assert report in REPORTS and report not in reports, report
            assert set(dimensions) == set(DIMENSIONS), (report, dimensions.keys())
            cells = {}
            for dimension in DIMENSIONS:
                cell = dimensions[dimension]
                status = cell.get("status", cell.get("mark"))
                assert status in STATUSES, (report, dimension, status)
                assert isinstance(cell["qualification"], str) and cell["qualification"].strip()
                assert 1 <= len(cell["anchors"]) <= 3
                details = []
                normalized_anchors = []
                for original_anchor in cell["anchors"]:
                    assert original_anchor not in ANCHOR_CORRECTIONS, "Correct the lane locator instead of silently normalizing it"
                    anchor = original_anchor
                    normalized_anchors.append(anchor)
                    relative, line_text = anchor.rsplit(":", 1)
                    assert relative in registered, relative
                    row = registered[relative]
                    assert row["proposal"] == report, (report, anchor)
                    source_path = ROOT / relative
                    assert source_path.resolve().is_relative_to((ROOT / "docs/round-3/ideas").resolve())
                    contents = source_path.read_bytes()
                    assert digest(contents) == row["checkout_sha256"], relative
                    lines = contents.decode("utf-8-sig").splitlines()
                    line = int(line_text)
                    assert 1 <= line <= len(lines), anchor
                    assert lines[line - 1].strip(), ("blank source anchor", anchor)
                    details.append({"path": relative, "line": line,
                                    "line_text": lines[line - 1],
                                    "source_git_blob": row["git_blob"],
                                    "source_checkout_sha256": row["checkout_sha256"]})
                cells[dimension] = {"status": status, "mark": MARKS[status],
                                    "anchors": normalized_anchors,
                                    "source_review_anchors": cell["anchors"],
                                    "qualification": cell["qualification"],
                                    "anchor_details": details}
            reports[report] = {"source_review": path_relative, "dimensions": cells}
    assert set(reports) == set(REPORTS)
    reports = {name: reports[name] for name in REPORTS}
    per_dimension = {}
    total = Counter()
    for dimension in DIMENSIONS:
        counts = Counter(reports[name]["dimensions"][dimension]["status"] for name in REPORTS)
        per_dimension[dimension] = {status: counts[status] for status in STATUSES}
        total.update(counts)
    assert sum(total.values()) == 90
    return {
        "schema_version": 1, "source_commit": PIN,
        "method": "Consolidation of three editorial close-reading lanes, with original qualifications preserved. Marks describe articulated commitments, not implementation completeness, novelty, efficacy, or independent statistical votes.",
        "qualification_scope": "Qualifications retain the source-review wording about submitted artifacts. Fresh Lean compilation and subsequent evidence upgrades are recorded separately in evidence/lean and in the report; they do not change the design-commitment marks.",
        "status_definitions": {
            "explicit": "The report articulates this commitment with enough detail for the stated comparison dimension.",
            "partial": "A material part is articulated, but a component of this compound comparison dimension is not developed; read the qualification.",
            "absent": "The reading lane found no substantive treatment of this dimension, within its stated source scope.",
        },
        "dimensions": {key: {"column": f"D{i}", "description": text}
                       for i, (key, text) in enumerate(DIMENSIONS.items(), 1)},
        "source_reviews": lanes, "reports": reports,
        "anchor_corrections": {old: {"corrected": new, "reason": "The earlier lane locator pointed at a blank line. The lane was corrected to the substantive rendering/fidelity passage before consolidation; its qualification and mark were unchanged."}
                               for old, new in ANCHOR_CORRECTIONS.items()},
        "counts": {"reports": 9, "dimensions": 10, "cells": 90,
                   "total": {status: total[status] for status in STATUSES},
                   "per_dimension": per_dimension},
    }


def render_table(data: dict) -> str:
    rows = [
        "% Generated by scripts/verify_convergence.py --write; edit the reading records.",
        r"\begingroup\small",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.12}",
        r"\noindent Editorial marks: E = explicit, P = partial, A = absent.",
        r"These describe the proposed designs; they do not score novelty or implementation.",
        r"\begin{center}",
        r"\begin{tabular}{@{}p{0.85in}*{10}{>{\centering\arraybackslash}p{0.34in}}@{}}",
        r"\toprule",
        "Proposal & " + " & ".join(f"D{i}" for i in range(1, 11)) + r"\\",
        r"\midrule",
    ]
    for name in REPORTS:
        marks = [data["reports"][name]["dimensions"][dimension]["mark"] for dimension in DIMENSIONS]
        rows.append(name.capitalize() + " & " + " & ".join(marks) + r"\\")
    rows.append(r"\midrule")
    for status in STATUSES:
        values = [str(data["counts"]["per_dimension"][dimension][status]) for dimension in DIMENSIONS]
        rows.append(status.capitalize() + " & " + " & ".join(values) + r"\\")
    rows.extend([r"\bottomrule", r"\end{tabular}", r"\end{center}",
                 r"\noindent D1: conservative Lean elaboration; D2: same-object scoped evidence;",
                 r"D3: separate structure data and proof properties; D4: dependent behavioral",
                 r"composition and consequence; D5: bounded property inference; D6: explicit",
                 r"observation and transport guarantees; D7: proof-linked behavioral synthesis;",
                 r"D8: denotation, checker soundness, and original-target bridge; D9: statement,",
                 r"method, and kernel truth distinguished; D10: matched Lean baselines and stop rules.",
                 "",
                 r"\noindent Of 90 cells, 89 are explicit, one is partial, and none is absent.",
                 r"Obsidian explicitly develops behavioral application and dependent composition,",
                 r"but does not separately develop the full pre/postcondition consequence rule;",
                 r"its D4 mark is therefore partial under this compound criterion.",
                 r"All source locators and qualifications are retained in",
                 r"\href{convergence.json}{\texttt{convergence.json}}.",
                 r"The shared prompt and prior syntheses limit the independence of these readings.",
                 r"\endgroup", ""])
    assert data["counts"]["total"] == {"explicit": 89, "partial": 1, "absent": 0}, "Update the table prose if editorial coding changes"
    return "\n".join(rows)


def validate() -> dict:
    expected = consolidate()
    actual = json.loads((HERE / "convergence.json").read_text(encoding="utf-8"))
    assert actual == expected, "Consolidated JSON is stale or differs from its source reviews"
    actual_tex = (HERE / "crosswalk-table.tex").read_text(encoding="utf-8")
    assert actual_tex == render_table(expected), "TeX crosswalk is stale or differs from its JSON"
    anchors = sum(len(cell["anchors"]) for report in actual["reports"].values()
                  for cell in report["dimensions"].values())
    return {"status": "passed", "source_commit": PIN, "validated_anchor_occurrences": anchors,
            **actual["counts"], "scope": "Editorial coding and artifact consistency, not claim verification or novelty scoring."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        data = consolidate()
        (HERE / "convergence.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        (HERE / "crosswalk-table.tex").write_text(render_table(data), encoding="utf-8")
    print(json.dumps(validate(), indent=2))
