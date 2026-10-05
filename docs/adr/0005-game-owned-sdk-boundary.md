# Game-owned and SDK regions: every loadable section is mixed until a range-level split is measured

The byte gate is scoped to **game-owned** bytes ([ADR-0001](0001-completion-target.md), [ADR-0003](0003-open-source-only.md)), so the boundary must be a recorded decision. Decided: **no whole section is game-owned.** Every loadable code and data section of the retail EE executable is **mixed**, the gate reports its per-section verdict but counts none of its bytes as matched, and the game-owned set is empty until bytes are attributed by address range.

**Measured on the pinned executable** (reproduce: `python3.14 tools/boundary_measurements.py games/ford-racing-2 --output <dir>`; recorded in `notes/evidence/fr2-matching-harness/results/boundary-measurements.json`) (`SLES_517.05`, SHA-256 `2167…ea95`, 38 named sections):

- 165 distinct `__FILE__` path strings (NUL-terminated, string-start anchored `../…\.(c|cpp|s)`), all in `.rodata`: 109 under `../fr2/` (the game) and 56 under `../modules4/` (engine modules: `system/ps2`, `graphics/ps2`, `3d`, `sound/ps2`, `ui`). Two code bases are linked together, so the game is not one contiguous region even before the SDK.
- 10 Sony library stamps (`PsII…`), all in `.data`, for `libkernl`, `libgraph`, `libdma`, `libcdvd`, `libipu`, `libmc` and others at 2500–2550. Stamps date SDK libraries; they do not bound those libraries' code ranges.
- Nothing measured assigns an address range in `.text`, `.data`, `.rodata`, `.lit4` or `.sdata` to the SDK or to the game.

**Scope table** (implemented in `tools/matching_diff.py`, never supplied by the caller of the gate): metadata sections (`.shstrtab`, `.mdebug*`, `.reginfo`, `.DVP.ovlytab`, `.DVP.ovlystrtab`) are `excluded`; every other section is `mixed`. `game_owned` and `substitute_region` stay defined and countable, but no section is in them today.

**Consequence.** `matched_bytes` is 0 until range-level attribution exists, whatever the per-section verdicts say. That is the intended reading of "nothing approximately matched is ever counted as matched": an identical `.text` is a real, reported pass and still not a matched fraction, because part of it is SDK bytes that are only ever satisfied by a substitute.

**Falsifier / how this changes.** A measured range split, for example per-translation-unit ranges from `__FILE__` attribution (`notes/evidence/fr2-source-map/`) cross-checked against SDK function signatures, moves ranges, not sections, into `game_owned` or `substitute_region`. That work is the next ticket under #5.
