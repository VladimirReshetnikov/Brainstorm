# Fennel / Heather / Juniper reproduction lane

Inputs are pinned to Brainstorm `58ced1ce667b3ba1ed162a0c6280959536c8bc5f` and remain read-only. This lane uses Python 3.14.4 on Windows. No Lean/Lake, LaTeX/PDF build, external repository execution, network call, or Git mutation was performed. Fresh Lean checking belongs to the root synthesis receipts.

`reproduce.py` captures all 66 original package files, validates their SHA256 values against immutable Git blobs, copies only runtime sources byte-for-byte into `runs/`, and executes the documented suites/demos there. `reproduction.json` retains exact commands, working directories, exit codes, timeouts, stream hashes, copied-source hashes, produced-artifact hashes, and before/after input hashes. All 14 commands exited successfully; no `.pyc` files were produced. Logs are in `logs/`.

`audit.py` reads those byte-identical copies. It compares 27 generated JSON/Lean artifacts to the author outputs, checks 128 shared finite Horn profiles across Fennel and Juniper, tests coverage and admissible-domain mutations, and reproduces stale positive Lean files after a negative second request in a reused output directory. `audit.json` retains the exact limitations, successful assertions, subprocess commands, and artifact hashes. `audit.stdout.txt` is the captured final execution output and `audit.stderr.txt` is empty. Intentional stale-output fixtures live under `adversarial/*-reuse/`; they must not be interpreted as current successful proofs of their second requests.

The reference scripts were read before execution. Runtime source files are unchanged. Harness-only adaptations were isolated working directories, `-B`, `PYTHONDONTWRITEBYTECODE=1`, explicit UTF-8 environment variables, and canonical title-case Git input paths. An initial inventory-only attempt stopped on lower-case Git paths before execution; the corrected harness is retained. No proposal source repair was made here.

From the repository root, the reproducible invocations are:

```powershell
python -B docs/round-4/synthesis/evidence/fennel-heather-juniper/reproduce.py
python -B docs/round-4/synthesis/evidence/fennel-heather-juniper/audit.py
```

These commands write only this lane's evidence outputs. A later reproduction should retain its own receipt rather than interpret older timings as current measurements. JSON artifact comparisons ignore only explicitly listed Python/platform/time fields; Lean comparisons normalize CRLF to LF and nothing else.

The full editorial reading is in `../../review-notes/fennel-heather-juniper.md`. `convergence.json` contains twelve qualitative dimensions with exact TeX/code anchors and implementation qualifications. Neither this matrix nor finite Python counts measure novelty, human productivity, or formal correctness of the implementations.
