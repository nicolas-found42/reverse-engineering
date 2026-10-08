# Geometry-to-VU dispatch evidence status

The checked-in JSON files in this directory preserve an exploratory static
analysis, but its source inputs were Ghidra exports, extracted overlay files,
and scratch geometry experiments that are not available as public inputs in
this checkout. The packet trace, selected VU instruction descriptions, entry
mapping candidates, and rejected scale-fit counts therefore have no committed
reproducer. Treat those values as archival notes only; this README makes no
reproducible claim about a particular packet builder, VU entry, geometry
interface, or serialized-coordinate scale. The candidate rows are not promoted
to interfaces or validated dispatch entries.

The public tool that currently validates executable-derived VU evidence is
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
for the overlay spans selected by the parser. It does not reproduce the static
dispatch trace, establish VU semantics or scheduling, or validate a geometry
scale. The exploratory artifacts remain available for context, with the scope
and provenance in `static-trace.json` and `source-provenance.json`.
