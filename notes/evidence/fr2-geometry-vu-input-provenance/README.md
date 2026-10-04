# Bounded VU input provenance at MSCAL 0x5cc

This static trace links one packet builder's matrix-like V4-32 transfer to
VF01–VF08 at the VU entry selected by MSCAL 0x5cc. It separately maps the
geometry UNPACK fields, TOP-relative loads, immediate constants, and the
FTOI4 output conversion. It does not establish that the packet ran, that the
VU ran, or that the geometry UNPACK data is what the TOP-relative loads use.

`FUN_00128ca0` writes command `0x6c080000`, followed by eight 16-byte values,
then the command word derived from `0x14000000 | *(gp-0x6dec)`. Using the
pinned PS2SDK VIF fields, `0x6c080000` decodes as UNPACK V4-32, NUM=8,
destination address 0. The first four qwords come from caller memory at
`s0+0x00..0x30`; the next four come from `0x70003160..0x70003190`. At the
selected entry, the first eight sequential LQI operations load VU qwords
0–7 into VF01–VF08. The packet builder emits a V4-32 NUM=8 transfer at
destination 0 before this MSCAL, but effective placement also depends on
upstream VIF cycle/mode state (including STCYCL/STMOD and row state), which
is not proven here. Therefore this is a compatible-layout correspondence,
not a demonstrated byte-for-byte dataflow from the packet values to VF01–08;
the field meanings of the loaded qwords also remain unknown.

The same entry then executes XTOP VI01. The Sony VU User's Manual defines
XTOP as reading the VIF TOP register into the integer register. Between the
explicit V4-32 command and MSCAL word in the traced `FUN_00128ca0` buffer
writes, the code appends those eight qwords and no BASE/OFFSET word. This
bounded span does not account for TOP state established by earlier VIF
traffic or the helper preamble. `FUN_00128e88`, called later by
`FUN_001288b0`, emits geometry V3-16
and V4-8 UNPACK commands to selected absolute addresses `0x208` or `0x2c8`
(with offsets 0 and 1), then emits BASE and OFFSET commands after its later
MSCNT. Those later commands cannot set TOP for the earlier MSCAL in this
packet-building path. The TOP register value latched by that MSCAL therefore
remains dependent on preceding VIF state and is not tied here to either
geometry destination. The static link between those geometry payloads and
the TOP-relative loads is unresolved.

The bounded instructions show raw LOI words `0x44400000` (768.0) and
`0x45c00000` (6144.0) preceding SUBI operations on VF15.xyz and VF12.xy.
They are exact constants in these operations; no serialized-coordinate
normalization or world scale follows from them. The transform chain then
uses VF01–VF08, divides Q from VF00.w by VF17.w, multiplies VF17.xyz by Q,
and converts VF17.xyz into VF16.xyz with FTOI4. The Sony manual defines
FTOI4 as fixed-point conversion with four fractional bits (multiply by 16
with truncation toward zero per its examples and conversion section). This
states the conversion format only; it does not establish output units,
clamping behavior for every input, or hardware execution. No ITOF instruction
occurs in the bounded pair-204-through-255 / overlay-6 pair-0-through-4
span.

The package retains exact selected saved-export instructions and overlay pair
bytes, source hashes, Jev calls/results, the manual scrape metadata, and a
selected VIF command-builder trace in JSON files beside this note. The bounded PCSX2 VIF-state summary records
that MODE affects unpack values and that pinned VIF1 latches TOPS before
updating TOPS from BASE/OFFSET according to DBF. Jev verified the MODE
dependency. The TOP-latch implementation claim remains at review; the claim
that this game packet has known MODE/cycle/TOP state was unsupported and
relation-contradicted. The VIF1 implementation does not identify the game
packet's VIF instance. Jev marked the V4-32 decoding claim for
review at confidence 0.64; bit-field arithmetic against the pinned PS2SDK
macro and enum resolves that narrow encoding question deterministically.
The original Jev verification also accepted a broad statement that the
`FUN_00128ca0` block did not set BASE/OFFSET; this bundle narrows that claim
to the inspected V4-32-through-MSCAL buffer span because earlier helper
traffic is not fully decoded here.
The manual screen also returned `review` at injection probability 0.29; the
screened excerpt contains only VU instruction definitions and examples, with
no agent-directed text. Both original outcomes are retained unchanged.

No original game routine, emulator, VU routine, or UI was executed. This
bundle includes only bounded metadata and selected instruction excerpts, not
full-program assembly or decompilation.

The independent root byte check reconciles53 selected EE words and41 selected
VU pairs against original ELF bytes, checks the two LOI raw binary32 literals,
confirms the eight LQI register operands and the bounded57-pair no-ITOF scan,
and rechecks34 selected command-builder words against the saved listing and
ELF. All input hashes match. [root-validation.json](root-validation.json)
retains these checks with the unresolved MODE/cycle/ROW/TOP limitations.
