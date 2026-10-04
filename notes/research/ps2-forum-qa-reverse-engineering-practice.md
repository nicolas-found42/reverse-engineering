# PS2 reverse-engineering practice from public Q&A and forums

Research date: 2026-10-04. Scope: practitioner Q&A on finding code, recovering types, the Ghidra R5900 module, PS2 SDK/IOP/VU1/GS specifics, and pitfalls, applied to static offline recovery of the PAL Ford Racing 2 EE executable. This file adds to `notes/modern-reverse-engineering-methods.md`, `notes/research-modern-re-awesome-github.md`, `notes/evidence/fr2-static-recovery/tools-research.md` and `notes/evidence/fr2-continuation/next-phase.md`; it does not repeat their tool survey.

Read this first: the evidence is thinner than the question list implies. Stack Exchange Reverse Engineering has almost no PS2-specific answers. The best PS2-specific material turned out to be GitHub issue threads of the Ghidra EE extension, a few Reddit threads, and generic (non-PS2) RE.SE answers by experienced authors. Questions 3 and 4 are only partly answered; see "Still unresearched".

Provenance of every claim below is in the source table. Forum text is treated as leads unless it traces to documentation or a project's own source. Nothing was executed, built, downloaded or posted. Evidence files are in the session scratchpad `research-qa/`.

## Short answers

### 1. Finding code that direct-call analysis misses; code versus data in .text

Concrete static techniques practitioners describe:

- **Know what recursive descent cannot do.** Pure recursive traversal misses functions called by computed address or only referenced from pointer tables, so tools add pointer heuristics (RE.SE 2580, 0xea; RE.SE 2347, PSS quoting The IDA Pro Book). The same book passage says recursive descent separates code from data better than linear sweep. This is the conceptual basis for our 157 KB "unowned but code-shaped" set: it is the part direct calls cannot reach, so it needs a second seed source (below).
- **Seed sources beyond JAL.** (a) Words in .data/.rodata/.sdata that are aligned and fall inside .text (function-pointer tables, vtables, callback tables). (b) `jr $reg` after a table load (switch tables). (c) `j` (not `jal`) targets outside the current function, which are tail calls: the EE extension owner states MIPS tail calls use jumps, so Ghidra treats thunk and callee alike (EE issue 113). (d) Library members contiguous in link order: if one library function is found, its address neighbours are library functions too (RE.SE 18169, Anton Kukoba, unaccepted, score 2).
- **Switch tables.** Ghidra's "could not recover jumptable ... too many branches" usually means a real table whose bounds the decompiler cannot derive; the documented remedy is adding targets manually and running `SwitchOverride.java`, and `FindUnrecoveredSwitchesScript.java` finds the sites (RE.SE 25917, Shane Reilly, score 7, not accepted; cites Ghidra docs). Unverified against R5900 output.
- **Code versus data.** RE.SE 2580 (Codoka) says exact separation needs indirect-target resolution, which is undecidable in general, so any classifier is heuristic. For us that means a region's status must be an evidence level, not a binary label.
- **vtables.** RE.SE 31325 (score 5, no answers) shows the common failure: functions with no references because vtable references are not created in a stripped binary. No practitioner solution was found. A project-specific fix would be a data-pointer scan, not a Ghidra setting.
- **Compiler-emitted aids.** On a Reddit PS2 thread, `.gnu.linkonce.t.*` section names carried C++ symbols for template and inline functions; `c++filt` or the Chaos Compiler Collection (ccc) demangler read them (r/REGames 174nu4j, igor_sk, score 2). That only applies if the retail ELF still has such sections. Whether FR2 does is unchecked.

### 2. Structs, types and naming at scale

