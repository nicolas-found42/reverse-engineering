# Jev decision ledger — continuation session 2026-10-04

Receipts are `<id>.json` in this directory (exact arguments, full MCP result, evidence hashes). Created by tools/jev_call.mjs against @jkudish/jev-mcp 0.13.0, model typesafe/jev-1.13 via OpenRouter.

| id | tool | question | result | disposition |
| --- | --- | --- | --- | --- |
| d001-screen-issue-1 | jev_screen | intake of tracker issue #1 | pass, injection 0.04 | used as task data |
| d001-screen-issue-2 | jev_screen | intake of tracker issue #2 | review, injection 0.29 (threshold 0.25) | inspected: the "do not / must" text is the spec's own agent requirements; no credential request, tool redirection or rule override. Used as task data only. |
| d002-dsstore-policy | jev_decide | handling of Finder .DS_Store | operational failure: requirements must be strings (schema) | retained; corrected call below |
| d002b-dsstore-policy | jev_decide | same, corrected schema | selected ignore_exact_basename_reported, confidence 1, no warnings, no escape | applied (visible exclusion + test); original destructive alternatives rejected |
| d003-review-dsstore-patch | jev_review | review of the .DS_Store patch | action review (confidence_below_auto_accept); correctness 1.97, spec 1.98, test_gap 0.23 (conf 0.66), blast 0.83 (conf 0.53), composite 0.91 | NOT auto. Retained as review. Independent evidence: 16/16 tests, pyright 0 errors, real-corpus formats pass (replay/formats-after-fix.log). |

Deterministic-only decisions (no semantic call): hash/identity replay of static/runtime/formats; test and type-check execution; process check (no PCSX2 running).

jgrep: `jgrep --json -t 0.5 "excludes or ignores files from a comparison or failure check by name" tools/corpus_contract.py` exit 0, 2 hits (lines 51-110, 111-170) = the intended change.

## Audio investigation cycle (decisions d004-d010)

