# Jev receipts for the Loadcore relocation and GP phase

Source: pinned `https://raw.githubusercontent.com/ps2dev/ps2sdk/89b9d8cf249f927192c57804ce5e55e99e34002d/iop/system/loadcore/src/loadcore.c`. Focused excerpts used for calls are preserved in `jev-screened-excerpt.txt`, `jev-verify-primary-evidence.txt`, and `jev-verify-allocation-evidence.txt`.

## Screen

Exact purpose: “Use pinned PS2SDK Loadcore source as evidence for Sony IOP IRX metadata GP semantics and relocation rules.”

`jev_screen` result: model `typesafe/jev-1.13`, provider `openrouter`; injection `0.03`, substance `0.98`, relevance `0.96`; thresholds block `0.75`, review `0.25`; action `pass`; reason “no signals above thresholds”; usage 2,871 input tokens and 57 output tokens.

## Direct source verification

First `jev_verify` used the six exact claims below and the primary-source excerpt in `jev-verify-primary-evidence.txt` plus a brief Ghidra source/log excerpt:

1. “In pinned PS2SDK Loadcore, struct iopmod's third field is gp, after mod_id and EntryPoint.” — verified, confidence `1.00`, supports `1.00`, auto.
2. “Loadcore ProbeExecutableObject copies iopmod->gp into ModuleInfo.gp, and loadrelelf adds the allocated text_start base to ModuleInfo.gp.” — verified, confidence `0.95`, supports `0.97`, auto.
3. “For ET_SCE_IOPRELEXEC modules, Loadcore allocates MemSize plus 0x30 bytes and sets text_start to the allocation result plus 0x30, so the runtime load base is selected dynamically.” — unsupported, confidence `0.58`, supports `0.03`, says-nothing `0.72`, contradicts `0.25`, review. The initial evidence excerpt had omitted the allocation lines, so this is preserved as an evidence-gap disposition.
4. “Loadcore copies PT_LOAD file bytes to text_start, zero-fills up to memsz, then applies every SHT_REL section using text_start as the base.” — verified, confidence `0.99`, supports `0.99`, auto.
5. “The pinned ApplyElfRelSection implements R_MIPS_32 by adding base; R_MIPS_26 by combining base with the encoded jump target; HI16 by adding base and the signed low half from the immediately next relocation row then carrying into the HI half; and LO16 by adding base to the word and retaining the low 16 bits.” — verified, confidence `0.94`, supports `0.96`, auto.
6. “The current Ghidra MIPS importer fallback GP is not an observed Sony runtime GP value for these IRX modules.” — verified, confidence `0.97`, supports `0.97`, auto.

The separate follow-up `jev_verify` added the previously omitted direct allocation excerpt (`jev-verify-allocation-evidence.txt`) and two exact claims:

1. “For ET_SCE_IOPRELEXEC IRX modules, Loadcore calls AllocSysMemory using ModuleInfo.MemSize plus 0x30, then sets fi.text_start to the returned address plus 0x30.” — verified, confidence `0.88`, supports `0.92`, auto.
2. “The pinned Loadcore loadrelelf adds the selected text_start address to the relative gp and EntryPoint values before copying and applying relocations.” — verified, confidence `0.93`, supports `0.95`, auto.

## Local corpus claim verification

A later `jev_verify` checked local measured summaries for the 24-module corpus. It verified the base-zero limitation (`0.86` confidence, auto), same-function-inventory claim (`1.00`, auto), and absence of executable GP-based memory operations (`1.00`, auto). Its first claim—combining source semantics and local extraction, “The third 32-bit field in the PS2SDK iopmod structure is the GP-relative value, and Loadcore computes module GP as selected text_start plus that value.”—was verified at confidence `0.73` but marked `review` (supports `0.82`, contradicts `0.17`, says-nothing `0.01`). This aggregate check is retained as a review flag; the earlier focused direct-source checks above separately gave the field-order claim `1.00` and assignment-plus-base claim `0.95`, both auto.

## Scratch-script review

`jev_review` was run once on `relocate_iop_irx.py` and `ProbeIopGpContext.java`, with the local test and final Ghidra run summary. It returned action `escalate`, composite `0.633875`, `safe_to_apply=0.39`; both files were limited by the `test_gap` rubric. Relocation helper: `safe_to_apply=0.41`, correctness confidence `0.53`, spec-match `0.61`, test-gap `0.23`, blast-radius confidence `0.90`, composite `0.84125`, action `escalate`. GP probe: `safe_to_apply=0.39`, correctness confidence `0.32`, spec-match `0.62`, test-gap `0.20`, blast-radius confidence `0.99`, composite `0.4265`, action `escalate`. The model reported reasons `confidence_below_review` and `safe_to_apply_below_review`. These are private scratch helpers; the review escalation remains open and is not represented as a passing Jev approval. It was not retried.

All scores are judgment signals. Exact local scripts, command logs, input hashes, and test outcomes are retained beside this receipt; the program evidence is local and no full game pseudocode or binary payload was sent in the Jev calls.
