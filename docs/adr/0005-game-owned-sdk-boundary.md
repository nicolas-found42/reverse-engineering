# Game-owned and SDK regions: every loadable section is mixed until a range-level split is measured

The byte gate is scoped to **game-owned** bytes ([ADR-0001](0001-completion-target.md), [ADR-0003](0003-open-source-only.md)), so the boundary must be a recorded decision. Decided: **no whole section is game-owned.** Every loadable code and data section of the retail EE executable remains **mixed** at section granularity. One local `.text` range is now attributed as `game_owned` and two local `.text` ranges as `substitute_region` (FlushCache `0x001eade0` + SignalSema `0x001eab80`); all other bytes remain mixed or unresolved until measured by address range.

**Measured on the pinned executable** (reproduce: `python3.14 tools/boundary_measurements.py games/ford-racing-2 --output <dir>`; recorded in `notes/evidence/fr2-matching-harness/results/boundary-measurements.json`) (`SLES_517.05`, SHA-256 `2167…ea95`, 38 named sections):

- 165 distinct `__FILE__` path strings (NUL-terminated, string-start anchored `../…\.(c|cpp|s)`), all in `.rodata`: 109 under `../fr2/` (the game) and 56 under `../modules4/` (engine modules: `system/ps2`, `graphics/ps2`, `3d`, `sound/ps2`, `ui`). Two code bases are linked together, so the game is not one contiguous region even before the SDK.
- 10 Sony library stamps (`PsII…`), all in `.data`, for `libkernl`, `libgraph`, `libdma`, `libcdvd`, `libipu`, `libmc` and others at 2500–2550. Stamps date SDK libraries; they do not bound those libraries' code ranges.
- Nothing measured assigns an address range in `.text`, `.data`, `.rodata`, `.lit4` or `.sdata` to the SDK or to the game.

**Scope table** (implemented in `tools/matching_diff.py`, never supplied by the caller of the gate): metadata sections (`.shstrtab`, `.mdebug*`, `.reginfo`, `.DVP.ovlytab`, `.DVP.ovlystrtab`) are `excluded`; every other section is `mixed`. `game_owned` and `substitute_region` stay defined and countable, but no section is in them today.

**Consequence.** A section-wide match still earns no matched credit. A byte-identical per-unit build can earn credit only when its entire span is inside a recorded game-owned range; the aggregate section ledger remains conservative until it accounts for those range splits. This is the intended reading of "nothing approximately matched is ever counted as matched": an identical `.text` is a real, reported pass and still not a matched fraction, because it contains bytes outside the attributed range.

**Falsifier / how this changes.** Additional measured range splits, for example per-translation-unit ranges from `__FILE__` attribution (`notes/evidence/fr2-source-map/`) cross-checked against callers and SDK function signatures, move ranges, not sections, into `game_owned` or `substitute_region`. The first local split and its falsifier are recorded below; complete attribution remains open under #5.

## Measured local split: `misc3d_db_id` accessor

Assign `.text[0x001d1800, 0x001d183c)` (60 bytes) to `game_owned`. Keep the
referenced `.sbss` address `0x00290ac4` unresolved and mixed; this decision
covers only the code bytes. The evidence and the commands used to reproduce the
range check are in [`notes/evidence/fr2-first-unit/README.md`](../../notes/evidence/fr2-first-unit/README.md).

The source map identifies entry `0x001d1800` at line 188 of
`../fr2/source/app3d/misc3d.c`. In that bounded span, the code checks a
miscellaneous 3D database-id sentinel, returns the loaded value, or calls the
shared error routine with the source path, line, and a database-specific
failure message. A direct caller at `0x001942e8` is independently attributed to
`../fr2/source/entity/mobile/obstacle/obstacle.c`; four additional saved callers
are recorded in the local evidence record. The shared error routine at
`0x00105888` is separately mapped to `../modules4/system/ps2/asyncf.c`, outside
the attributed span. This caller and helper cross-check narrows the source-path
lead to a game-specific accessor with an engine dependency, rather than
including the engine helper in the owned range.

The hand-written unit at
[`reconstruction/ee/app3d/misc3d_db_id.c`](../../reconstruction/ee/app3d/misc3d_db_id.c)
compiles and links at `0x001d1800` to the pinned 60 retail bytes. A reversed
sentinel branch and a four-byte shift of the linked diagnostic string both fail
the real comparison. These results establish a local source-build boundary and
placement check; they do not identify the original compiler or prove the name
of the original routine. The candidate compiler is still marked exploratory,
so AC05 remains incomplete. This decision does not attribute the data global,
other code in `.text`, or any other range.

**Falsifier.** An overlapping SDK attribution, a disjoint control-flow boundary,
or a contradictory source-map/caller relationship for any byte in
`0x001d1800–0x001d183b` revokes this split. Until such evidence appears, all
remaining ranges keep their prior mixed/unresolved status.

## Measured local split: `FlushCache` kernel stub (substitute)

