"""Verify round-two source identities and the 9-by-8 proposal crosswalk.

Read-only by default. Optional --json writes only a validation receipt. This is
structural/provenance validation, not PDF parity, mathematical proof checking,
language implementation testing, or verification of a reviewer's interpretation.
Requires Python 3.10+ and pypdf for PDF page-count metadata.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pypdf

ROOT = Path(__file__).resolve().parents[4]
SYNTHESIS = ROOT / "docs/round-2/synthesis"
EXPECTED_BASE = "f333ff6cefc8b1f5c9aae79613d10ef95a7ba928"
EXPECTED_REPORTS = {"accord", "cadence", "concord", "facet", "locus", "meridian", "noema", "prism", "vantage"}
EXPECTED_FEATURES = {"R", "O", "G", "V", "D", "L", "P", "E"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def safe_source(path: str) -> Path:
    result = (ROOT / path).resolve()
    require(result.is_relative_to(ROOT), f"Source path escapes repository: {path}")
    require(not Path(path).is_absolute(), f"Source path is not repository relative: {path}")
    require(result.is_file(), f"Missing source file: {path}")
    return result


def read_blobs(queries: list[str]) -> dict[str, tuple[str, bytes]]:
    """Read exact committed bytes in one read-only Git process."""
    unique = list(dict.fromkeys(queries))
    process = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT,
                             input=("\n".join(unique) + "\n").encode(),
                             capture_output=True, check=True)
    output, offset, result = process.stdout, 0, {}
    for query in unique:
        end = output.index(b"\n", offset)
        header = output[offset:end].decode().split()
        require(len(header) == 3 and header[1] == "blob", f"Expected committed blob: {query}: {header}")
        blob, _, size_text = header
        size = int(size_text)
        start, stop = end + 1, end + 1 + size
        raw = output[start:stop]
        require(len(raw) == size and output[stop:stop+1] == b"\n", f"Malformed Git batch result: {query}")
        require(hashlib.sha1(f"blob {size}\0".encode() + raw).hexdigest() == blob,
                f"Git blob identity mismatch: {query}")
        result[query] = (blob, raw)
        offset = stop + 1
    require(offset == len(output), "Unexpected additional Git batch output")
    return result


def source_sections(lines: list[str]) -> dict[str, tuple[int, int]]:
    headings, section, subsection, appendix = [], 0, 0, False
    for line_number, line in enumerate(lines, 1):
        if line.startswith(r"\appendix"):
            appendix, section, subsection = True, 0, 0
        match = re.match(r"\\(section|subsection)\{", line)
        if not match:
            continue
        level = 1 if match[1] == "section" else 2
        if level == 1:
            section, subsection = section + 1, 0
        else:
            subsection += 1
        number = chr(64 + section) if appendix else str(section)
        if level == 2:
            number += f".{subsection}"
        headings.append((number, level, line_number))
    boundaries = {}
    for index, (number, level, start) in enumerate(headings):
        end = next((later_start - 1 for _, later_level, later_start in headings[index+1:]
                    if later_level <= level), len(lines))
        boundaries[number] = (start, end)
    return boundaries


def validate() -> dict:
    register = json.loads((SYNTHESIS / "source-register.json").read_text(encoding="utf-8"))
    convergence = json.loads((SYNTHESIS / "convergence.json").read_text(encoding="utf-8"))
    require(register["schema_version"] == convergence["schema_version"] == 1, "Unsupported register schema")
    require(register["source_base_commit"] == convergence["source_base_commit"] == EXPECTED_BASE,
            "Unexpected pinned source base")
    require(register["required_ancestor_of_review_head"] == EXPECTED_BASE, "Unexpected ancestry requirement")
    head = git("rev-parse", "HEAD").decode().strip()
    ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", EXPECTED_BASE, head], cwd=ROOT)
    require(ancestry.returncode == 0, "Merged source base is not an ancestor of current HEAD")
    packages = register["packages"]
    require(len(packages) == 9 and {p["id"] for p in packages} == EXPECTED_REPORTS,
            "Expected exactly the nine round-two report packages")
    require(register["package_count"] == 9, "Incorrect package count")
    all_files = [f for p in packages for f in p["files"]]
    require(len(all_files) == register["tracked_package_file_count"], "Incorrect tracked package-file count")
    require(len({f["path"] for f in all_files}) == len(all_files), "Duplicate package source file")
    previous = register["previous_syntheses"]
    require(len(previous) == 2, "Expected two separately classified previous syntheses")
    files = all_files + [f for p in previous for f in p["current_files"]]
    queries = [f'{f["git_commit"]}:{f["path"]}' for f in files]
    queries += [f'{p["revision_cited_by_round_two"]}:{p["tex_path_at_cited_revision"]}' for p in previous]
    blobs = read_blobs(queries)
    pdf_pages, line_cache = {}, {}
    for entry in files:
        path = entry["path"]
        require(entry["git_commit"] == EXPECTED_BASE, f"Source has unexpected commit: {path}")
        blob, raw = blobs[f"{EXPECTED_BASE}:{path}"]
        current = safe_source(path)
        data = current.read_bytes()
        require(blob == entry["git_blob_sha1"], f"Committed blob SHA mismatch: {path}")
        require(hashlib.sha256(raw).hexdigest() == entry["git_blob_sha256"], f"Committed SHA-256 mismatch: {path}")
        require(len(raw) == entry["git_blob_size_bytes"], f"Committed byte length mismatch: {path}")
        require(hashlib.sha256(data).hexdigest() == entry["worktree_sha256"], f"Working source SHA-256 mismatch: {path}")
        require(len(data) == entry["worktree_size_bytes"], f"Working source byte length mismatch: {path}")
        if "line_count" in entry:
            lines = data.decode("utf-8-sig").splitlines()
            require(len(lines) == entry["line_count"], f"Line count mismatch: {path}")
            if path.endswith(".tex"):
                line_cache[path] = lines
        if "pdf_pages" in entry:
            pages = len(pypdf.PdfReader(current).pages)
            require(pages == entry["pdf_pages"], f"PDF metadata page count mismatch: {path}")
            pdf_pages[path] = pages
    for package in packages:
        tracked = set(git("ls-tree", "-r", "--name-only", EXPECTED_BASE, "--", package["directory"]).decode().splitlines())
        require(tracked == {f["path"] for f in package["files"]}, f"Incomplete pinned package inventory: {package['id']}")
        require(package["tex_path"] in line_cache, f"Missing primary TeX: {package['id']}")
        require(pdf_pages[package["pdf_path"]] == package["pdf_pages"], f"Inconsistent package page count: {package['id']}")
    for prior in previous:
        query = f'{prior["revision_cited_by_round_two"]}:{prior["tex_path_at_cited_revision"]}'
        blob, original = blobs[query]
        require(blob == prior["tex_blob_sha1_at_cited_revision"], f"Prior-synthesis blob mismatch: {prior['id']}")
        require(hashlib.sha256(original).hexdigest() == prior["tex_blob_sha256_at_cited_revision"],
                f"Prior-synthesis SHA-256 mismatch: {prior['id']}")
        current_tex = next(f for f in prior["current_files"] if f["path"].endswith(".tex"))
        relocated = blobs[f'{EXPECTED_BASE}:{current_tex["path"]}'][1]
        require((original == relocated) == prior["same_tex_content_after_relocation"],
                f"Prior-synthesis relocation claim mismatch: {prior['id']}")
    require(set(convergence["feature_definitions"]) == EXPECTED_FEATURES, "Incorrect feature identifiers")
    require(convergence["report_count"] == 9 and convergence["feature_count"] == 8 and convergence["cell_count"] == 72,
            "Incorrect convergence dimensions")
    rows = convergence["rows"]
    require(len(rows) == 72, "Expected 72 crosswalk cells")
    pairs = [(r["report_id"], r["feature"]) for r in rows]
    require(len(set(pairs)) == 72 and set(pairs) == {(p,f) for p in EXPECTED_REPORTS for f in EXPECTED_FEATURES},
            "Crosswalk has missing or duplicate report/feature cells")
    by_id = {p["id"]: p for p in packages}
    ref_count = 0
    for row in rows:
        package = by_id[row["report_id"]]
        path = package["tex_path"]
        require(row["report"] == package["name"] and row["tex_path"] == path, "Crosswalk report/source mismatch")
        require(row["evidence_scope"] == "proposal-only", "Crosswalk inflates evidence beyond proposals")
        require(row["status"] in {"explicit", "partial", "absent"}, "Unknown crosswalk status")
        require(bool(row.get("qualification")), "Missing evidence qualification")
        require(row["status"] == "absent" or bool(row["references"]), "Supported cell has no reference")
        lines = line_cache[path]
        sections = source_sections(lines)
        for reference in row["references"]:
            start, end = reference["tex_lines"]
            require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
                    f"Out-of-bounds source citation: {row['report']} {row['feature']} {reference}")
            section = reference["section"]
            require(section in sections, f"Unknown source section: {row['report']} {section}")
            section_start, section_end = sections[section]
            require(section_start <= start <= end <= section_end,
                    f"Citation extends outside its stated section: {row['report']} {row['feature']} {reference}; section {sections[section]}")
            ref_count += 1
    require(dict(Counter(r["status"] for r in rows)) == convergence["status_counts"], "Status-count mismatch")
    return {
        "status": "passed", "validated_utc": datetime.now(timezone.utc).isoformat(),
        "source_base_commit": EXPECTED_BASE, "current_head": head, "base_is_ancestor": True,
        "package_count": 9, "tracked_package_files_verified": len(all_files),
        "prior_syntheses_classified_separately": 2, "crosswalk_cells_verified": 72,
        "crosswalk_references_in_bounds_and_stated_sections": ref_count,
        "crosswalk_status_counts": convergence["status_counts"], "pdf_page_metadata": pdf_pages,
        "scope": "Source hashes, exact committed blobs, ancestry, inventory, PDF page-count metadata, and crosswalk structure/source bounds only. No PDF parity, mathematical validity, interpretation correctness, proof-language implementation, or empirical benefit is certified.",
        "python": sys.version, "pypdf": pypdf.__version__,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="optional output validation receipt")
    args = parser.parse_args()
    try:
        result = validate()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Source verification FAILED: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
