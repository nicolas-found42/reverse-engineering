# Ford Racing 2 reverse engineering: completion matrix and finish criteria

State as of 2026-10-04 for the unchanged PAL SLES-517.05 corpus (corpus ID `e69a2afb…7dab`). Baseline: milestone #2 at commit `38d1574`. Everything below is offline and read-only; no emulator was started and no window opened in this continuation.

Confidence figures are the `confidence` Jev reported; its auto/review decision also needs the top probability and margin to clear thresholds, so a figure near 0.85 can still be `auto`. Status classes come from `jev_classify` over atomic single-status findings (receipt `d019`, stable catalog, `manual_review` class, thresholds 0.85 / 0.50). Where Jev returned `review`, the class below was set by the catalog's own written precedence rules and is marked **rule**; the Jev result stays in the receipt and is not presented as automatic approval. An earlier pass over compound findings (`d018`) returned 10 of 16 `review`, which is why the findings were split; both receipts are kept.

## Completion matrix

| Area | Finding | Class | Basis (receipts) | Limits and what is missing |
| --- | --- | --- | --- | --- |
| Archive | 990 files equal an independent archive read by length and SHA-256; two real loads match | verified behavior (auto, conf 1.00) | milestone; fresh replays `replay2` | Only the unchanged PAL corpus |
| Static | Complete 3,446-function export, replayed as a passing check | verified behavior (**rule**; Jev conf 0.61, review) | milestone; fresh replay | Export content only |
| Static | Six loader stages tied to instruction bytes and runtime observations | verified behavior (auto, conf 0.98) | milestone; reasoner review | Loader only |
| Static | No decompiled C | missing prerequisite (auto, conf 0.99) | milestone README | Native macOS decompiler absent; not required by #2 |
| Runtime | Two real loads (one raw, one zlib), each repeated | verified behavior (auto, conf 0.96) | milestone captures; offline replay passes again | Two assets; replay is not a fresh capture |
| Runtime | Other asset types and game states | missing observation (auto, conf 0.91) | none | Needs new captures; the capture path opens debugger windows |
| Sound banks | Descriptor chains cover the payload exactly (27 banks) | supported bounded profile (auto, conf 0.87) | milestone | Structure only |
| Sound banks | All 305 spans obey PS-ADPCM block structure; decoder equals ffmpeg `adpcm_psx` sample for sample | verified behavior (auto, conf 0.88) | `d005–d010`, `results/audio-result.json` | Software-reference agreement only |
| Sound banks | Bit-exactness with SPU2 hardware | missing observation (auto, conf 0.85) | claim judged unsupported in `d010` | No hardware oracle locally |
| Sound banks | How the game uploads and plays samples | missing observation (auto, conf 0.96) | none | EE/IOP/SPU2 path unobserved |
| Music | 20 streams: 2 channels, 0x8000 interleave, header turn count = observed turns (20/20), ADPCM-valid; 40 excerpts equal ffmpeg | verified behavior (auto, conf 0.87) | `d007–d010` | No end or loop flags exist in the streams |
| Music | Meaning of the `.mih` second word | unresolved interpretation (auto, conf 0.87) | `d007`, `d010` | Not a loop flag position |
| Models | First u32 equals the name-pool end offset (56/56); zero pad to 16 bytes | supported bounded profile (auto, conf 0.84) | `d014–d016`, `results/model-result.json` | Corrects the milestone's "leading count"; the milestone contract output is unchanged |
| Models | Texture-library section: 56/56 walked, 2,370 textures, 1,856 level-0 images decoded (formats 1, 3), next-section record table fits 56/56 | supported bounded profile (auto, `d032` 0.95–1.0; decode-coverage sub-claim review 0.71, resolved by the corpus test) | `d032–d034`, `verify_textures.py` | Format 4, 45 images under 16 px, mips, geometry not decoded; patch review `d034` was `escalate` and is resolved by tests, a mutation test, fuzzing and jgrep |
| Models | Geometry layout | unresolved interpretation (**rule**; Jev conf 0.66, review) | `d015` | Later header words are not a stable structure; only 16-bit index runs seen |
| PTG | Eight gear sprites decode; uppercase R and N confirmed by the user | verified behavior (**rule**; Jev conf 0.81, review) | milestone | User confirmation is the ground truth |
| PTG | Header relations hold on all 548 files | supported bounded profile (auto, conf 0.99) | `d011–d013`, `results/ptg-result.json` | Header only |
| PTG | 17 `0xDDDDDDDD` files: exact size model, row-major tile extent floats, constant descriptors | supported bounded profile (**rule**; Jev conf 0.69, review) | `d012b` verified both claims at 0.99–1.0 | Structure only |
| PTG | Palette location, tile pointer values, descriptor constants | unresolved interpretation (**rule**; Jev conf 0.46, review) | `d012` | Raw-index render is recognizable but not decoded |
| PTG | Body layout of the 491 header-only tiled files | not yet probed (auto, conf 0.88) | none | |
| UI, text, config | 216 `.dat`, 45 `.ui`, 16 `.cfg`, 5 `.mbf` | not yet probed (auto, conf 0.99) | none | |
| Consumers | EE, IOP and VU consumers of loaded buffers | not yet probed (**rule**; Jev conf 0.57, review) | none | IOP module set not enumerated |
| Capture | A windowless PCSX2 capture mode | missing prerequisite (**rule**; Jev conf 0.75, review) | none | The user forbade repeating focus theft |
| Tooling | Native macOS Ghidra decompiler | missing prerequisite (auto, conf 0.91) | none | Follow-up per issue #2 |
| Scope | The overall finish line | missing prerequisite (**rule**; Jev conf 0.62, review) | none | A user decision; see below |

