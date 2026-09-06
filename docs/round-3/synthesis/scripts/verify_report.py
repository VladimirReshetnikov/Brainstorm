"""Validate the round-3 synthesis and its retained evidence, without rerunning it.

Requires pypdf and the two sibling validators. Git provenance checks are read-only.
No Lean, companion, LaTeX, service, or external repository execution occurs here.
validation.json is replaced only after every check, including the independently
recorded visual review, succeeds. A previous receipt is not current validation.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

from pypdf import PdfReader
from verify_sources import validate as validate_sources
from verify_convergence import validate as validate_convergence

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
PIN = "58bb54219f494b29310ff77384732129411da887"
LEANT_PIN = "823259f7e3c6d24e990d3f48f78c4f1c4f88059e"
DJEX_PIN = "22da13fd69ce54dd1e47db9faba28eb2869629d1"
TEX_INPUTS = {"unified-report.tex", "crosswalk-table.tex"}
LEAN_COUNTS = {"basalt": (2, 2), "fiber": (3, 3), "gneiss": (2, 2),
               "karst": (12, 11), "moraine": (16, 3), "schist": (8, 8),
               "tephra": (6, 3)}
PROPEXT_TARGETS = {
    "MoraineReference.LengthExpr.model_sound",
    "MoraineReference.LengthExpr.promote_model_spec",
    "Schist.AffineCertificate.eval_nf",
    "Schist.AffineCertificate.check_sound",
    "Schist.AffineCertificate.original_target",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(base, relative):
    """Resolve a receipt path within its documented root, independently of cwd."""
    require(isinstance(relative, str) and relative, "Empty receipt path")
    require(not PureWindowsPath(relative).is_absolute(), f"Expected relative path: {relative}")
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()), f"Receipt path escapes its root: {relative}")
    require(path.is_file(), f"Missing retained file: {path}")
    return path


def bound_file(base, relative, expected):
    path = local(base, relative)
    require(isinstance(expected, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected),
            f"Invalid SHA-256: {relative}")
    require(sha(path) == expected.lower(), f"Hash mismatch: {path}")
    return path


def text_file(path):
    return path.read_text(encoding="utf-8-sig")


def normalize(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text))


def validate_document():
    build = read(HERE / "evidence/pdf-build-receipt.json")
    require(set(build["tex_inputs"]) == TEX_INPUTS, "Build must bind exactly both TeX inputs")
    for path, digest in build["tex_inputs"].items():
        bound_file(HERE, path, digest)
    require(build.get("tex_sha256", build["tex_inputs"]["unified-report.tex"])
            == build["tex_inputs"]["unified-report.tex"], "Main TeX hashes disagree")
    pdf = bound_file(HERE, "unified-report.pdf", build["pdf_sha256"])
    require(build["passes"] == 3, "Three strict LaTeX passes are not recorded")
    log_path = local(HERE, "evidence/pdf-build-log.txt")
    if "log_sha256" in build:
        bound_file(HERE, "evidence/pdf-build-log.txt", build["log_sha256"])
    log = text_file(log_path)
    bad_log = (r"^!|LaTeX Error|Fatal error|Emergency stop|Overfull|Missing character|"
               r"undefined|Rerun to get|Label\(s\) may have changed|"
               r"destination with the same identifier|duplicate.*destination")
    require(not re.search(bad_log, log, re.I | re.M), "Final LaTeX log has errors or unresolved output")
    require("Output written on " in log, "Final LaTeX log has no completed PDF")
    # The package uses ordinary literal commands. This is a structural check,
    # not a general TeX parser; final engine diagnostics are checked above.
    tex = "\n".join(text_file(HERE / name) for name in sorted(TEX_INPUTS))
    tex = re.sub(r"(?<!\\)%[^\n]*", "", tex)
    inputs = re.findall(r"\\(?:input|include)\{([^}]+)\}", tex)
    require(inputs == ["crosswalk-table.tex"], "Unexpected TeX include graph")
    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    require(len(labels) == len(set(labels)), "Duplicate TeX label")
    refs = re.findall(r"\\(?:ref|pageref|eqref|autoref)\*?\{([^}]+)\}", tex)
    require(set(refs) <= set(labels), f"Undefined TeX reference: {set(refs) - set(labels)}")
    bib = re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", tex)
    require(len(bib) == len(set(bib)), "Duplicate bibliography key")
    groups = re.findall(r"\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}", tex)
    cites = {key.strip() for group in groups for key in group.split(",")}
    require(cites <= set(bib), f"Missing bibliography keys: {cites - set(bib)}")
    links = []
    for target in re.findall(r"\\href\{([^}]+)\}", tex):
        url = urlsplit(target)
        if url.scheme in {"http", "https", "mailto"}:
            continue
        require(not url.scheme and not url.netloc, f"Unrecognized hyperlink scheme: {target}")
        path = (HERE / unquote(url.path)).resolve()
        require(path.is_relative_to(ROOT.resolve()) and path.is_file(), f"Broken local PDF link: {target}")
        links.append(target)
    reader = PdfReader(pdf)
    texts = [page.extract_text() or "" for page in reader.pages]
    require(texts and all(len(t.strip()) > 70 for t in texts), "Unexpected nearly blank PDF page")
    extracted = normalize("\n".join(texts))
    require("\ufffd" not in extracted, "Replacement character in extracted PDF text")
    phrases = ["Executive assessment", "Corpus, provenance, and standards of evidence",
               "Where the reports converge and where their choices differ",
               "A common semantic core", "Inference that can be predictable",
               "Observations, constructions, and exact meaning",
               "Worked case I: exact quotients without a vacuous benchmark",
               "Worked case II: finite observations of infinite operators",
               "Worked case III: analytical contracts and strength of conclusions",
               "Relational interfaces and a correction to the corpus",
               "Leant: from candidate identity to proved behavior",
               "Certified computation: what is now actually checked",
               "An implementation that tests the authoring hypothesis",
               "Evaluation that can change the design decision",
               "Questions for the next iteration", "Convergence crosswalk",
               "Earlier questions, restated with current answers", "Validation and reproducibility"]
    for phrase in phrases:
        require(phrase in extracted, f"Expected PDF section missing: {phrase}")
    return {"status": "passed", "pdf_pages": len(texts), "pdf_sha256": sha(pdf),
            "tex_inputs": build["tex_inputs"], "recorded_latex_passes": 3,
            "final_build_log_sha256": sha(log_path), "labels": len(labels),
            "bibliography_entries": len(bib), "local_links_checked": len(links),
            "required_section_phrases": len(phrases), "all_pages_nonblank": True,
            "scope": "Current bytes match the retained build receipt; final log and PDF text checked. No rebuild or independent reconstruction of the recorded three passes."}


def axiom_inventory(log):
    require(not re.search(r"\berror:|declaration uses ['\"]sorry|sorryAx", log, re.I),
            "Lean log contains an error or admitted proof")
    inventory = {}
    pattern = r"^'([^']+)' (?:does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])\s*$"
    for name, raw in re.findall(pattern, log, re.M):
        axioms = sorted({item.strip() for item in raw.split(",") if item.strip()})
        require(set(axioms) <= {"propext"}, f"Unexpected audited axioms for {name}: {axioms}")
        require(name not in inventory or inventory[name] == axioms, f"Conflicting repeated axiom query: {name}")
        inventory[name] = axioms
    return inventory


def validate_lean():
    receipt = read(HERE / "evidence/lean/receipt.json")
    require("version 4.32.0," in receipt["version"], "Unexpected Lean version")
    require(receipt["LEAN_NUM_THREADS"] == "0", "Lean environment receipt differs")
    rows = receipt["cases"]
    require(len(rows) == 7 and {r["proposal"] for r in rows} == set(LEAN_COUNTS), "Expected seven distinct original Lean files")
    registered = read(HERE / "source-register.json")["files"]
    originals = {r["path"] for r in registered if r["path"].endswith(".lean")}
    require({r["source"] for r in rows} == originals, "Lean receipt does not cover all original Lean files")
    combined, per_file = {}, {}
    for row in rows:
        name = row["proposal"]
        require(row["exit_code"] == 0 and row["audit"]["exit_code"] == 0, f"Unsuccessful Lean execution: {name}")
        original = bound_file(ROOT, row["source"], row["source_sha256"])
        copied = bound_file(HERE, row["copied_source"], row["source_sha256"])
        require(original.read_bytes() == copied.read_bytes(), f"Changed original Lean copy: {name}")
        require(len(row["command"]) == 2 and row["command"][0] == receipt["executable"]
                and PureWindowsPath(row["command"][1]).name == copied.name, f"Unexpected Lean command: {name}")
        original_log = text_file(bound_file(HERE, row["log"], row["log_sha256"]))
        original_inventory = axiom_inventory(original_log)
        audit = row["audit"]
        audit_source = text_file(bound_file(HERE, audit["source"], audit["source_sha256"]))
        original_text = text_file(original)
        require(audit_source.startswith(original_text), f"Axiom harness changed original source: {name}")
        suffix = audit_source[len(original_text):]
        suffix = re.sub(r"--[^\n]*", "", suffix)
        queries = re.findall(r"^\s*#print axioms ([\w.]+)\s*$", suffix, re.M)
        require(queries == audit["targets"], f"Axiom harness queries differ: {name}")
        require(not re.sub(r"^\s*#print axioms [\w.]+\s*$", "", suffix, flags=re.M).strip(),
                f"Axiom harness contains additional code: {name}")
        audited = axiom_inventory(text_file(bound_file(HERE, audit["log"], audit["log_sha256"])))
        require(set(audit["targets"]) <= set(audited), f"Missing requested axiom outputs: {name}")
        require(all(audited.get(k) == v for k, v in original_inventory.items()), f"Original/audit logs disagree: {name}")
        declarations = re.findall(r"^\s*theorem\s+([\w.]+)", original_text, re.M)
        require((len(declarations), len(audited)) == LEAN_COUNTS[name], f"Lean declaration/audit counts differ: {name}")
        source_queries = re.findall(r"^\s*#print axioms ([\w.]+)\s*$", audit_source, re.M)
        require(all(any(target == query or target.endswith("." + query) for query in source_queries)
                    for target in audited), f"Unbound axiom output: {name}")
        require(not set(combined) & set(audited), f"Duplicate target across Lean files: {name}")
        combined.update(audited)
        per_file[name] = {"source": row["source"], "named_theorem_declarations": len(declarations),
                          "unique_audited_declarations": len(audited), "axioms": audited}
    require(len(combined) == 32, "Expected 32 unique audited original declarations")
    require({name for name, axioms in combined.items() if axioms} == PROPEXT_TARGETS,
            "The five propext-only audit targets differ")
    extra = read(HERE / "evidence/lean/synthesis-receipt.json")
    require(extra["exit_code"] == 0 and extra["theorems"] == 2 and extra["version"] == receipt["version"],
            "Synthesis Lean receipt differs")
    extra_source = bound_file(HERE, "evidence/lean/SynthesisChecks.lean", extra["source_sha256"])
    extra_log = bound_file(HERE, "evidence/lean/SynthesisChecks.log", extra["log_sha256"])
    synthesis_axioms = axiom_inventory(text_file(extra_log))
    expected = {"Round3Synthesis.refute_via_realization", "Round3Synthesis.reverse_via_observations"}
    require(set(synthesis_axioms) == expected and not any(synthesis_axioms.values()), "Synthesis axiom inventory differs")
    require(len(re.findall(r"^\s*theorem\s+", text_file(extra_source), re.M)) == 2, "Synthesis theorem count differs")
    require(set(re.findall(r"^\s*#print axioms ([\w.]+)\s*$", text_file(extra_source), re.M)) == expected,
            "Synthesis axiom queries differ")
    return {"status": "passed", "version": receipt["version"], "original_files": 7,
            "named_theorem_declarations": sum(x[0] for x in LEAN_COUNTS.values()),
            "unique_audited_original_declarations": 32, "audited_without_axioms": 27,
            "audited_with_only_propext": 5, "files": per_file,
            "additional_synthesis_theorems": synthesis_axioms,
            "scope": "Unchanged source copies, successful retained execution receipts, and named axiom-query logs. The 49 named theorem declarations are not all axiom-audited; 32 distinct original declarations are. The two synthesis implications retain their explicit premises. No new Lean run, frontend verification, or external repository build."}


def validate_input_hashes(mapping, reports):
    register = read(HERE / "source-register.json")
    expected = {r["path"]: r["checkout_sha256"] for r in register["files"] if r["proposal"] in reports}
    require(mapping == expected, f"Lane input inventory differs: {reports}")
    for path, digest in mapping.items():
        bound_file(ROOT, path, digest)


def successful_python(row):
    require(row["exit_code"] == 0 and "-B" in row["command"], f"Python success/-B missing: {row['report']}")


def unittest_success(log, count):
    require(re.search(rf"^Ran {count} tests? in ", log, re.M) and re.search(r"^OK\s*$", log, re.M),
            f"Expected {count} passing unittest methods in retained log")
    require(not re.search(r"^FAILED|^ERROR:|^FAIL:|Traceback \(most recent call last\)", log, re.M),
            "Python log contains failed tests")


def stream_logs(lane, row, run_dir):
    return {stream: text_file(bound_file(lane, f"{run_dir}/{stream}.txt", row[f"{stream}_sha256"]))
            for stream in ("stdout", "stderr")}


def validate_python():
    counts = {}
    lane = HERE / "evidence/basalt-fiber-gneiss"
    data = read(lane / "reproduction.json")
    require(data["input_pin"] == PIN and data["source_files_unchanged"] is True, "First Python lane provenance differs")
    validate_input_hashes(data["source_files"], {"basalt", "fiber", "gneiss"})
    require(len(data["runs"]) == 3 and {r["report"] for r in data["runs"]} == {"basalt", "fiber", "gneiss"}, "First lane coverage differs")
    for row in data["runs"]:
        successful_python(row)
        name = row["report"]
        source = bound_file(ROOT, row["source"], row["source_sha256"])
        inside_report = source.relative_to(ROOT / f"docs/round-3/ideas/{name}").as_posix()
        bound_file(lane, f"runs/{name}/{inside_report}", row["copied_source_sha256"])
        require(row["source_sha256"] == row["copied_source_sha256"], f"Changed Python copy: {name}")
        logs = stream_logs(lane, row, f"runs/{name}")
        result = read(bound_file(lane, row["receipt"], row["receipt_sha256"]))
        require(result == row["result"] and result["status"] == "passed", f"Python result differs: {name}")
        if name == "fiber":
            require(result["groups"] == len(result["counts"]) == 31 and result["finite_checks"] == sum(result["counts"].values()) == 1298,
                    "Fiber group/check counts differ")
            require(json.loads(logs["stdout"]) == result, "Fiber output differs from receipt")
            counts[name] = {"groups": 31, "finite_checks": 1298}
        else:
            number = result["test_methods_run"] if name == "basalt" else result["tests"]
            require(number == {"basalt": 24, "gneiss": 32}[name] and result["failures"] == result["errors"] == 0,
                    f"Python test result differs: {name}")
            unittest_success(logs["stderr"], number)
            counts[name] = {"test_methods": number}
    lane = HERE / "evidence/karst-moraine-obsidian"
    data = read(lane / "reproduction.json")
    require(data["pinned_source_commit"] == PIN and data["input_files_unchanged"] is True and data["source_bytes_match_pin"] is True,
            "Second Python lane provenance differs")
    validate_input_hashes(data["input_files"], {"karst", "moraine", "obsidian"})
    require(len(data["runs"]) == 3 and {r["report"] for r in data["runs"]} == {"karst", "moraine", "obsidian"}, "Second lane coverage differs")
    for row in data["runs"]:
        successful_python(row)
        name = row["report"]
        require(row["cwd"] == f"docs/round-3/synthesis/evidence/karst-moraine-obsidian/runs/{name}", f"Unexpected Python cwd: {name}")
        require(len(row["copied_sources"]) == (2 if name == "moraine" else 1), f"Python copy count differs: {name}")
        for copy in row["copied_sources"]:
            source = bound_file(ROOT, copy["source"], copy["sha256"])
            require(source.is_relative_to(ROOT / f"docs/round-3/ideas/{name}"), f"Wrong report's Python source: {name}")
            bound_file(lane, copy["copy"], copy["sha256"])
        logs = stream_logs(lane, row, f"runs/{name}")
        if name == "moraine":
            require(row["tests"] == 32, "Moraine method count differs")
            unittest_success(logs["stderr"], 32)
            names = re.findall(r"^(test_\w+)\s+.*\.\.\. ok\s*$", logs["stderr"], re.M)
            require(names == row["passed_named_tests"] and len(set(names)) == 32, "Moraine named test log differs")
            counts[name] = {"test_methods": 32}
        else:
            result = json.loads(logs["stdout"])
            if name == "karst":
                require(result["status"] == "all finite checks passed" and len(result["groups"]) == 8,
                        "Karst group result differs")
                require(all(g["status"] == "passed" for g in result["groups"]), "Karst has a failed group")
                require([{k: g[k] for k in ("name", "cases")} for g in result["groups"]] == row["groups"], "Karst recorded counts differ")
                counts[name] = {"groups": row["groups"]}
            else:
                require(result["test_count"] == row["test_count"] == len(result["cases"]) == 608,
                        "Obsidian case count differs")
                require(all(c["passed"] is True for c in result["cases"]), "Obsidian has a failed case")
                require(dict(Counter(c["kind"] for c in result["cases"])) == row["counts_by_kind"] == result["counts_by_kind"],
                        "Obsidian case kinds differ")
                counts[name] = {"cases": 608, "counts_by_kind": row["counts_by_kind"]}
    lane = HERE / "evidence/schist-tephra-trellis"
    data = read(lane / "receipt.json")
    require(data["pin"] == PIN and data["sources_unchanged"] is True and data["scripts_inspected_before_execution"] is True,
            "Third Python lane provenance differs")
    validate_input_hashes(data["source_hashes_before_and_after"], {"schist", "tephra", "trellis"})
    require(len(data["runs"]) == 3 and {r["report"] for r in data["runs"]} == {"schist", "tephra", "trellis"}, "Third lane coverage differs")
    for row in data["runs"]:
        successful_python(row)
        name = row["report"]
        source = bound_file(ROOT, row["source"], row["source_sha256"])
        require(row["working_directory"] == f"docs/round-3/synthesis/evidence/schist-tephra-trellis/{name}", f"Unexpected Python cwd: {name}")
        require(row["copied_source_sha256"] == row["source_sha256"], f"Changed Python copy: {name}")
        bound_file(lane, f"{name}/{source.name}", row["copied_source_sha256"])
        require({source.name, "stdout.txt", "stderr.txt"} <= set(row["artifacts"]), f"Incomplete Python artifacts: {name}")
        for artifact, digest in row["artifacts"].items():
            bound_file(lane / name, artifact, digest)
        number = {"schist": 10, "tephra": 23, "trellis": 31}[name]
        require(row["tests"] == number, f"Third-lane count differs: {name}")
        if name != "trellis":
            unittest_success(text_file(lane / name / "stderr.txt"), number)
            if name == "tephra":
                result = read(lane / name / "check_results.json")
                require(result["status"] == "passed" and result["test_methods"] == number
                        and result["failures"] == result["errors"] == 0, "Tephra JSON result differs")
            counts[name] = {"test_methods": number}
        else:
            result = read(lane / name / "results.json")
            require(result["status"] == "all reference tests passed" and result["test_count"] == len(result["tests"]) == number,
                    "Trellis JSON result differs")
            require(all(t["expected_acceptance"] == t["observed_acceptance"] for t in result["tests"]), "Trellis has a mismatched acceptance")
            positive = sum(t["expected_acceptance"] is True for t in result["tests"])
            require(result["positive_count"] == positive == 9 and result["negative_count"] == number - positive == 22,
                    "Trellis positive/negative counts differ")
            require("31 tests passed (9 positive, 22 negative)." in text_file(lane / name / "stdout.txt"), "Trellis stdout differs")
            counts[name] = {"cases": number, "positive": positive, "negative": number - positive}
    return {"status": "passed", "lanes": 3, "successful_retained_runs": 9, "counts_by_report": counts,
            "scope": "Retained exit codes, source/copy/log hashes, and result consistency. No companion rerun or universal correctness proof; counts have different units and are not summed across reports."}


def validate_leant():
    lane = HERE / "evidence/leant-review"
    data = read(lane / "source-register.json")
    require(data["pinned_commit"] == data["live_head_at_snapshot"] == LEANT_PIN, "Leant snapshot pin differs")
    require(len(data["files"]) == len({r["source_path"] for r in data["files"]}) == 9, "Leant snapshot file inventory differs")
    for row in data["files"]:
        path = bound_file(lane, row["retained_copy"], row["sha256"])
        raw = path.read_bytes()
        require(len(raw) == row["bytes"] and len(raw.decode("utf-8").splitlines()) == row["lines"], f"Leant snapshot dimensions differ: {path}")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], f"Leant retained Git blob differs: {path}")
        require(row["url"] == f"https://github.com/VladimirReshetnikov/Leant/blob/{LEANT_PIN}/{row['source_path']}", "Leant source URL differs")
        scope = row["read_scope"]
        require(scope["kind"] == "full" and scope["line_start"] == 1 and scope["line_end"] == row["lines"], "Leant static read range differs")
    djex = read(lane / "djex-register.json")
    require(djex["parent_pin"] == LEANT_PIN and djex["pinned_commit"] == DJEX_PIN
            and djex["parent_gitlink"] == f"160000 commit {DJEX_PIN}\tlib/Djex", "Djex recorded Gitlink differs")
    excerpt = bound_file(lane, djex["retained_excerpt"], djex["excerpt_sha256"])
    ranges = djex["ranges"]
    require(ranges == [[321, 390], [1341, 1480]], "Djex recorded reviewed ranges differ")
    numbers = [int(n) for n in re.findall(r"^(\d+):", text_file(excerpt), re.M)]
    require(numbers == [n for start, end in ranges for n in range(start, end + 1)], "Djex excerpt line coverage differs")
    require(all(1 <= start <= end <= djex["full_blob_lines"] for start, end in ranges), "Djex excerpt bounds invalid")
    return {"status": "passed", "leant_pin": LEANT_PIN, "retained_full_files": 9,
            "djex_pin": DJEX_PIN, "djex_reviewed_ranges": ranges,
            "scope": "Retained Leant full-file byte/Git-blob consistency and Djex excerpt hash/line coverage. No live repository comparison, external execution, or claim that the unretained full Djex blob has been revalidated."}


def validate_visual(document):
    visual = read(HERE / "evidence/visual-review.json")
    require(visual["status"] == "passed", "Visual review did not pass")
    require(visual["pdf_sha256"] == document["pdf_sha256"], "Visual review is for another PDF")
    require(visual["pages_reviewed"] == list(range(1, document["pdf_pages"] + 1)), "Visual review does not cover every PDF page")
    return {"status": "passed", "pdf_sha256": document["pdf_sha256"],
            "pages_reviewed": visual["pages_reviewed"],
            "scope": "Independent visual-review receipt bound to every page of this PDF; this script does not perform visual inspection."}


def validate():
    provenance = validate_sources()
    convergence = validate_convergence()
    document = validate_document()
    lean = validate_lean()
    python = validate_python()
    leant = validate_leant()
    visual = validate_visual(document)
    evidence = {p.relative_to(HERE).as_posix(): sha(p)
                for p in sorted((HERE / "evidence").rglob("*")) if p.is_file()}
    package = {name: sha(HERE / name) for name in
               ["source-register.json", "convergence.json", "unified-report.tex", "crosswalk-table.tex", "unified-report.pdf"]}
    package.update({p.relative_to(HERE).as_posix(): sha(p) for p in sorted((HERE / "scripts").glob("*.py"))})
    return {"status": "passed", "validated_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "Read-only provenance, editorial-crosswalk structure, document/build/visual receipt binding, and retained execution-evidence consistency. This validation reruns no experiment or build and does not certify general mathematics, the proposed frontend, service correctness, or authoring productivity.",
            "source_validation": provenance, "convergence_validation": convergence,
            "document_validation": document, "lean_validation": lean,
            "python_validation": python, "leant_snapshot_validation": leant,
            "visual_review_validation": visual, "package_sha256": package, "evidence_sha256": evidence}


def main():
    result = validate()
    # No output receipt is created or replaced on any earlier failure.
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "pdf_pages": result["document_validation"]["pdf_pages"],
                      "source_commit": PIN, "convergence_cells": 90, "original_lean_files": 7,
                      "unique_original_axiom_audits": 32, "additional_lean_theorems": 2,
                      "retained_python_runs": 9, "retained_leant_full_files": 9,
                      "all_pages_visually_reviewed": True, "evidence_files_hashed": len(result["evidence_sha256"]),
                      "receipt": "validation.json"}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, AssertionError, subprocess.CalledProcessError) as exc:
        print(f"Report validation FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
