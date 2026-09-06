"""Assemble source identity and proposal-only convergence registers.

Reads pinned Git objects/current source files. Writes only the round-two
synthesis registers; never runs proof tools or changes a source package.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

import pypdf

ROOT = Path(__file__).resolve().parents[5]
SYNTHESIS = ROOT / "docs/round-2/synthesis"
BASE = "f333ff6cefc8b1f5c9aae79613d10ef95a7ba928"
PRIOR_REVIEW_BASE = "494be9d5ab41a5ae219fc6f800e6aee3c93bce39"
PACKAGES = [
    ("accord", "Accord", "Accord: A Certified Worksheet Language", "accord"),
    ("cadence", "Cadence", "Cadence: A Mathematical Language of Certified Transformations", "cadence"),
    ("concord", "Concord", "Concord: A Query-Directed Proof Language with a Verified Symbolic Core", "concord"),
    ("facet", "Facet", "Facet: Mathematical Objects with Certified Computational Presentations", "facet"),
    ("locus", "Locus", "Locus: Mathematical Workspaces and Certified Computation", "Locus_Proof_Language_Proposal"),
    ("meridian", "Meridian", "Meridian: A Mathematical Language with Certified Computation", "meridian"),
    ("noema", "Noema", "Noema: Mathematical Objects, Scoped Relations, and Certified Computation", "noema"),
    ("prism", "Prism", "Prism: A Proof Language with Certified Mathematical Computation", "prism"),
    ("vantage", "Vantage", "Vantage: Mathematical Objects, Explicit Views, and Certified Computation", "vantage"),
]
FEATURES = {
    "R": "Computation result states its exact relation or guarantee.",
    "O": "Fixed mathematical objects have certified representations or observations.",
    "G": "Scoped guards compose without silently strengthening the intended meaning.",
    "V": "Verified algorithms or checkers are distinguished from concrete execution authority and reification.",
    "D": "Ordinary theorem and definition packages have separately identified operational policy.",
    "L": "Providers use exact host targets; displayed edits replay exactly; negative outcomes retain their actual strength.",
    "P": "Publication retains evidence and states its replay boundary.",
    "E": "Evaluation shares assets with Lean, uses negative neighbors, and specifies measurable outcomes and stopping decisions.",
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def file_record(path: str, commit: str = BASE) -> dict:
    raw = git("show", f"{commit}:{path}")
    current = ROOT / path
    worktree = current.read_bytes()
    blob = git("rev-parse", f"{commit}:{path}").decode().strip()
    filtered = git("hash-object", f"--path={path}", "--", path).decode().strip()
    if filtered != blob:
        raise RuntimeError(f"Working source differs from pinned commit: {path}")
    result = {
        "path": path, "git_commit": commit, "git_blob_sha1": blob,
        "git_blob_sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob_size_bytes": len(raw),
        "worktree_sha256": hashlib.sha256(worktree).hexdigest(),
        "worktree_size_bytes": len(worktree),
    }
    if path.endswith((".tex", ".py", ".md", ".json", ".sh", ".ps1")):
        result["line_count"] = len(worktree.decode("utf-8-sig").splitlines())
    if path.endswith(".pdf"):
        result["pdf_pages"] = len(pypdf.PdfReader(current).pages)
        result["pdf_metadata_scope"] = "Page count only; not rendered, not checked for TeX/PDF parity."
    return result


def own_crosswalk() -> dict:
    references = {
        "Facet": {
            "R": [("4.2",415,448),("4.3",450,470)],
            "O": [("4.1",378,413),("4.2",415,423),("5.6",599,611)],
            "G": [("5.2",510,529),("5.3",536,554),("5.4",556,578)],
            "V": [("6.1",614,644),("6.2",646,673),("6.3",675,687)],
            "D": [("5.1",489,508),("12.1",1319,1333),("12.2",1335,1349),("12.3",1351,1367)],
            "L": [("11.3",1212,1255),("11.4",1257,1282),("11.5",1284,1304)],
            "P": [("13.2",1389,1400),("13.3",1402,1415),("13.4",1417,1443),("13.5",1445,1463)],
            "E": [("14.3",1501,1538),("15.1",1564,1595),("15.2",1597,1618),("15.4",1640,1649),("D",1885,1934)],
        },
        "Locus": {
            "R": [("4.1",448,474),("4.4",528,558)],
            "O": [("3.1",351,373),("5.1",598,620),("5.4",678,688)],
            "G": [("4.5",560,577),("5.3",644,676),("3.3",395,411)],
            "V": [("4.1",463,474),("4.2",476,504),("4.3",506,526),("4.6",579,593)],
            "D": [("5.1",598,620),("12.7",1670,1682),("A.3",1968,1988)],
            "L": [("11.3",1445,1470),("11.4",1472,1495),("11.5",1497,1517),("11.6",1519,1537)],
            "P": [("12.2",1572,1592),("12.3",1594,1611),("12.5",1630,1649),("12.6",1651,1668)],
            "E": [("13.3",1741,1772),("14.1",1777,1795),("14.2",1797,1815),("14.3",1817,1841),("14.4",1843,1853)],
        },
        "Meridian": {
            "R": [("4.1",444,494),("4.2",497,529),("4.3",532,544)],
            "O": [("3.1",308,326),("7.1",904,923),("11.5",1586,1593)],
            "G": [("6.2",739,772),("6.3",775,810),("6.4",813,833),("7.2",926,952)],
            "V": [("5.1",568,605),("5.2",608,635),("5.3",638,662)],
            "D": [("3.4",398,417),("7.1",904,923),("7.5",1015,1034)],
            "L": [("11.2",1492,1516),("11.3",1519,1540),("11.4",1543,1575),("11.5",1578,1600)],
            "P": [("12.2",1649,1672),("12.3",1675,1696),("12.4",1699,1727)],
            "E": [("14.1",1819,1848),("14.2",1851,1871),("14.3",1874,1926),("14.4",1931,1942)],
        },
    }
    notes = {
        "R": "Exact relation strength belongs to the request/result, independently of evidence-production route.",
        "O": "Retained semantic object with exact or observational presentations; limited replacement permissions.",
        "G": "Actual intermediate objects and instantiated guards remain scoped; sufficient conditions do not become silent assumptions.",
        "V": "Program correctness, concrete returned bytes, reification, and actual evidence execution remain distinct.",
        "D": "Stable theorem/definition interfaces coexist with algorithms/checkers; role and policy metadata are separately versioned.",
        "L": "Exact host-owned target and origin; displayed replacement independently replayed; search failure is not logical negation.",
        "P": "All formal assertions and accepted data need evidence; pinned replay is distinct from upgrades and open search.",
        "E": "Shared libraries and algorithms, nearby invalid cases, measured work and comprehension, optional no-new-syntax outcome.",
    }
    rows = []
    for report, cells in references.items():
        for feature, refs in cells.items():
            rows.append({
                "report": report, "feature": feature, "status": "explicit",
                "references": [{"section": s, "tex_lines": [a,b]} for s,a,b in refs],
                "note": notes[feature],
                "qualification": (
                    "Proposal-level commitment; no language implementation. Numerical usability thresholds await a pilot."
                    if feature == "E" else
                    "Proposal-level commitment; the companion is finite Python arithmetic, not implementation validation."
                ),
            })
    return {"scope": "Source-stated proposals, not implemented or experimentally confirmed capabilities.",
            "source_checkout": BASE, "feature_definitions": FEATURES, "rows": rows}


def main() -> None:
    subprocess.run(["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=ROOT, check=True)
    packages = []
    for ident, name, title, folder in PACKAGES:
        directory = f"docs/round-2/ideas/{folder}"
        paths = git("ls-tree", "-r", "--name-only", BASE, "--", directory).decode().splitlines()
        files = [file_record(path) for path in paths]
        tex_path, pdf_path = f"{directory}/{ident}.tex", f"{directory}/{ident}.pdf"
        packages.append({
            "id": ident, "name": name, "title": title, "directory": directory,
            "tex_path": tex_path, "pdf_path": pdf_path,
            "pdf_pages": next(f["pdf_pages"] for f in files if f["path"] == pdf_path),
            "files": files,
        })
    previous = []
    for ident, title, old, current in [
        ("primary-round-one", "Mathematical Ideas, Checked Evidence", "docs/synthesis/unified-report", "docs/round-1/synthesis/unified-report"),
        ("comparative-round-one", "Nine Blueprints for a Mathematician's Proof Language over Lean", "docs/unified_report/unified_report", "docs/round-1/unified_report/unified_report"),
    ]:
        files = [file_record(current + ext) for ext in (".tex", ".pdf")]
        original = git("show", f"{PRIOR_REVIEW_BASE}:{old}.tex")
        current_blob = git("show", f"{BASE}:{current}.tex")
        previous.append({
            "id": ident, "title": title, "current_files": files,
            "revision_cited_by_round_two": PRIOR_REVIEW_BASE,
            "tex_path_at_cited_revision": old + ".tex",
            "tex_blob_sha1_at_cited_revision": git("rev-parse", f"{PRIOR_REVIEW_BASE}:{old}.tex").decode().strip(),
            "tex_blob_sha256_at_cited_revision": hashlib.sha256(original).hexdigest(),
            "same_tex_content_after_relocation": original == current_blob,
            "role": "Prior synthesis/context, not one of the nine new source reports or an independent vote.",
        })
    register = {
        "schema_version": 1, "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "source_base_commit": BASE, "required_ancestor_of_review_head": BASE,
        "scope": "Source identities, tracked-package inventory, and PDF page-count metadata only. No PDF/TeX parity, Lean proof, or language implementation claim.",
        "hash_note": "Git blob hashes describe canonical committed bytes; worktree hashes separately include checkout line-ending representation.",
        "pdf_metadata_tool": f"pypdf {pypdf.__version__}",
        "package_count": len(packages), "tracked_package_file_count": sum(len(p["files"]) for p in packages),
        "packages": packages, "previous_syntheses": previous,
    }
    write_json(SYNTHESIS / "source-register.json", register)
    own = own_crosswalk()
    own_path = Path(__file__).resolve().parent / "crosswalk.json"
    write_json(own_path, own)
    lanes = [
        SYNTHESIS / "evidence/accord-cadence-concord/crosswalk.json",
        own_path,
        SYNTHESIS / "evidence/noema-prism-vantage/crosswalk.json",
    ]
    rows = []
    by_name = {p["name"]: p for p in packages}
    for lane in lanes:
        data = json.loads(lane.read_text(encoding="utf-8"))
        for source_row in data["rows"]:
            row = dict(source_row)
            package = by_name[row["report"]]
            row["report_id"] = package["id"]
            row["tex_path"] = package["tex_path"]
            row["review_lane_source"] = lane.relative_to(ROOT).as_posix()
            row["evidence_scope"] = "proposal-only"
            rows.append(row)
    order = {p["name"]: i for i,p in enumerate(packages)}
    rows.sort(key=lambda row: (order[row["report"]], list(FEATURES).index(row["feature"])))
    convergence = {
        "schema_version": 1, "source_base_commit": BASE,
        "scope": "Explicit support within nine source proposals. Correlated authorship/task/examples; no independence, consensus probability, implemented-capability, or usability inference.",
        "feature_definitions": FEATURES,
        "status_meanings": {
            "explicit": "The complete stated commitment is present as a design proposal; qualifications remain attached.",
            "partial": "Only part of the conjunction is supported; identify the missing part.",
            "absent": "No support identified after review; absence is not opposition.",
        },
        "report_count": len(packages), "feature_count": len(FEATURES), "cell_count": len(rows),
        "status_counts": dict(Counter(row["status"] for row in rows)),
        "rows": rows,
    }
    write_json(SYNTHESIS / "convergence.json", convergence)
    print(json.dumps({"packages": len(packages), "source_files": register["tracked_package_file_count"],
                      "pages": {p["name"]:p["pdf_pages"] for p in packages},
                      "crosswalk_cells": len(rows), "status_counts": convergence["status_counts"]}, indent=2))


if __name__ == "__main__":
    main()
