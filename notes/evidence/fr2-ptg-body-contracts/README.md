# PTG body-variant census (issue #28)

Scope: structural census only. Every one of the 548 unchanged-PAL `.ptg` files
satisfies the universal header relations in `tools/ptg_profile.py` AND lands in
exactly one body variant below, so no header-only file disappears from coverage.
This census does not claim palette, pointer, descriptor-constant, upload, or
lifetime semantics; those stay unresolved and block AC20/AC24 completion.

## Variants (measured 2026-10-09, pinned in variant-census.json)

| Variant | Files | Cell | Descriptor w0 | w12 | Pixel span |
|---|---|---|---|---|---|
| sprite | 16 | 32 | nonzero | d0820004 | 1024-byte table at [176,1200) + stride rows (`format_contracts.sprite`) |
| tiled4096 | 287 | 32 | zero | d0410010 | 4096 * count, no tail |
| tiled1024 | 202 | 32 | nonzero | d0820004 | 1024 * count + 1040 tail (includes the 17 last-word-`0xDDDDDDDD` files) |
| tiled1024c16 | 23 | 16 | zero | d0410004 | 1024 * count, no tail |
| tiled256 | 19 | 16 | nonzero | d0820001 | 256 * count + 1040 tail |
| barsub512 | 1 | 16 | zero | d0410002 | 512 * count, no tail (`GRAPHICS/GAME/Barsub.ptg;1`) |

Total: 16 + 287 + 202 + 23 + 19 + 1 = 548.

## Universal tiled skeleton (all 532 non-sprite files)

- Prefix words at [32, 80): eleven `0xDDDDDDDD`, one 16-aligned address at word 9.
- Per-tile 16-byte records at [80, 80+16*count): row-major coverage floats,
  one 16-aligned address, one `0xDDDDDDDD` pad.
- Per-tile 64-byte descriptors: ten `0xDDDDDDDD` padding words, word1 zero,
  one 16-aligned address at word 10; words 0/1/12/13/14 constant within a file.
- All four embedded address fields (prefix word 9, record pointer, descriptor
  words 0 and 10) are 16-aligned and exceed the file size: not file offsets.
  Their units and meanings are unresolved, not guessed.
- The 16 sprite files additionally satisfy `format_contracts.sprite()` and carry
  a valid record plus a `d0820004`-family descriptor at bytes 80..160; their
  pixel span is row-structured (index table + stride rows with `0xDD` padding),
  not an opaque tile block. Gear pins: gear0 = uppercase R, gear1 = uppercase N.
## EE consumer binding (static only; `tools/test_ptg_consumer_binding.py`, 7 tests)

- EE loader `0x22a910` (`texgraph.c`: "Unable to load a texture graphic from
  a filename without a .psd extension") accepts `.psd`/`.ptg` requests
  (comparators `psd`/`ptg` at vaddr `0x28ef08`); 35 static call sites.
- UI init `0x169cd8` issues 25 of those calls with static `GRAPHICS...PSD`
  names (25 `lui a0,0x25` + `jal 0x22a910` pairs, e.g. `STARTEU.PSD` at
  file `0x6ade0`); the remaining 10 call sites pass computed names.
- All 39 static non-format `GRAPHICS...PSD` requests resolve
  case-insensitively (extension `.PSD` -> `.ptg`) to corpus files: 3
  `tiled_dd` (`StartEU`, `freq`, `loadEU`, all 300-tile 640x480) + 36
  `tiled_header_only`. Format requests (`MATRIX/%s`, `LIVERY/%s`, ...) and
  the gear `70gear%d`/`gear%d` speedo strings resolve through computed
  names, not pinned here.
- Negative control: a `.XYZ` extension resolves to no corpus file and
  matches neither loader comparator.
Anchor: EE loader 0x22a910 (texgraph.c) accepts .psd/.ptg requests; all 39 static GRAPHICS requests resolve to corpus .ptg files.
- No palette, tile-pointer-unit, descriptor-constant, decoded-plane, upload,
  or lifetime semantics are claimed; those stay unresolved.

## Falsifiers

- A 549th `.ptg` file, a header-relation violation, a file matching no variant
  row, or a gear pixel-hash change fails `tools/test_ptg_body_census.py`.
- Mutating any pinned tool source fails the same test (source pins in
  variant-census.json).
- A loader-byte change, a new `0x22a910` caller, an unresolving static
  request, or a comparator change fails `tools/test_ptg_consumer_binding.py`.
- Wrong pointer-pad words, truncated pixel planes, and corrupt sprite index
  tables fail `tools/test_ptg_verifier.py` (criterion 3 controls).
- Claiming palette/pointer/descriptor/upload meaning from this census alone is
  an overclaim: the test pins no such semantics.

## Reproduction

```sh
bash tools/check.sh test_ptg_body_census
python3 tools/verify_ptg.py corpus games/ford-racing-2 --output .scratch/evidence/ptg
```
