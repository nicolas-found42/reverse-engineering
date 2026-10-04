# Small-data global types and literal-pool constants (EE executable)

After the gp context fix, gp-relative globals resolve to addresses but have no types. This change types the ones whose accesses agree, and makes the float-literal pool (`.lit4`) show as numbers.

## Method

`tools/small_data_plan.py` reads every gp-relative load or store in the saved functions. The mnemonic fixes the width (`lb`, `lh`, `lw`, `ld`) and an FPU access shows a float; `lb` versus `lbu` (or `lh` versus `lhu`) shows the sign. A global gets a type only when every access agrees and nothing uses its address as an array or structure base. Integer words stay untyped because an integer and a pointer use the same instructions. Plan: 1,023 entries (987 float, 28 uchar, 4 char, 2 short, 2 ushort). Skipped: 709 integer-or-pointer words, 146 store-only bytes or halves without sign evidence, 38 address-taken, 13 mixed widths, 2 wide accesses.

One guarded transaction (`ApplySmallDataTypesV1.java`, driver `pipeline/do_types.sh`) applies the SHA-pinned plan on a byte-identical project copy that already has the gp context. It rolls back unless the listing, function snapshots, instruction, symbol and function counts, and every memory block flag are unchanged, and each applied address holds the planned type and mutability. Result: 1,023 applied, 0 conflicts, 872 marked constant.

## The literal pool

All 872 accessed `.lit4` addresses are read by an FPU load. No saved function writes any of them, no absolute write reference exists, and none is address-taken. The ELF marks the section writable, so "constant" is an inference from access evidence, not a proof; unsaved code (73,756 code-shaped bytes) could still write. Jev chose to mark the items constant (see `jev-receipts.json`).

## What failed first, and why it matters

1. **Attempt 1** cleared the block write flag and ran with the default exporter options. The reconciliation failed (4 of 5): 46 functions outside my plan's function list changed, because the plan lists only gp-relative accessors and these functions reach typed globals by other instruction forms. The check was too narrow; it now also counts a function as touching when its old pseudocode names a planned address (46 of 46 do). Both results are kept here.
2. The "names replaced" check had passed only because its pattern missed the new `FLOAT_0028dd80` spelling. The real effect was none: no constant had been inlined. The check now counts any 8-digit address in the pool range. Run on attempt 1's export it fails (`attempt1-strict-check-…json`), which is the negative control.
3. **Cause found by experiment.** On one function in memory, the decompiler shows `0.0048780483` once the data is marked constant and the decompiler uses the program's options. The block flag and the respect-read-only switch changed nothing. The repository exporter used default options, so `ExportDecompilation.java` now has an opt-in `FR2_DECOMP_OPTIONS=program`, recorded in the manifest.
4. **Attempt 2** used per-data constant mutability. Both the baseline and the new project were exported with program options so the comparison is fair.

## Result (reconciliation 5 of 5, matched exports)

- Listing unchanged in all 5,454 functions.
- 4,789 functions whose old pseudocode names no planned address are identical. 662 functions changed: 616 are in the plan's accessor list, and the other 46 name a planned address in their old text. The check does not test that the 616 name one; their link is the gp-access instruction evidence.
- Pool address tokens 1,072 → 4 (0.37%; limit 5%). The 4 left are in two functions that touch constants the plan never typed.
- Undefined-type tokens 23,267 → 23,142 (−125, my arithmetic; `jev_verify` contradicted this claim at 0.91 without a stated reason). Warnings 781 → 780. Arity mismatches 3,940, unchanged.
- The exporter option alone changes 26 of 5,454 functions in the unchanged baseline, so exports made with and without it must not be compared.

## Not established

The types are access-pattern evidence, not original declarations. 709 integer-or-pointer words and 146 store-only bytes/halves have no type. The pool is not proven constant at run time.

## Review record

`jev_gate` on the final change returned **escalate** (safe_to_apply 0.14; limiting rubric: test gap; composite 0.59). Seven of nine claim checks verified; the other two went to review. The gate also marked the deliberate overclaim "whether the literal pool is constant at run time is proven" as *verified* (0.77, review). That is wrong against this bundle's own evidence ("not proven") and is recorded here as a miss of the gate, not accepted.

The escalation stands. Two negative controls exist for the guard (`negative-control-wrong-plan-sha.json`, `negative-control-address-outside-blocks.json`), and the strict check was shown to fail on attempt 1. The transaction's drift checks (snapshot, counts, read-back, block flags) have no deliberately failing run.
