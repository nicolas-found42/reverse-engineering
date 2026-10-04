# Relocation-aware IOP export inventory

The literal IRX table scan stopped at zero words that carry `R_MIPS_32` relocations. Such a word becomes the supplied load base and points to module offset zero after relocation. It is a valid export slot in the measured loader profile. This prematurely truncated twelve tables in the earlier [literal crosswalk](../fr2-iop-observed-crosswalk/README.md), concealing 450 export slots. The old parser and its results remain available as the unrelocated view; this package adds an explicit relocation-aware view to [ps2_irx_crosswalk.py](../../../tools/ps2_irx_crosswalk.py).

The new view uses the already tested [static relocation model](../../../tools/ps2_irx_relocations.py). It requires a nonzero synthetic load base, validates the measured ELF/program/section/relocation profile, checks that import stubs and library header identities remain unchanged, and requires every emitted export pointer site to have an `R_MIPS_32` relocation. It subtracts the synthetic base to recover module-relative targets, then checks alignment and `.text` bounds. An unrelocated zero still terminates the table. A relocated word that wraps to zero is rejected as a false terminator. The module inputs are immutable bytes, and no original routine executes.

[Pinned ps2sdk loadcore source](https://github.com/ps2dev/ps2sdk/blob/ac92a9f657d2e531dd8f060250b07f2a5ac6dea5/iop/system/loadcore/src/loadcore.c) supports this arithmetic: its loader adds the start address at an `R_MIPS_32` site, and its client linker scans export pointers after loading until a null pointer. A fresh Firecrawl scrape of that exact primary source returned HTTP 200; [r073](r073-source-screen.json) passed the source screen. The source hash is `2eb29f11cce431de18f8d5f64c64e4eda22507bfca26487a57b53b63750e0d78`. This is a software comparator and static byte model, with no claim of observed runtime allocation or hardware equivalence.

Both [base 0x1000](corpus-base-1.json) and [base 0x100000](corpus-base-2.json) pass the exact 24-module inventory and source-slice checks. [Their comparison](two-base-comparison.json) verifies identical normalized import edges, including provider module hashes and relative targets. Each view contains 748 import stubs, 28 export tables, and **746 export entries**. It yields **582 unique candidates, 15 ambiguous candidates, and 151 unmatched stubs** under literal full-library/version/ordinal matching. Thirteen export slots refer to offset zero; [the discovery metadata](zero-pointer-discovery.json) identifies the twelve prematurely truncated tables. The two `stdio` providers remain distinct candidates; registration/load order has not selected either. The earlier 217/0/531 counts are historical raw-view results.

All 13 focused crosswalk tests and all 12 relocation-model tests pass. New falsifiers distinguish a relocated zero pointer from a genuine terminator, reject zero synthetic base and missing pointer relocations, and reject a wraparound pointer hidden after a relocated zero. The original failing regression and wraparound red test are preserved. Three changed Python files have zero pyright errors, warnings, or informations. The full suite passes **265 tests in 41.905 seconds**. Exact logs are indexed in this directory.

[Jev r074](r074-jev-gate.json) remains escalated with `safe_to_apply: 0.38`. It verifies the real-corpus/two-base claim at 0.92; the zero-pointer regression claim remains review at 0.57; the execution/allocation limit claim remains review at 0.75; the compound test/type claim is unsupported at low confidence 0.28 even with actual logs supplied as evidence. These results are unchanged. Direct inspection of the exact relocation-site arithmetic, test assertions, immutable real-corpus receipts, and successful compiler/type/test outputs supports the bounded metadata change. No model approval or complete runtime compatibility is asserted.

Reproduce a fresh relocation-aware receipt:

```sh
python3 tools/ps2_irx_crosswalk.py games/ford-racing-2/extracted \
  --inventory .scratch/mesh/codex-root/executable-inventory-01.json \
  --boundaries .scratch/mesh/codex-root/executable-boundaries-01.json \
  --synthetic-load-base 0x1000 \
  --out .scratch/evidence/iop-relocated-exports
```

The export offsets now provide a larger, explicitly bounded Ghidra recovery backlog. Candidate matching does not establish callable semantics, original function boundaries, library registration, load order, or runtime binding. The 151 unmatched stubs do not prove absent runtime providers. Full generated module code and byte images remain ignored scratch artifacts.
