# VIF DMA-tag and DIRECT packet audit

This is a bounded, read-only static audit of the shared VIF packet writer at
`0010f8f8`, the VIF1 chain submitters, and the initialization chain that writes
BASE/OFFSET before its own MSCAL. It uses the saved 3446-function static export
for executable `SLES_517.05` (`216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`)
plus the saved decompiler export. No game routine, emulator, or rendering UI
was run.

`0010f8f8` does not put a computed DMA REF descriptor in its packet. It starts
a new inline DMA CNT tag, places VIF FLUSHA (`0x13000000`) and DIRECT(2)
(`0x50000002`) in the tag's upper 64 bits, then appends a two-qword packed GIF
packet. The GIF tag is `0x1000000000008001, 0x0e`: one loop, EOP set, packed
format, one register descriptor, and A+D (`0x0e`). The following A+D pair uses
register address `0x4e`, which PS2SDK names `GS_REG_ZBUF_1`; the computed
64-bit value is its data payload. The source computes that value from
sign-extended 16-bit `DAT_002324fa`, the result of MIPS64 arithmetic-shifting
`((uint16_t)DAT_002324ec << 48)` right by 24, and `(iGpffff911c == 0)` shifted
to bit 32. For `DAT_002324ec` values below `0x8000`, that second term is
`DAT_002324ec << 24`; the exact runtime values and full GS meaning of those
source fields are not claimed here.

The helper sets the inline tag's first word prefix to `0x10000000` (ID=CNT),
zeros the address word, and later patches QWC using the span from tag start to
the current cursor. With the two GIF qwords, the resulting tag QWC is 2. The
tag's upper words are VIF commands, not a VIF command stream in the DMA tag's
ordinary QWC payload. VIF1 submission paths clear QWC at MMIO `0x10009020`,
write the masked tag address to VIF1 TADR at `0x10009030`, then start the
chain by writing CHCR `0x145` at `0x10009000`. PS2SDK places TTE at bit 6 and
STR at bit 8, so both flags are set. The pinned PCSX2 VIF1 chain
implementation transfers the tag's upper 64 bits when TTE is set.

The initialization path `0022dbb8 -> 0022fc90 -> 001124c0` builds a separate
one-qword END tag: tag word 0 is `0x70000001`, word 1 is zero, and tag upper
words are `0x03000388` (BASE immediate `0x388`) and `0x02000000` (OFFSET
immediate 0). Its one-qword payload starts with `0x14000000 | uGpffff920c`
(MSCAL opcode; the lower immediate is not resolved here), followed by three
zero words. `001124c0` calls `0021b5b0`, which sets TADR and starts VIF1 using
CHCR `0x145`. This proves BASE/OFFSET precede that initialization packet's
own MSCAL. It does not prove these settings are the active TOP-relative state
for later geometry packets or MSCNT consumers.

An earlier scratch hypothesis treated `0010f8f8`'s computed qword as a DMA
REF/tag field. That interpretation is superseded by the exact instruction
stores and SDK GIF/GS register definitions above; its prior Jev review result
is retained in `receipts/jev-verify-initial.json` rather than overwritten.

## Render-path state and selector trace

The bounded call path through `001ce288` appends `00128ca0`'s V4-32 matrix
packet before calling `001288b0` to append geometry packets. Each
`00128e88` geometry tail emits STMOD `0x05000000` (mode 0) and STCYCL
`0x01000404` (CL=4, WL=4), followed by MSCNT, BASE, and OFFSET. The next
visible loop iteration appends another matrix packet after that tail. The
matrix packet uses command `0x6c080000` (V4-32, NUM=8, immediate address 0,
mask bit clear). It copies four 16-byte chunks from `param_1` at offsets
`0`, `0x10`, `0x20`, and `0x30`, then loads four more vectors from EE
scratchpad `0x70003160`, `0x70003170`, `0x70003180`, and `0x70003190`. In the
visible render path, `00126c18(4)` calls `00127c00(1)` before `00128ca0`;
the nonzero branch of `00127c00` calls `00128518`, which uses `00115560` to
write those four scratchpad vectors. This proves producer-to-packet source
addresses, not semantic names for the values. The call to `00115518` in
`00128ca0` fills a local buffer that is not read again in the saved function
body, so it is not the producer for the scratchpad vectors. In the static
append order, the preceding tail therefore sets the
mode/cycle words before the next matrix UNPACK. Pinned PCSX2 source supports
direct unmasked component writes for mode 0 and a full-data cycle path at
CL=WL=4.

