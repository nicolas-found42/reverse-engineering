# EE candidate-recovery pipeline (static only)

Scripts used to produce the bundles under `notes/evidence/fr2-ee-next-seeds/`. They read the ELF, a pinned Ghidra export (`inventory.json`, `coverage.json`, `decompilation/manifest.json`) and drive headless Ghidra on byte-identical copies of an ignored project; they never execute original game code. Paths are repository-relative and point at ignored scratch directories, so they are provenance records rather than a portable tool.

- `seedlib.py`, `cfg_seed.py`, `scan.py`: raw-word structural walker from one seed; direct-call frontier scan.
- `make_seed_config.py` + `check_seed_config_root_v4.py`: single-seed config (V3/V4 guards) and its independent re-derivation.
- `make_batch_config.py` + `check_batch_config_root.py`: schema-2 batch config (V5 guard) and its independent re-derivation.
- `run_guard.sh`, `do_seed.sh`, `do_batch.sh`, `export_verify.sh`, `chain.py`: drivers (copy project, run guard once, read-only export, verifier, reconcile).
- `post_seed.py`, `post_batch.py`: reconciliation of the new export against the pinned baseline.
- `InspectSeedRefs.java`: read-only listing of references into seed spans.
