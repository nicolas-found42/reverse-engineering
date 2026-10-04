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
| Texture library section | Done for formats 1 and 3 at level 0 (1856 of 2370 images); 56/56 sections end where the next section's record count begins | `verify_textures.py`, `ps2_container.py`, `tools/test_ps2_textures.py`; two images viewed |
| Format 4 (4-bit) pixels, 45 images under 16 pixels, mip pixels, palette table entries | Not decoded | Listed in the verifier's `unresolved` |
| Table of 0x34-byte records after the textures | Serialized traversal recovered and bounds checked; rendering meaning remains partial | `tools/ps2_sections.py`; [section-chain evidence](../fr2-static-recovery/results/sections.json) |
| Later loaders (0x70-byte records with floats), geometry and VU1 data | Section boundaries and recursive serialized lengths recovered; vertex/index/render semantics remain unresolved | Eight VU chunks have exact byte reassembly and static VIF upload matches; this does not establish geometry semantics |
| Stage 1 chain to end of file | Done for the bounded 56-file corpus | 54 files use the loader-derived 68-byte header; two exact-hash legacy profiles use 60 bytes, without evidence that the current executable selects that profile |
| Stage 2 geometry invariants | Open | Full vertex/index/texture-reference semantics and the requested cross-file checks remain incomplete |
| Stage 3 render preview | Open | No new owner-observed render result is established by static source recovery |

## Next steps, in order

1. Connect the recovered serialized geometry sections to their VU and renderer consumers using the saved instruction stream, then derive vertex/index/texture-reference invariants with explicit rejection cases.
2. Keep exact EOF and profile guards on all 56 model files while adding semantic extraction; retain the two legacy-profile limits.
3. Resolve the remaining 4-bit pixel and mip/palette layouts against the loader's GS upload code.

The owner subsequently expanded the goal to full game decompilation. [The static recovery bundle](../fr2-static-recovery/README.md) and [combined checkpoint](../fr2-combined-recovery/README.md) track the broader EE/IOP/VU work. That expansion does not turn the geometry or render stages into completed work.