This is a static packet-order and bounded data-layout result. It does not
prove DMA scheduling, VIF execution timing, VU consumption, or the matrix
values' meaning. Between geometry tail and next matrix, the visible direct
call path adds FLUSHA/DIRECT and GIF/GS packets; `0010fa70`, `0010fa20`, and
`00127c00` update helper state or CPU-side values. In the `001ce288` direct
callee closure, `00128e88` is the only function writing literal STMOD
`0x05000000` and STCYCL `0x01000404` words. Unresolved indirect-call effects
remain outside this claim.

`00128e88` also toggles two distinct globals. `uGpffff9218` selects `uVar14`
as `0x208` or `0x2c8`; this value is data in the V4-32 TOPS-relative packet
and contributes to a later V4-8 command immediate. It is not the V4-32
UNPACK destination, which is TOPS-relative address zero from command
`0x6c058000`. `uGpffff921c` separately selects tail BASE (`0x3aa` when zero,
otherwise `0x388`). Both are cleared by
`001124c0` and `0022fda8`, and the `001ce288` direct-callee closure has no
other writer besides `00128e88`. If both have been reset before the loop,
this path keeps them paired as it alternates `uVar14=0x208` with BASE `0x3aa`,
then `uVar14=0x2c8` with BASE `0x388`. Those are distinct packet roles, not a
header-buffer equivalence. Other functions outside that closure write one or both
globals, and reset reachability before this loop has not been proven, so
this is not a process-global invariant. Details and source hashes are in
`render-path-mode-cycle-and-buffer-selector.json`; the attempted new Jev
receipt records a wrapper failure and was not retried.

The static VU instruction consumer and a conditional link from this packet's
`uVar14` lane are documented separately in
[`fr2-geometry-vu-consumer`](../fr2-geometry-vu-consumer/README.md). The
overlay continuation reads `TOP+3.z` into `vi03` and then loads VU data through
that base. The selected value can reach that lane only when the VIF mode/cycle
and TOPS state match the documented path; no runtime state or XGKICK-pointer
semantics are claimed.

## Evidence and limits

`selected-evidence.json` records exact instruction anchors, input hashes,
source pins, and the bounded packet layouts. `jgrep-summary.json` records the
semantic search queries and their true exit statuses. Large generated C files
and raw jgrep chunks remain in ignored `.scratch/`; this note contains only
selected facts and hashes.

The public sources used for encoding definitions are [PS2SDK DMA registers](https://ps2dev.github.io/ps2sdk/dma__registers_8h.html),
[PS2SDK DMA tags](https://ps2dev.github.io/ps2sdk/dma__tags_8h.html),
[PS2SDK GIF tags](https://ps2dev.github.io/ps2sdk/gif__tags_8h.html), and
[PS2SDK GS registers](https://ps2dev.github.io/ps2sdk/gs__gp_8h.html). The
TTE transfer path was checked against pinned PCSX2 source
[`Vif1_Dma.cpp` at `81526d4dc7cc70e4ae75abb35a789417456c6d43`](https://github.com/PCSX2/pcsx2/blob/81526d4dc7cc70e4ae75abb35a789417456c6d43/pcsx2/Vif1_Dma.cpp).

Remaining unknowns include the call-time values of the GS payload fields and
the initialization MSCAL immediate, the specific queued-submission point for
the later `0010f8f8` render packet, whether queued packet order matches append
order at execution, and whether the initialization BASE/OFFSET is used by any
later TOP-relative packet. The separate synthetic VIF/VU audit establishes
emulator mechanism only; it is not evidence of the game's runtime state.
