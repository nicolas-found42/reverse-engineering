# Corrected object-row to VU0 transform provenance supplement

Root independently corrected the prior serialized map before commit. The loader cursor advances by 4,2,2,4 before the first `lwc1 -4(s1)`, making its effective row offset +8; later mapped loads advance another4bytes each. The parser row base follows the four-byte count word, matching the loader loop entry. Old prose/tools/metadata/tests are preserved under `superseded-field-map-01/`; original Jev receipts remain unchanged and do not prove the source map. Current corpus and mutation evidence is in [root-correction/README.md](root-correction/README.md).

This supplement follows the transform path one level below the earlier consumer audit. It identifies the serialized source row for one exact track asset and maps the fields into the runtime row and transform call. It preserves the original Jev receipts and does not rename geometry planes or claim renderer submission.

## Source row and writer

The loader's root-name parser, `FUN_00123908`, stores the root-name count at `+0xb4`, the root-name offset array at `+0x88`, and relocates each root entry relative to the file buffer. `FUN_00124cb8` scans that ordered root-name array and returns an ID containing the matching low-16-bit index. `FUN_001213d8` uses the ID's low 16 bits to select a `0x58`-byte descriptor. In `FUN_0011ed90`, that descriptor's `+0x30` slot receives the per-name expanded-row buffer.

At `FUN_0011ed90` instructions `0011f950–0011f9dc`, the row source cursor advances 32 bytes per iteration. The writer loads 16-bit header values, then copies binary32 words into runtime offsets `+0x0c`, `+0x10`, `+0x14`, `+0x18`, `+0x1c`, and `+0x20`. Its destination pointer advances `0x24` bytes (`0011f97c`). The precise transform-field mapping is:

| Runtime row field | Serialized source row field | Writer evidence |
| --- | --- | --- |
| `+0x0c` | `+0x08` | `lwc1` at `0011f970`, `swc1` at `0011f980` |
| `+0x10` | `+0x0c` | `lwc1` at `0011f990`, `swc1` at `0011f9a0` |
| `+0x14` | `+0x10` | `lwc1` at `0011f9a8`, `swc1` at `0011f9b4` |
| `+0x18` | `+0x14` | `lwc1` at `0011f9b8`, `swc1` at `0011f9c0` |

`tools/ps2_sections.py` describes these serialized rows as the `expanded_24` span: 32 bytes in the file per row. The name “expanded_24” denotes the 36-byte runtime stride, not a proven semantic structure name.

## Consumer and constructor distinction

In `FUN_0012d4b8`, the grid cell's original runtime-row pointer is saved in register `s0`. `FUN_00121590` receives the source row's first word and builds a separate generated object; the caller then stores the returned pointer back into the grid cell. The subsequent `lwc1` instructions still read the original runtime row via `s0` (`0012dd70–0012dd88`), so the four transform fields are not taken from the generated object's new memory.

The caller passes runtime `+0x18` (serialized `+0x14`) as `FUN_00113aa8`'s first scalar, zeros its second and third scalar inputs, and passes runtime `+0x0c`, `+0x10`, and `+0x14` (serialized `+0x08`, `+0x0c`, and `+0x10`) as scalar inputs four through six. The helper routes a nonzero first scalar through VU0 microprogram call `0x268`. It writes inputs four through six directly to output words 12 through 14 and writes binary32 `1.0` to word 15. Thus the three latter fields are the output matrix's translation column/tuple by their write position; their coordinate-axis convention is not identified here. The first scalar is a VU0 trigonometric input in this call shape, but its angle unit, axis name, and supported range are not established by this trace.

The recursive helpers are separate structures: `FUN_001205e0` writes `0x80`-byte recursive nodes; `FUN_001208d0` writes `0x2c`-byte child records. They are not the writer for this 32-to-36-byte expanded-row mapping.

## Exact corpus anchor and falsifiable check

