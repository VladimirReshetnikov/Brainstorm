"""Reproduce the imported synthesis's editorial tables without writing to its package."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
SOURCE = ROOT / "docs/round-2/unified_report"
PIN = "84af03f49f89a31b47ff3416ccdbc9180fd6b438"
REPORTS = ["Locus", "Accord", "Cadence", "Concord", "Facet", "Meridian", "Noema", "Prism", "Vantage"]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

def inventory():
    return {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p)
            for p in SOURCE.rglob("*") if p.is_file()}

before = inventory()
(OUT / "tools").mkdir(parents=True, exist_ok=True)
copy = OUT / "tools/make_tables.py"
shutil.copyfile(SOURCE / "tools/make_tables.py", copy)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
run = subprocess.run([sys.executable, "-B", str(copy)], cwd=OUT, env=env,
                     capture_output=True, timeout=60)
(OUT / "stdout.txt").write_bytes(run.stdout)
(OUT / "stderr.txt").write_bytes(run.stderr)
assert run.returncode == 0, run.stderr.decode(errors="replace")
after = inventory()
assert before == after, "An original package file changed during reproduction"

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

matches = {}
for filename in ["feature_matrix.csv", "negative_suite.csv", "question_tally.csv"]:
    matches[filename] = {"byte_identical": (SOURCE / filename).read_bytes() == (OUT / filename).read_bytes(),
                         "newline_normalized_identical": (SOURCE / filename).read_text(encoding="utf-8") == (OUT / filename).read_text(encoding="utf-8"),
                         "parsed_rows_identical": read_csv(SOURCE / filename) == read_csv(OUT / filename),
                         "source_sha256": digest(SOURCE / filename), "reproduced_sha256": digest(OUT / filename)}
    assert matches[filename]["parsed_rows_identical"]
matrix = read_csv(OUT / "feature_matrix.csv")
suite = read_csv(OUT / "negative_suite.csv")
questions = read_csv(OUT / "question_tally.csv")
assert len({row["id"] for row in matrix}) == len(matrix)
assert len({row["id"] for row in suite}) == len(suite)
assert len({row["id"] for row in questions}) == len(questions)
for row in matrix:
    counts = Counter(row[report] for report in REPORTS)
    assert set(counts) <= {"Y", "P", "N"}
    assert int(row["explicit"]) == counts["Y"]
    assert int(row["explicit_or_partial"]) == counts["Y"] + counts["P"]
for row in suite:
    assert int(row["suites"]) == sum(bool(row[report]) for report in REPORTS)

provenance = defaultdict(list)
for row in suite:
    for report in REPORTS:
        for local_id in filter(None, row[report].split(",")):
            provenance[(report, local_id)].append(row["id"])

paths = {r: ROOT / "docs/round-2/ideas" / ("Locus_Proof_Language_Proposal" if r == "Locus" else r.lower()) / ("locus.tex" if r == "Locus" else r.lower() + ".tex") for r in REPORTS}
source_rows = {}
for report, path in paths.items():
    lines = path.read_text(encoding="utf-8").splitlines()
    if report in {"Cadence", "Concord", "Noema"}:
        lo, hi = {"Cadence": (1661, 1688), "Concord": (997, 1007), "Noema": (803, 820)}[report]
        # These source tables have unnumbered rows. The imported rN is ordinal.
        starts = [i for i in range(lo, hi + 1) if " & " in lines[i - 1]]
        source_rows[report] = {f"r{index + 1}": {"line": line, "text": lines[line - 1]} for index, line in enumerate(starts)}
    else:
        prefix = {"Locus": "T", "Accord": "A", "Facet": "T", "Meridian": "[DCVAFLP]", "Prism": "N", "Vantage": "V"}[report]
        found = {}
        for i, line in enumerate(lines, 1):
            match = re.match(rf"^({prefix}[0-9]+)\s*&", line)
            if match:
                assert match[1] not in found, (report, match[1])
                found[match[1]] = {"line": i, "text": line}
        source_rows[report] = found
    for entry in source_rows[report].values():
        entry["tex_path"] = str(path.relative_to(ROOT)).replace("\\", "/")

missing_source_ids = [{"report": r, "local_id": i, "canonical_ids": cs} for (r, i), cs in provenance.items() if i not in source_rows[r]]
unmapped_source_ids = [{"report": r, "local_id": i, **entry} for r, entries in source_rows.items() for i, entry in entries.items() if (r, i) not in provenance]
assert not missing_source_ids
source_locators = [{"report": r, "local_id": i, "canonical_ids": provenance.get((r, i), []), **entry} for r, entries in source_rows.items() for i, entry in entries.items()]
(OUT / "negative-source-locators.json").write_text(json.dumps(source_locators, indent=2) + "\n", encoding="utf-8")

tex = (SOURCE / "unified_report.tex").read_text(encoding="utf-8")
table_marks = []
for line in tex.splitlines():
    match = re.match(r"^([A-F][0-9]+) & .*? & ((?:\\[YPN][ypn](?: & )?){9}) & ([0-9]+)\\\\$", line)
    if match:
        marks = re.findall(r"\\([YPN])[ypn]", match[2])
        table_marks.append((match[1], marks, int(match[3])))
assert len(table_marks) == len(matrix), len(table_marks)
for code, marks, count in table_marks:
    row = next(x for x in matrix if x["id"] == code)
    assert marks == [row[r] for r in REPORTS] and count == int(row["explicit"])

mutation_tex_rows = []
for line in tex.splitlines():
    match = re.match(r"^(M[0-9]+) & .* & ([0-9]+)\\\\$", line)
    if match:
        row = next(x for x in suite if x["id"] == match[1])
        assert int(match[2]) == int(row["suites"])
        mutation_tex_rows.append(match[1])
assert len(mutation_tex_rows) == 68 and set(mutation_tex_rows) == {r["id"] for r in suite}

noninherited = [row for row in matrix if row["group"] != "Inherited foundation"]
input_names = ["tools/make_tables.py", "feature_matrix.csv", "negative_suite.csv", "question_tally.csv", "unified_report.tex"]
input_blobs = {}
for name in input_names:
    relative = "docs/round-2/unified_report/" + name
    pinned_blob = git("rev-parse", PIN + ":" + relative)
    assert git("hash-object", "--path", relative, relative) == pinned_blob
    input_blobs[name] = pinned_blob
result = {
    "schema_version": 1, "review_kind": "Editorial tally reproduction and targeted source audit, not an independent recoding of 522 feature cells",
    "review_head": git("rev-parse", "HEAD"), "source_commit": PIN,
    "source_commit_is_ancestor": subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", PIN, "HEAD"]).returncode == 0,
    "python_version": sys.version, "command": [sys.executable, "-B", str(copy)], "cwd": str(OUT),
    "returncode": run.returncode, "original_package_files_unchanged": before == after,
    "original_package_files": before, "generated_csv_comparisons": matches,
    "canonical_input_blobs": input_blobs, "current_inputs_match_pinned_blobs": True,
    "feature_matrix": {
        "rows": len(matrix), "cells": len(matrix) * len(REPORTS),
        "unanimous": sum(int(r["explicit"]) == 9 for r in matrix),
        "at_least_seven_explicit": sum(int(r["explicit"]) >= 7 for r in matrix),
        "inherited_rows": len(matrix) - len(noninherited), "noninherited_rows": len(noninherited),
        "noninherited_unanimous": sum(int(r["explicit"]) == 9 for r in noninherited),
        "noninherited_at_least_seven": sum(int(r["explicit"]) >= 7 for r in noninherited),
        "marks": dict(Counter(r[report] for r in matrix for report in REPORTS)),
        "noninherited_unanimous_ids": [r["id"] for r in noninherited if int(r["explicit"]) == 9],
        "tex_marks_and_counts_match_csv": True,
        "automated_source_mining": False, "per_cell_source_locators_in_original": False,
        "novelty_comparison_in_generator": False},
    "negative_suite": {
        "canonical_rows": len(suite), "report_canonical_incidence_count": sum(int(r["suites"]) for r in suite),
        "expanded_local_reference_occurrences": sum(len(cs) for cs in provenance.values()),
        "unique_local_source_rows_referenced": len(provenance),
        "source_table_row_count": sum(len(v) for v in source_rows.values()),
        "tex_mutation_rows": len(mutation_tex_rows), "tex_mutation_ids_and_counts_match_csv": True,
        "source_table_rows_by_report": {r: len(entries) for r, entries in source_rows.items()},
        "at_least_seven_suites": [r["id"] for r in suite if int(r["suites"]) >= 7],
        "five_or_six_suites": [r["id"] for r in suite if 5 <= int(r["suites"]) <= 6],
        "singleton_rows": [r["id"] for r in suite if int(r["suites"]) == 1],
        "source_rows_mapped_more_than_once": [{"report": r, "local_id": i, "canonical_ids": cs} for (r, i), cs in provenance.items() if len(cs) > 1],
        "missing_source_ids": missing_source_ids, "unmapped_source_rows": unmapped_source_ids,
        "executable_mutation_tests": False, "positive_neighbor_records": False},
    "question_tally": {"rows": len(questions), "rows_with_unanimous_in_variation": sum("Unanimous" in r["variation"] for r in questions),
                       "per_report_answer_records": False, "response_denominators": False, "computed_modes": False},
    "not_run": ["Lean", "Lake", "PDF generation", "original package generator in original path"],
}
(OUT / "receipt.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in ["feature_matrix", "negative_suite", "question_tally"]}, indent=2))
