# Continuation evidence (after milestone #2)

New offline checks for the unchanged PAL corpus, each separate from the three milestone checks and from each other. Each writes an immutable UTC/UUID result directory with `result.json` and `report.md`; `pass` exits 0, `fail` 1, missing prerequisites `incomplete` 2. No emulator is started and no window is opened. Run from the repository root with Python 3.10 or newer (3.14 was used); the audio oracle needs `ffmpeg` on `PATH` (without it, `--oracle ffmpeg` is `incomplete`, never a pass).

```sh
python3 tools/verify_audio.py corpus games/ford-racing-2 --oracle ffmpeg
python3 tools/verify_ptg.py corpus games/ford-racing-2
python3 tools/verify_model.py corpus games/ford-racing-2
```

Single inputs: `verify_audio.py bank MSH MSB`, `stream MIH MIB`; `verify_ptg.py file PTG`; `verify_model.py file PS2`. All accept `--output`.

## What is verified

| Check | Verified on the corpus | Not claimed |
| --- | --- | --- |
| Audio | All 305 bank sample spans and 20 music streams satisfy PS-ADPCM block structure; spans end with one flag-3 block (206) or a flag-1 block plus a flag-7 end marker with 0x77 filler (99, all in `speech.msb`); any other end-flag placement fails as outside the measured classes; music has two channels, 0x8000 interleave and a header turn count equal to the observed turns (20/20). The reference decoder equals ffmpeg 9.0.2 `adpcm_psx` sample for sample on all 305 spans and 40 music excerpts. | Bit-exactness with SPU2 hardware, playback, loop behavior, the meaning of the `.mih` second word |
| PTG | Header relations on all 548 files; the 17 files with last word `0xDDDDDDDD` have size `1120 + 1104 × count`, per-tile pointer records whose floats are the covered fraction at the row-major position, and 64-byte descriptor blocks (ten words fixed at `0xDDDDDDDD`; five words constant within a file) | Palette, tile pointer values, descriptor constants, the 491 other multi-tile bodies |
| Model | The first u32 equals the name-pool end offset in all 56 models, with zero padding to the next 16-byte boundary | Geometry and the later header |

## How corpus mode establishes completeness

Each corpus command first pins the executable, archive header and archive data, then reads the archive independently and takes the expected file list and per-file SHA-256 from it. A missing expected file makes the run `incomplete`; a file whose content differs from the archive output, or a header or payload with no partner in the archive, fails. No count is hard-coded in the tools. Spans larger than 1 MiB would be structure-checked but not decoded, and the result says so (the corpus maximum is 80 KB). `verify_ptg.py file` returns `incomplete` for a single-tile file outside the sprite contract so a damaged sprite cannot look like a pass.

## Corrections found along the way

- The first audio decoder used a rounded feedback term, clipped history and decoded end-marker filler; it matched ffmpeg on 1 of 305 spans. The oracle showed it wrong and it was fixed (truncating feedback, unclipped history, silence for flag 7).
- The model's first word was recorded in milestone #2 as an unresolved "leading count"; it is the name-pool end offset. The milestone contract output is unchanged.
- An early inference that PTG tiles were stored in a permuted order was wrong; the pointer-record floats show row-major order.
- An independent reviewer found that corpus mode accepted a mirror with files removed, that mid-stream end flags passed, that `format_contracts.model()` was quadratic (output unchanged by the fix), and that `jev_call.mjs` could lose or corrupt receipts. All were fixed test-first; see `jev/INDEX.md` entries d021-d025.

## Jev record

`jev/` holds one immutable receipt per decision (exact arguments, full result, evidence hashes, timing); `judgment-dispositions.json` records each result and what was done with it; `jev/INDEX.md` is the human index. Review and gate results that were not `auto` stay recorded as such. `index.json` carries SHA-256 for every file here and locates the original local results. `results/` holds the final audio, PTG and model results; earlier audio runs against the first decoder remain in the ignored scratch area.

Jev is advisory. Byte equality, the oracle, tests and the real corpus decide factual acceptance. Model-threshold reliability on game hypotheses is unmeasured.

See [completion-matrix.md](completion-matrix.md) for the status of every area and the finish criteria.