- The strongest accepted-style advice (RE.SE 33207, joxeankoret, accepted, 2024-09-08): the realistic way to improve decompiler output is to import names, prototypes, structs, enums and defines from available source into the project, almost always by hand; headers usually need editing first. Matching binary functions to source functions without debug info is hard. LLM and name-inference tools were described by him as unreliable (his opinion; consistent with `modern-reverse-engineering-methods.md` treating AI output as candidate-only).
- Ghidra Function ID needs an exact hash match, BSim is fuzzier, and no ready PS2 library database exists (EE extension owner chaoticgd, issue 112, 2026-02-15). FLIRT-style patterns need the same compiler version and options (RE.SE 19590, Igor Skochinsky, score 5, not accepted); better patterns come from object files or archives with relocation wildcards. At scale one needs many compiler builds. His practical alternative for a single binary is matching manually through string literals and function cross-references.
- PS2Recomp's analyzer ships an SCE SDK symbol database built from debug-info PS2 games, mostly Japanese, dependent on samples that retained relocations; its own README calls matches a high-confidence hint, not a catalogue, and says ambiguous matches are ignored. It also says its JAL scanner is test-only and not preferred for retail games (ran-j/PS2Recomp ps2xAnalyzer README).
- Ghidra data-type-archive pitfalls: importing prototypes into a file archive duplicates built-in types, giving `float.conflict` style types (RE.SE 33314, Sami Liedes, score 2, no answers). A pointer into the middle of a struct had no delta feature as of April 2020 (RE.SE 21242, Florian Magin, score 2); current status not checked.
- Judging decompiler output quality: practitioners here offer no metric. A thread on thunks shows a concrete failure to guard against: metrics taken from decompiler output for an 8-byte tail-call wrapper described the callee (EE issue 113). Any per-function quality score computed from pseudocode must first exclude or resolve tail-call wrappers.

### 3. Ghidra and the R5900 module

Documented failure modes, each from one maintainer-answered thread:

| Symptom | Cause given | Fix or workaround |
| --- | --- | --- |
| `gp0xffff8090` style operands and missing globals | Ghidra could not find where `gp` is assigned; newer Ghidra no longer handled `move gp,a0` as the assignment (EE issue 118, 2026-04-27, open) | Set the `gp` register value by hand; owner suggests reading it in the PCSX2 debugger. For a static project, read it from the startup code instead. The address analyzer is `MipsR5900AddressAnalyzer.java` |
| Thunk or tail-call wrapper decompiles as its callee | MIPS tail calls use jumps (EE issue 113, closed, owner answer) | Treat `j`-ending small functions as wrappers before computing metrics |
| Corrupted immediates, odd function jumps in an ELF | Relocation handling, `R_MIPS_26` (RE.SE 21697, 0xec, accepted score 5, 2019; EE issue 75, 2024: relocations applied even with the importer option off, fixed in a later build) | Check the relocation table; load without relocations or as a raw binary for comparison |
| Calls to symbols fail with "Block is non-existent" | Loader skipped zero-size or overlay-named sections (r/REGames 1attl99, 2024, no answers visible) | Unresolved in the thread |
| Branch delay slots | Ghidra shows encoded order; likely branches (`beql`) execute the slot only if taken (RE.SE 19606, Igor Skochinsky, 2018; ChrisG accepted) | Account for the nullified slot when judging block ownership |
| Strange `li` where a MIPS reference says `addiu` | `li` is a pseudo-instruction; the PS2 CPU needs PS2-specific references such as ps2tek (r/ghidra ollag1, pelrun score 5) | Use ps2tek for MMI/COP2 encodings, not vanilla MIPS manuals |

Open or unread titles worth a check by someone with time (titles only, not read): EE issues 85/86 (COP2 interlock bit), 65 (`lqc2` as float[4]), 58 (global variable storage), 96 (constant reference analyzer stuck), 98 (COP0.Count), 124 (incomplete analysis), 62 (unaligned load/store analyzer). The project's own tool note already records the README tip to disable the Decompiler Parameter ID analyzer when functions fail.

### 4. PS2 specifics

