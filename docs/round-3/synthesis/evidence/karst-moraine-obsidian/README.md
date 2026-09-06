# Karst, Moraine, and Obsidian review evidence

- `reproduction.json`: fresh Python commands, tool identity, exit codes, input/output hashes, original-result comparisons, and proof that all 26 input files remained byte-identical to pinned commit `58bb54219f494b29310ff77384732129411da887` during the run.
- `reproduce.py`: isolated reproduction helper. Run with `python -B`; it writes only into this evidence directory and runs byte-identical copies.
- `runs/`: copied Python sources and captured stdout/stderr. Karst also writes its result JSON beside the copied script.
- `convergence.json`: ten-dimension editorial reading crosswalk. This is source attribution, not a novelty or usability measurement.
- `primary/`: a pinned external source and hash receipt confirming the finite/free hypotheses missing from Moraine's tensor-family exposition.
- `fetch_primary.py`: reproduces that single read-only primary-source retrieval.

The critical discussion is in `../../review-notes/karst-moraine-obsidian.md`.
No original source directory was modified, and this lane invoked neither Lean nor Lake. The parent owns fresh Lean validation separately. The Python successes do not establish a verified frontend, a verified Python implementation, or a universal theorem beyond the paper models' stated proofs.
