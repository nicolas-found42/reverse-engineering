# Static geometry transfer contract (bounded)

This note records what the saved instruction stream proves about one object
record's two transfer groups and the packet writer they reach. It identifies
the machine-level UNPACK formats and byte counts. It does not identify vertex
axes, positions, attributes, world scale, or a renderer, and it does not claim
that either conditional path ran in a game session.

## Record and call flow

The pinned executable is `Ford Racing 2` SHA-256
`216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`. Its
saved static export is SHA-256
`554f29697a3569e10b466e18caea5260d96b5a3a8741b586d811fa26beaa6383`.
The exported language is `r5900:LE:32:default`.

In `FUN_001288b0`, `FUN_0021b710` returns the record pointer in `v0`. The
instruction at `00128930` copies that value to `s2` in the delay slot of the
call at `0012892c`; MIPS delay-slot execution means the copy happens before
`FUN_0021b6e0` starts. The latter helper's return is saved separately in `s5`
at `00128938`. This distinction was checked directly against the instruction
addresses; an earlier interpretation that treated the `s2` value as the
second callee's return is superseded and incorrect.

The record has two statically followed groups:

| Group | count | header pointer | payload pointer |
| --- | --- | --- | --- |
| first | `record+0x1c` | `record+0x20` | `record+0x24` |
| second | `record+0x28` | `record+0x2c` | `record+0x30` |

Each loop reloads the transfer count from `header+2` into `a0` in a delay
slot before calling `FUN_00128e88`; the payload source is passed in `a1`.
On the first-group path, the caller sets `a3=0` before the writer call. The
second-group path does not set `a3` to zero, so its optional branch remains
conditional on the caller's value.

## Packet writer behavior

`FUN_00128e88` encodes the count as `n << 16` in VIF NUM bits. It emits these
UNPACK command-byte bases and REF payload lengths:

| Transfer | command byte | PS2SDK mode | source bytes | REF QWC |
| --- | ---: | --- | ---: | ---: |
| first source | `0x69` | V3-16 | `6*n` | `ceil(6*n/16)` |
| second source | `0x6e` | V4-8 | `4*n` | `ceil(4*n/16)` |
| optional source | `0x65` | V2-16 | `4*n` | `ceil(4*n/16)` |

The QWC formulas are the function's own integer sequences: `(3*n+7)>>3`,
`(4*n+15)>>4`, and `(2*n+7)>>3`, respectively. For positive `n`, they equal
the ceiling formulas above. The code's REF tag identifier is `3` (REF).

The UNPACK destination base is selected as `0x208` when the saved selector is
zero, otherwise `0x2c8`; the V4 command uses base `+1`, and the optional V2
command uses base `+2`. These are UNPACK immediate address values. The pinned
PS2SDK documents the address field in VU-memory quadword units. The optional
V2 command is skipped if the writer's saved `a3` argument is zero. The first
group caller supplies zero; whether the second group's optional branch is
taken is unresolved.

The immediates used for these three commands do not set UNPACK bit 14. The
pinned PS2SDK definition maps this bit to USN: zero selects signed extension.
That establishes the input extension mode for these encoded commands, not
the semantic interpretation of any component or resulting VU value. The
commands also leave FLG bit 15 clear. PS2SDK defines NUM zero specially as
256; this static trace does not establish a zero count for these groups, so
the special case is not used to infer a record size.

## Evidence and limits

`jev-static-vif-claims.json` preserves the exact Jev inputs and full result for
eight claims. All eight were verified, with zero contradicted, unsupported, or
review claims. `firecrawl-ps2sdk-headers.json` preserves the exact Firecrawl
requests and full returned text for the three source-pinned PS2SDK files;
`jev-ps2sdk-screen.json` preserves the screening input/result. Their hashes,
along with source hashes, are in `source-provenance.json`.

The SDK source is pinned to PS2SDK commit
`ac92a9f657d2e531dd8f060250b07f2a5ac6dea5`. It defines the VIF encoding and
helper conventions used above. It does not prove that this executable follows
the SDK helper implementation internally.

Open questions include the meaning and ordering of the V3/V4/V2 components,
their units or scale, the VU microprogram that consumes these destinations,
whether both destinations or the optional V2 path are selected at runtime,
and how these transfers link to a final rendering call. No packet-writer or
VU routine was run to establish this contract; it is a static, bounded
instruction-to-format interpretation.
