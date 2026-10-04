# Static mip upload descriptor audit

This read-only audit traces the PAL model mip descriptors through the texture
loader and GS packet builder, then checks their byte counts against the
container corpus. It validates the static dimensions and transfer-size
relationship for observed levels. It does not execute the game, perform a GS
upload, inspect GS memory, or prove rendered output.

## Static path

In `FUN_0022ba30`, the loader reads the mip count from descriptor offset
`+0x35`, places the additional-level record array at `+0x2c`, and stores the
level-zero image pointer at `+0x28`. It allocates level zero and then the
additional levels, using `0x10` bytes per level record. The per-level source
pointer is stored at record offset `+8`; dimensions halve on each subsequent
level. The allocation-size branch selects 4, 2, 1, or 0.5 bytes per pixel for
formats 1, 2, 3, and 4 respectively.

`FUN_00222358` submits the base image and then processes up to three additional
level slots. Each active slot halves both upload dimensions, references its
`0x10`-byte record, obtains a destination address, and submits the image with
the source pointer at record `+8`. It then packs the derived level descriptors
into the texture's mip table. `FUN_0022c660` updates each extra-level record's
halfword at `+2` using the format and halved dimensions. Its descriptor setup
also branches on the mip count.

The packed/direct distinction comes from bit 8 of the descriptor's 64-bit
field at `+0x38`. With that bit clear, the transfer builder uses the logical
dimensions from exponent bits 15 and 19 and the direct PSM/bit-depth table
fields. With the bit set, it uses dimensions from bits 23 and 27 and the
packed PSM/bit-depth fields. In every inspected packed corpus item, those
transfer dimensions are half the logical width and height. The selected
format rows correspond to these transfer representations:

| Texture format | Descriptor bit 8 | Transfer PSM | Transfer bits per pixel | Transfer dimensions |
| --- | --- | --- | --- | --- |
| 1 | clear | 0 | 32 | logical width × height |
| 3 | clear | 19 | 8 | logical width × height |
| 3 | set | 0 | 32 | half width × half height |
| 4 | clear | 20 | 4 | logical width × height |
| 4 | set | 2 | 16 | half width × half height |

`FUN_00222110` computes the transfer QWC as width × height × transfer bits per
pixel, shifted right by 7. For all observed levels, this equals the container
plane byte size divided by 16. This explains why the packed indexed routes can
transfer the serialized bytes using a higher-bit-depth PSM with half-sized
dimensions; it is a static byte-count relation, not proof of runtime GS state.

## Historical 54-file result and all-56 correction

The first run used an uppercase `*.PS2;1` filesystem glob on a case-sensitive
volume. It covered 54 files, 2,353 textures, and 4,906 levels. That result is
retained as a historical scoped subset in the scratch result cited below.
The archive-bound correction uses `Baseline.entries('.ps2;1')` and verifies
each file's bytes and SHA-256 against the pinned archive. It includes the two
lowercase archive paths `/3DDATA/debug.ps2;1` and `/3DDATA/misc.ps2;1`, which
add 17 textures. See
[`archive-bound-coverage-correction-01.json`](archive-bound-coverage-correction-01.json)
and the linked all-56 scratch verifier/result there.

The archive-bound corpus contains 56 PAL model files, 2,370 texture records,
4,941 total image levels, and 2,571 extra levels. Source-plane and predicted
transfer bytes match at 79,708,000 bytes. The level-count distribution is
0 extra mips: 1,027 textures; 1: 115; 2: 1,228. Every serialized mip record's
word at offset `+8` is zero on disk and is later replaced with a source pointer.
The 54-file figures below are retained to identify the earlier scoped run.

## Historical 54-file corpus result

The bounded corpus contains 54 PAL model files and 2,353 texture records. It
has 1,022 textures with no extra mip levels, 109 with one, and 1,222 with two.
There are 4,906 total image levels, including 2,553 extra levels. The loader's
extra-level upload loop has three slots, and the measured corpus uses at most
two. All level offsets are 16-byte aligned; all computed transfer sizes match
their source-plane sizes. The checked source and predicted transfer totals are
both 79,571,296 bytes, with no rejected level. The smallest level plane is 32
bytes, so the QWC calculation divides evenly for every measured level.

All 2,553 serialized mip records are 16 bytes and contain nonzero data. Their
third 32-bit word (record offset `+8`) is zero in every file record; the loader
replaces that field with the runtime image pointer. The raw record words have
9, 75, 1, and 3 distinct values respectively. The upload path also reads
record offsets `+2`, `+4`, and `+12`, and `FUN_0022c660` writes the halfword at
`+2`. The current container parser skips the serialized record contents, so
full semantics for the other fields are still open; this audit does not assign
meanings to values beyond their observed reads and writes.

## Reproducibility and limits

The ignored scratch script is
`.scratch/mesh/codex-root/texture-independent-review/audit_mip_upload_static.py`
(SHA256 `f92d8087c2fca237197ed59e1f62eebdaee5c8f4008aa70f700a119b08734d4c`).
Its result is
`.scratch/mesh/codex-root/texture-independent-review/independent-mip-upload-static-audit.json`
(SHA256 `7b47a504feddeed90aeec1862320ade9b323a2a12949e78dd07da34b1d98f05a`).
The durable Jev request and receipt are linked from [index.json](index.json).

The all-56 Jev request is preserved, but its recovered result file is an abbreviated agent-reported summary. The original complete result envelope (including probability distributions and `same_subject` fields) was not found in available scratch or transcript sources. See the receipt metadata; no unchanged question was rerun to reconstruct missing output.

The executable SHA256 is
`216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`; the
static export SHA256 is
`554f29697a3569e10b466e18caea5260d96b5a3a8741b586d811fa26beaa6383`.
The format-table initializer evidence is
[`texture-format-table-constant-provenance-01.json`](../texture-format-table-constant-provenance-01.json).
No claim is made that the parser's generic maximum of eight mip levels is
supported by the upload routine. The largest observed count is two, and no
runtime or visual equivalence claim is made.

The independent root recount is preserved in [root-validation.json](root-validation.json).
It confirms the all-56 plane arithmetic, zero serialized source-pointer words
and script/result hashes, then checks 19 selected mip-loader/upload instruction
words against their original ELF PT_LOAD bytes. The complete all-56 static
result is [archive-bound-all56-result.json](archive-bound-all56-result.json).
The root Jev gate remains escalated (safe-to-apply 0.59), with all three bounded
claims verified and no per-claim review flags; see [root-jev-gate.json](root-jev-gate.json)
and [root-manual-disposition.json](root-manual-disposition.json). The earlier
agent's compact all-56 judgment is retained only as an abbreviated reported
summary; its full raw result was not found. No unchanged judgment was rerun.

The historical 54-file Jev receipt is also abbreviated: it omits probability
distributions and subject scores, and no complete raw result is indexed here.
It is retained as a reported summary, rather than a complete calibrated
judgment. The independent raw ELF/corpus checks and complete root gate are
separately preserved.
