# gp context for the EE executable

Before this change Ghidra had no gp value at any of the 5,454 saved-function entries, so every gp-relative global printed as an offset name (`uGpffff9118`, `&gp0xffffa920`): **13,609 tokens in 1,871 functions**. The earlier quality counter matched only the `gp0x` spelling and reported 241 tokens in 85 functions; `tools/verify_decompilation_quality.py` now matches both spellings (test added).

## What was done

One guarded transaction, `tools/ghidra/experimental/SetGpContextV1.java`, sets gp = `0x295d70` over every initialized executable block. The value rests on three static facts: the ELF `.reginfo` gp_value, the entry routine's only gp write (`move gp,a0`, a0 = `0x295d70`, which the guard recomputes from the `lui`/`addiu` pair), and the offset map below. The guard rolls back unless function snapshots (entry, body, name, comment, instruction count) and the instruction, data, symbol and function counts are unchanged and gp reads back as the pinned value at every function entry. Driver: `pipeline/do_gp.sh`. Check: `tools/gp_context_check.py` (8 tests).

Jev chose this approach over per-function context, post-processing the text and more investigation (`jev_decide` 0.91; see `jev-receipts.json`).

## Result (reconciliation 6 of 6)

- Gp names: 13,609 → 0.
- Listing unchanged for all 5,454 functions; the 3,583 functions without gp names have identical pseudocode.
- 1,870 of 1,871 functions show every predicted address. The one other function (`00107588`) reads a byte of a 4-byte variable (`DAT_00290618._2_1_` for `0x29061a`), which is a correct resolution that the exact-address check does not match.
- Independent test: all 2,171 distinct offsets land inside `.sdata` (10,576 tokens), `.lit4` (1,085) or `.sbss` (1,948) when gp is `0x295d70`. None land elsewhere.

## What got worse

Warnings rose 757 → 768 (`Globals starting with '_' overlap smaller symbols` 89 → 101) and undefined-type tokens rose 23,229 → 23,279. Resolved accesses now meet real symbols at other widths. Fixing that needs data types for the small-data globals, which this change does not do. Call-arity counts are unchanged.

## Not established

Whether every thread uses gp `0x295d70`: only the main thread's setup was seen, and thread parameter structures were not examined. The single value is consistent with every gp-relative operand found, which is evidence for it but not proof. Types of the globals and their names are unrecovered.

## Review record

`jev_gate` on the final change returned **escalate** (safe_to_apply 0.17; limiting rubrics blast radius and test gap). Five of its six claim checks verified; the sixth (the 6-of-6 reconciliation) verified at 0.83 with 0.15 contradicted, below the auto threshold. The cause named was a test gap: the Java guard has no unit test, only a real run. Two things were added in response, and the escalation stands as recorded:

- The first strengthened guard rejected the correct entry routine because `lui` and `addiu` name sub-registers differently (`a0`, `a0_lo`). That rejection is a real guard decision on a real program and was fixed with `getBaseRegister()`.
- `negative-control-wrong-pin.json`: the same guard compiled with a wrong pin (`0x295d71`) on a fresh project copy rejects with `.reginfo gp_value 00295d70 differs from the pinned gp`.

The drift checks (function snapshot, counts, gp read-back) have no deliberate failing run. They are exercised only on the passing path.
