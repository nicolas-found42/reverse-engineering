# Independent GS palette upload mapping review

This review independently checks the static palette-index mapping used by the
FR2 texture upload paths. It confirms format 3 (PSMT8) across all 256 CLUT
entries and format 4 (PSMT4) across the selected first 16 entries. It does not
execute the game or an emulator and does not establish rendered RGBA colors,
alpha handling, or runtime reachability.

## Evidence and method

The reproducible audit is in the ignored scratch file
`.scratch/mesh/codex-root/texture-independent-review/audit_clut4_first16.py`.
Its output is
`.scratch/mesh/codex-root/texture-independent-review/independent-clut-upload-audit.json`.
The corrected script SHA256 is `a25e3285b3f8d5cdf3eac8d01260fff9f8b2158b9ca8ac1ec8d61e8c7dba196e`;
the corrected result SHA256 is `eba8ded52faee5a46b75374a07f786f5e105bd6ec189e559c4d651726482acb0`.
The script parses address tables from pinned PCSX2 commit
`81526d4dc7cc70e4ae75abb35a789417456c6d43`, maps row-major PSMCT32 upload
coordinates to physical words, composes the T32/I8 block selection with the
T32/I4 16-word sub-block permutation, and checks every resulting label.

For format 3, the static table initializer gives row+9 = 19 (PSMT8) and row+10
= 0 (PSMCT32). The format builder at `0022c660` reads those fields at
`0022c8a8` and `0022c8f0`; its shifts and masks place them in PSM/CPSM while
the constant OR is `0x20000004`. The descriptor-derived term is masked to four
bits and shifted right by two, so it cannot set CSM bit 23 or CSA bits 24–28.
The resulting selected format-3 fields are PSMT8, PSMCT32, CSM 0, CSA 0.

The game’s staging permutation at `0022c048` exchanges palette-index bits 3
and 4. The independent 16x16 PSMCT32 upload/table composition returns labels
0 through 255 in order when this permutation is applied. The no-permutation
control is not identity: its first 32 values exchange the 8–15 and 16–23
ranges. This checks the full 256-entry I8 path rather than extrapolating from
the first 16 entries.

The initializer's format-4 row also records byte `row+14 = 128`. This is
proven by `li t2,-0x80` at `0022f988` (bytes `80ff0a24`) followed by
`sb t2,0x4a(s0)` at `0022fa40` (bytes `4a000aa2`). The low byte stored is
`0x80`.

For format 4, the same static builder selects PSMT4 with PSMCT32 and CSM/CSA
zero. The selected first 16 labels map to 0 through 15 for both an 8x2 upload
and a 16x16 upload after the game permutation. The 16x16 no-permutation
control fails. A bounded scan found 19 format-4 references to 0x400-byte
palettes; all 19 are in group A according to the container’s palette-block
counts.

## Limits and implementation distinction

The audit uses pinned GS address tables as an independent layout composition.
It does not claim that PCSX2’s CPU helper literally indexes through every
named table: in particular, the I4 helper uses vector shuffles. The pinned
`WriteCLUT_T32_I8_CSM1` source documents the I8 block formula and calls the
16-word helper; the audit composes that formula with the tables and upload
address map rather than replaying vector code instruction-for-instruction.
The result is an address/index ordering check, not a renderer equivalence
proof.

An earlier scratch script/result pair mapped offset `0x4a` to register `t0`
instead of `t2`, reporting format-4 `row+14 = 2`. This unrelated byte did not
participate in the PSM/CPSM/CSM/CSA assertions or the upload lookup. The old
script SHA256 was `b7f8142b3899b7d3963edbd46360803b5c7e7e78a6fce0297b2c45127cffc6b7`;
its output SHA256 was `9dd8ef261238037e17240799dc650067d97cfa52e8ed174e540db6fcde440c49`.
Both are retained in ignored scratch with `-superseded-row4-byte` in their
filenames. The corrected calculation now pins the exact load/store instruction
text and bytes. The earlier Jev verification is retained without a retry:
the six claims covered only selected selector fields, upload mappings, corpus
group counts, and scope, all of which are unchanged by this correction.

## Jev record

The final six bounded claims were verified by Jev (6 verified, 0 contradicted,
0 unsupported, 0 requiring review). The compact receipt is
[`jev-format3-format4-verify.json`](jev-format3-format4-verify.json).
The result remains checked against deterministic source/table calculations;
the judgment is corroboration, not proof. Earlier Jev format-4 review output
is retained at
`.scratch/mesh/codex-root/texture-independent-review/jev-clut4-first16-verify.json`
and hash `a80c2316066d4712a7bb44c8f23fe9948e7d2a6bb401ea953fa723a31c8f7330`.

## Pinned inputs

- Game executable SHA256: `216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`.
- Static instruction export SHA256: `554f29697a3569e10b466e18caea5260d96b5a3a8741b586d811fa26beaa6383`.
- `GSTables-pinned.cpp` SHA256: `4fc8ae3ef65d610ef8c1f8059b3a9ef8ae7fce5762a77e71410c7d0f0b12306b`.
- `GSClut-pinned.cpp` SHA256: `9f4ed253c162855bc4d2838c08b522cbd28b6af96d03abd44cf0f83415bb1e32`.
- `GSLocalMemory-pinned.h` SHA256: `5814409b86b13ffb68952e318f314464881ddad38edc3115a6a44d84e27df20a`.
- `GSRegs-pinned.h` SHA256: `b063ccbf49f8b3cc351dbd32ea1ae9a60950c72f4ac4c3acb7465e30b8ceee32`.

The separate independent packed/linear texture-index review remains at
`.scratch/mesh/codex-root/texture-independent-review/review_public_gs_tables.py`
(SHA256 `e503af1edfd591567b12f2b3ac7600ebc659eec660578cd6667a8bc65c88986a`)
and
`.scratch/mesh/codex-root/texture-independent-review/independent-public-table-audit.json`
(SHA256 `2605c3b3e2ec5d37784213bb49c54393e30a5eb566210fc879aceb3e061df3ec`).
That audit independently parses the public address tables across 31 packed
profiles and compares indexed bytes with decoded corpus indices. It reports
1,321 packed format-3 items and 441 packed format-4 items, checking 57,782,272
and 15,067,968 pixel indices respectively. It is linked here for parent review;
this note does not independently promote or broaden those claims.
