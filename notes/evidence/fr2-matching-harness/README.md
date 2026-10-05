# Matching harness: section extractor, byte-diff gate and IP rails (issue #5)

Corpus: PAL `SLES_517.05`, SHA-256 `2167…ea95`, behind `corpus_contract.corpus_identity`. Static and offline: nothing here compiles, links or runs game code.

| Piece | Code | Check |
| --- | --- | --- |
| Section extractor (#6) | `tools/matching_sections.py` | `results/sections-inventory.json`: 38 named sections (32 file-backed) as exact bytes, address, offset, size, SHA-256 |
| Per-unit byte-diff gate (#7) | `tools/matching_diff.py` | pass / fail with located first difference / incomplete, in the `write_result` verifier shape |
| Boundary decision (#10) | `docs/adr/0005-game-owned-sdk-boundary.md` | every loadable section is `mixed`; `matched_bytes` is 0 until a range split is measured |
| IP rails (#17) | `LICENSE`, `docs/LEGAL.md`, `tools/ip_rails.py`, `tools/hooks/pre-commit` | refuses staged MIPS ELFs, Sony-stamped binary blobs and never-commit paths (case-insensitive). A heuristic guard rail: inert until `git config core.hooksPath tools/hooks`, bypassable with `--no-verify`, blind to repacked or compressed containers. Re-checked against every tracked file: none refused |

Tests: `tools/check.sh test_matching test_ip_rails` (24+ tests: positive fixture, negative control, incomplete control per rule).

## Real-corpus runs (reproduce with the commands shown)

Inventory (38 sections, 32 file-backed): `python3.14 tools/matching_sections.py games/ford-racing-2 --output <dir>`.
ADR-0005 counts (165 distinct source paths, 109 `fr2` / 56 `modules4`, all in `.rodata`; 10 SDK stamps, all in `.data`): `python3.14 tools/boundary_measurements.py games/ford-racing-2 --output <dir>`.

- Identical units: `python3.14 tools/slice_units.py games/ford-racing-2 DIR && python3.14 tools/matching_diff.py games/ford-racing-2 DIR` gives **pass**, exit 0, `matched_bytes` 0, `mixed_bytes_identical` 1,652,399. `.bss .sbss .spad .vubss .vudata` have no file bytes and are listed under `sections_without_file_bytes`.
- One word changed: `python3.14 tools/slice_units.py games/ford-racing-2 DIR --corrupt .text:0x1234`, then the gate: **fail**, exit 1, first difference at `00101234`.

## Not established

- No section is game-owned, so the matched fraction is 0 by construction. Range-level attribution is the next step.
- The compiler id, the linker substitution and any rebuilt unit are open (#8, #9, #11).
