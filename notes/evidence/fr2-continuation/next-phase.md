# Mesh, VU and render reconstruction: bar and status

Scope chosen by the project owner after milestone #2. Offline and static only: no emulator, no debugger window. The bar below was chosen with Jev (receipt `d035`, `chain_then_geometry_invariants`, all three requirements supported); it extends criterion 2 of the completion matrix with stages that can fail on the real corpus.

## Bar

1. **Section chain.** The translated section walker consumes every one of the 56 `.PS2` models exactly to end of file, with validated counts, negative and boundary tests, and a pinned immutable result.
2. **Geometry invariants.** For each recovered geometry section, extraction with checks that can fail: indices within the vertex counts, finite floats, bounding boxes that agree across files of the same kind, texture indices within the texture library.
3. **Render preview.** Selected models are rendered and the owner reviews them. A review is recorded as a user observation, never as proof of a factual claim.

Each stage claims only what it measured, keeps an unresolved list, and gets Jev claim checks with deliberate overclaims recorded as unsupported. "The whole game is reverse engineered" is not a stage.

## Status

| Part | Status | Evidence |
| --- | --- | --- |
| Name tree and section boundary | Done (56/56) | `verify_model.py`; loader `FUN_00123908` |
| Texture library section | Bounded static level 0 interpretation for all 2,370 format 1/3/4 images; 56/56 sections retain their measured boundaries | [Upload audit](../fr2-texture-upload-audit/README.md); complete index/RGBA hash receipts; renderer equivalence unproved |
| Format4 and small indexed level 0images | Decoded under descriptor/upload/CLUT guards | 469 four-bit images and 230 direct eight-bit profiles; nineteen large palette blocks handled; oldswizzle error retained |
| Mip pixels, palette table semantics and runtime CLUT state | Open | Listed in the verifier's `unresolved` |
| Table of 0x34-byte records after the textures | Serialized traversal recovered and bounds checked; rendering meaning remains partial | `tools/ps2_sections.py`; [section-chain evidence](../fr2-static-recovery/results/sections.json) |
| Later loaders (0x70-byte records with floats), geometry and VU1 data | Section boundaries and recursive serialized lengths recovered; vertex/index/render semantics remain unresolved | Eight VU chunks have exact byte reassembly and static VIF upload matches; this does not establish geometry semantics |
| Stage 1 chain to end of file | Done for the bounded 56-file corpus | 54 files use the loader-derived 68-byte header; two exact-hash legacy profiles use 60 bytes, without evidence that the current executable selects that profile |
| Mapped object-row floats | 113,812 finite input words across 56 models; corrected serialized offsets 8/12/16/20 | [producer/consumer correction](../fr2-geometry-consumer-audit/root-correction/README.md); mesh and VU output meaning unproved |
| Stage 2 geometry invariants | Open | Full vertex/index/texture-reference semantics and the requested cross-file checks remain incomplete |
| Stage 3 render preview | Open | No new owner-observed render result is established by static source recovery |

## Next steps, in order

1. Connect the recovered serialized geometry sections to their VU and renderer consumers using the saved instruction stream, then derive vertex/index/texture-reference invariants with explicit rejection cases.
2. Keep exact EOF and profile guards on all 56 model files while adding semantic extraction; retain the two legacy-profile limits.
3. Extend the measured level-zero contract to mip/palette state against exact loader GS packet construction, retaining any unsupported profile.

The owner subsequently expanded the goal to full game decompilation. [The static recovery bundle](../fr2-static-recovery/README.md) and [combined checkpoint](../fr2-combined-recovery/README.md) track the broader EE/IOP/VU work. That expansion does not turn the geometry or render stages into completed work.

The broader generated host executable now [links statically](../fr2-link-interface-audit/README.md) with 4,746 guest entry addresses. It has not been executed. The [IOP relocation-aware export crosswalk](../fr2-iop-relocated-exports/README.md) and [13 provisional metadata entries](../fr2-iop-entry-recovery/README.md) add bounded static recovery evidence; they do not complete source, geometry or runtime equivalence.

The current [fourth-candidate EE export](../fr2-ee-next-seeds/README.md) has 3,842 generated functions/zero API failures, and the [IOP export union](../fr2-iop-export-recovery/README.md) has 2,388 generated functions/zero API failures. Neither proves complete function discovery or recovered source identity. The latest texture integration passes 297 Python tests and the six-file type check. Earlier baseline receipts stay unchanged.

The additional [mip field/address trace](../fr2-texture-mip-field-audit/README.md) preserves75 small packed mip records with conditional address-coverage gaps and separates source allocation, TBW and DBW fields. [Synthetic CPU GS uploads](../fr2-gs-low-width-audit/README.md) establish software width-clamping behavior and the primary manual range, without original game execution. The next guarded EE candidates and the geometry matrix/header interpretation remain under review.
