# Laurel / Rowan / Sorrel reproduction evidence

Input commit: `58ced1ce667b3ba1ed162a0c6280959536c8bc5f`.

`reproduce.py` copied all three author packages to `copies/`, then ran 12 inspected documented Python suite/demo commands using `-B`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONHASHSEED=0`, and `PYTHONIOENCODING=utf-8`. It refuses to overwrite existing copies. To repeat from scratch, use a new isolated output directory with the same relative root arrangement or change the runner's output location deliberately.

`receipt.json` records the exact executable/arguments, working directories, exit codes, timing, standard-stream paths/hashes, all original and copied-source hashes, and final generated hashes. All commands passed under Python 3.14.4. Input inventories contain 25 Laurel, 9 Rowan and 11 Sorrel files; all remained unchanged. No bytecode was generated.

`semantic_probes.py` runs four additional adversarial/contrast probes against the isolated copies. `verify_lane.py` records its exact command, standard streams, result/source hashes, repeats the input immutability check, and compares regenerated Lean/example JSON artifacts with the originals. `probe-receipt.json` distinguishes byte differences from text identity after universal-newline normalization. Fresh generated files use Windows line endings, so text identity must not be described as byte identity.

`semantic-probes.json` preserves the Rowan cyclic-conjunctive diagnostic frontier, Sorrel supported-route/export-selection mismatch, Laurel's sufficient-frontier contrast, and a partial antichain whose support is dominated after saturation. `SorrelSelectionProbe.lean` is an uncompiled-by-this-lane conditional Init-only export. Root owns any Lean compilation evidence.

Scope: Python model execution and static/mathematical review only. No Lean/Lake/TeX build, Git mutation, external repository mutation, real frontend, kernel-proved arithmetic rule, verified reifier, or authoring study is established by these receipts.
