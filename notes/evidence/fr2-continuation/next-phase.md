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
| Table of 0x34-byte records after the textures | Count and fit verified; meaning not recovered | Next step, from `FUN_0011ed90` |
| Later loaders (0x70-byte records with floats), geometry and VU1 data | Not started | |
| Stage 1 chain to end of file | Open | Needs the later sections translated |

## Next steps, in order

1. Translate the 0x34-byte record table and each following loop of `FUN_0011ed90`, one section at a time; extend the walker only when the loader text supports it.
2. After each section, check the chain on all 56 files and add negative tests.
3. Resolve the 4-bit pixel layout against the loader's GS upload code, not by guessing from images.
