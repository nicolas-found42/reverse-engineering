# FR2 static recovery: discovery and section evidence

This note records the bounded static recovery completed against the extracted `SLES_517.05` executable and the model corpus. It reports instruction, pointer, and byte-layout evidence. It does not claim whole-game source recovery, original function extents, geometry semantics, or gameplay reachability except where a bounded machine-code dispatch is explicitly described.

## Executable identity and function inventory

The executable used throughout is ELF32 little-endian MIPS, SHA-256 `216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95` (`games/ford-racing-2/extracted/SLES_517.05`). The original saved Ghidra inventory had 3,453 functions. A first isolated discovery pass added 381 provisional analysis functions at exact address-taken `LAB_` targets. The pass required an unowned pre-state, an explicit source-side address store, matching raw executable bytes, an existing instruction decode, and a negative-frame `addiu sp,sp,imm` opcode. Reanalysis retained all 381. A separate pass then added three provisional functions at file-backed `.rodata` dispatch-table entries 2, 4, and 8. The resulting isolated static inventory has 3,837 functions: `3,453 + 381 + 3 = 3,837`.

The first 381 candidates' function bodies total 51,276 bytes. A deterministic body audit found no overlap with the 3,453 pre-existing function bodies and no candidate-to-candidate overlap. Their full 51,276-byte total equals the `.text` owned-instruction-byte increase. The later three targets each passed the same body-overlap gate against the 3,834-function starting inventory and one another. Their Ghidra-proposed bodies are:

| Entry | Proposed body bytes | Basis |
|---|---:|---|
| `001fcd18` | 140 | `.rodata` slot `0028b858`, table index 2 |
| `00200c80` | 144 | `.rodata` slot `0028b860`, table index 4 |
| `00200770` | 496 | `.rodata` slot `0028b870`, table index 8 |

The 11-word table begins at `0028b850`, ends at `0028b87c` exclusive, and is read by `FUN_00200648`. The caller clamps the selector to `0..10` and performs an indexed indirect `jalr v0` at `00200710` (`09f84000`). Each of the three table words equals its target address; Ghidra records an exact DATA reference from each slot to its target. Target bytes match the ELF and begin with a decoded `addiu sp,sp,-0x20` whose opcode fields encode a negative stack frame. This establishes statically addressable dispatch entries. It does not establish normal gameplay reachability or exact original function boundaries; the body sizes above are Ghidra control-flow results.

### Discovery gate correction

An early scratch version of the table-candidate creator passed the pointer slot as the target and the code address as the source to its reference predicate. The independent probe showed exact incoming DATA references, while the creator falsely reported all three as missing and created none. The arguments were corrected; the successful run is `data-table-create-results-04.json`. The corrected gate records incoming references and checks the `.rodata` table bytes, bounded `jalr`, raw target bytes, pre-existing instruction decoding, negative-frame opcode, and proposed-body intersections before using `CreateFunctionCmd` with `SourceType.ANALYSIS`. Earlier failed/rejected output remains available as a debugging record and is superseded by the corrected run.

## Model section-chain profile

The corpus run is pinned to corpus id `e69a2afbd6db606d166e40bae32c436691e134722ad153200859961a5f517dab`, executable SHA-256 above, archive header SHA-256 `f4e4a4f91cd89bcaa8c2772e6cba2a839d92fbe222290c8c751777a81963731d`, and archive data SHA-256 `357fc371f47e366bf507b721e26eed9f1205516c19b793e0316ccecc2175a722`. The bounded corpus run parsed all 56 models to exact EOF, with no unsupported files or failures:

| Later-header profile | Models | Consumption rule |
|---|---:|---|
| `loader68` | 54 | Consume 17 serialized u32 words / 68 bytes. Word 0 is checked as `17`; allocation words are compared with parser-observed record/node/pair totals, leaving the ignored loader word unconstrained except by the observed profile. |
| `measured_legacy60` | 2 | Consume exactly 15 observed u32 words / 60 bytes, then map them logically as `[17] + raw15 + [0]` for the existing allocation-index comparisons. Selection is restricted by the two measured model SHA-256 values below. This is a structural fit only; the current `FUN_0011ed90` loader disassembly does not show selecting this profile. |

The two measured legacy files are `3DDATA/TRACKS/Brands.PS2;1` (5,449,792 bytes, SHA-256 `0b6235f545e870c7237a256952f4ab1ee261528ab466b2d403e9fb393b31fbb8`) and `3DDATA/TRACKS/Canyon.PS2;1` (4,249,888 bytes, SHA-256 `bf689b86a426489f84e24a250a5fb26ea1655bcaba907f17769ba4d601ed5f48`). Both match the measured 60-byte profile and pass the same allocation checks, final zero-padding check, and exact-EOF check. Neither match proves that the current executable loader accepts or selects the profile.

