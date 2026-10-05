# Ford Racing 2: progress audit against the owner's stated goal

Owner's goal: **full game reverse engineering**. The project's own bar (`notes/evidence/fr2-continuation/decompilation-bar.md`) and the agent-agnostic handoff's six workstreams define what that decomposes into. This audit states, per stage, what is **measured with a check that can fail**, what is **open**, and the **live numbers**. Static and offline only; nothing here runs game code.

Corpus: PAL `SLES_517.05`, SHA-256 `2167…ea95`. Latest saved-function baseline: **5,454** (no g4 yet).

## The six workstreams (from the continuation handoff)

| # | Workstream | State | Live measurement | What is open |
| --- | --- | --- | --- | --- |
| 1 | EE discovery / boundaries | Mostly measured | 1,247,328 executable bytes; **1,140,024 owned (91.4%)**; code-shaped unlisted **73,756**; spans anchored/via/unreferenced 56/7/155; batches g1–g3 added 412/113/211 | g4 unrun (41-seed config regenerated, `dropped:{}`); the remaining 73,756 unlisted bytes are blocked by guard limits, not by missing evidence |
| 2 | EE signatures / types / references | Partly measured | gp offset names **13,609 → 0**; **1,023** inferred small-data types; **872** literal-pool constants; 146 `.c`/`.cpp` units attributed | **3,940** call-arity mismatches; **23,142** undefined-type tokens; **709** integer-or-pointer small-data words |
| 3 | IOP and EE–IOP interfaces | Partly measured | 24 modules; **2 of 24 profiled** (STREAM, LGDEV); import stubs **436 of 748 named** (**312 unresolved**); union export **2,388** generated functions; **24,783** observed relocations | 22 modules unprofiled; EE→IOP name transfer; runtime load base unproved |
| 4 | VU interfaces | Bounded evidence, open | 8 mapped chunks, **13,584 bytes**, **1,698 instruction pairs** reassemble byte-exact; VU0 `0x268` host model max abs diff **9.38e-7** | no entry map from MSCAL callers; no VU decompiler exists in any public tool |
| 5 | Asset consumers / subsystem behavior | Open | 56/56 model sections reach EOF; 2,370 textures parsed; 27 sound banks, 20 music streams, 548 PTG headers | geometry layout "unresolved interpretation"; PTG palette/tile pointers unresolved; **UI/text/config not probed** (216 `.dat`, 45 `.ui`, 16 `.cfg`, 5 `.mbf`); EE/IOP/VU consumers of loaded buffers unmapped |
| 6 | Readable source / reproducible build | Least measured | 4,746 recompiled function units compile; a static host link with 4,746 guest entry addresses; address accounting **1,227,700 bytes** of 1,247,328 | no readable reconstructed C tree, no reproducible compiler/build target, no byte-comparison of compiled output to the original |

## Staged bar (project's own D1–D6)

Independent classification (`jev_classify`, this session, stable catalog, thresholds 0.85/0.50):

| Stage | Class | Auto/review |
| --- | --- | --- |
| D1 EE byte accounting | measured with check | auto 1.00 |
| D2 EE boundaries | partly measured | review 0.70 |
| D3 decompilation quality | partly measured | auto 1.00 |
| D4 IOP | partly measured | auto 0.96 |
| D5 VU | open, bounded evidence | auto 0.87 |
| D6 asset consumers | open, bounded evidence | auto 0.98 |
| UI/text/config | not probed | auto 1.00 |

D2 came back `review` (top 0.70) only because g4 is unrun while g1–g3 are done — a scope nuance, not a contradiction.

## Claim check (`jev_verify`, this session)

8 verified, 1 contradicted, 1 unsupported. The two non-verified items were **planted controls**:

- "VU microcode is fully decompiled to readable C" — **contradicted** (0.99). No public tool decompiles VU code; the project only has byte-exact reassembly.
- "The game is fully reverse engineered and ready to rebuild" — **unsupported/contradicted** (0.99).

Real claims verified: 5,454 functions; 91.4% owned bytes; 73,756 code-shaped unlisted; gp tokens 13,609→0; 3,940 arity + 23,142 type tokens open; 2 of 24 IOP modules profiled; 2,388 IOP functions; no readable source/build yet.

## Honest bottom line

The **binary-side** work is between roughly **half and two-thirds** done in bytes owned and functions found, but **ownership is not decompilation**: the saved functions are provisional structural candidates with no proven identity, types, signatures or behavior. The parts that make a decompilation *readable and reproducible* — type/signature recovery (workstream 2) and the readable-source/build target (workstream 6) — are the **least** measured. Discovery is no longer the bottleneck; **semantics and types are**.

### The one thing that changes this most

The owner's stated goal (full reconstruction with a reproducible build) is **broader than the bar the project currently measures**. The completion matrix already says it: "A broader effort is complete when the user names the area and a measurable bar for it." The single highest-leverage next action is to settle a **completion spec** — pick the target (byte-identical matching decomp? readable reconstruction? host-runnable build?) and its oracle — because tool choice follows from it. An **LLM / decompiler-in-the-loop** pipeline is the newest lever for readable C and type recovery at scale, and should be evaluated in that spec, not adopted ad hoc.

Receipts for this audit: `jev-extract-*`, `jev-audit-*`, `jev-verify-audit`, `jev-classify-stages`, `jev-find-next-step`, `jev-rerank-workstreams`, `jev-compare-audit-vs-bar`, `jev-noul-audit`, `jev-decide-next` in `.scratch/fr2-audit/`.


## Jev gate on this audit

`jev_gate` over this document **escalated** on `test_gap` confidence only (composite 0.815, `safe_to_apply` 0.36) — the same expected pattern for a findings document with no unit test; correctness 1.52 and spec_match 1.84. Both **planted controls** were correctly caught: "the audit proves the game is fully reverse engineered" (contradicted 1.00) and "the audit's numbers are a percentage of game-behavior recovery" (contradicted) — the second confirms this document's own warning that **byte ownership is not a percentage of decompilation**. One real claim ("D1 measured / D5,D6 open") came back unsupported because the classification text was not in the evidence set — an input gap, not a defect; the classification is in `jev-classify-stages.json`. Full receipts: `.scratch/fr2-audit/`.