Assign `.text[0x001eade0, 0x001eadf0)` (16 bytes) to `substitute_region`.
The span is the measured four-word kernel call wrapper `addiu v1,zero,100;
syscall; jr ra; nop` at saved-function entry `FUN_001eade0`, with syscall
number 100 (`0x64`) mapping to the single pinned-SDK name `FlushCache` in
`ee/kernel/include/syscallnr.h` (ps2sdk `ac92a9f6`). Twenty-eight static
direct `jal` transfers target this entry (25 in `.text`, 3 in executable
init/user sections), grouped by saved-function ownership into 23 saved
callers including retail `entry` at `0x00100008`; every other linked byte
keeps its prior status. The recorded evidence is
[`adr0005-flushcache-boundary.json`](../../notes/evidence/fr2-ps2sdk-substitute/adr0005-flushcache-boundary.json),
which binds the range bytes, the syscall number/name evidence, the call/site
contract (`void FlushCache(int operation)`, `$a0` operation, observed
arguments 0 and 2), and the full static consumer list. Substitute bytes are
never matched, even when a substitute build is coincidentally byte-identical.

Reproduce the transfer total from the pinned executable with:

```sh
python3 - <<'PY'
import struct
import sys
sys.path.insert(0, "tools")
from ps2_executables import parse_elf
data = open("games/ford-racing-2/extracted/SLES_517.05", "rb").read()
elf = parse_elf(data)
total, text = 0, 0
for sec in elf["sections"]:
    if not (sec["flags"] & 4) or not sec["size"] or not sec["offset"]:
        continue
    for k in range(0, sec["size"] - 3, 4):
        word = struct.unpack_from("<I", data, sec["offset"] + k)[0]
        if word >> 26 == 3:
            target = ((sec["address"] + k + 4) & 0xF0000000) | ((word & 0x3FFFFFF) << 2)
            if target == 0x001EADE0:
                total += 1
                text += sec["name"] == ".text"
print("direct transfers to 0x001eade0:", total, "(.text:", str(text) + ")")
PY
```

Reproduce the saved-caller grouping and the observed arguments from the
committed evidence with:

```sh
python3 -c 'import json; d = json.load(open("notes/evidence/fr2-ps2sdk-substitute/adr0005-flushcache-boundary.json")); s = d["static_consumers"]; print("saved callers:", s["distinct_saved_callers"], "sites:", sum(len(c["call_sites"]) for c in s["callers"])); print("observed args:", d["interface"]["observed_call_site_arguments"])'
```

**Falsifier.** A game-owned source claim for any byte in
`0x001eade0–0x001eadef`, an overlapping non-substitute attribution, or
disjoint CFG evidence placing these bytes in another unit revokes this split.

## Measured local split: `SignalSema` kernel stub (substitute)

Assign `.text[0x001eab80, 0x001eab90)` (16 bytes) to `substitute_region`.
The span is the measured four-word kernel call wrapper `addiu v1,zero,66;
syscall; jr ra; nop` at saved-function entry `FUN_001eab80`, with syscall
number 66 (`0x42`) mapping to the single pinned-SDK name `SignalSema` in
`ee/kernel/include/syscallnr.h` (ps2sdk `ac92a9f6`). Sixty-nine static
direct transfers target this entry (67 `jal`, 2 `j`, all in `.text`),
grouped by saved-function ownership into 47 saved callers;
the semaphore id arrives in `$a0`, overwhelmingly loaded from memory rather
than an immediate, so no observed argument values are recorded. The recorded
evidence is
[`adr0005-signalsema-boundary.json`](../../notes/evidence/fr2-ps2sdk-substitute/adr0005-signalsema-boundary.json),
which binds the range bytes, the syscall number/name evidence, the call/site
contract (`s32 SignalSema(s32 sema_id)`, `$a0` semaphore id), and the full
static consumer list. Substitute bytes are never matched, even when a
substitute build is coincidentally byte-identical.

Reproduce the transfer total from the pinned executable with:

```sh
python3 - <<'PY'
import struct
import sys
sys.path.insert(0, "tools")
from ps2_executables import parse_elf
data = open("games/ford-racing-2/extracted/SLES_517.05", "rb").read()
elf = parse_elf(data)
jal, jmp = 0, 0
for sec in elf["sections"]:
    if not (sec["flags"] & 4) or not sec["size"] or not sec["offset"]:
        continue
    for k in range(0, sec["size"] - 3, 4):
        word = struct.unpack_from("<I", data, sec["offset"] + k)[0]
        if word >> 26 in (2, 3):
            target = ((sec["address"] + k + 4) & 0xF0000000) | ((word & 0x3FFFFFF) << 2)
            if target == 0x001EAB80:
                jal += word >> 26 == 3
                jmp += word >> 26 == 2
print("direct transfers to 0x001eab80:", jal + jmp, "(jal:", str(jal) + ", j:", str(jmp) + ")")
PY
```

Reproduce the saved-caller grouping from the committed evidence with:

```sh
python3 -c 'import json; d = json.load(open("notes/evidence/fr2-ps2sdk-substitute/adr0005-signalsema-boundary.json")); s = d["static_consumers"]; print("saved callers:", s["distinct_saved_callers"], "sites:", s["total_call_sites"])'
```

**Falsifier.** A game-owned source claim for any byte in
`0x001eab80–0x001eab8f`, an overlapping non-substitute attribution, or
disjoint CFG evidence placing these bytes in another unit revokes this split.