The parser keeps serialized input spans separate from expanded memory records. Relevant source-grounded translations include:

- `FUN_001205e0`: 27 serialized dword reads (108 bytes) per node; its child count is read from the fourth dword at input offset `+0x0c`; descendants are traversed in preorder. The in-memory child stride is a separate loader-side output detail.
- `FUN_001208d0`: eight fixed dwords (32 bytes), then a masked pair descriptor at `+0x20`, 8-byte pair records beginning at `+0x24`, then the masked child count. The zero-descriptor/zero-child baseline is 40 bytes.
- The final tail record fixed body is 15 dwords / 60 bytes, not 16 dwords / 64 bytes. Its vector and byte payloads are validated against global allocation counts; the final 16-byte alignment bytes must be zero.
- The `stack_21c` writes are pointer relocations in already loaded memory and consume no serialized bytes. A branch-delay-slot `addiu s1,+4` paired with a `lw -4(s1)` reads the current count word; it is not a skipped dword.

### Parser investigation corrections

Earlier scratch analyses omitted two `lwc1` reads in `FUN_001208d0` at `00120998` and `001209a4`, shifting the descriptor and child-count positions by eight bytes. The corrected direct cursor accounting is recorded in `.scratch/mesh/codex-helpers/jev-helper-correction-disposition.json`; do not rely on the superseded helper claims. A separate first pass over the post-loop cursor added an erroneous prefix to a row-table formula; exact instruction accounting showed two count dwords followed by each positive row's count word and six floats per item. The final-record fixed body was also corrected from 64 to 60 bytes by counting the 15 actual loads. Dispositions retain the prior disagreements and the source addresses used to resolve them.

## Experimental duplicate-target jump-table recovery

`tools/ghidra/experimental/VerifiedJumpTableOverride.java` and `ordered-jumptable-override.patch` are isolated experiment artifacts for one verified computed jump at `0017f5dc` in `FUN_0017f510`. The Java script pins the executable SHA-256, requires language `r5900:LE:32:default`, checks the function body contains the computed branch, pins the patched native decompiler SHA-256, and hashes the script and patch. It also pins the seven exact table words at `0025cb60`, selector initialization/scaling, loop increment/bound/delay slot, and argument-setting target instructions. It checks all seven destination occurrences, including the repeated target `0017f628`, then checks eight generated-C assertions before writing a per-function C file and manifest into a fresh output directory.

The native patch enables ordered matching only when supplied destinations contain duplicates. Unique-target lists retain the legacy set-based path. Ordered targets are carried through cloning and encode/decode. An out-of-order duplicate-bearing sequence fails the ordered normalization check and falls back to the trivial model. Tests recorded in the scratch evidence cover duplicate order, persistence after reopening the saved project, unique-target permutation compatibility, and a deliberately mismatched duplicate sequence. A guarded export over the 3,837-function copied project generated all 3,837 functions with zero API errors; the ordinary historical baseline still has its known failure at `0017f510`.

This remains experimental and copy-only. It does not alter the installed Ghidra binary or original project. A positive run using the pinned native/script/patch hashes generated all 3,837 functions with zero API errors; the recovered `0017f510` C hash exactly matches the guarded function output (`68cedd349d0ffb13f5132aaf4bed5971721443d1b7c5322a7e9214d76c305e9d`) and all eight assertions passed. A baseline-native negative run was rejected on hash mismatch before writing source, object, or manifest. Jev's narrowed review escalated with low confidence (`safe_to_apply=0.17`); that is advisory review, not approval. Continue to restrict execution to a disposable copied project and retain the exact run manifest and adjacent native build/source provenance.

## Evidence index and limits

Exact machine-readable results stay in `.scratch`; full function inventories and per-function C/assembly dumps are not copied into this note. Key artifacts and SHA-256 digests are listed in [`provenance.json`](provenance.json). The complete 56-model result is `.scratch/evidence/sections/20261004T090536Z-7e3930a192e945499eda27207014ba9b/result.json`; its report contains per-file counts and offsets. The original 381-candidate creation/body receipts and the later three-candidate receipts remain in `.scratch/mesh/codex-helpers`. Jev inputs/results remain at their original scratch paths; this note retains safe conclusions and receipt identities instead of embedding whole reports.

The static inventory count, body non-overlap, exact EOF, and generated-C byte/pattern checks are structural facts. They do not prove original source extents, full code discovery, game behavior, runtime dispatch reachability, geometry meaning, recompilability, or whole-game equivalence. The physical executable coverage remains incomplete: the root verifier reports 941,700 listed bytes and 305,628 unlisted bytes across 1,247,328 physical executable bytes, excluding 13,584 zero-filled DVP placeholder bytes. The remaining unlisted executable bytes need classification.
