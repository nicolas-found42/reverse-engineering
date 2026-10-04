# PS2 / MIPS console reverse-engineering methods from public YouTube transcripts

Research date: 2026-10-04. Scope: methods that could transfer to the static, offline recovery of the PAL Ford Racing 2 EE executable. Existing notes were read first (`notes/modern-reverse-engineering-methods.md`, `notes/research-modern-re-awesome-github.md`, `notes/evidence/fr2-static-recovery/tools-research.md`, `notes/evidence/fr2-continuation/next-phase.md`). This file only adds material those do not contain. Nothing here was run against the game; every technique below is a lead until measured on this ELF.

## Method and safety record

- Candidate discovery: `yt-dlp --flat-playlist` title searches and Firecrawl searches (metadata only), about 90 distinct candidates. 32 were ordered with `jev_rerank` on title/description/chapters; the ranking is in the scratchpad (`research-yt/jev_results.md`).
- Transcript route (deviation to disclose): YouTube's signed `timedtext` URLs returned empty bodies to `curl` (HTTP 200, 0 bytes). I therefore used the already-installed `yt-dlp --skip-download --write-subs --write-auto-subs` to write caption JSON only (no audio/video fetched, nothing installed), and for six videos the Firecrawl `scrape` transcript. Firecrawl returns transcript text inline in the tool result, so for those the text reached my context before it could be screened to a file; I treated it as data and screened the excerpt before using anything from it.
- All captions are YouTube auto-captions (ASR). Terms are often wrong ("gidra/gedra" = Ghidra, "EDA" = IDA, "Redux" = PCSX-Redux, "M2C/MTC" = m2c). Technical claims below are paraphrased from screened excerpts in which I normalised only obvious ASR slips; timestamps are caption-block starts (about +/-20 s). Firecrawl-inline transcripts carry no timestamps; for those I cite description chapters or give no time.
- Every excerpt used was passed through `jev_screen`. Results are in the table and in `research-yt/screens.jsonl` (18 screens). Nothing was blocked and nothing needed `review`. One screen returned `skip` on relevance only (SOTN-PSP, injection 0.01 under the narrow purpose "PS2 methods"); it was re-screened with the task's own scope (MIPS console matching decompilation) and passed at 0.96 relevance. Both results are recorded.
- `jev_verify` was run once over 19 claims against the screened excerpts: 13 verified, 2 contradicted, 4 unsupported (4 flagged review). Six of the 19 were deliberate overclaim controls; all six came back contradicted or unsupported, as intended. Per-claim results are marked `[V]`, `[V-review]`, `[C]`, `[U]` below.
- Not used: the PCSX2 `GSRendererSW.cpp` LOD excerpt; no emulator, game, or tool from any source was run; no login, comments, likes, or downloads of media.

## Source table

Jev rerank = relevance to "static offline PS2/MIPS RE techniques" (candidate title+description only). Screen = injection / substance / relevance, action.

