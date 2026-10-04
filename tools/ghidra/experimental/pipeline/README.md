# EE candidate-recovery pipeline (static only)

Scripts used to produce the bundles under `notes/evidence/fr2-ee-next-seeds/`. They read the ELF, a pinned Ghidra export (`inventory.json`, `coverage.json`, `decompilation/manifest.json`) and drive headless Ghidra on byte-identical copies of an ignored project; they never execute original game code. The drivers resolve the repository root from their own location (`env.sh`), so they run from any directory. Required environment: `JAVA_HOME` (a JDK for Ghidra) and `GHIDRA_HEADLESS` (path to `support/analyzeHeadless`). Optional: `PYTHON` (default `python3`) and `FR2_WORK` (ignored scratch output directory, relative to the repository root, default `.scratch/mesh/codex-audit/frontier-3845-01`). The Python helpers expect the repository root as the working directory. The project-copy check compares sorted `sha256  relative/path` records, not bare hashes.

- `seedlib.py`, `cfg_seed.py`, `scan.py`: raw-word structural walker from one seed; direct-call frontier scan.
- `make_seed_config.py` + `check_seed_config_root_v4.py`: single-seed config (V3/V4 guards) and its independent re-derivation.
- `make_batch_config.py` + `check_batch_config_root.py`: schema-2 batch config (V5 guard) and its independent re-derivation.
- `run_guard.sh`, `do_seed.sh`, `do_batch.sh`, `export_verify.sh`, `chain.py`: drivers (copy project, run guard once, read-only export, verifier, reconcile).
- `post_seed.py`, `post_batch.py`: reconciliation of the new export against the pinned baseline.
- `InspectSeedRefs.java`: read-only listing of references into seed spans.

## Guard revision note

`CreateEeCandidateV5.java` was changed after the r1 to r3 batch commits: the per-candidate integrity check now runs inside the Ghidra transaction, before it commits, instead of after (code review finding on PR 3). The revision that ran r3 has SHA-256 `5b57b6d14a4a6ce2198b6275c89a064342e4d94d8f0595f612c24c5f1049e1fa` (as pinned in `batch-r3-candidates/bundle-manifest.json`; recoverable from commit `a89ec75`). The current file has SHA-256 `36d47f03ba2405c15990e347d24d8afb82f9ad5517c4f6c8716d68e7d0dfe5f5`. Replaying batch r3 (same 176-seed config, SHA-256 `7ea2a9c5...e784`) with the current guard and drivers on a fresh copy of the r2 project gave 4,718 functions, verifier pass, reconciliation 16 of 16 checks, 620 warnings, byte-identical coverage and all 4,718 per-function decompiled C files, and an inventory equal to the committed export once callee/caller list order is normalised. The export manifest differs only in per-function timing. The replay output is ignored scratch and is not committed.
