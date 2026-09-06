"""Generate the appendix's 72 representative source locators from convergence.json."""

import json
from pathlib import Path


SYNTHESIS = Path(__file__).resolve().parents[2]
data = json.loads((SYNTHESIS / "convergence.json").read_text(encoding="utf-8"))
rows = data["rows"]
assert len(rows) == 72
lookup = {(row["report"], row["feature"]): row for row in rows}
reports = list(dict.fromkeys(row["report"] for row in rows))
assert len(reports) == 9 and len(lookup) == 72
assert set(lookup) == {(report, feature) for report in reports for feature in "ROGVDLPE"}


def cell(report, features):
    locators = []
    for feature in features:
        ref = lookup[report, feature]["references"][0]
        start, end = ref["tex_lines"]
        locators.append(
            rf"\textbf{{{feature}}}: \S{{}}{ref['section']}, lines {start}--{end}"
        )
    return " \\newline\n".join(locators)


output = [
    "% Generated from the first source reference of every convergence.json cell.",
    "% Exactly 72 proposal-level cells; the full JSON retains all references and qualifications.",
    r"\begingroup",
    r"\small",
    r"\begin{longtable}{@{}P{.8in}P{2.45in}P{2.45in}@{}}",
    r"\toprule",
    r"Report & R/O/G/V source locators & D/L/P/E source locators\\",
    r"\midrule",
    r"\endfirsthead",
    r"\toprule",
    r"Report & R/O/G/V source locators & D/L/P/E source locators\\",
    r"\midrule",
    r"\endhead",
    r"\midrule",
    r"\multicolumn{3}{r}{\emph{Continued on next page}}\\",
    r"\endfoot",
    r"\bottomrule",
    r"\endlastfoot",
]
for index, report in enumerate(reports):
    if index:
        output.append(r"\addlinespace[.65em]")
    output.append(rf"\textbf{{{report}}} & " + cell(report, "ROGV") + " &\n"
                  + cell(report, "DLPE") + r"\\")
output.extend([r"\end{longtable}", r"\endgroup", ""])
target = SYNTHESIS / "crosswalk-table.tex"
target.write_text("\n".join(output), encoding="utf-8")
print(f"Wrote {target}: 9 reports, 72 representative locators.")
