# Geometry-to-VU dispatch evidence status

The JSON records in this directory preserve a bounded static analysis of the
retail executable and VU overlays. The saved Ghidra export remains local, so
its pseudocode interpretations are not regenerated from public source here.
The VU verifier independently checks recorded EE instruction-byte anchors
against the pinned retail ELF and mapped VU instruction bytes against their
overlay bytes. This makes the listed entry candidates reproducible at the byte
level; it does not prove the saved export's control-flow interpretation,
execution, or that the candidate list is exhaustive.

The current map records five static VIF1 MSCAL construction paths: overlay 0
initialization entry 0 and conditional entry 0xd0; overlay 4 entry 0x2688;
overlay 5 entries 0x2aa0 and 0x2e60. Overlay 5 entry 0x2e60 has a partial
static packet/input trace. No overlay has a complete caller census or runtime
entry observation. The overlay-5 interface remains partial: packet execution,
the applicable MODE/cycle/TOPS state, REF inputs, and the meaning of values read
by the VU are unresolved. These records do not establish complete
input/output contracts, VU scheduling, or geometry semantics. No
serialized-coordinate scale is asserted.

The public tool that validates executable-derived VU evidence is
[`tools/verify_vu.py`](../../../tools/verify_vu.py). Given the local corpus
executable and the required DVP GNU `objdump` and assembler, it extracts the
overlay spans from that executable, disassembles and reassembles them, and
requires exact byte equality. Run it with:

```sh
python3 tools/verify_vu.py \
  games/ford-racing-2/extracted/SLES_517.05 \
  --objdump /path/to/dvp-objdump \
  --assembler /path/to/dvp-as
```

The command writes a receipt and private work files under
`.scratch/evidence/vu/`. A pass establishes byte-preserving mnemonic roundtrip
for the selected overlay spans and validates the entry-map evidence anchors.
It does not prove the static-export call graph, exclude indirect or
data-driven dispatch, establish runtime VIF state, VU semantics or scheduling,
or validate a geometry scale. The exploratory artifacts remain available for
context, with scope and provenance in `static-trace.json` and
`source-provenance.json`.
