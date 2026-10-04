# IOP static recovery evidence

The bounded IRX parser and corpus verifier run offline from the repository root:

```sh
python3 tools/verify_irx.py games/ford-racing-2/extracted \
  --inventory .scratch/mesh/codex-root/executable-inventory-01.json \
  --boundaries .scratch/mesh/codex-root/executable-boundaries-01.json \
  --output notes/evidence/fr2-static-recovery/iop/results
python3 tools/test_ps2_irx.py
```

The immutable run recorded in [the result](results/20261004T094558Z-d5361c498cad468ba50e450e88c7b88b/result.json) passes with 24 modules: 9 standalone IRX files and 15 exact slices from `IOPRP255.IMG`. The result pins inventory and boundary inputs and records hashes, byte counts, offsets, module metadata, and per-module table counts. Totals are 166 import libraries / 748 import stubs and 28 export libraries / 296 offsets. The 14-test suite covers valid tables, truncation/termination errors, invalid library names and import opcodes, unaligned and false-positive magic, wrong CPU, out-of-bounds and zero-sized sections, exact corpus provenance, missing sources, hash mismatches, byte-count mismatches, and embedded-boundary mutations, and standalone ELF identity mismatches, and exact import-stub/terminator encoding mutations. The upstream IOP header and local corpus jointly support the measured profile: `jr $ra` (`0x03e00008`), `addiu` with `rs=rt=0`, an all-zero two-word terminator, and 16-bit version values. Other IRX encodings outside this profile are rejected pending evidence. Table-magic words with nonzero reserved fields also fail closed.

Import indices are numeric until matched to the correct library/version/index API catalog. Export offsets are recorded but are not certified as callable entries. The parser does not apply relocations or recover source. The list covers the 24 pinned IRX ELF candidates only; it does not claim whole-game code completeness.

The related private-copy Ghidra run is summarized in [ghidra-summary.json](ghidra-summary.json). It used `MIPS:LE:32:default` after repairing an overwritten stock MIPS include in a private Ghidra copy. The export has 2,241 saved functions and pseudocode artifacts with no decompiler API errors; 91 warning comments are listed separately by category in the summary. Ghidra skipped `.iopmod`; its GP values came from a synthetic section-GOT-base+0x7ff0 fallback, not recovered runtime GP. Sony ET `0xff80` relocation/load-base behavior and complete function discovery remain unverified. Full pseudocode is kept only in ignored scratch space and is not copied here.

[ghidra-provenance.json](ghidra-provenance.json) pins hashes of the upstream stock language source, the private include/spec repair, and the local Ghidra run logs. Jev screens and exact verification receipts for research/claims remain in the ignored audit scratch tree; the repository evidence here stays limited to safe summaries, hashes, counts, and bounded metadata.

The exact Jev review results and dispositions are in [jev/INDEX.md](jev/INDEX.md). The final gate escalated rather than auto-approving: it left the parser failure-mode summary unsupported at low confidence and the import-ABI summary at review. That judgment is preserved. This evidence bundle does not present Jev as a correctness proof or claim its approval.