| id | tool | question | result | disposition |
| --- | --- | --- | --- | --- |
| d004-rank-next-work | jev_rerank | order 9 mixed candidate workstreams | max relevance 0.47; audio ranked 6th at 0.19 despite strongest measured evidence | Not acted on. Query was an omnibus mixing investigations, housekeeping and a user question; ordering judged unreliable. Retained unchanged; replaced by a narrower, differently structured jev_decide (d005), not a retry. |
| d005-decide-first-investigation | jev_decide | first investigation among 5 real investigations + gather-evidence | audio_adpcm_decode_and_falsify 0.99, confidence 0.98, no escape, no contradicted requirement | Applied. PTG probe was the supported runner-up (0.01) and is next. Caveat: evidence text mentioned d004 was judged unreliable, which may have steered the answer. |
| d006-decide-audio-placement | jev_decide | new CLI vs extend bank() contract vs notes only | new_verify_audio_command, confidence 1; extend_bank_contract contradicted on both requirements | Applied (separate verify_audio.py; milestone-#2 contract and results untouched). jgrep-2: no existing ADPCM decoder in tools/ (hits only in the new module). |
| d007-verify-audio-claims | jev_verify | 8 claims vs counts/controls/tests | 4 verified auto; claim 0 unsupported (review 0.63), claim 2 verified at review 0.70; two deliberate overclaims (playback; mih word1 = loop start) unsupported | Overclaims not made. word1 stays UNRESOLVED (no loop flags exist in the streams). Claims 0 and 2 lacked per-span evidence, not contradicted. |
| d007b-verify-audio-claims-with-code | jev_verify | claims 0 and 2 with verifier source as new evidence | both verified auto (0.99, 0.97) | Resolved by new evidence, not by retrying unchanged inputs. |
| d008-review-audio-patch | jev_review | per-file review of the first audio patch | escalate (confidence_below_review); safe_to_apply 0.72-0.76, composite 0.83 | NOT auto. Retained. Led to an independent ffmpeg oracle, which FALSIFIED the first decoder (1/305 exact). See d009. Independent code review still required at milestone review. |
| d009-decide-decoder-alignment | jev_decide | how to change decoder after oracle mismatch | align_to_ffmpeg_document_as_software_equivalent 0.98, no escape | Applied: truncating feedback, flag-7 = silence; claim worded as software-reference agreement, not hardware-exact. |
| d010-verify-oracle-claims | jev_verify | 7 claims vs oracle run, mismatch investigation, tests | 5 verified auto; hardware-exact claim unsupported (review 0.36, contradicts 0.57); loop-from-mih unsupported | Overclaims not made. Unclipped filter history discovered by a follow-up measurement (not by Jev). |

Deterministic-only decisions (no semantic call): running the ADPCM structure probe and the ffmpeg comparison; the clipped-vs-raw history experiment (decided by byte equality against the oracle); pyright/tests; the read_bounded size bound (decided by the issue's bounded-processing rule; found by jgrep-4, p=0.90).

jgrep: jgrep-2 (ADPCM decoder duplicate search) exit 0 hits only in new module; jgrep-3..6 self-review rules on tools/spu_adpcm.py + tools/verify_audio.py: debug output exit 1, unbounded file read exit 0 (fixed), swallowed exceptions exit 1, unchecked index exit 1.

Commits (local, not pushed): ca41902 DS_Store fix; 938bdde jev_call.mjs; 8f3183f verify_audio + spu_adpcm.

Operational notes: an accidental re-run of the oracle scratch script via `import` occurred during diagnosis (harmless, read-only, output duplicated).

## Cycle 2: PTG, model, classification, independent-review fixes (d011-d026)

| id | tool | question | result | disposition |
| --- | --- | --- | --- | --- |
| d011-decide-ptg-next | jev_decide | next step for PTG | bank_invariants_as_verifier 0.93 | Applied (verify_ptg); edge-matching and consumer tracing not pursued |
| d012-verify-ptg-claims | jev_verify | 8 PTG claims | 6 verified (2 at review), colors-decoded contradicted, permuted-order unsupported | Overclaims not made; claims 0,1 re-asked with source evidence (d012b) |
| d012b | jev_verify | PTG header/size claims with source | both verified auto 1.0/0.99 | Resolved by new evidence |
| d013-review-ptg-patch | jev_review | PTG patch | escalate composite 0.88 | NOT auto; covered by independent review |
| d014-decide-model-finding-placement | jev_decide | where to record the model finding | new_verify_model_command 1.0 | Applied |
| d015-verify-model-claims | jev_verify | model claims | 2 verified, stable-structure contradicted, geometry unsupported | False claims not made |
| d016-review-model-patch | jev_review | model patch | escalate composite 0.91 | NOT auto; covered by independent review |
| d017-decide-next-work | jev_decide | next work | consolidate 0.93 | Applied |
| d018/d019 | jev_classify | status classes for the completion matrix | d018 compound: 10/16 review; d019 atomic: 16/24 auto | see dispositions |
| d020-verify-matrix-claims | jev_verify | matrix claims vs primary results | 8 verified, 2 overclaims unsupported | Overclaims not made |
| d021-d025 | jev_decide | design choices for fixing independent-review findings | d021-d023 clear; d024 low confidence 0.41 with contradicted requirement (not applied); d025 revised 1.0 | see dispositions |
| d026-review-fix-patch | jev_review | fix patch | escalate composite 0.80 | NOT auto; second-pass independent review requested |

Independent review (fresh-context agent, no edits allowed): found no blocker and five should-fix defects (corpus completeness not asserted; mid-stream end flags passing; unbounded processing in model(), bank decode and deinterleave; jev_call.mjs losing/corrupting receipts; doc inaccuracies). All were fixed test-first (d021-d026). A second pass over the fixes was requested from the same reviewer.

jgrep: jgrep-7..9 (ptg), 10..12 (model), 13..17 (fix diff files). All hits inspected; no defects. Examples: padding slice guarded by the size-multiple-of-16 check; archive paths come from the pinned header and the milestone contract already rejects unsafe paths.

Deterministic-only: fresh replays of the three milestone checks (replay2, all pass, inputs and corpus ID identical to the originals); the clipped-vs-raw history experiment; the quadratic-fix equality proof (SHA-256 of model() output over 56 models identical); all test/pyright runs.

Commits (local, not pushed): ca41902, 938bdde, 8f3183f, cf4d2da, 40fbb69; fixes and docs pending commit.

## Final gate (d027)

jev_gate over the cumulative final patch (15 files, 91 KB of diffs, evidence: corpus summary, state, independent review record, tests, completion matrix). Result: escalate. Claims 0-8 (genuine): 5 verified auto, 4 verified at review confidence; claim 9 (planted control: whole game reverse engineered) contradicted 0.99. Patch review: composite 0.79, safe_to_apply 0.58, per-file escalate with low-confidence blast_radius/test_gap. Not auto-approved; not rerun; independent review is the resolution. The planted control forces an aggregate escalate, so only per-claim verdicts are informative.

Second-pass independent review: confirmed the fixes; one claimed regression (reply-then-exit) not reproducible with a flushing server; minor items fixed test-first (R2-R5). Commits d4f7f2c and 2ce0348.

## Cycle 3: mesh phase, texture library (d028-d035)

| id | tool | question | result | disposition |
| --- | --- | --- | --- | --- |
| d028-find-model-loader-chunks | jev_find | locate pointer relocation in loader chunks | partial 0.67 | used to locate only |
| d029-find-model-loader-chunks | jev_find | locate name-tree walk | absent 0.21 in searched function | used to locate only |
| d030-find-model-loader-chunks | jev_find | locate float-field handling | answered 0.90 | used to locate only |
| d031-decide-mesh-method | jev_decide | method for recovering the model container layout | translate_section_parsers, conf 1 | applied |
| d032-verify-texture-claims | jev_verify | 7 texture-library claims incl. 2 overclaims | 5 verified (claim1 review 0.14), 4-bit decoded contradicted, geometry unsupported (review) | overclaims not made; claim1 split in d033 |
| d033-verify-decode-coverage-atomic | jev_verify | atomic decode coverage claims | verified 0.98 auto; under-16 claim review 0.71 | not relabeled; resolved by the deterministic corpus test |
| d034-review-texture-patch | jev_review | review of the texture patch | escalate; safe_to_apply 0.41, no named defect | not auto-approved; resolved by tests, mutation, fuzz, jgrep; result stays escalate |
| d035-decide-mesh-phase-bar | jev_decide | bar for the mesh/VU/render phase | chain_then_geometry_invariants, conf 1 | applied in next-phase.md |

jgrep: jgrep-18 (debug output, 0 hits), jgrep-19 (unvalidated offset slicing, 2 hits at ps2_container.py:173-187 p=0.67 and verify_textures.py:36-67 p=0.54; inspected, ranges are bounded by parse()'s need() checks). Deterministic-only: pyright, full suites, the swap mutation, the 3,000-mutation fuzz.
