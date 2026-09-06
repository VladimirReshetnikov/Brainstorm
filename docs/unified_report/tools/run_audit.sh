#!/usr/bin/env bash
# Reproduce the corpus audit reported in Section 3 of unified_report.pdf.
# Usage: bash run_audit.sh /path/to/ProveIt
# Writes audit_results.json and audit_summary.txt beside this script.
set -euo pipefail
root="${1:?usage: run_audit.sh <ProveIt-root>}"
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
sample=()
while IFS= read -r line; do
  case "$line" in ''|'#'*) continue;; esac
  sample+=("$root/$line")
done < sample_manifest.txt
python audit_proveit.py "$root/Analysis/FabiusFunction/Lean/FabiusFunction" --sample "${sample[@]}" | tee audit_summary.txt
