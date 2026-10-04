# Serialized mip fields and conditional address coverage

The traced uploader distinguishes allocation size, sampler width and transfer width in each 16-byte mip record. All 2,571 extra-mip records across the 56 SHA-bound archive models were counted. Four word fields now have bounded static interpretations; their on-disk values are not runtime addresses or evidence that a level renders correctly.

| Byte offset in record | Traced use | Serialized observation |
|---:|---|---|
| +0, low16 | Allocation return stored here, then used for mip TBP and upload DBP | Zero in every record |
| +2, high16 of word0 | Allocation increment passed to `00222080`; `0022c660` recalculates it through `0022c9f0` | Nine distinct full-word0 values |
| +4, low16 | Width packed into MIPTBP1 TBW1/2/3 | 1:498; 2:2,060; 4:13 |
| +8, full32 | Loader stores source pointer; uploader reads it as transfer source | Zero in every serialized record |
| +12, low16 | Destination width passed to the packet builder and shifted into BITBLTBUF DBW | 0:224; 1:1,939; 2:408 |

The high halves at +6 and +14 remain unresolved. This particular uploader consumes their low halves only; that does not prove other routines ignore them. The PSM/bits-per-pixel choice occurs once before the mip loop from descriptor bit8, and width/height halve each iteration. The allocator-return provenance links upload DBP and sampled mip TBP in this path, but other writes and the exact dynamic allocation/base state are not established.

The root read the relevant C field flow and separately matched all 14 saved instruction anchors to bytes in unique file-backed ELF segments. In particular `002224ac` is `LHU a3,+0xc(s0)` with bytes `0c000796`; an earlier informal message called it LW, which is incorrect. [root-word-validation.json](root-word-validation.json) records the actual check. The full generated C and original instruction inventories remain ignored.

The conditional packed-indexed address experiment uses the pinned public PCSX2 page/block/column tables, the measured record+4 TBW and record+12 DBW, and equal upload/sample bases normalized to zero. It checks 1,740 packed extra mips across 31 dimension/width profiles. In 75 logical8×8 records—53 format3 and22 format4—32of64 sample-pixel starts fall outside the nibble addresses written by the assumed4×4 transfer. Those records serialize allocation1, TBW2 and DBW2. Every other measured profile has full sample-start coverage under these assumptions. This is address-set coverage, not an all-mip value-permutation check.

Equal source-byte and transfer-byte totals do not resolve that address gap. Actual preceding VRAM writes, allocation alignment and runtime texture state remain unknown. The findings do not demonstrate texture corruption or silicon behavior, and no mip decoder behavior was changed. Level-zero decoding retains its separately measured strict mappings. The zero-width record software audit is in [fr2-gs-low-width-audit](../fr2-gs-low-width-audit/README.md).

Jev’s field pass retained six verified claims, with the DBW semantic label flagged for review (confidence0.37; same_subject0.27). The root resolves only the bounded packet-field placement from the reviewed left-shift48 dataflow and pinned register layout, supported by the LHU raw anchor. The parsed complete result including probabilities and same_subject plus its analyst interpretation is preserved with the exact request. The root’s separate intersection pass verified the conditional75-record count and insufficiency of byte totals; it marked a deliberately tested hardware-corruption claim unsupported. That unsupported claim is rejected. Both calls retain their original thresholds and results.

The byte-count evidence covering 4,941 total levels and 79,708,000 source bytes is separate: [all-model mip count audit](../fr2-texture-upload-audit/mip-upload-static-audit/README.md). The current evidence supports static field flow and constrained software/address models; it does not complete mip reconstruction or rendering equivalence.

The agent checker copy is archived with its original path assumptions. Its recorded invocation is `python3 .scratch/mesh/codex-root/texture-independent-review/audit_mip_record_words.py` from the repository root; the ignored original output and source SHA remain in the root-validation receipt. The root intersection checker uses the repository working directory and preserves its scratch output.
