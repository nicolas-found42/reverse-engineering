# Static VU dispatch and entry provenance

This is a bounded static continuation of the geometry-to-VIF trace. It ties
one packet-building path to a concrete VIF `MSCAL` immediate, maps that
immediate to bytes in a recovered VU overlay, and records a short span of
instructions at the entry. It does not claim runtime execution, final
rendering semantics, or a serialized-coordinate scale.

## Dispatch path

During initialization, `FUN_0022fc90` calls `FUN_0022fd48`, then
`FUN_0022fda8`, then `FUN_00230180`, and finally tail-calls `FUN_001124c0`.
The first helper sets up the guarded VIF1 upload chain documented in the
[earlier VIF bundle](../fr2-geometry-vif-contract/README.md). `FUN_0022fda8`
stores `0x5cc` in the global at `gp-0x6dec`: its instructions materialize
`0x2e60` and shift right by three. The object packet builder
`FUN_00128ca0` later reads this global and ORs it with `0x14000000`, then
stores that command word into the shared packet buffer. The pinned PS2SDK
defines VIF command byte `0x14` as `MSCAL`, so this word encodes
`MSCAL 0x5cc`.

The caller `FUN_001ce288` reaches `FUN_00128ca0` only after
`FUN_00126c18(4)` returns nonzero; the zero branch skips the packet-building
block. On that nonzero path it subsequently calls `FUN_001288b0`, which
appends the two groups documented in the earlier bundle. This proves a
conditional packet-construction order in the saved instruction stream. It
does not prove that a DMA launch or the VU program ran.

There is also an initialization builder path: `FUN_001124c0` ORs the value
at `gp-0x6df4` with `0x14000000`. `FUN_0022fda8` stores zero at that global,
so the constructed command value there is `0x14000000` (`MSCAL 0`). The role
and execution of this separate zero-entry command are not inferred here.

## Address mapping and entry instructions

The saved overlay map places VIF1 overlay 5 at VU byte address `0x2800` with
length `0x800`, so its byte range is `[0x2800, 0x3000)`. The `MSCAL`
immediate is `0x5cc`; using the VU instruction-pair width of eight bytes,
`0x5cc * 8 = 0x2e60`. That is overlay 5 local offset `0x660`, pair 204.
The 16 bytes at executable file offset `0x11ba78` match the extracted
overlay bytes at local offset `0x660` exactly. The address arithmetic and
byte comparison are recorded in `static-trace.json`. Jev left this compound
mapping claim for review at 0.76 confidence; the source offsets, subtraction,
and byte equality were then independently checked deterministically. The
review disposition is retained rather than changed.

At this address, the disassembly begins with instructions that load VF01
through VF08 from VU addresses 0 through 7, then contains `xtop vi01` and
loads relative to that TOP value. The bounded subsequent span includes chained
MULAX/MADDAY/MADDAZ/MADDW instructions, the immediate loads `768` and `6144`
with SUBI operations, a `div q,vf00w,vf17w`, a later `mulq.xyz` using Q, and
`ftoi4.xyz vf16,vf17` at the first pair of overlay 6. These are exact
instruction facts. They do not prove that either geometry UNPACK destination
is the data consumed by these loads, nor what axes, units, or transforms the
registers represent. No numeric output or hardware equivalence is claimed.

## Rejected scale fit

The root's exploratory max-absolute-bound divided by 16,384 hypothesis
remains rejected: among 16,018 nonempty groups, 1,051 fail its endpoint bound
even after a one-step tolerance. The retained counterexamples include
`3DDATA/TRACKS/Brands.PS2;1` records with endpoint bounds `[-0.5, 0.5]` on
the first two dimensions while the fit predicts approximately `[-1, 1]`.
The root also reports raw signed-16 coordinates near `+/-32767`. This is a
counterexample to that fit, not evidence for a replacement scale. The exact
scratch outcome is copied to `rejected-scale-experiment.json` with its source
hash recorded in `static-trace.json`.

## Validation and open questions

The existing VU roundtrip report is pinned to the same executable and reports
all eight overlays extracted and reassembled with exact source/assembled hash
matches. This work used the saved export, overlay extraction, disassembly,
and byte comparisons only; no game, VU routine, emulator, or UI was run.
`jev-vu-dispatch-claims.json` preserves the complete call arguments and
result: six claims verified, none contradicted or unsupported, and the
address-to-overlay claim retained for review. The two scoped jgrep searches
for MSCAL/DMA behavior returned zero matches; exact saved-export address
filtering was used for the subsequent trace.

Still unresolved are the final DMA dispatch for the per-object packet,
whether this entry consumes V3-16/V4-8 data from either selected destination,
the semantic role of the immediate constants, and any relation between
serialized signed-16 values and output coordinates or world scale.

Root validation independently reconciled 27 selected EE instruction words against the original executable and saved listing, checked all 42 quoted VU instruction pairs against the pinned assembly, and repeated the 16-byte executable-to-overlay comparison. All recorded scratch-source hashes matched. See [root-validation.json](root-validation.json).
