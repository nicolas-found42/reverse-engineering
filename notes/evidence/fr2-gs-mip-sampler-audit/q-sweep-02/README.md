# Q-based LOD sweep (supplement 02)

Extends the fixed-LOD audit with six authored cases using LCM=0, L=0, K=0 (TEX1 = 136, LCM bit clear, MXL 2, MMAG/MMIN field 2) and homogeneous per-sprite Q of 1, 0.5 and 0.25 on both sprite vertices, in UV and ST modes. The three authored constant-color planes (8x8, 4x4, 2x2; colors red, green, blue) are the same as in the parent audit. The ten original cases are repeated unchanged inside the same binary, so the run has 16 cases.

## Observed result

Process exit 0, empty stderr. All six Q-based cases read the level-0 TEX0 base plane (`0x800000ff`) for all four output pixels. The manual Q-based formula (GS User's Manual pp62/127, per root's visual review in the parent directory) predicts levels 0, 1, 2 for Q = 1, 0.5, 0.25, so four Q cases disagree. With the four fixed-LOD disagreements the run has 8 manual disagreements in 16 cases. Result SHA-256 `7d7143919204d642968b75e672d128af5a64a02e83462ab69c8ce5037ec9f427`.

The public source explains this: `SampleTexture` takes no LOD input and `DrawSprite` calls it with q=1.0, and nothing in `gs_cpu_backend.cpp` reads TEX1 or MIPTBP1. This is a gap in the public CPU backend relative to the manual. It is not hardware observation, not original-game behavior, and not evidence of what Ford Racing 2 draws sample.

Jev verify r100 returned five verified claims, zero contradicted or unsupported, minimum confidence 0.93 (`jev-verify-r100-request.json`, `jev-verify-r100-result.json`). The request file records claims and evidence identifiers, not the full evidence text.

## Limits and history

- Sprite-specific hardware Q handling is not independently verified; expected levels use the manual LOD formula with homogeneous Q on both vertices.
- Constant-color, point-sampled CT32 planes only. No filtering, derivative or timing claim. Direct `GSDrawState` entry only; the original game was not executed. No production runtime patch.
- `probe-draft-original.cpp` (SHA-256 `6346bf72...`) is the unexecuted worker draft. `probe.cpp` differs in two ways: Q-case outcomes are recorded instead of asserted, and framebuffer readback uses block base 4096 (FRAME.FBP=128) instead of the draft's 128. The first compiled run of the draft-based probe aborted in the fixed-mode assertion because of that base error; its stderr and a note are in `failed-attempt-01/`. The 01 artifacts were checked byte-identical against `01-preservation-before.json` (19 files) before and after the run.
- Reproduce from the repository root with `python3 run_probe_02.py` against the ignored scratch layout; it re-pins the public revision, sources, libraries and symbol exclusions (4,746 guest names absent).