| # | Video | Speaker / channel | Date | Transcript | Screen | Rerank |
|---|---|---|---|---|---|---|
| 1 | [PS2 game hacking & reverse engineering](https://www.youtube.com/watch?v=gG5N53aNikk) 1:15:24 | Xeeynamo | 2019-07-18 | ASR, timestamped | .02/.97/.94 pass | 0.72 |
| 2 | [GT Racing AI (PSX) Part 5 - unpack GTMAIN.EXE](https://www.youtube.com/watch?v=6tuSvjPUQ6o) 22:05 | NDR008 | 2022-08-11 | ASR, timestamped | .02/.97/.89 pass | 0.40 |
| 3 | [GT Racing AI (PSX) Part 7b](https://www.youtube.com/watch?v=wIGjK0zMzGo) 18:41 | NDR008 | 2022-11-05 | ASR, timestamped | .02/.97/.74 pass | 0.43 |
| 4 | [Introduction to Ghidra: modding and RE games](https://www.youtube.com/watch?v=3c7yBlkQ_fE) 52:04 | bordplate (Norwegian security conf.) | 2024-08-29 | ASR, timestamped | .02/.98/.95 and .02/.97/.46 pass | 0.30 |
| 5 | [PS2Recomp - how to get started](https://www.youtube.com/watch?v=xCeB6Vsm9n4) 26:06 | Plastered Crab | 2026-02-25 | ASR inline, no timestamps; chapters from description | .02/.98/.94 pass | 0.69 |
| 6 | [PS2 native PC ports get MASSIVE NEWS](https://www.youtube.com/watch?v=4DVpn1nWxCI) 9:00 | TheGamersJoint | 2026-01-27 | ASR, timestamped | .01/.98/.69 pass | 0.38 |
| 7 | [GambiCast #05 - Ethan Roseman](https://www.youtube.com/watch?v=KhAxDbJeDQA) 51:33 | GambiConf (ethteck, decomp.me author) | 2025-12-08 | ASR, timestamped | .02/.98/.55 pass | 0.23 |
| 8 | [Retro Game Decompilation Using AI](https://www.youtube.com/watch?v=sF_Yk0udbZw) 37:01 | Macabeus / Codeminer42 | 2025-12-04 | ASR, timestamped (2nd fetch) | .04/.98/.88 pass | n/r |
| 9 | [Decompiling SOTN for PSP - PSPHDC 2025](https://www.youtube.com/watch?v=or4_z8pGEQ4) 21:33 | xeeynamo / PSP HDC | 2026-09-16 | ASR inline, no timestamps | .01/.98/.23 skip; re-screen .01/.99/.96 pass | 0.28 |
| 10 | [PlayStation 2 Emulation with TellowKrinkle](https://www.youtube.com/watch?v=ISEiz7HkCEI) 51:48 | Software Engineering Daily (PCSX2 dev) | 2024-11-13 | ASR, timestamped | .01/.98/.86 pass | 0.14 |
| 11 | [USENIX Sec '20 - Datalog Disassembly](https://www.youtube.com/watch?v=i_9c9YxsFuY) 12:17 | Flores-Montoya, Schulte (GrammaTech) | 2020-09-14 | ASR, timestamped | .01/.99/.66 pass | n/r |
| 12 | [CERIAS - Automated Function Boundary Detection in Stripped Binaries](https://www.youtube.com/watch?v=k1sztWD0Fs4) 50:56 | Jim Alves-Foss (Univ. Idaho) | 2022-04-11 (talk 04-06) | ASR, timestamped | .02/.99/.92 pass | n/r |
| 13 | [reverse engineering GTA San Andreas with autonomous LLM agents](https://www.youtube.com/watch?v=zBQJYMKmwAs) 6:48 | DryxioGTA | 2026-02-19 | ASR inline, no timestamps; chapters from metadata | .05/.98/.51 pass | 0.20 |
| 14 | [Fatal Frame 100% Decompiled](https://www.youtube.com/watch?v=kg6a6LI2VhQ) 10:39 | Video Game Esoterica | 2026-03-25 | ASR, timestamped | .01/.98/.77 pass | 0.29 |
| 14b | [Mikompilation/Himuro README](https://github.com/Mikompilation/Himuro) (project docs, used to check #14) | Mikompilation | page of 2026-10-04 | web page | .02/.98/.91 pass | - |
| 15 | Descriptions only: [CTR decompile overview](https://www.youtube.com/watch?v=V9QlFzSVDAU) (no captions), [Silent Hill 1.1 decomp](https://www.youtube.com/watch?v=1RluG7VeyuM) | Darkaiser (2022-04-02), nodiscnobuy (2026-04-07) | | descriptions | .02/.97/.82 pass | 0.48 / 0.18 |

Read for triage but not used (no screen, no claims drawn): GT Racing AI Part 6 `vy98V4HlIS0` (dynamic memory poking with PCSX-Redux). Remainder of the not-read list is under the last heading.

## Findings per video

### 1. Xeeynamo, Kingdom Hearts II on PS2 (2019)

Tutorial level; the tooling is PCSX2 + Cheat Engine + IDA, not Ghidra, and the workflow is dynamic. Useful pieces:

- 07:31-07:54: every MIPS opcode is 4 bytes, so instruction boundaries are never ambiguous on this ISA; the speaker says most PS2 games are GCC-compiled C/C++. 18:55: PS2 has its own EE MIPS documentation because it extends plain MIPS. (Unverified lead for FR2: the compiler claim is a generalisation.)
- 15:55-17:44: JAL/JR delay slot explained; useful as a reminder that "the instruction after a call belongs to the call".
- 28:11-35:49: find the writer of a known value by a write breakpoint, then locate the same address in the disassembly of the stripped executable; the speaker notes the executable has no symbols (35:49). Not applicable offline, but the output (a dated list of writer->field pairs) is the type of evidence FR2 can only get statically from store/load patterns.
- 46:15-49:13 `[V]`: a multiply by 12 against an index shows the table element size (12 bytes); the same value is then found in a game data file at `index*12`. 53:44-57:31 `[V]`: sets the decompiler compiler option to GNU, defines a 12-byte struct, then corrects a field to a halfword when the load is `lhu`.
- Technique to transfer (Q2): derive struct stride from the `index * constant` in the code and cross-check it against the data file; a measured stride on both sides is stronger than either.

### 2. NDR008, Gran Turismo 1 (PS1) Part 5, unpacking `GTMAIN.EXE` (2022)

- 01:33-03:21: Ghidra decodes only the start stub of the packed executable; the speaker identifies a decompression routine and its end-pointer constants. 04:23-05:05: breakpoint after the stub, then raw RAM dump; 08:57-13:32: rewrap as a PS-X EXE at the load address; after that Ghidra analysis finds many functions, mostly SDK routines (caption at about 14:13). `[V]`
- Relevance to FR2 (Q1): a code-shaped but unreachable region can be compressed or overlay data that a static pass never sees as code. The speaker's route is dynamic; FR2's offline equivalent is to test whether any of the 157 KB of "code-shaped" bytes is high-entropy compressed payload that merely passes a permissive opcode filter.
- Part 7b (video 3), 02:32-07:55 and 11:32: shows paired "input value / applied value" fields for throttle and brake (applied value ramps, simulating ABS) and 16-bit fields. This is dynamic poking; only the field-pair pattern may transfer to racing-game car structs and is an unverified lead.

### 3. bordplate, Ghidra for game modding (Ratchet and Clank, PS3 port; 2024)

The speaker explains PS2 R&C is hard to mod because levels are separate dynamically-loaded binaries (01:49-04:19), so he works on the PS3 port, whose single binary has no dynamic loading (03:57). Lessons:

- 07:34, 14:30-15:15: with no symbols, defined strings and their cross references are the first entry points. 15:38-16:39 `[V]`: label uncertain functions with a leading question mark so unreviewed hypotheses are visibly provisional and re-nameable.
- 17:22-23:28: find a "spawn" function by following an error string's callers, check call arguments against an external level-editor's object ids, then patch to test. 
- 30:55-35:33 `[V]`: repeated `ptr + offset` use is the signal for a struct; auto-create the struct, then fix its size from the stride used while walking a list (0x100 turns `x + 0x100` into `x + 1`). 36:34-39:47: type the first parameter, then fields fall out of `printf` formats (`%d` -> class id) and float instructions (field must be float).
- Lead for FR2 (Q1, Q3): a different build of the same game (here a port with no overlays) can serve as a Rosetta stone for names and structure. FR2 also shipped on other platforms; whether a symbolised or string-richer build is obtainable is unverified and outside the current input set.

### 4. Plastered Crab, PS2Recomp setup (2026)

Chapters from the description: 05:18 get ELF, 07:35 Ghidra analysis and function map, 15:57 analyzer -> TOML, 17:00 edit TOML, 17:51 generate C++, 21:40 entry runner, 23:41 what comes next. `[V]`

- In the Ghidra analyzer options he loads language R5900LE, turns the Non-Returning Functions analyzer off, selects the GNU demangler, and enables STABS (in the 07:35-13:13 chapter). A Ghidra script exports a CSV of function addresses/sizes, which the PS2Recomp analyzer reads from the TOML. The config lists `printf`, `malloc`, `free` as stubs and `abort`, `exit` as skips (17:00-17:51).
- The run loop (21:40-23:41): the generated runner "will not work first try" and prints unimplemented PS2 stub errors; the author fixes the TOML/runtime and regenerates. `[C]` for the overclaim "the tutorial shows the game running correctly": the speaker explicitly says it does not.
- Speaker's own scope limit: he did not cover C++ changes needed to boot, and says he is still learning that step.
- Q1/Q3 link: the non-returning-functions toggle matters for function bounding. Ghidra's analyzer can end a function at a call it believes never returns and leave following code undefined. FR2's existing notes record the EE-reloaded README's suggested analyzer setting; whether the saved FR2 project had it off is not stated in the notes read.

### 5. TheGamersJoint, PS2 static recompiler news (Jan 2026)

News tier, shown to calibrate claims. 01:02-01:44: says OpenGOAL is not a static recompilation; the team had to reverse-engineer Naughty Dog's GOAL language. 03:29-04:37: static recompilation does not make "drop an ISO, get an exe"; per-game work remains. 07:45: the PS2 recompiler project (by "Ranj") was still early. No technique here beyond that. The only OpenGOAL content found on YouTube in this search is user-level (setup guides, reviews); no transcript of a Jak decompiler design talk was found (see gaps).

### 6. Ethan Roseman (ethteck), GambiCast (2025)

- 03:47: matching decompilation means byte-identical rebuilds; 35:06 `[C]` for the claim that researchers need it: he says the opposite (academia mostly does not need byte matching), so papers on "decompilation accuracy" are not measuring this standard.
- 11:35-14:26 `[V-review]`: compiler identification is a question of whether the community owns the compiler; evidence used are other titles and dev tools from the same studio, binary identifiers in the executable if any, and then brute-force over compilers/flags on one function. A decomp.me preset from another game of the same developer is the cheapest start (14:05).
- 15:30-16:33: for MIPS platforms (named: PSP, PS1, PS2, N64) splat is both binary splitter and linker-script generator (the linker script is what makes the rebuild put every piece at its original address).
- 30:26-31:50: a Paper Mario ROM tail held apparently duplicate overlay code that turned out to be older map versions with debug strings; dead overlay code can sit unreferenced in an image.
- 32:32: he and others are building tools that match functions across games; 47:16-48:40: compiler behaviours are researched ad hoc and rarely documented.
- 36:32-41:33: summary of static vs dynamic recompilation; he says he is not an expert. He notes the IDO compiler itself was statically recompiled to run natively. Treat as second-hand.

### 7. Macabeus, LLM-assisted matching decompilation (2025)

- 08:34 `[V]`: matching = readable C that rebuilds to the original binary; Ghidra output is a reference, not matching input, because it lacks the compiler and flags and can contain logic errors (08:34-10:00).
- 10:45: objdiff compares original and rebuilt object files and shows when registers differ but mnemonics agree. 14:24-14:44 `[V]`: for most PlayStation titles the custom GCC is unavailable, so projects use an older GCC plus an assembly post-processing tool; decomp.me presets are the starting point.
- 16:55-17:16 `[V]`: his definition of "100%": every assembly function has C that compiles to the same assembly (a per-function match, with the build checksum as a gate, 31:36).
- 31:36-33:22: an agent loop that runs `make`, sees the checksum fail, reads an objdiff report, and finds that a struct offset was wrong; at 33:22 a vector database of function embeddings is used to pick examples. The hypothesis that clusters of solved functions make unsolved ones easy is his own and untested.
- Scope: Game Boy Advance and N64 examples; PS2 is not evaluated.

### 8. xeeynamo, SOTN for PSP (PSPHDC 2025)

No timestamps (inline transcript); order of topics only. `[passed on re-screen]`

- The compiler hunt: GCC output was wrong; Metrowerks CodeWarrior 1.1 was closer but lacked the right `seb/seh` casts for integer narrowing; version 1.3, supplied by a community member, gave the first match. Finding the compiler was only the start: a wrapper tool (pre/post-process) was needed to inline assembly and fix relocations so GNU binutils could link.
- Pipeline: splat reads a metadata file (segment bounds, known symbols), splits code and data into files, emits an undefined-symbol list and a linker script; spimdisasm is a disassembler whose output re-assembles identically; the "Ship of Theseus" order replaces assembly with C one function at a time while the linked binary stays valid; m2c output is "not pseudo C" but possibly inaccurate; asm-differ and decomp.me are the loop.
- Cross-build trick: the PSP build's different function order suggested C files were compiled in alphabetical order, which located source-file boundaries; global-versus-struct-member hints; a function that matches on two builds ports to a third.
- Relevance (Q1/Q3): TU boundary hypotheses from executable layout. The speaker's claims about the compiler order are one project's observation, not a rule.

### 9. TellowKrinkle (PCSX2), architecture and FP (2024)

- 06:24-09:16: EE is a 300 MHz MIPS with two vector units; VU0 is tightly coupled, microprograms are short; VU1 is closer to a vertex stage and ends with an instruction that kicks data to the GS; GS only rasterises already-transformed 2-D vertices with a depth value. (Consistent with the project's existing VU1/VIF/GS audits; the speaker is a PCSX2 developer.)
- 10:42-11:25: a few games rely on cycle-exact EE/VU synchronisation; VU timing is tracked closely.
- 11:25-20:38 `[V]` (0.81 conf): PS2 floats have no infinities or NaNs, the top exponent encodes larger finite numbers, and PCSX2 clamps after operations; addition keeps one guard bit and truncates, and some multiplications by 1.0 change specific values (he defers details to another dev's blog). 09:58 `[C]` for the overclaim that VU code translates easily to GPU vertex shaders: he says it cannot.
- For FR2: any host-run differential or recompiled output needs PS2 float semantics, not IEEE. The repository already audits several COP1 paths (`fr2-fpu-static-audit`, `fr2-fpu-control-audit`); the guard-bit and multiply anomalies are speaker claims and unverified here.

### 10. Datalog Disassembly (USENIX 2020) and Function Boundary Detection (CERIAS 2022)

Both are x86/x64 Linux research talks. Neither says anything about MIPS or R5900 (`[U]` for any claim that the Datalog tool supports R5900). The techniques are architecture-neutral, and R5900 has fixed 4-byte instructions, which removes the hardest part of boundary recovery.

Datalog Disassembly:
- 03:40-05:03 `[V]`: decode every offset in the code sections into a superset of candidate instructions; mark offsets that fail to decode; a recursive rule propagates invalidity backwards (any instruction that must fall through, jump or call to an invalid address is invalid) to a fixed point.
- 05:23-06:26: forward traversal over all candidate blocks, starting from addresses found in data sections; then score blocks (entry point, address appears in data, jumped to from another block), aggregate, and resolve overlaps.
- 06:46-09:34: a plain "number in the address range is a pointer" rule produces false positives; supporting evidence (def-use of registers, constant propagation, access size/stride) raises or lowers confidence; a pointer into an instruction start is positive evidence, one that overlaps a data access is negative.
- 09:55-11:00: validated by reassembling and running tests, over 99.7 percent of 7,658 x64 benchmark binaries; its authors note exact reassembly is undecidable, so heuristics are needed.

Alves-Foss (function starts):
- 05:39-07:05 `[V]`: runs of no-op padding after a jump are not a reliable function end; compilers split one source function into several parts and give one function two entry points; a switch jump through a table fooled a commercial tool.
- 08:06-10:11: records every call/jump/return; considers function alignment (every 4 or 16 bytes); backward-slices an indirect jump to the table (works about 90 percent of the time by his account); exception handlers are part of the function though not reachable.
- 10:33-14:48: start from known call targets, walk "inflection points", treat tail-call jumps and non-returning calls explicitly; when a function is marked non-returning, re-analyse its callers because they may have been merged too much.
- 15:51-16:54: treat padding as not part of the function and say so; "starts correct" is the key output.
- 18:43-24:19 `[V]`: with rare positives, accuracy is meaningless (a tool reporting nothing scores 99 percent); use precision and recall against ground truth taken from unstripped builds; 28:48-35:11: plot per-binary distributions and investigate failures (an apparent 98 percent hid one dataset of near-duplicate binaries; fixing it gave 99.8 percent).
- Limits stated by the speaker: x86/x64 Linux, GCC/clang/Intel only; no obfuscation.

### 11. DryxioGTA, autonomous LLM reversing loop (2026)

Chapters: 3:27 review/verification loop, 5:34 in-game test. Reverser LLM and checker LLM drive Ghidra headless; the checker is satisfied when the C++ agrees "line by line" with the Ghidra decompile and assembly; a third pass reviews; then a build and an in-game test. The speaker says the output is functional, not clean, he ran it unattended without reading the code, and he advises using it as help rather than replacement `[V]`. `[U]/[C]` for "byte-matching with the original binary": nothing in the video says so. For FR2 the point is negative: agreement between two LLMs and "it runs" are weak checks; the decompile (an intermediate also produced by a tool) is the reference, not the original bytes.

### 12. Fatal Frame decompilation status (2026) and project docs

- Video 02:09-04:39: the PS2 Fatal Frame decomp project is "100 percent decompiled" with a per-function green heat map; 03:14-03:55: that is not a PC port and does not automate one. The video never says byte-matching, compiler, or objdiff (`[U]`, review).
- Project docs (Himuro README) `[V]`: goal is a matching source decompilation of Fatal Frame 1 for three regions (US, EU, JP), progress badges use matched code percent and matched functions (decomp.dev), build needs a 32-bit original GCC on Linux and a PS2-specific binutils build (decompals), the input executable is pinned by SHA-1 per region, and a translation unit is switched from assembly to C in a per-region YAML, then reconfigure and rebuild. Latest commit at fetch time (2026-10-04): "decompiled (jp) and revisited (us,eu)".
- Conflicting/unresolved: the video date (2026-03-25) says 100 percent while the repository still takes decompile-and-revisit commits (2026-10-04). Whether "100 percent" meant one region, matched code, or function coverage is not established by either source.
- Not a transcript item but a project anchor: this is the clearest public PS2 EE matching project the search found, and it defines "done" as byte match per region, measured by objdiff-based percentages.

### 13. Descriptions only

CTR (PS1 racing, 2022): says about 90 percent of game code is understood, does NOT rebuild into anything functional, and serves only as documentation (a non-matching, non-buildable decompile counts as "decompiled"). Silent Hill 1.1 (PS1, 2026): states PS1 games spread logic over overlays and that the main executable acts as a memory handler; the port is built on a decompilation "made with Claude and Psycross" (claims unverified).

## Synthesis by question

### Q1. Finding and bounding functions, code versus data in stripped binaries

What the sources actually show:
- Fixed-width ISA removes instruction-boundary search (Xeeynamo 07:31). The remaining problems are code-versus-data, function starts, and function ends.
- Candidate-superset plus scoring plus overlap resolution is the best-documented static method (Datalog 03:40-06:26). Evidence signals: reachable from a known entry or call, address present in a data section (function pointer tables), branched to by other candidates, alignment; negative signals: falls into an invalid word, overlaps a recognised data access. Backward invalid-instruction propagation is cheap and deterministic.
- Function end: do not trust padding or a trailing `nop` run; handle tail jumps and non-returning calls explicitly; recover indirect-jump tables by backward slicing (Alves-Foss 05:39-14:48). The PS2Recomp tutorial's Ghidra setup disables the non-returning-functions analyzer (chapter 07:35), consistent with the mis-ending risk.
- Strings and call arguments are the anchor for naming (bordplate 07:34, 17:22), and packed or compressed regions can look like code to a pattern filter but are invisible to a static pass (GT part 5, 01:33-13:32).
- Not covered by any video found: how to prove a region is data. Only the scoring approach and measured controls get close.

### Q2. Types, structs, calling conventions at scale

- Convention basics (a0-a3 arguments, v0 result, delay slots) appear only as tutorial level (Xeeynamo 07:54-17:44).
- Struct recovery by stride and field width is shown at one-struct scale (Xeeynamo 46:15-57:31; bordplate 30:55-39:47): pointer-plus-offset cluster, auto-create, set size from loop stride, set field types from instruction width (`lhu` is a halfword) and printf formats, mark uncertain labels.
- At scale: Macabeus (33:22) proposes embeddings to find similar already-solved functions as prompt examples and notes struct offsets as the failure that objdiff exposed (31:36); both are unvalidated outside GBA. m2c-style context did not fix 128-bit pointer scale in this repository's own audit (`fr2-m2c-audit`), so a video claim about context helping should be treated as unproven for EE `lq/sq`.
- No video shows a large-scale type-recovery pipeline for PS2.

### Q3. Matching compiler, SDK, library code

- Compiler availability is the gating question (ethteck 11:35); evidence sources are same-studio titles, tool releases, executable identifiers, then a function trial over compilers and flags.
- PlayStation titles: usually no official compiler; projects use an older GCC with an assembly fix-up tool (Macabeus 14:44). For the PS2 specifically, Himuro's README names an original 32-bit GCC, run on Linux, and a PS2 binutils fork; the pinned tooling listing in `tools-research.md` already shows EE GCC entries in the decomp.me compiler catalogue.
- SOTN-PSP shows how compiler flags decide what code looks like: no optimisation means close to the source, and a second build lets you infer TU boundaries and struct membership.
- Library code: PS2Recomp config stubs `printf`, `malloc`, `free` and skips `abort`, `exit` (17:00-17:51); GT part 5 sees mostly SDK routines after unpacking (13:32-14:33). Neither video shows systematic SDK signature matching.

### Q4. VU, IOP, GS and VIF specifics

Thin coverage; the most relevant source is TellowKrinkle (06:24-09:16 for roles, 11:25-20:38 for FP). No transcript found that reverse-engineers VU1 microcode, IOP IRX modules, VIF packet streams from a shipped game, or GS register writes. The Tom Marks homebrew streams on VIF/VU1 (see below) were not readable here, so VIF packet-building detail from developer streams is unverified. The recompiler tutorial leaves GPU/VIF rendering as a later step.

### Q5. Verifying correctness and what "done" means

| Source | What "done" meant | Check used |
|---|---|---|
| Macabeus 16:55 | every function has C that rebuilds to identical assembly | build checksum plus objdiff |
| Himuro README | matching source decompilation per region | matched code percent and matched functions via objdiff; pinned SHA-1 inputs |
| Fatal Frame video | "100 percent decompiled" (undefined) | heat map; no check stated |
| CTR description | about 90 percent understood; not buildable | none; documentation only |
| DryxioGTA | "functional" | second-LLM parity review plus in-game test |
| Datalog Disassembly | reassemblable | reassemble and run the original test-suites; correct symbolisation |
| Alves-Foss | function starts right | precision/recall vs symbols from unstripped builds |
| PS2Recomp tutorial | generated C++ builds | runtime stub errors; no correctness claim |

Observed pattern: only the matching projects define a check that can fail without a human judging it. The two quantitative techniques that transfer without a compiler are ground-truth hold-outs (Alves-Foss) and reassembly equivalence (Datalog).

## Directly applicable next steps for Ford Racing 2

Ranked by value over cost. Each has a check that could fail. All are static and offline; none depends on a speaker claim being true.

1. **Calibrate a candidate-block scorer on the already-owned `.text` before applying it to the 157 KB of unowned code-shaped bytes** (sources: Datalog 03:40-06:26; Alves-Foss 18:43-24:19). Treat the 969,432 function-owned bytes with their 4,718 starts as ground truth; hide a random fraction of the starts; run decode-superset plus backward invalid propagation using `tools/r5900_shape.py` plus signals (direct call target, address stored in a data word, branch target, `addiu $sp, $sp, -N` prologue, 8/16-byte alignment); resolve overlaps; report precision and recall of hidden starts, never accuracy. Check that could fail: precision on hidden starts below the level you need to promote unowned candidates (set the bar before running); also fail if the shape filter alone passes more than a measured fraction of known data words (the module itself warns data often passes).
2. **Audit unowned ranges that follow calls to non-returning-looking functions** (Alves-Foss 10:33-14:48; PS2Recomp tutorial chapter 07:35). List unowned spans whose predecessor ends with a call and no `jr $ra` and no unconditional branch; check against the saved Ghidra analyzer options for Non-Returning Functions. Check that could fail: if fewer than a stated share of the 157 KB lies immediately after such calls, this is not the main cause of the gap and should be dropped.
3. **Recover jump tables by backward slice for `jr $reg` that is not `jr $ra`** (Alves-Foss 08:06-10:11). For each indirect jump, slice backwards to the table base and bound (`sltiu` compare), read targets from the ELF, and test that each target lies in or immediately next to an already-owned function. Check that could fail: more than a small fraction of table targets landing mid-instruction, in zero fill, or in data; or a slice that disagrees with an existing saved reference.
4. **Test whether any unowned region is compressed rather than code** (GT part 5, 01:33-13:32). Compute entropy and instruction-field regularity per 256-byte block in the unowned set versus owned code and known compressed assets. Check that could fail: if high-entropy blocks pass the opcode-shape filter at the random-word rate they are not code; if the owned-code distribution overlaps them heavily the test has no power, and should say so.
5. **Identify the compiler before any matching claim** (ethteck 11:35-14:26; Himuro README). Look for a compiler identification section, STABS/debug records (the EE-reloaded README and the PS2Recomp tutorial both enable STABS recovery), version strings and library signatures in the PAL ELF; then try five small leaf functions against the EE GCC entries in the decomp.me compiler catalogue. Check that could fail: no EE GCC build and flag set reproduces any of the five exactly; in that case "matching" is out of reach for those units and the evidence tier stays structural.
6. **Hypothesise translation-unit boundaries from layout** (SOTN-PSP talk). Cluster the 4,718 functions by `$gp` or literal-pool locality, `.rodata`/`.sdata` partitions, and address order, and test whether adjacent functions cluster by shared globals. Check that could fail: cluster boundaries not aligning with data-section partitions at a rate above shuffled controls. (One project's observation of alphabetical file order is not a rule; test, do not assume.)
7. **Struct recovery by stride from existing data** (Xeeynamo 46:15-49:13; bordplate 30:55-35:33). For car/track/model record arrays already parsed in `tools/` (28-byte HDR records, 0x34 and 0x70 section records), find the code that multiplies an index by that constant, and require code stride and file stride to agree with exact end-of-file arithmetic. Check that could fail: any index with a different stride than the parser or non-integer record counts.
8. **Define explicit completion tiers and report the match rate separately** (Himuro README; Macabeus 16:55; CTR description). Tier A structural candidate (current), B decompilation compiles, C per-function byte-match under a pinned compiler and flags, with a ratio of C over total in the manifest. Check that could fail: the manifest must reject any "100 percent" wording unless the tier and denominator are stated; use the CTR and Fatal Frame cases as negative examples of the ambiguity.
9. **Keep the float semantic gap as a standing differential test** (TellowKrinkle 11:25-20:38). Extend the synthetic COP1 probes to overflow-to-large-finite, no-NaN propagation, multiply-by-zero and by-one, and add-truncation, with expected values from the Sony manuals, not from a host. Check that could fail: a case where the pinned translator agrees with host IEEE but the manual says otherwise; speaker claims on guard bits and multiplications must be confirmed in the manual or PCSX2 source before use.
10. **Do not accept LLM-reviewer agreement as verification** (DryxioGTA 3:27-5:34). If an agent is used for naming or C drafts, gate acceptance on a deterministic comparison (instruction-level reference, differential trace, or byte match), never reviewer consensus. Check that could fail: any accepted function that cannot be re-compared mechanically.

## Unverified leads, unavailable transcripts and blocked sources

Unverified leads (speaker claims; not confirmed by project docs):
- PS2 games are mostly GCC-compiled (Xeeynamo 07:54): a generalisation; FR2's own compiler is unknown.
- PS2 FP details beyond "no Inf/NaN and clamping" (guard-bit count, multiply-by-one anomaly): speaker-reported; he defers specifics to another developer.
- "Compiler behaviours are poorly documented; no large-scale effort exists" (ethteck 47:16): opinion.
- Alphabetical source order and struct hints from cross-build comparison (SOTN-PSP): one project's observation.
- Whether another FR2 platform build (symbols or debug strings) exists and could be used as in the bordplate talk: not established; no second FR2 binary is in the workspace.
- Datalog Disassembly and Alves-Foss results are x86/x64 Linux only; no evidence for MIPS/R5900.
- Fatal Frame: "100 percent decompiled" (video) versus ongoing "decompiled and revisited" commits (README); definition of 100 percent unresolved. Silent Hill "made with Claude" and the CTR "90 percent understood" claims are description text only.
- A Jak and Daxter or OpenGOAL decompiler design talk, a Gran Turismo PS2 matching-decomp talk, an IOP/IRX reverse-engineering talk, and a VU1 microcode reverse-engineering talk were searched for and not found among the public videos surfaced; those gaps remain.

Transcripts unavailable or not read:
- `V9QlFzSVDAU` CTR overview: no captions; description only.
- `Hz88DYftkbc`, `U_NhjvRz7Js` (Tom Marks PS2 homebrew, VIF/VU1 programs): subtitle fetch returned HTTP 429 repeatedly; descriptions only; not used.
- `or4_z8pGEQ4`, `xCeB6Vsm9n4`, `zBQJYMKmwAs`: the subtitle fetch returned 429 so I used Firecrawl's inline transcript; consequently no timestamps (chapters given where YouTube provides them).
- Not read, judged low value from title/description or length: `-b-liVgTV8Q` (3-hour Jak stream), `HYUykYjc4NI` (SOTN decomp stream), `PYwVWYUs-TQ` (GT2 recomp, PS1), `zXiZIcT1PZc` (Alien Resurrection PS1), `Qx6LQh0_agU` (PCSX2 debugger pointer hunting), `1lw3dgvkH64`, `IWNMLkim4ac`, `M_A8XzvQ61E`, `cIa2e6S_cTc` (news videos), `Br8V1GGM16U`, `Qgvql3EqVGA`, `IRv_xKS4q7o`, `rM4r_w1nTbY` (architecture overviews).
- Read for triage only, not used: `vy98V4HlIS0`.

Blocked sources: none. Screen failures: none. One `skip` on relevance only (video 9, first screen), resolved by a re-screen under the task scope as recorded above. Auto-caption terms flagged uncertain: IDA/"EDA", Ghidra/"gidra", PCSX-Redux/"Redux", m2c/"M2C/MTC", "mobies" (Insomniac game objects), the "Ranj" developer name (spelled variously), "Psycross".

Artifacts (scratchpad, not in the repo): `research-yt/screens.jsonl` (all screen results), `jev_results.md` (rerank and verify records), caption files `*.txt` and `*.json3`.
