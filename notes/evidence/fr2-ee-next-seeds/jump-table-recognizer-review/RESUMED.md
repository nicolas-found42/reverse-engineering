# Resumed first-slice work, 2026-10-04

The user authorized resuming after the initial escalation. The original README, receipts, source hashes, and failed GPR0 control remain a historical record of the first review; they do not describe the corrected source as ready.

The GPR0 defect now has a regression that failed before the fix and passed after it. Register-zero writes cannot supply a table-address definition. A second genuine failing control exposed JR0 dispatch recognition; JR0 is now refused. Reserved fields in SLL, LUI, ADDU and JR were each observed to cause a false accept, then guarded and tested. ELF-reader tests cover interior mapping, alignment/count/extents, BSS/executable/unallocated sections, ambiguous section mappings and truncated payloads.

The refreshed specification review found no confirmed remaining defect. A reported BEQ-after-LW concern did not reproduce: nearest-non-NOP load discovery already rejects it. The disagreement is retained here; no red test is claimed for it. A BEQ-after-scaling case did reproduce and is now rejected by the supported compiler-profile ordering check, with a red-then-green regression.

Twenty-six focused tests pass. The raw-byte scan remains 24 recognized sites out of 29 across 408 seeds. These results establish only the measured utility profile, not safety of the future walker or Java transaction. No original code was executed. Pipeline integration is the next slice.