Asset: `games/ford-racing-2/extracted/files/3DDATA/TRACKS/Fukuoka.PS2;1`, SHA-256 `3dae1e8ff73ec00a97a88136d3a96976cd4db005d9326cc83972962a960428ec`, 5,554,160 bytes. Its root-name index 1224 is `FUKUOKA_CUT_UP`; parsed later record 1224 has `expanded_24 = {offset: 5428020, count: 1223, stride: 32, size: 39136, end: 5467156}`. This agrees with `FUN_0012d4b8` constructing the lookup name with the literal format `%s_CUT_UP`; it does not assert that this file was dynamically loaded during this audit.

For every row in the bounded span `[5428020, 5467156)`, I interpreted little-endian words at source offsets `+0x08`, `+0x0c`, `+0x10`, and `+0x14` as IEEE binary32. All 4,892 values are finite. Their measured ranges are:

| Source field / runtime field | Measured values across 1,223 rows |
| --- | --- |
| `+0x08` / `+0x0c` | `-1472` to `1472` |
| `+0x0c` / `+0x10` | exactly `0` |
| `+0x10` / `+0x14` | `-896` to `832` |
| `+0x14` / `+0x18` | exactly `0` |

The first row at file offset `0x52d334` is a compact witness: raw source words begin `0x000004c7, 0x0000ffff, 0x44b80000, 0x00000000, 0x44500000, 0x00000000`; the four consumed binary32 fields are therefore `0x44b80000`, `0x00000000`, `0x44500000`, and `0x00000000`. The transform's three copied translation inputs are finite for this span, and its homogeneous final word is fixed at `1.0`. I did not execute the game routine or calculate/claim the VU0-derived rotation output; finite inputs alone do not establish finite rotation outputs for the measured scalar range.

## Remaining limits

No specific coordinate axes, angle units, object semantic name beyond the serialized `FUKUOKA_CUT_UP` root, geometry-plane meaning, vertex/index relationship, or VIF1/VU1 draw submission is established. The existing `six_byte`, `four_byte`, and other geometry planes remain unnamed. The transform trace is static code plus a bounded byte-span measurement, not a runtime observation.

## Receipts and provenance

- Jev request and full result: `jev-object-provenance-verify-02.json` (5 verified, 0 contradicted, 0 unsupported, 0 needing review; advisory).
- Existing audit receipts remain unchanged: `jev-consumer-link-verify-01.json` and `jev-object-float-trace-verify-01.json`.
- Scoped jgrep outcomes for the producer and transform caller are preserved in ignored scratch: `.scratch/mesh/codex-geometry/object-trace-02/`.
- Executable SHA-256: `216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`; static export SHA-256: `554f29697a3569e10b466e18caea5260d96b5a3a8741b586d811fa26beaa6383`.
- Relevant source hashes: `FUN_0011ed90.c` `8cedf6847f21090b17e082d4c2a2d423cc2d57d08c392db6d7dc9125bb5d87cc`; `FUN_001205e0.c` `2b306167d909b8d3e058bd352c84aaf744aadeb939f1dec8b4a6df8f85d18d87`; `FUN_001208d0.c` `1fe4e6b836c92dceb94a572c95095650c36fbbb0abd0b802caffbf37dc805446`; `FUN_001213d8.c` `eda9d12d923c6c209515c9470b233e3a60fe8e094001b5b18fa8071163f01335`; `FUN_00121590.c` `b9d61309258b11290e9c4f21ad5e8a076ad99f5bb0602c7841b434c19b39d00f`; `FUN_00124cb8.c` `c30f110ae220190cb992dbf35a2e59afbd0ed25860548f2dc88f02ad452dc484`; `FUN_0012d4b8.c` `87efb37aa5e8fe70c09f5c0e2e9ce86fe6b2ea5956b1f2b70540c341972ab34a`; `FUN_00113aa8.c` `2c32a0775537459f4d055c7cca1fba9731a2b2ab6fc2ca0943c5d0d76aed8cfa`; `tools/ps2_sections.py` `837be19ffe5819584845d2fe2dd2d5562f98470009c1f3573e8f46ffeb7f3d6d`; `tools/format_contracts.py` `d8fbc9e679ad1e0813a6d2d0d3422668870771651020c8ce781cb8e6b35c330d`; asset SHA-256 as above.