- **SDK and compiler identification.** Generic answers say GCC often leaves a version string even in stripped binaries (RE.SE 18115, Igor Skochinsky, accepted, 2018) and that library identification can start from strings that name library source files. For PS2 this is a lead to test against FR2's `.comment`, `.mdebug` and string pool. No PS2-specific thread settled the ee-gcc version question.
- **Library identification.** The EE extension owner said a library database would be real work (issue 112); open feature requests exist for static library and IRX identification (issues 114, 115). A Reddit comment says a `ghidra-ps2sdk` project once existed and was taken down (r/gamedev 1q5t0pf, khedoros, 2026-01-07; the repo's absence not independently checked).
- **IRX.** Owner statement: IOP modules carry an identifying string and an export table tying functions to IDs, so identification should be easier than for static libraries (issue 112, 2026-02-16). PCSX2 keeps a common-module-name list in `IopModuleNames.cpp` (as linked by the owner; not read). A search-engine summary (not screened, not verified) said the export table magic is `0x41c00000` and import stubs hold a jump and a function number; this matches what is publicly documented in PS2SDK `irx.h` but was not read here.
- **VU1, VIF, GIF, model formats.** No Q&A thread with usable static technique was found. Two RE.SE posts about PS2 asset formats describe emulator-process tracing and trial editing, which does not apply to our offline bar. See "Still unresearched".

### 5. Pitfalls and warnings

- Do not trust name matches from a signature database without a second signal: PS2Recomp's database ignores ambiguous matches and was sampled mostly from Japanese games (README). A rrisque issue claims signature matching replaced named game functions with libc stubs (rrisque/PS2Recomp issue 16; unverified lead, see below).
- Do not read a tail-call wrapper's decompiler metrics as its own (issue 113).
- Do not generalise "MIPS" support: pelrun (r/ghidra ollag1, score 5) warns the PS2 CPU has dozens of custom instructions.
- Do not accept relocation-adjusted ELF output without checking relocations: two independent threads (2019, 2024) trace corrupted disassembly to relocation handling.
- Several answer authors in the RE.SE threads, including Igor Skochinsky, say outright that signature matching and name inference are brittle; neither authors nor tool maintainers offered an exact accuracy figure.
- Tools warned against: none by name in the screened text beyond the caveats above. A reader may note the ps2xAnalyzer README itself marks its JAL scanner "test only".

## Sources

Screen results: "pass" is from `jev_screen` on excerpts. Votes are as shown at fetch time. Reddit and Stack Exchange accepted flags are stated where visible. Dates are the post or answer date.

| # | URL | Author handle | Date | Votes / accepted | Screen |
| --- | --- | --- | --- | --- | --- |
| 1 | https://reverseengineering.stackexchange.com/questions/18115 | Igor Skochinsky | 2018-04-29 | 1, accepted | S1 pass (inj 0.02) |
| 2 | https://reverseengineering.stackexchange.com/questions/19590 | Igor Skochinsky | 2018-10-10 | 5, not accepted | S1 pass |
| 3 | https://reverseengineering.stackexchange.com/questions/175 | Igor Skochinsky | 2013-03-23 | 27, accepted | S1 pass |
| 4 | https://reverseengineering.stackexchange.com/questions/3044 | Peter Andersson | 2013-11-17 | 9, not accepted | S1 pass |
| 5 | https://reverseengineering.stackexchange.com/questions/18169 | manduca; Anton Kukoba | 2018-05-13/14 | 2 / 2, not accepted | S1 pass |
| 6 | https://reverseengineering.stackexchange.com/questions/2347 | Igor Skochinsky; PSS | 2013-06-26 | 12 / 12 (PSS accepted) | S2 pass (inj 0.02) |
| 7 | https://reverseengineering.stackexchange.com/questions/2580 | 0xea; Codoka | 2013-08-04; 2015-04-10 | 31 / 5 | S2 pass |
| 8 | https://reverseengineering.stackexchange.com/questions/31325 | micheal65536 | 2022-12-28 | 5, no answers | S2 pass |
| 9 | https://reverseengineering.stackexchange.com/questions/21242 | Florian Magin | 2020-04-16 | 2, not accepted | S2 pass |
| 10 | https://reverseengineering.stackexchange.com/questions/33207 | joxeankoret | 2024-09-08 | 2, accepted | S3 pass (inj 0.02) |
| 11 | https://reverseengineering.stackexchange.com/questions/25917 | Shane Reilly | 2020-09-17 | 7, not accepted | S3 pass |
| 12 | https://reverseengineering.stackexchange.com/questions/33314 | Sami Liedes | 2024-11-21 | 2, no answers | S3 pass |
| 13 | https://reverseengineering.stackexchange.com/questions/19606 | ChrisG; Igor Skochinsky | 2018-10-12/15 | 7 (accepted) / 3 | S3 pass |
| 14 | https://reverseengineering.stackexchange.com/questions/21697 | 0xec (PS2 ELF relocation) | 2019-07-20 | 5, accepted | S3 pass |
| 15 | https://reverseengineering.stackexchange.com/questions/32564 | Iman Abdollahzadeh | 2023-12-12 | 0, no answers | S3 pass |
| 16 | https://www.reddit.com/r/REGames/comments/1attl99/ | Enda_of_Eire | 2024-02-18 | 5, no visible replies | S4 pass (inj 0.02) |
| 17 | https://www.reddit.com/r/REGames/comments/174nu4j/ | cakehonolulu1; igor_sk | 2023-10-10/11 | 1 / 2 | S4 pass |
| 18 | https://www.reddit.com/r/REGames/comments/14rrnry/ | Redgabriel_13; khedoros | 2023-07-05/06 | 2 / 2 | S4 pass |
| 19 | https://www.reddit.com/r/ghidra/comments/ollag1/ | WaitForItTheMongols; AND_MY_HAX; pelrun | 2021-07-16 | 9; 5; 5 | S4 pass |
| 20 | https://www.reddit.com/r/gamedev/comments/1q5t0pf/ | Erym03; khedoros | 2026-01-06/07 | 0; 1 | S4 pass |
| 21 | https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/118 | israpps; bigianb; chaoticgd (owner) | 2026-04-27 | open, 6 comments | S5 pass (inj 0.02) |
| 22 | https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/112 | Risae; chaoticgd (owner) | 2026-02-15 | closed | S5 pass |
| 23 | https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/113 | Red-tv141; chaoticgd | 2026-02-17 | closed | S5 pass |
| 24 | https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/114 and /115 | Risae | 2026-02-27 | open feature requests | S5 pass (title level) |
| 25 | https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/75 | modusc896d352; chaoticgd | 2024-07-19 | closed | S5 pass |
| 26 | https://raw.githubusercontent.com/ran-j/PS2Recomp/main/ps2xAnalyzer/Readme.md | ran-j (repo) | fetched 2026-10-04 | n/a | S5 pass |

Jev verification (`jev_verify`, one call, 8 claims against the screened excerpts): 7 verified (confidence 0.93 to 1.0), 1 contradicted. The contradicted claim was a deliberate overclaim ("JAL scanner recommended for retail games"); the README says test-only. No claim was unsupported.

Read after a `jev ask` injection pre-screen (all 0.01 to 0.04) but not formally `jev_screen`ed and not relied on: RE.SE 15571, 26996, 20610, 22676, 21346, 6259, 11495, 21510, 21935, 18760, 311, 29823; ps2dev viewtopic 10671 and 11075 (Wayback copies; fetched, unread); RetroReversing PS2 unstripped page (fetched, unread); a Ford Racing 3 article on 32bits.substack.com (fetched, unread); suXin space pointer-tracking note (fetched, unread); EE issues 53, 54, 58, 60, 62, 65, 84, 85, 92, 96, 98, 122, 124, 127 and rrisque/ran-j PS2Recomp issues 4, 6, 9, 16, 18 to 24, 194, 196, 206, 209, 236, 260 (fetched, unread). No Jev tool returned `review` or `block` on anything screened.

## Directly applicable next steps for Ford Racing 2, ranked

Each step names a check that can fail. All are static; none needs the emulator.

1. **Pin down `gp` and count unresolved gp operands.** Read the startup code's `gp` assignment (it may be `lui/addiu` or `move gp,reg`), set it as the register value over all of .text, and re-export. Check: the number of `gp0x` style operands in the exported pseudocode (target 0), and every resolved gp-relative load lands inside .sdata, .sbss or .data. Fails if operands remain or resolve outside initialized segments. Basis: EE issue 118.
2. **Resolve the 157 KB of unowned code-shaped bytes by seed class, not by one pass.** Build candidate entry sets from (a) aligned words in data sections that point into .text, (b) `j` targets that leave their function, (c) switch table targets from `jr` after table loads. Check: for each seed, a recursive-descent decode ends in `jr ra` or a known tail jump with zero invalid R5900 opcodes and no fall-through into data; compare the invalid-opcode rate against a baseline of random 4-byte aligned data windows from the same section. Fails if code-shaped regions decode no better than the data baseline. Basis: RE.SE 2580, 2347, EE issue 113.
3. **Audit tail calls separately.** Classify every small function that ends in a jump to another function as a wrapper and exclude it from pseudocode-derived metrics and function counts that the next-phase note uses. Check: no recovered function body overlaps another's entry, and wrapper count is stable between two runs. Fails if bodies overlap or counts differ. Basis: issue 113 and the PS2Recomp function-boundary threads (leads only).
4. **Name library code by anchor plus neighbours, not by signature hash alone.** Name a few SDK or libc routines from distinctive strings, then test whether neighbours in address order form contiguous library regions. Check: a named anchor's two neighbours either name-match library behaviour (strings, call shape) or the region assumption is dropped. Fails if anchors are scattered with no contiguity. Treat any PS2Recomp SDK-database hit as a hint requiring a second signal (README caveat).
5. **Check the ELF for aids before inventing work.** Inspect program and section headers, `.comment`, `.mdebug`, stabs and `.gnu.linkonce.*` names, and the `R_MIPS_26` relocation table. Check: report which of these exist; if linkonce or mdebug exist, demangle and import them; if relocations exist, compare disassembly with and without them. Fails if none exist (then record that for step 4). Basis: r/REGames 174nu4j, RE.SE 21697, EE issue 75.
6. **Switch tables.** Collect Ghidra's jump table warnings from the 620 warning comments in the current export, extract table bounds from the preceding compare, and add targets. Check: each table's entries all fall inside the same function's range and land on instruction boundaries. Fails if targets leave the function (then the pattern is a tail-call table). Basis: RE.SE 25917.
7. **IRX identification from structure.** Walk each IRX module's name string, export table (with its magic) and import stubs, then compare function counts with the 13 provisional metadata entries in `fr2-iop-entry-recovery`. Check: every import stub's function number is within the matching library's export count. Fails on any out-of-range number. Basis: EE issue 112 owner statement; the magic value needs confirmation against PS2SDK headers.
8. **Treat MMI/COP2 semantics as unverified in any generated host code.** A PS2Recomp downstream fork's issue 22 claims about 35 MMI ops were mistranslated and HI/LO was treated as 64-bit (lead only). Check: write three or four single-instruction tests derived from ps2tek (for example 128-bit parallel adds and HI/LO pairs) against the generated functions that use them. Fails if any result differs from the documented semantics.
9. **Type recovery plan.** Import only types actually evidenced by field accesses and known SDK structs; expect manual header edits and `.conflict` duplicates (RE.SE 33207, 33314). Check: each imported struct's field offsets agree with at least two distinct access sites. Fails if offsets collide.

## Unverified leads, conflicts and blocked sources

Unverified leads (not traced to documentation or a project's own source):

- The `ghidra-ps2sdk` project "taken down" (r/gamedev 1q5t0pf): single commenter's statement.
- IRX export magic `0x41c00000` and import stub shape: seen only in a search-engine summary; likely documented in PS2SDK `irx.h`, not read.
- rrisque/PS2Recomp issues (all filed 2026-10-03 by one author): 4 (function boundary detection merges adjacent functions in stripped ELFs), 9 (tail jumps emit direct calls that bypass overrides), 16 (signature matching replaces named functions with libc stubs), 22 (MMI mistranslation). Titles and short bodies only; the author is not the main maintainer, and the same-day batch suggests a single-session audit. Check before using.
- ran-j/PS2Recomp pull requests 206, 209, 236 touch function maps and indirect-call promotion; titles only.
- Search-engine summaries of ps2tek, Dr HS Fortuna VU tutorials and a PS2Recomp VIF1 issue were not opened.

Conflicts:

- Accepted RE.SE answer 18115 suggests matching library code by compiler-version strings; RE.SE 19590 and 18169 say library matching without the exact compiler build rarely works. These do not contradict: version strings help choose a build to test, they do not guarantee a match.
- RE.SE 2580 answers disagree on whether disassembly is "exact" (0xC0000022L says exact for each opcode; others say separating code from data is not). Different questions; keep them apart.
- No other direct conflicts found.

Blocked or unreachable (not bypassed):

- reddit.com direct (HTTP 403 to scripts) and the search tool's domain filter for reddit and stackoverflow: used the public Arctic Shift archive for thread text instead.
- psx-place.com and forums.pcsx2.net (403 direct; Wayback copy was too short to use), ps2-home.com and forum.gamehacking.org (403), forums.ps2dev.org (origin timed out; Wayback copies only for two threads).
- Jev screens blocked nothing. The PCSX2 `GSRendererSW.cpp` excerpt was not requested or read.

## Still unresearched or unverified

- Question 4 is mostly open: VU1 microcode static analysis, VIF unpack and DMA tag parsing from consuming code, GS register packet recovery, and finding vertex formats from the code that consumes them have no screened forum evidence in this note.
- The ps2dev, psx-place and PCSX2 forum threads and the Ford Racing 3 article, RetroReversing PS2 pages and suXin note were fetched or located but not read or screened.
- Ghidra Data Type Manager workflow at scale, BSim and Function ID on R5900 were not tested; only maintainer statements were recorded.
- Whether FR2's retail ELF has `.mdebug`, stabs, `.gnu.linkonce` names or relocations is unchecked.
- ee-gcc and SDK version for FR2 is not determined by any source here.
- Compliance note on screening order: the tool takes text as an argument, so I read each fetched file after a `jev ask` injection pre-screen (scores 0.01 to 0.04) and then passed a bounded excerpt of what I used to `jev_screen`. A few search-engine result summaries and Firecrawl result snippets were seen without screening; the facts taken from them are labelled leads above.
