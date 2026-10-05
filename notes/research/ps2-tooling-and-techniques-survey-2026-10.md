# PS2 / MIPS reverse-engineering tooling and techniques: 2026-10 survey

Research date: 2026-10-05. Scope: public GitHub repos, curated lists, primary tool docs/source, and primary academic papers (arXiv / NDSS / USENIX / ACM / IEEE). This note **adds to** `notes/research/ps2-github-decompilation-practices.md` (the 2026-10-04 GitHub PS2-practice survey) and does not repeat it. Static and offline only: nothing was cloned, built, installed, downloaded as a binary, or run; no emulator, no game file, no blocked PCSX2 text.

Method: four parallel background subagents (this is `/research`'s delegate-the-legwork shape). GitHub via `gh search repos` / `gh api` / `gh_grep`; arXiv abs pages + publisher PDFs/DOIs for papers; `web_extract`/`web_search` for lists. External notes read here were passed to `jev_screen` (`pass`, injection 0.04-0.05). Community claims below are **leads**, not reproduced facts.

---------------------------------------------------------------------------------------------------------------

## A. The nearest neighbours to this project (highest signal)

- **nathanialf/ico** — https://github.com/nathanialf/ico — updated 2026-10-05, 5,097 commits, v1.0.0. A **byte-matching rebuild of the ICO PAL PS2 boot ELF** (`SCES_507.60`): "every byte the console loads is identical to the disc's (the ROM image SHA-1 matches), and so is the ELF file itself." Build chain: `splat → ee-as / ee-gcc → ee-ld → SHA-1-verified ELF`, VU1 microprograms assembled with `dvp-as` from **`ps2dev/binutils-gdb` branch `dvp-v2.45.1` commit `3eb45ea3`** — the *same* DVP binutils this repo already built. It gates the ELF by hash, ships `docs/LEGAL.md` + a no-ROM pre-commit hook, and has a per-section progress dashboard (`.text`, **`.vutext`**, `.data`, `.rodata`, **`.lit4`**, `.sdata`). This is the **closest working analogue to the owner's stated goal** (a reproducible, byte-matched PAL PS2 ELF rebuild) and the best template for the missing "workstream 6" (readable source + reproducible build). **Maturity: active, single-author.** Applies directly as a methodology and toolchain reference, not code.

- **widberg/fror-research** — https://github.com/widberg/fror-research — updated 2026-02-19, 80 commits. Notes + ImHex `.hexpat` patterns for **Razorworks** Ford Racing engine formats (`3dobj*/pcg/pvs/spc/fonts/binfo`, save). **Important correction:** the analysed binary is the **PC** Windows build — Detect It Easy reports `PE32 x86, Watcom linker 2.18`; dumpbin shows `AUTO/.idata/DGROUP/.bss/.reloc`. So it does **not** describe the PS2 EE. Its one PS2-relevant item is a lead: a listed `[PS2] Ford Racing 2 USA Beta [SLUS-20788] [2003-07-28]` (1.3 MB) on `debugging.games`. A sibling beta build *could* carry debug info (cf. `zipzip11/ps2-dwarf1`), but it is a lead, not a resource, and a debug-symbol oracle would need owner approval before use. **Maturity: dormant, single-author.**

- **celophi/so3-decomp** (Star Ocean 3 PS2, 15 code overlays rebuild byte-for-byte), **Megami-Decomps/dds-decomp** (DDS1&2 PS2, splat+decomp.dev CI), **Lynder063/rac-deadlocked-decomp** (same author as the already-cited rac1-decomp), **RossyDoubleUnderscore/ICO-decomp** (splat config that names the exact `.DVP.ovlytab` / `.DVP.overlay` sections FR2 also has) — https://github.com/celophi/so3-decomp , https://github.com/Megami-Decomps/dds-decomp , https://github.com/Lynder063/rac-deadlocked-decomp , https://github.com/RossyDoubleUnderscore/ICO-decomp — all active 2026. Current, concrete **matching-decomp pipelines** (splat YAML + `symbol_addrs` + section progress) to mirror for FR2, and overlay handling directly relevant to FR2's eight `.DVP.overlay..` sections.

- **Druthulu/xsig** — https://github.com/Druthulu/xsig — 2026-09-07, MIT, single Python file. **Relocation-masked per-function signatures** for MIPS: keeps opcodes/registers/constants, masks `j`/`jal` 26-bit targets (by opcode) and `R_MIPS_HI16/LO16` low halves. Found only PsyQ-library code shared across the BFM/Xenogears/Vagrant Story/Tomba decompilations — byte evidence that separated library from engine code in an afternoon. **Directly implements** the repo's planned "relocation-masked fingerprints" step. **Limit that matters here:** both sides need relocation information; a fully-linked ELF without emitted relocations (FR2) cannot be signed faithfully — so on FR2 this works on a **recompiled** object (from `tools/*` or PS2Recomp) vs a matching build, not on the retail ELF alone.

- **encounter/objdiff** (https://github.com/encounter/objdiff) and **Decompollaborate/mapfile_parser** (https://github.com/Decompollaborate/mapfile_parser) — ready-made **instruction-level object/function diffing** and GNU/Metrowerks **map-file parsing**. These are the missing pieces of a matching-decomp harness: `objdiff` is what decomp.dev runs; `mapfile_parser` parses an EE linker map if one is ever obtained.

## B. GitHub tools added or re-confirmed (not in the prior note)

- **jagger1407/Ps2ElfTool** — https://github.com/jagger1407/Ps2ElfTool — 2026-09-18. Lists/exports PS2 ELF sections and disassembles them into ps2dev-assembler-ready MIPS asm. New/basic. Quick offline section dump + reassembly scaffolding for `.text`/`.vutext`/`.user_section*`.
- **harryhardcastle/ps2disSharp** — https://github.com/harryhardcastle/ps2disSharp — 2026-07-02. Maintained C# PS2 disassembler (descends from ps2dis); its file-disassembly path is usable offline (its PCSX2/PINE features are out of scope).
- **Red-tv141/PS2_Scoring_Radar** — https://github.com/Red-tv141/PS2_Scoring_Radar — 2026-04-03. A Ghidra script that two-pass scans a **stripped** PS2 binary (every `jal` + P-Code decompilation + `jalr`/vtable heuristics) to classify functions. A working example of static Ghidra analysis on a stripped EE binary.
- **zipzip11/ps2-dwarf1** — https://github.com/zipzip11/ps2-dwarf1 — 2026-06-19. Standalone DWARF v1 extractor + Ghidra import for PS2 ELF32/MIPS. Only applies if an FR2 **sibling** build ships DWARF v1; FR2's own `.mdebug.eabi64` is empty.
- **Raikaru/mwccps2-debugger** — https://github.com/Raikaru/mwccps2-debugger — 2026-07-12, MIT. Opens Metrowerks PS2 compiler internals to explain why equivalent C emits different R5900 code. Only relevant if FR2 was MWCC-built (unconfirmed; FR2-era UK studios mostly used SN/ee-gcc).
- **sp00nznet/MidwayRecomp** (N64Recomp forked to MIPS-IV R5000 LE) and **Gui-Tora/dmc-recomp** (R5900/IOP static recompilation of DMC PAL `SLES_503.58` via PS2Recomp, with a function-boundary/IOP-service blocker log) — https://github.com/sp00nznet/MidwayRecomp , https://github.com/Gui-Tora/dmc-recomp . Design references for PS2Recomp-style EE passes and for the IOP-service blockers FR2 will hit when naming IRX ordinals.
- **frno7/iopmod** — https://github.com/frno7/iopmod — **updated revision 2026-07-01** (prior note saw 2024-12-29). Re-confirms `ET_IOPMOD 0x80`, `SHT_IOPMOD 0x70000080`, `IOPMOD_IMPORT_MAGIC 0x41e00000`, `IOPMOD_EXPORT_MAGIC 0x41c00000`. Still the cleanest primary source for IRX import/export magic.
- **PredatorCZ/Technyx** — https://github.com/PredatorCZ/Technyx — 2025-11-21. Extracts `CDFILES.DAT`/`ARCHIVE.AR`/`.ARC`/audio from **Eutechnyx** racing titles. **FR2 is Razorworks, not Eutechnyx** (corroborated by Open-PS2-Loader's per-title patch table, which lists Eutechnyx titles but not FR2) — so no direct format match; useful only as a UK-racing-engine reference.
- **No Ford Racing 2 EE decompilation repo exists** (search-limited; absence is not proof). FR2 PS2 developer confirmed **Razorworks** (Wikipedia; PSBBN TitlesDB lists `SLES_517.05` and `SLUS_207.88` as Razorworks).

## C. Curated lists (and which the context-awesome MCP misses)

MCP-missed, high signal: **terremoth/awesome-ps2**, **sammwyy/awesome-ps2**, **ninjadynamics/PS2Docs** (curated R5900/VU/GS/DMA docs), **VelocityRa/awesome-game-file-format-reversing** (~1000 tools, very active), **CharlotteCross1998/awesome-game-decompilations** (per-console decomp index), **RetroReversing/retroReversing**, **psi-rockin/ps2tek** (VU reference), **ReversingID/Awesome-Reversing** (format reversing), **wtsxDev/reverse-engineering**, **dsasmblr/game-hacking**, **extremecoders-re/re-list**, **marethyu/awesome-emu-resources**, **larsbrinkhoff/awesome-cpus** (MIPS manuals). MCP-covers: alphaseclab/awesome-reverse-engineering, tylerha97/awesome-reversing, nforest/awesome-decompilation, rshipp/awesome-malware-analysis, AllsafeCyberSecurity/awesome-ghidra, radareorg/awesome-radare2, command-tab/awesome-n64-development, derekturtleroe/awesome-emulators, gmh5225/awesome-game-security. Top tools reachable through these lists: **chaoticgd/ghidra-emotionengine-reloaded**, **astrelsky/ghidra_MIPSR5900**, **Goatman13/ps2_ida_vu_micro**, **chaoticgd/vutrace**, **ran-j/PS2Recomp**, **ps2dev/ps2sdk + ps2toolchain-iop**, **psi-rockin/ps2tek**.

## D. Toolbox for a stripped R5900 ELF (mature and cutting-edge)

- **Ghidra headless + P-Code** — https://github.com/NationalSecurityAgency/ghidra . The whole FR2 pipeline already rides on this. Ghidra 12.0 adds a low-P-Code abstract interpreter (Ca' Foscari LiSA) and an experimental **Z3 symbolic emulator** — both directly useful for the R5900 `lui/addiu` HI/LO propagation the native decompiler does weakly.
- **Ghidra FunctionID + BSim** — https://ghidra.re/ghidra_docs/GhidraClass/BSim/README.html . FunctionID needs exact hashes (no PS2 `.fidb` exists), but **BSim** indexes fuzzy high-P-Code feature vectors — the right tool for short, relocation-shifted R5900 library routines; seed a BSim DB from `libgcc`/SDK objects. This is the strongest lever against FR2's 3,940-arity / IOP-stub naming backlog.
- **Ghidra `.gdt` datatype archives** — https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/Features/Base/ghidra_scripts/CreateExampleGDTArchiveScript.java . Bundle FR2's `sce` structs + field-access `unkNNN` types and share them.
- **pypcode** — https://github.com/angr/pypcode . Lift `.text` words to P-Code **without launching Ghidra**, so boundary/fingerprint tooling is scriptable in CI.
- **angr + archinfo** — https://github.com/angr/angr . Statically (never execute): CFG recovery, value-set analysis for jump tables, scope-reduced symbolic execution to resolve indirect targets — exactly FR2's remaining blocked seeds.
- **m2c + decomp.me** — https://github.com/matt-kempster/m2c (has a `mipsee`/PS2 dialect), https://github.com/decompme/compilers (PS2 ee-gcc/MWCC ids). Feed raw R5900 to get a readable C skeleton; pin a decomp.me scratch to the exact compiler era to prove a match compiles to the same bytes.
- **rizin + rz-diff** — https://github.com/rizinorg/rizin . `rz-diff -t functions` flags byte/structure-identical functions across two binaries → duplicate-routine clustering.
- **IDA + Lumina**, **Binary Ninja BNIL + sigkit + Sidekick** — secondary decompilers for cross-checking (any C-level disagreement is an analysis bug); sigkit generates/matches signature libraries; Sidekick is a commercial LLM type/name recovery path.
- **RetDec**, **Triton** — RetDec supports 32-bit MIPS and carries a library-signature removal concept; **Triton has no MIPS backend** (its transferable idea is SMT expression synthesis for equivalence proofs).
- **LLM decompilation (cutting edge)** — **LLM4Decompile** (https://github.com/albertan017/LLM4Decompile), **DeGPT** (NDSS 2024), **D-LiFT**, **CHISEL**, **AutoDecompiler**, and the agentic **ReVa** (https://github.com/cyberkaida/reverse-engineering-assistant) / **GhidraMCP** (https://github.com/lauriewired/GhidraMCP) that expose Ghidra's API to an LLM as MCP tools. Pattern: a referee/advisor/operator loop that rewrites decompiler C and validates by **re-compiling + diffing**, never one-shot generation.

## E. Academic literature (2023–2026 primary sources)

- **HELIOS** — https://www.ndss-symposium.org/wp-content/uploads/lastx2026-79.pdf (NDSS LASTX 2026). CFG/call-graph summaries fed to a general LLM: object-file compilability **45%→85.2%** (Gemini 2.0), **>94%** with compiler feedback; evaluated across **six architectures incl. MIPS**. **The only paper found reporting MIPS**, and it needs no fine-tuning — the lowest-cost LLM entry point for FR2.
- **LLM4Decompile** — arXiv:2403.05286 (EMNLP 2024): claims >100% re-executability improvement over GPT-4o/Ghidra; x86-64 only, so checkpoints do not decompile R5900, but the *method* (build a synthetic MIPS→C dataset with ee-gcc, fine-tune) transfers.
- **Nova** — arXiv:2311.13721 (ICLR 2025): assembly-native foundation model (hierarchical attention + contrastive); 14.8–21.6% Pass@1 gains. Right architecture for an R5900 fine-tune.
- **ReSym** — DOI 10.1145/3658644.3670340 (CCS 2024): LLMs + Prolog cross-check recover user-defined structs at precision ~72 / F1 ~85 on **stripped** binaries. The strongest paper for the type/structure goal.
- **DIRTY** (USENIX Sec 2022), **VarBERT** (IEEE S&P 2024), **Retypd** (PLDI 2016), **BinSub** (arXiv:2409.01841), **TYGR** (USENIX Sec 2024, on angr) — name/type recovery; TYGR's data-flow abstraction is architecture-agnostic in design but its trained model is x64-only.
- **XDA** (NDSS 2021), **RustBound** (SMARTSP 2024), **Nucleus**, **ByteWeight**, **"Padding Matters"** (arXiv:2504.21520) — function-boundary detection; all x86-trained, and RustBound confirms mainstream tools detect starts well but **ends poorly** — matching FR2's tail-call/dead-strip reality.
- **jTrans** (ISSTA 2022), **Trex** (NDSS 2021), **DeepBinDiff** (NDSS 2020) — binary similarity/diffing for the matching loop (Trex needs execution → out of scope).
- **angr SoK** (IEEE S&P 2016), **SE survey** (arXiv:2508.06643) — how to use symbolic execution without path explosion.
- **SoK: AI-Augmented Binary Reversing** — arXiv:2606.17398 (2026): 246 papers / 22 inference domains; the index over the field. **Decompile-Bench** (NeurIPS 2025); **AutoFirm** (arXiv:2406.12947) — library identification by embedded version strings at scale (the firmware analogue of FR2's `PsII`-stamp / hash matching).
- **No primary source decompiles PS2/R5900 specifically.** Every MIPS claim rests on HELIOS's six-architecture evaluation.

## F. Applicability ranking to FR2 (what to adopt, in order)

1. **Set up the matching-decomp harness before writing more C** (only if the owner's target is a byte-matched rebuild): `splat` + `m2c` + `objdiff` + `mapfile_parser`, gated by ELF SHA-1 like `nathanialf/ico`. This is the single biggest missing capability (workstream 6) and the ICO repo is a working template that uses the **same `dvp-as` branch** already in this repo.
2. **Adopt a CFG-summary + general-LLM loop (HELIOS-style) as a hypothesis generator**, with a real **re-compile + byte-diff** validator; use `DeGPT`-style refinement only on top of a passing build. Record LLM output as a hypothesis, never ground truth (D-LiFT: LLM-refined code added new inaccuracies in 93.2% of already-correct functions).
3. **BSim + a `.gdt` type archive + `xsig`-style masked hashing** (on a recompiled object) to attack the 3,940 arity mismatches and name the SDK/libgcc/IOP routines from a real signature base.
4. **Resolve the blocked seeds with angr static VSA** (indirect `jr` targets, jump tables) — pairs with the pending g4 work.
5. **Keep VU as byte-exact disassembly/reassembly** (no public tool decompiles VU; `dvp-as` + `ps2tek` remain the references).

## G. Unverified leads, limits, not found

- `fror-research` is the **PC** build (PE/Watcom), not PS2; its formats (`pcg/pvs/spc/textures.pc`) are PC-side. Its FR2 PS2 beta (1.3 MB, `debugging.games`) is unverified and would need owner approval to use as a debug oracle.
- `nathanialf/ico` was read from its README/commit page, not built; the byte-match claim is the author's, not reproduced here.
- `ps2-dwarf1` applies only if an FR2 sibling ships DWARF v1.
- LLM-decompilation accuracy numbers are x86 and author-reported; **no R5900 evaluation exists**.
- `gh` search hit the 30/min rate limit; coverage is thorough but not exhaustive. `.DVP.ovlytab` appears in public source only in EE:Reloaded, `Fantaskink/SOTC` and `RossyDoubleUnderscore/ICO-decomp` — FR2's exotic section names remain essentially undocumented.
- Not found: any Public PS2 Ford Racing (1/2/3/Off Road) decompilation; any peer-reviewed PS2/R5900 decompilation.
- Skipped (instruction-bearing agent text): `hkmodd/ps2-recomp-Agent-SKILL`, `anzaldoivan/psxdecomp`, `nate-santos/ps2-recompilation-guide`.
- Blocked sources: none. No screen reached `review` or `block`.

## Receipts

`jev-screen-*` (external notes, all pass), `jev-compare-note-vs-summaries`, `jev-review-research-note` in `.scratch/fr2-research-survey-2026-10/`. Subagent transcripts: `/Users/Nicolas/.hermes/profiles/coder/cache/delegation/live/deleg_62a37b16/task-{0..3}.log`.