## Milestone #2 acceptance (issue #2, 12 criteria)

| Criterion | Status | Basis |
| --- | --- | --- |
| Three separate commands emit report plus `pass`/`fail`/`incomplete`; only `pass` exits 0 | Met | Fresh replays in this session: all three exit 0; synthetic tests cover exit codes |
| Static report not limited to 200 entries; synthetic beyond-200 fixture | Met | Milestone test and 3,446-entry export |
| Loader stages tied to instruction bytes and hashes; unresolved stages block pass | Met | Milestone loader map |
| Real raw and zlib events, repeated, with identities and host/guest distinction | Met, with a limit | Recorded capture; replay is offline and says so |
| Capture output matches independent extraction | Met | Milestone result |
| Verifier rejects stale hashes, wrong records, omitted observations | Met | Milestone tests |
| Complete corpus accounted for, unsupported PTGs listed | Met | Fresh formats replay: 48/1,037/990/604/386, 27, 56, 548 |
| Four profiles have negative and boundary tests | Met | Milestone tests |
| Unknowns preserved; uppercase R/N regression | Met | Milestone tests |
| Synthetic and real results reported separately; missing prerequisites are `incomplete` | Met | README and tests |
| Jev decisions retained; non-auto and API errors not presented as approval | Met, and extended | The milestone gate stays **escalate**; this continuation adds `jev/` receipts and dispositions |
| Reviewable tooling, provenance index, all checks pass before closure | Met except publication | Work is committed locally; nothing is pushed and issue #2 is still open |

Closure: at the project owner's direction the commits were pushed to `main` (`2ef0194`), the project map was reconciled with the native sub-issue relationship, and #2 was closed as completed with a comment that maps the evidence and states the Jev status. The closure rests on the executed checks, tests and independent review, not on a Jev approval: the milestone gate remains `escalate`.

## Finish criteria

The user's stated standard is autonomous, evidence-backed work with Jev behind every semantic decision, with no debugger windows. Issue #2 states what "done" means for the milestone and lists audio decoding, mesh recovery, full PTG, and UI/text grammars as **separate investigations**. "The whole game is reverse engineered" is not a testable condition, so it is not used as a finish line.

1. **Milestone #2 is complete when** all 12 acceptance criteria are evidenced (above), the three checks pass on the real corpus, and the tracker reflects it. All three hold; #2 is closed.
2. **A recovered area is complete when** it has (a) a separate executable check with a real-corpus pass, (b) negative and boundary tests, (c) a claim limited to what was measured, (d) at least one independent oracle or falsifier where one exists, (e) Jev claim checks with overclaims recorded as unsupported, and (f) its unresolved questions listed.
3. **The ledger is complete when** every semantic decision has a receipt and a disposition, every `review`, `escalate` or operational failure has an independent resolution or stays flagged, and deterministic-only decisions are logged separately.
4. **A broader effort is complete when** the user names the area and a measurable bar for it. Without that, the open areas above remain listed, not finished.

Status against these: criteria 1 and 3 are met; criterion 2 is met for audio, PTG header level, and model boundaries; the unmeasured areas stay open.

## Scope decision

The project owner chose to extend the effort to **mesh, VU and render reconstruction**. That phase needs its own measurable bar, which is not covered by the criteria above and is defined in [next-phase.md](next-phase.md) (chosen with Jev, `d035`).
