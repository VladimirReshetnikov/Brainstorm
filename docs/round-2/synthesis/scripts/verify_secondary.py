"""Read-only provenance validation for the imported secondary round-two synthesis.

Validate exact pinned Git blobs, separate checkout hashes, tracked inventories,
ancestry, text line counts, and PDF page-count metadata. No original script is
executed and no output file is written. This does not certify report judgments,
historical log completeness, current Lean execution, mathematics, or PDF parity.
Requires Python 3.10+, Git, and pypdf; validate() returns a JSON-compatible dict.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import PurePosixPath
import subprocess
import sys

import pypdf

from verify_sources import ROOT, git, read_blobs, require, safe_source

EXPECTED_BASE = "84af03f49f89a31b47ff3416ccdbc9180fd6b438"
DIRECTORY = "docs/round-2/unified_report"
REGISTER = ROOT / "docs/round-2/synthesis/evidence/secondary-review/source-register.json"
FILE_ROLES = {
    "README.md": "secondary-synthesis-documentation",
    "build.sh": "historical-build-script",
    "experiments/lean/Axioms.lean": "historical-lean-experiment-source",
    "experiments/lean/LinComb.lean": "historical-lean-experiment-source",
    "experiments/lean/LinComb.log": "historical-compiler-log",
    "experiments/lean/PolyCert.lean": "historical-lean-experiment-source",
    "experiments/lean/PolyCert.run1.log": "historical-compiler-log",
    "experiments/lean/PolyCert.run2.log": "historical-compiler-log",
    "experiments/lean/README.md": "historical-experiment-documentation",
    "experiments/lean/Supply.lean": "historical-lean-experiment-source",
    "experiments/lean/Supply.log": "historical-compiler-log",
    "feature_matrix.csv": "editorial-feature-coding",
    "negative_suite.csv": "editorial-mutation-coding",
    "question_tally.csv": "editorial-question-coding",
    "tools/make_tables.py": "editorial-table-generator-source",
    "unified_report.pdf": "secondary-synthesis-rendering",
    "unified_report.tex": "secondary-synthesis-source",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inventory(revision: str) -> set[str]:
    return set(git("ls-tree", "-r", "-z", "--name-only", revision, "--", DIRECTORY)
               .decode("utf-8").rstrip("\0").split("\0"))


def validate() -> dict:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    require(register["schema_version"] == 1, "Unsupported secondary register schema")
    require(register["source_base_commit"] == EXPECTED_BASE, "Unexpected secondary source pin")
    require(register["required_ancestor_of_review_head"] == EXPECTED_BASE,
            "Unexpected secondary ancestry requirement")
    require(register["directory"] == DIRECTORY, "Unexpected secondary source directory")
    require(register["classification"] == "secondary-synthesis" and
            register["contribution_to_proposal_count"] == 0,
            "Secondary synthesis must not count as a tenth proposal")
    require(register["historical_execution"]["evidence_status"] == "imported-historical-records",
            "Historical logs must not be labeled fresh execution")
    require(register["historical_execution"]["certifies_current_execution"] is False and
            register["historical_execution"]["certifies_general_checker_soundness"] is False,
            "Imported experiment evidence is overstated")
    head = git("rev-parse", "HEAD").decode().strip()
    ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", EXPECTED_BASE, head],
                              cwd=ROOT, capture_output=True)
    require(ancestry.returncode == 0, "Secondary source pin is not an ancestor of current HEAD")
    expected = {f"{DIRECTORY}/{path}" for path in FILE_ROLES}
    files = register["files"]
    paths = [entry["path"] for entry in files]
    require(register["tracked_file_count"] == len(files) == len(expected) == 17,
            "Expected all 17 imported tracked files")
    require(len(paths) == len(set(paths)) and set(paths) == expected,
            "Duplicate, missing, or unexpected secondary source entry")
    require(inventory(EXPECTED_BASE) == expected, "Pinned secondary inventory differs")
    require(inventory(head) == expected, "Current HEAD secondary inventory differs")
    tracked = set(git("ls-files", "-z", "--", DIRECTORY).decode("utf-8")
                  .rstrip("\0").split("\0"))
    require(tracked == expected, "Current index secondary inventory differs")
    queries = [f"{revision}:{path}" for revision in dict.fromkeys([EXPECTED_BASE, head])
               for path in paths]
    blobs = read_blobs(queries)
    pdf_pages = {}
    for entry in files:
        path = entry["path"]
        relative = PurePosixPath(path)
        require(not relative.is_absolute() and ".." not in relative.parts and "\\" not in path,
                f"Nonportable source path: {path}")
        require(entry["git_commit"] == EXPECTED_BASE, f"Unexpected file pin: {path}")
        role = FILE_ROLES[str(relative.relative_to(DIRECTORY))]
        require(entry["role"] == role, f"Incorrect imported artifact role: {path}")
        blob, raw = blobs[f"{EXPECTED_BASE}:{path}"]
        require(blobs[f"{head}:{path}"][0] == blob, f"Current HEAD changed imported content: {path}")
        current = safe_source(path).read_bytes()
        require(blob == entry["git_blob_sha1"], f"Pinned Git blob SHA-1 mismatch: {path}")
        require(sha(raw) == entry["git_blob_sha256"], f"Pinned blob SHA-256 mismatch: {path}")
        require(len(raw) == entry["git_blob_size_bytes"], f"Pinned blob byte count mismatch: {path}")
        require(sha(current) == entry["worktree_sha256"], f"Checkout SHA-256 mismatch: {path}")
        require(len(current) == entry["worktree_size_bytes"], f"Checkout byte count mismatch: {path}")
        if path.endswith(".pdf"):
            require(current == raw, f"Imported PDF differs from committed bytes: {path}")
            pages = len(pypdf.PdfReader(BytesIO(current)).pages)
            require(pages == entry["pdf_pages"], f"PDF page-count metadata mismatch: {path}")
            require("line_count" not in entry, f"PDF should not have a text line count: {path}")
            pdf_pages[path] = pages
        else:
            require(current.replace(b"\r\n", b"\n") == raw.replace(b"\r\n", b"\n"),
                    f"Checkout differs beyond line-ending representation: {path}")
            require(len(raw.decode("utf-8-sig").splitlines()) == entry["git_blob_line_count"],
                    f"Pinned text line-count mismatch: {path}")
            require(len(current.decode("utf-8-sig").splitlines()) == entry["line_count"],
                    f"Checkout text line-count mismatch: {path}")
    return {
        "status": "passed", "validated_utc": datetime.now(timezone.utc).isoformat(),
        "source_base_commit": EXPECTED_BASE, "current_head": head, "base_is_ancestor": True,
        "classification": "secondary-synthesis", "contribution_to_proposal_count": 0,
        "tracked_files_verified": len(files), "historical_lean_sources": 4,
        "historical_compiler_logs": 4, "pdf_page_metadata": pdf_pages,
        "source_register_sha256": sha(REGISTER.read_bytes()),
        "scope": "Pinned Git objects, current HEAD/index tracked inventory, exact recorded checkout hashes, line-ending equivalence, text line counts, and PDF page-count metadata only. Imported logs remain historical records; no rerun, general checker soundness, report interpretation, mathematical validity, or TeX/PDF parity is certified.",
        "python": sys.version, "pypdf": pypdf.__version__,
    }


def main() -> int:
    try:
        result = validate()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Secondary provenance verification FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
