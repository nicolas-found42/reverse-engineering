# PS2 decompilation practices on GitHub, applied to the Ford Racing 2 EE corpus

Research date: 2026-10-04. Scope: public GitHub repos, READMEs, docs, source, issues, plus three community web pages
(RetroReversing, ps2tek) cited by those repos. This note adds to, and does not repeat,
`notes/modern-reverse-engineering-methods.md`, `notes/research-modern-re-awesome-github.md`,
`notes/evidence/fr2-static-recovery/tools-research.md` and `notes/evidence/fr2-continuation/next-phase.md`
(Ghidra + EE:Reloaded, splat, decomp.me, m2c, PS2Recomp as tools are already recorded there).

## Method and limits

- Text was fetched to files in the session scratchpad (`gh api` raw contents, `curl` for three web pages). Nothing
  was cloned, built, installed, executed or downloaded as a binary. No emulator, no game file, no PCSX2
  `GSRendererSW.cpp` excerpt.
- Every excerpt used here was passed to `jev_screen` (purpose: research PS2 reverse engineering methods) before use:
  42 screens, all `pass` (injection 0.01 to 0.02), none `review`, none `block`. Log with revisions:
  `/private/tmp/claude-502/-Users-Nicolas-Documents-github-hermes-reverse-engineering/06a510a0-8efe-495f-8ec4-48ceff0ef27a/scratchpad/research-gh/screens.tsv`.
  A screen needs the text in the model's context, so bounded excerpts were displayed and screened before any claim was
  written from them; the short READMEs of vifterpreter, gmi-forge, wrench, decomp-compat-kit, recvx, jak-project,
  tmb_decomp and nightfire-re were displayed one step before their (passing) screen and are used only lightly.
- `jev_verify` checked 20 claims against the screened text: 15 verified, 4 contradicted (the 4 deliberate overclaims I
  planted, e.g. "the SDK DB is a complete catalog", "dead-strip rule proven for every object"), 1 unsupported
  (Ghidra decompiles VU1). Four items returned `review` (PsII wording, IRX stub wording, PS2Recomp boundary priority,
  the VU1 overclaim); they are worded conservatively below. Jev rerank ordering of the 28 candidate sources is advisory
  and was based on my own one-line summaries of each source.
- Community claims are leads. "Verified" here means: the claim is present in the project's own README, doc, source or
  issue text. It does not mean the claim was reproduced, and nothing here was tested on FR2.
- Not found: any public Gran Turismo 3/4 matching or decompilation repo (GitHub repo search, a handful of queries;
  absence of hits is not proof). GT4 appears only as a PS2Recomp bring-up issue (#171, address-table error).
  Silent Hill 2 appears as `oohweee/sh2-proto-decomp`, a prototype build that carries DWARF (see Q3).

## Local facts used (read-only, from existing evidence)

From `notes/evidence/fr2-static-recovery/results/executables.json`, EE executable `SLES_517.05` (1,662,804 bytes):
`.text` 0x100000 size 1,145,812; `.vutext` 13,696; eleven executable `.user_section*` sections
(`.user_section1..8`, `19`, `_uncommon`, `_init`, total 87,820 bytes) after `.ctors`/`.dtors`/`.reginfo`;
`.data` 126,188; `.rodata` 255,028; `.lit4` 3,652; `.sdata` 6,599; `.sbss`; `.bss`; `.spad`; `.eh_frame` 4 bytes;
`.mdebug.eabi64` present but size 0; `.DVP.ovlytab` plus eight `.DVP.overlay..` sections. I did not find these section
names in any public source (searched GitHub code and web; zero hits). Their role is unexplained here.

---------------------------------------------------------------------------------------------------------------

## Q1. Finding and bounding functions in a stripped EE ELF (unreferenced code, jump tables, data-in-text)

What the projects actually do (none of them rely on one automatic pass):

1. **Seed from a real analyzer, then own every byte.** God Hand, Kingdom Hearts, rac1, Persona 4 run `splat` on the
   loaded image (`objcopy -O binary` of the ELF to a `.rom`; generated YAML with `platform: ps2`, `compiler: EEGCC`,
   `gp_value`, a `.vutext` `textbin` segment) and seed `symbol_addrs.txt` from Ghidra
   ([splat Quickstart-Elf](https://github.com/ethteck/splat/blob/1d09139b886f/docs/Quickstart-Elf.md),
   [god-hand-decomp README](https://github.com/LucasPicoli/god-hand-decomp) rev 58bcee16a279). splat can hint file
   splits (`find_file_boundaries`) and rodata-to-text pairing, but its docs say the user must still find real splits.
2. **Persona 4 and rac1 keep an exhaustive function window map and give every window an owner**: matched C, retail
   assembly, handwritten asm, linker remnant, library. Persona 4 reports 13,102 windows, all mapped
   ([README](https://github.com/Raikaru/Persona4-Decompilation) rev 152fb5236194, 2026-10-04).
   rac1 keeps `handwritten_asm.txt` (212 functions, 83,520 bytes) and `linker_remnants.txt` (69 entries, 276 bytes) and
   states that boundary-error buckets ("fallthrough fragment", "epilogue fragment") are boundary bugs to fix, not
   functions to decompile
   ([ASM_CLASSIFICATION](https://github.com/Lynder063/rac1-decomp/blob/9ca0f7f71f88/docs/ASM_CLASSIFICATION.md)).
3. **Linker artifacts explain much "code-shaped" residue** (rac1, SN ProDG / ee-gcc era, PAL R&C1):
   - The retail linker dead-stripped unreferenced functions. Rule found 2026-09-23: the first `floor(size/8)*8` bytes
     vanish; a function of size 4 mod 8 leaves its final delay-slot word plus an alignment nop. Proven on three libgcc
     objects against Sony's prebuilt `libgcc.a`; for other objects it is only "consistent with"
     ([DECOMP_PROGRESS](https://github.com/Lynder063/rac1-decomp/blob/9ca0f7f71f88/docs/DECOMP_PROGRESS.md),
     section "Retail's linker dead-stripped unreferenced functions").
   - Resulting shapes: a lone `addiu $sp,$sp,N; nop` at an object head ("orphan epilogue fragment"), one-instruction
     fragments with no `jr $ra`, runs of them. rac1's triage rules: a 4-byte "function" is almost never real; a body that
     opens with a positive `addiu $sp` is the tail of another function; no `jr $31` and no tail jump means a remnant
     ([tools/rank_candidates.py](https://github.com/Lynder063/rac1-decomp/blob/9ca0f7f71f88/tools/rank_candidates.py)).
   - Inter-object fill was `0xCDCDCDCD` in `core_text` (49 runs, each ending 8-byte aligned); the other code segment
     had none, so its object boundaries came from other evidence (same DECOMP_PROGRESS file).
   - 19 object starts were hidden inside splat functions; one splat object was three SDK objects back to back.
4. **Indirect and unreferenced entries** (PS2Recomp, EE:Reloaded):
   - `ExportPS2Functions.java` adds entries Ghidra did not mark as called: `lui` followed within four instructions by
     `addiu`/`ori` on the same register (so the low half may sit in a delay slot), kept only if the target looks
     callable (`addiu sp,sp,-N` in the first four words, or an `ra` spill within eight, or a bare leaf `jr ra` when the
     value is a call argument); plus any aligned word in a non-executable initialized block that passes the same test and
     either sits in `.ctors/.dtors/.init_array` or has another candidate within 32 bytes
     ([source](https://github.com/ran-j/PS2Recomp/blob/c5a9d0257341/ps2xRecomp/tools/ghidra/ExportPS2Functions.java), 2026-09-30).
   - Community workbench observation (one title, Valkyrie Profile 2): a JAL-target scanner finds targets reached only by
     `J` or only through pointer tables poorly (646 functions vs Ghidra 973); remaining gaps are fed back through a
     `CreateFunctionsAt` script from a hand-kept address list
     ([known-issues](https://github.com/phmdacosta/ps2recomp-workbench/blob/fdc7bd7cf550/docs/known-issues.md)).
   - EE:Reloaded ships 141 function-start patterns (`jr ra`+delay slot or `j X; addiu sp` shared returns followed by
     `addiu sp,sp,-N`, `lui; addiu sp`, `lui gp; addiu gp`) and syscall-stub patterns
     ([r5900_LE_patterns.xml](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/blob/ae013ee1475d/data/patterns/r5900_LE_patterns.xml)).
   - OpenGOAL does not need discovery: GOAL code has a type word before every function and the code zone ends one word
     past the last `jr ra`; its prologue/epilogue decoder (saved GPRs/FPRs, `fp` setup) is a transferable idea, not code
     ([decompiler/README](https://github.com/open-goal/jak-project/blob/efb21c3e8c5a/decompiler/README.md)).
5. **Jump tables vs tail-call function pointers.** spimdisasm's changelog records that these two patterns are easily
   confused and that mis-identification broke neighbouring symbols (release 1.39.1 was yanked). rac1 keeps compiler jump
   tables in the *data* segment, not next to the code that uses them
   ([spimdisasm CHANGELOG](https://github.com/Decompollaborate/spimdisasm), branch 1.x rev 4b5d4c68eeb9;
   [rac1 TOOLCHAIN](https://github.com/Lynder063/rac1-decomp/blob/9ca0f7f71f88/docs/TOOLCHAIN.md)).
6. **Data-in-text.** `.vutext` is carved out as a binary blob (`textbin`) and spimdisasm hard-codes not disassembling it
   (changelog 1.17.3: it polluted symbol analysis). sh2-proto keeps VU1 microprograms as data. rac1 and Persona 4 treat
   hand-written assembly as its own class.
7. **Decode-rate heuristics are unsafe as a code/data test.** One recompilation findings repo withdrew a published
   untranslated-code figure because its >92% decode threshold scored the ELF entry point (known code) at only 54.7%
   over a 256-byte window and a data region at 0.0%
   ([WoS findings README](https://github.com/InitialDad/PS2Recomp-WoS-Findings) rev 674f7d86e87d). Our
   `tools/r5900_shape.py` plus `controls` in `verify_text_denominator.py` already carry control sets; keep that discipline.

Applicable statically: items 3, 4, 5 below in "Next steps" (remnant partition, address-taken sweep, jump-table split).

## Q2. Types, structs, calling convention and signatures at scale

- **With debug info the problem disappears.** `.mdebug` (STABS) is parsed by `chaoticgd/ccc` (`stdump` emits C++/JSON;
  2.x also reads ELF and SNDLL symbols) and imported by EE:Reloaded's STABS analyzer; PaRappa 2 and sh2-proto derive
  prototypes, locals and headers from symbol/DWARF dumps
  ([ccc](https://github.com/chaoticgd/ccc), [parappa2 docs/decompilation.md](https://github.com/parappadev/parappa2)).
  FR2's `.mdebug.eabi64` section is empty (local fact above), so none of this applies unless a sibling build exists.
- **Sibling builds substitute for symbols.** NFS:MW matches against a PS2 PAL alpha build whose debug dump gives member
  visibility and virtual-function order, plus the GameCube DWARF
  ([nfsmw](https://github.com/dbalatoni13/nfsmw) rev 1f2cdd799679). rac1 cross-checks names with other decomps of the
  same game and transfers names between builds by aligning function-size sequences (710 of 813 NTSC functions matched
  the PAL sequence, 87%). Persona 4 names ~300 RenderWare PS2-driver functions from another game's symbol table and
  link map ([RenderWare.md](https://github.com/Raikaru/Persona4-Decompilation/blob/152fb5236194/wiki/RenderWare.md)).
- **Middleware source as a type oracle.** Persona 4 recovered RenderWare 3.7.0.2 verbatim from the public source and
  compiled it with the matching compiler build; the PS2 driver had no public source. recvx-decomp names a CRI ADXT build
  date. If FR2 links RenderWare or CRI code, those are the cheapest type sources (unchecked for FR2).
- **SDK types.** `sce-symbol-scanner` has a work-in-progress `gdtbuilder` (a `.GDT` of SCE SDK types) and a Ghidra
  plugin meant to apply signatures ([README](https://github.com/LostTemplarRH/sce-symbol-scanner) rev 211920996aa3).
  EE:Reloaded's owner states Ghidra FunctionID needs exact hashes, BSim is fuzzier, and no PS2 library database exists
  ([issue 112](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/112), 2026-02-15).
- **No-symbol fallback is field-access inference.** PaRappa 2's guide uses `unkNNN` field names from observed offsets
  and a function-per-GPR style until names are earned; Sly 1 notes that `lq/sq` on `$s` registers is ordinary
  callee-saved spilling, not vector use (only `lqc2/sqc2` is real VU0 access)
  ([sly1 cheatsheet](https://github.com/TheOnlyZac/sly1/blob/a4eea5a9dfb4/docs/mips_ps2_cheatsheet.md)).
- **Honesty accounting.** sh2-proto counts 46 "fake matches" and fitted stand-ins separately from real matches; Persona 4
  separates byte-identical, named, typed and documented functions
  ([sh2-proto README](https://github.com/oohweee/sh2-proto-decomp) rev 778a9b55a8f4). A matching gate proves
  instructions, not types or meaning (same point in
  [decomp-compat-kit](https://github.com/LinuxJessi/decomp-compat-kit)).
- **Calling convention.** Nothing PS2-specific beyond the MIPS EABI64-style register use that m2c exposes as `mipsee`;
  stack spills of `$s0-$s7`, `$ra` use `sq`/`lq` or `sd`/`ld` depending on compiler build (see Q3), which matters when
  recognizing prologues.

## Q3. Compiler/SDK identification, library matching, sym/map leakage

- **Library function identification by relocation-masked hashing** (the closest thing to FIDB for PS2). `sce-symbol-scanner`
  hashes function bytes with relocated fields masked per MIPS relocation type (26-bit jumps keep opcode bits; HI16/LO16 and
  GPREL keep the top half; 32-bit words zeroed), then resolves candidates using unique-at-address, neighbour/predecessor
  /successor in the same library, and dependency consistency. It says short functions give false positives and it
  doubles as a function-bound finder because it checks bytes
  ([README and source](https://github.com/LostTemplarRH/sce-symbol-scanner), rev 211920996aa3, 2026-04-20).
  PS2Recomp's analyzer embeds a compatible database and warns it was built from PS2 games that carried debug info
  (mostly Japanese titles) and retained relocations, so it is a high-confidence hint, not a full catalog
  ([ps2xAnalyzer/Readme.md](https://github.com/ran-j/PS2Recomp/blob/c5a9d0257341/ps2xAnalyzer/Readme.md)).
  rac1 did the same against the real SDK `.a` members (libmc, libdbc, libpad2, libmpeg matched byte-for-byte with
  relocations masked) and concluded that archive member extents are the true object boundaries.
- **SDK version stamps.** Binaries embed `PsII` + an 8-byte right-trimmed library name + four ASCII version characters
  (for example `PsIIlibkernl2050`); the scanner reads them for ~50 known library names. Two independent sources agree
  on the string family (sce-symbol-scanner source; RetroReversing's unstripped-binaries notes; ps2kit's regex
  `PsIIlib[a-z0-9 ]{2,9}\d{4}`). The IOP side has module banners such as `PsIImcman   2020` (RetroReversing, community
  inference of SDK 2.0.2).
- **Compiler identification is by probing, not by reading metadata.** Persona 4: the ELF comment string comes from the
  linker and says nothing about the C compiler; different MWCC builds were compiled against retail and the decisive
  discriminators were `movz/movn` emission, top- vs bottom-tested loops, `sq` vs `sd` callee-saved spills, loop-end
  alignment nops ([The-Retail-Build](https://github.com/Raikaru/Persona4-Decompilation/blob/152fb5236194/wiki/The-Retail-Build.md)).
  rac1 found two SN sub-builds inside one ELF (one spills with `sq/lq`, one with `sd/ld`, switching at a known address),
  `-G2` small-data threshold from float-literal inlining plus `$gp` use, SDK code built by Sony's 2.9-ee compiler vs game
  code by SN's 2.95.3, and SN's own assembler adding `nop`s that GNU `as` does not (R5900 short-loop erratum; a `nop`
  between an FP compare and `bc1`, 191 of 191 sites) ([TOOLCHAIN](https://github.com/Lynder063/rac1-decomp/blob/9ca0f7f71f88/docs/TOOLCHAIN.md)).
  Sly 1, rac1, God Hand, Xenosaga use SN/Sony ee-gcc 2.9x to 2.96; Persona 4 mixes MWCCPS2 and ee-gcc 2.96; modern ps2dev
  GCC (15.2) was reported unable to match (rac1 history). decomp.me's compiler catalog lists these EE ids:
  `ee-gcc2.9-990721/991111(a,b-r4,-01)`, `2.95.2-273a/274`, `2.95.3-107/114/136`, `2.96`, `3.2-030210-beta2/030926/040921`,
  `iop-gcc2.8.1/2.95.2-102`, and 14 `mwcps2-*` builds
  ([compilers values.yaml](https://github.com/decompme/compilers) rev bf4f879ea19f, 2026-10-01).
  The SDK ships `libgcc` variants per compiler (2.9-ee-991111-01, 2.96-ee-001003-1, 3.2-beta2/030926/040921), so which
  libgcc routines/shapes appear narrows the compiler era
  ([RetroReversing static libs](https://www.retroreversing.com/static-libraries-ps2), page dated 2026-08-09, community).
- **Symbol/map leakage.** RetroReversing keeps a list of retail PS2 games that shipped symbols, some with `.map`,
  `SRCFILE.TXT` or `.XFF` side files; claims there cite forum posts. The fetched text has no Ford Racing entry
  (Jev-verified), which is a snapshot dated 2020-11-21 and proves nothing about FR2
  ([page](https://www.retroreversing.com/ps2-unstripped)). Prototypes (RE4 review, SH2/SH4 E3 builds) carry `.mdebug` or
  DWARF. CCC documents duplicate or fake function symbols in some games' `.mdebug`, so even leaked symbols need checking.

## Q4. IOP (IRX), VU0/VU1 microcode, VIF/DMA/GS packet code, statically

- **IRX**: ELF type 0x80 (`ET_IOPMOD`) with `SHT_IOPMOD` 0x70000080; import tables start with magic 0x41e00000 (then a
  zero word, a version word, an 8-byte library name) followed by one stub per function of `jr $ra` with the ordinal in
  the delay slot; export tables use 0x41c00000
  ([frno7/iopmod irx.h and module-symbol.S](https://github.com/frno7/iopmod) rev 12cdf14b78ed). ps2kit independently
  describes the same stubs (`jr $ra / addiu $0,$0,ordinal`, magic `0x41E00000`) and names ordinals from SDK headers
  ([docs/10-ps2kit.md](https://github.com/vs-sr-dev/pc-extermination/blob/9e42d65a3687/docs/10-ps2kit.md)).
  Ordinal-to-name sources: ps2sdk's per-module `exports.tab` (module name, version, ordered `DECLARE_EXPORT` list; 85
  files), IDAPy-PS2's JSON built by scraping ps2sdk, and `Ziemas/ghidra_irx`, which labels imports. The EE:Reloaded owner
  says IRX is R3000 code (use Ghidra's generic MIPS:LE:32), each IRX has an identifying string and an export table, and
  PCSX2 keeps a list of common module names ([issue 29](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/29),
  [issue 112](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/112)). IRX files almost never carry debug
  symbols (RetroReversing, forum-sourced).
- **EE syscalls**: stub-labelling scripts exist (IDAPy-PS2 `LabelExecutableSyscalls.py`); EE:Reloaded v2.1.25 reworked its
  syscall patterns because commercial SDKs patch the kernel and syscall numbers differ from the homebrew SDK
  ([CHANGELOG](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/blob/ae013ee1475d/CHANGELOG.md)).
- **VU microcode location**: in MPG VIF codes (0x4A......) or in DMA chains of `cnt` tags ending in `ret`. ps2kit's `vu.py`
  disassembles both halves, finds microcode in those two places and reports no unknown opcode across 22 programs
  (~7,000 instructions) of its one target game. `ps2_ida_vu_micro` finds MPG uploads but says branch targets are wrong
  below 0 or beyond 0xFFF/0x3FFF and when VIF codes more complex than MPG/UNPACK/NOP intervene. OpenGOAL's
  `VuDisassembler` handles VU0/VU1 with E-bit and branch-delay handling and can emit C++ (a translation, not a
  decompilation) ([VuDisasm](https://github.com/open-goal/jak-project/tree/efb21c3e8c5a/decompiler/VuDisasm)).
  `vutrace`'s `vudis` disassembles microcode memory dumps but its tracer needs a patched PCSX2 (dynamic; excluded here).
- **No tool decompiles VU code.** EE:Reloaded removed VU microcode disassembly in v2.0.0, tried a VU overlay importer
  (v2.1.28), and disabled the overlay table in v2.1.30. The owner doubts decompilation is viable: VU0's register file is
  shared with the R5900 and runs in lockstep (defeats data-flow analysis), and VU1 pipeline interlock quirks are hard to
  express in SLEIGH ([issue 122](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/122), 2026-06-08).
  Projects therefore keep microprograms as data/asm (sh2-proto, kh1/splat `textbin`) or translate them.
- **DMA/VIF/GIF/GS code**: static walkers exist as parsers, not decompilers: ps2kit `gs`/`vif`/`gsmem` (GS local-memory
  model: PSMCT32/24/16, PSMT8/4, CLUT, `TEX0` decode; it found 23,278 `TEX0` words in one game's meshes and rendered them),
  a heuristic `DMA tag (cnt/ret/end, QWC>0) + VIF NOP + DIRECT/DIRECTHL` packet test, and `vifterpreter` (Rust DMA/VIF
  parser). Sly 1's docs name the engine layers (VIFS, GIFS, DMAS helpers such as `AddVifMscal`). `gmi-forge` plans to
  emulate VIF unpack, run the VU1 program and parse the emitted GIF tags offline, but is at scaffold stage (M0); treat
  as design only.
- **Overlays/DVP**: Ghidra imports `.DVP.overlay..` sections and has an `ExportDvpOverlays.py` (VU1 text address
  0x11008000, 8-byte instructions); rac1 handles per-level code overlays by masked-fingerprint deduplication, and
  ps2kit's `mwo3` builds an ELF around overlays plus the host executable with call-target seeds.

## Q5. Known pitfalls that degrade static decompilation (as reported)

| Pitfall | Reported effect | Source (maintainer or project text) |
| --- | --- | --- |
| `$gp` unknown or set via `move gp,a0` | decompiler shows `gp0xffff8090`-style expressions; splat reports "failed to symbolize %gp_rel". Fix: set `gp_value` from the code that writes `$gp` (`lui/addiu` or `lui/addiu/daddu`) | EE:Reloaded [#118](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/118) (open), splat [#410](https://github.com/ethteck/splat/issues/410) |
| Fully linked ELF that still has a reloc table | relocations applied twice, doubled `jal` targets, analysis "explodes"; disable relocations on import | EE:Reloaded [#53](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/53), changelog v2.1.13 |
| Analysis regression across Ghidra/extension versions | less complete analysis after Ghidra 11.4 / extension 2.1.25 | EE:Reloaded [#124](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/124) (open, commenter report) |
| MIPS tail calls are `j`/`b` | thunk or tail-call bodies decompile as the callee; 8-byte function can show 12 branches | EE:Reloaded [#113](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/113), owner: consequence of Ghidra's decompiler |
| Branch-always thunks and unconditional branches | recompiler emitted `pc=target; return` (target never ran); resuming in the delay slot of an always-taken branch fell through | PS2Recomp [#86](https://github.com/ran-j/PS2Recomp/issues/86), [#260](https://github.com/ran-j/PS2Recomp/issues/260) |
| Mixed VU0 and MMI inside fragments | fragments found by entry discovery were misdecoded and over-sliced into the next function | PS2Recomp #86 (reported fixed by reporter) |
| Entry discovery duplicating tails | ~150 generated files sharing one end address; runaway 537 KB "function" | PS2Recomp [#63](https://github.com/ran-j/PS2Recomp/issues/63), workbench known-issues |
| 128-bit GPRs, `lq/sq` | `lq/sq` are ordinary `$s` spills; Ghidra's 128-bit typing is "sub-optimal"; MMI/VU instructions are pcode stubs so dataflow is lost | Sly 1 cheatsheet; EE:Reloaded [#65](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/65) |
| capstone on EE code | `lq/sq` and MMI decode as unrelated MSA/DSP instructions | ps2kit docs (author-reported) |
| Unaligned load/store pairs | `ldl/ldr`, `lwl/lwr` need a pre-analyzer to decompile | EE:Reloaded `MipsR5900PreAnalyzer`, changelog v2.1.16 |
| COP2 `.I` interlock suffix on `qmfc2/qmtc2/cfc2/ctc2` | mis-shown until v2.1.22 | EE:Reloaded [#85](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/issues/85) |
| VU0 macro mode | VU0 and EE share registers, defeating dataflow; `vcallmsr` reads CMSAR0 via `ctc2 $vi27` | EE:Reloaded #122; PS2Recomp [#262](https://github.com/ran-j/PS2Recomp/issues/262) |
| VU1 pipeline exposure, E-bit delay slot | a read right after a write may see the old value; the E-bit has a delay slot; I-bit makes the lower word a float | EE:Reloaded #122; [ps2tek](https://psi-rockin.github.io/ps2tek/) |
| PS2 float semantics | no NaN/Inf/denormals, round toward zero; `1*X` vs `X*1` differences reported on VU | ps2tek; PS2Recomp [#165](https://github.com/ran-j/PS2Recomp/issues/165) (contributor report, links unverified) |
| `.lit4`, `.sdata` | float literals live in `.lit4`; splat needed explicit `.lit4` support | splat [#352](https://github.com/ethteck/splat/issues/352) |
| Short-loop erratum, SN assembler | extra `nop`s from SN's assembler (`ps2eeas`); GNU `as` miscounts after a forward branch; `vadda.xyz` operand order, `symbol+offset` with `$gp`, `c1` macro differences | rac1 TOOLCHAIN/OVERLAYS; splat [#525](https://github.com/ethteck/splat/issues/525) (open) |
| Section headers stripped | some analyzers find no functions (RE4, Psychonauts); Ghidra route needed | PS2Recomp [#35](https://github.com/ran-j/PS2Recomp/issues/35) |
| Delay-slot register reuse | GCC reuses a register between the branch test and the slot; decompilers must evaluate the condition first | parappa2 [docs](https://github.com/parappadev/parappa2) |
| Syscall numbering differs by SDK | official vs homebrew numbering | EE:Reloaded changelog v2.1.25 |

---------------------------------------------------------------------------------------------------------------

## Sources

Screen column: all `pass`; injection / substance / relevance as returned. Full log in `screens.tsv` (path above).

| URL | What it is | Revision / date seen | Screen |
| --- | --- | --- | --- |
| https://github.com/Lynder063/rac1-decomp (docs/TOOLCHAIN.md, DECOMP_PROGRESS.md, ASM_CLASSIFICATION.md, OVERLAYS.md, tools/rank_candidates.py) | PAL R&C1 matching decomp; richest linker-artifact and SDK-matching notes | 9ca0f7f71f88, 2026-10-04 | pass 0.01-0.02 / 0.98-0.99 / 0.93-0.97 |
| https://github.com/LostTemplarRH/sce-symbol-scanner | SDK function identification by relocation-masked hashes; PsII scanner | 211920996aa3, 2026-04-20 | pass 0.02 / 0.99 / 0.96 |
| https://github.com/ran-j/PS2Recomp (README, ps2xAnalyzer/Readme.md, ExportPS2Functions.java, issues 35/63/75/86/165/171/260/262) | static recompiler; Ghidra export heuristics; user bug reports | c5a9d0257341, 2026-09-30 | pass 0.02 / 0.97-0.99 / 0.91-0.96 |
| https://github.com/phmdacosta/ps2recomp-workbench | community workbench, known-issues, CreateFunctionsAt | fdc7bd7cf550, 2026-09-06 | pass 0.02 / 0.99 / 0.96 |
| https://github.com/chaoticgd/ghidra-emotionengine-reloaded (README, CHANGELOG, patterns xml, PreAnalyzer, ExportDvpOverlays, issues 29/53/54/65/75/85/112-115/118/122/124) | R5900 Ghidra extension; maintainer statements | ae013ee1475d, 2026-08-25; v2.1.37 | pass 0.02 / 0.98-0.99 / 0.91-0.96 |
| https://github.com/chaoticgd/ccc | `.mdebug`/STABS and SNDLL symbol parsing, compiler-bug notes | pushed 2026-06-07 | pass 0.02 / 0.98 / 0.96 |
| https://github.com/chaoticgd/vutrace | VU1 tracer (PCSX2 patch) and `vudis` | pushed 2024-06-22 | pass 0.02 / 0.98 / 0.95 |
| https://github.com/ethteck/splat (wiki docs, issues 182/352/410/503/525) | splitter with PS2 support | 1d09139b886f, 2026-07-27 | pass 0.01-0.02 / 0.98-0.99 / 0.95-0.96 |
| https://github.com/Decompollaborate/spimdisasm | splat's disassembler (function/jumptable/hi-lo detection, R5900) | 4b5d4c68eeb9 (1.x), 2026-08-06 | pass 0.02 / 0.98 / 0.94 |
| https://github.com/decompme/compilers | decomp.me compiler catalog, PS2 ids | bf4f879ea19f, 2026-10-01 | pass 0.01 / 0.96 / 0.87 |
| https://github.com/open-goal/jak-project (decompiler/README.md, VuDisasm) | Jak decompiler and VU disassembler | efb21c3e8c5a, 2026-09-30 | pass 0.02 / 0.99 / 0.96 |
| https://github.com/oohweee/sh2-proto-decomp | SH2 prototype (DWARF, MWCC) matching decomp, LLM-written | 778a9b55a8f4, 2026-10-01 | pass 0.02 / 0.99 / 0.96 |
| https://github.com/Raikaru/Persona4-Decompilation (README, wiki RenderWare/Retail-Build/Compiler-Floors) | P4 decomp, multi-compiler, RenderWare source | 152fb5236194, 2026-10-04 | pass 0.02 / 0.99 / 0.95-0.97 |
| https://github.com/LucasPicoli/god-hand-decomp | splat + ee-gcc 2.96 + dvp-as pipeline | 58bcee16a279, 2026-10-03 | pass 0.01 / 0.99 / 0.96 |
| https://github.com/TheOnlyZac/sly1 | Sly 1 decomp, ProDG toolchain, cheatsheet | a4eea5a9dfb4, 2026-10-04 | pass 0.01 / 0.99 / 0.95 |
| https://github.com/parappadev/parappa2 , https://github.com/ethteck/kh1 , https://github.com/Fantaskink/SOTC | PaRappa 2 (prototype with symbols), KH1, SOTC | 45694de3b6ed; 0df3b6586d2d; 59b47f6004a1 | pass 0.02 / 0.98 / 0.96 |
| https://github.com/dbalatoni13/nfsmw | NFS:MW multi-platform decomp, PS2 alpha debug dump | 1f2cdd799679, 2026-10-02 | pass 0.02 / 0.98 / 0.89 |
| https://github.com/AshfordFamily/recvx-decomp ; abelbriggs1/tmb_decomp ; NightfireResearch/nightfire-re | other PS2 projects (short reads) | 12a05ddfeef5; 506f3177593b; acd94c29405b | pass 0.02 / 0.98 / 0.94 |
| https://github.com/vs-sr-dev/pc-extermination (docs/10-ps2kit.md, ps2kit/fingerprint.py, vu.py) | game-agnostic Python PS2 toolkit | 9e42d65a3687, 2026-10-02 | pass 0.02 / 0.99 / 0.98 |
| https://github.com/frno7/iopmod | IRX header/stub constants, iopmod-info (GPL-2.0) | 12cdf14b78ed, 2024-12-29 | pass 0.01 / 0.98 / 0.94 |
| https://github.com/ps2dev/ps2sdk (README, `exports.tab`) | open-source SDK; IOP export lists | ac92a9f657d2, 2026-10-03 | pass 0.01 / 0.98 / 0.91 |
| https://github.com/Ziemas/ghidra_irx ; grimdoomer/IDAPy-PS2 ; Goatman13/ps2_ida_vu_micro | IRX import labeller; IDA syscall/IOP scripts; VU microcode finder | 2d45b8ec73b7; 356fa94d7a00; c5f184bfdd3a | pass 0.02 / 0.99 / 0.96 |
| https://github.com/InitialDad/PS2Recomp-WoS-Findings | one-title findings repo with withdrawn claims | 674f7d86e87d, 2026-07-28 | pass 0.02 / 0.99 / 0.93 |
| https://github.com/0x5abe/vifterpreter ; gerson-henrique/gmi-forge ; chaoticgd/wrench ; LinuxJessi/decomp-compat-kit | VIF parser; VIF/VU1 decode plan; R&C tools; verification kit | 68f33f3625fe; fe47acce278a; be81b6d010e9; d9bb53dac364 | pass 0.02 / 0.98 / 0.96 |
| https://www.retroreversing.com/static-libraries-ps2 ; /irx-ps2 ; /ps2-unstripped | community SDK-library, IRX and unstripped-binary pages (forum-sourced) | updated 2026-08-09; 2021-03-25; 2020-11-21 | pass 0.01 / 0.98-0.99 / 0.92-0.96 |
| https://psi-rockin.github.io/ps2tek/ | PS2 hardware reference (EE, float format, VU) | fetched 2026-10-04 | pass 0.02 / 0.98 / 0.93 |

---------------------------------------------------------------------------------------------------------------

## Directly applicable next steps for Ford Racing 2 (ranked)

All are static and offline, use only the saved ELF and extracted files, and each states a result that would refute it.
Ranked by expected reduction of unexplained bytes per unit of work.

1. **Partition the unowned code-shaped spans by linker-artifact signatures before treating them as missing functions.**
   Classify each unowned span in `.text` and the eleven `.user_section*` regions as: (a) 4 or 8 bytes ending in a
   delay-slot-type word (`addiu sp,sp,+N`, `lw`, `sw`, `move`) plus `nop`; (b) a span whose first instruction is a
   positive `addiu sp,sp,N`; (c) no `jr ra` and no `j` tail; (d) fill words (`0xCDCDCDCD`, zero). Basis: rac1 dead-strip
   rule and triage rules (Q1.3).
   *Check that can fail:* if there are no `0xCDCDCDCD` runs of at least 8 bytes anywhere in executable sections, the
   rac1 fill-boundary method does not apply to FR2; and if classes (a)-(c) cover under ~10% of the 157 KB, the
   dead-strip explanation is not the main source of unowned code and the remainder needs the next steps. Do not call
   class (a)-(c) "decompiled"; mark them "residue, original function body unknown", as rac1 does.
2. **Fingerprint the toolchain from the executable itself, per region.** (i) Scan all executable and data sections for
   `PsII` stamps and `GCC:`/`SN Systems`/`ProDG`/`MW MIPS C Compiler` strings; (ii) histogram callee-saved spills in
   function prologues (`sq`/`lq` vs `sd`/`ld`) by address; (iii) count FP-compare followed immediately by `bc1`, and
   loops shorter than six instructions with and without a padding `nop` (SN's `ps2eeas` pads both, GNU `as` does not);
   (iv) look for libgcc/`__main`/64-bit division routine shapes and `.ctors` consumers.
   *Check that can fail:* if there are zero `PsII` hits and the spill mnemonic is uniform across the whole function
   table, neither SDK-version nor sub-build boundaries can be derived this way, and compiler era must come from probing
   with decomp.me ids (cost: manual). If the spill mnemonic changes inside a function rather than at a boundary between
   function runs, the "two builds, one boundary" model is false.
3. **Infer object/unit boundaries from the toolchain evidence and test the section hypothesis.** Candidate edges: spill
   mnemonic switches, 8-byte alignment after `jr ra`+`nop`, orphan epilogue heads, fill runs, and the start/end of each
   `.user_section*` and `.vutext` region. Compare with the existing 4,718-function table.
   *Check that can fail:* if function starts, spill mnemonics and gp-relative symbol clusters show no change at
   `.user_section*` edges, the "sections are unit groups" hypothesis (an untested guess; I found no public source for
   these section names) is rejected. rac1 got 19 object starts that splat had buried inside functions this way.
4. **Sweep address-taken and data-pointer entries with explicit plausibility, over every executable section and over
   `.data/.rodata/.sdata/.ctors`.** Reuse PS2Recomp's rules (lui+addiu/ori within four instructions including delay-slot low
   halves; prologue in first 4 words or `ra` spill in first 8; data words clustered within 32 bytes) but record
   rejected candidates too. Separate switch tables from function pointers by requiring an indexed `jr` with a bounds
   check and targets inside one function (spimdisasm confuses the two).
   *Check that can fail:* if more than a small fraction of "jump-table" targets land outside the enclosing function
   body, the table is a function-pointer or vtable array and must not drive CFG edges; if pointer candidates that pass
   the plausibility test land in the middle of existing functions, they are not entries.
5. **Relocation-masked fingerprints, first within the ELF, then against an SDK database if the owner approves.**
   Mask `jal` targets, `lui` immediates, `%lo` immediates and `$gp` offsets (as `sce-symbol-scanner` does), hash each
   function, and group duplicates; libgcc and newlib-like routines appear as clusters. Matching against
   `sce-symbol-scanner`'s `symbols.json` (~8.5 MB, derived from commercial binaries) is a separate decision: it was not
   downloaded here and its licence status was not checked. ps2sdk is community code, so its compiled bytes should not
   be expected to hash-match Sony's libraries (inference, untested).
   *Check that can fail:* hash a handful of functions you already know are duplicated (for example identical wrappers)
   and confirm the mask groups them; if short functions produce many false positives (the project warns of this), apply
   the minimum static-bit threshold idea and report only functions above it.
6. **IRX: name ordinals from ps2sdk `exports.tab` and cross-check with EE-side module paths.** Scan each IRX for the
   0x41e00000 and 0x41c00000 tables, apply ps2sdk export order by module name and version, and cross-check against
   `sceSifLoadModule` path strings and the `.iopmod` name/version in the extracted files (the repo already has
   `ps2_irx*` tools; this adds ordinal names).
   *Check that can fail:* for any module whose version differs from the ps2sdk `DECLARE_EXPORT_TABLE` version the
   ordinal names are suspect; if two modules of the same name give different stubs for the same ordinal, mark that
   ordinal unnamed instead of guessing.
7. **Differential-test the VU1 decoder on the eight DVP overlays and `.vutext`.** Decode with at least two independent
   tables (OpenGOAL `VuDisassembler`, ps2kit `vu.py`, plus our `tools/ps2_vu.py`) and require agreement on mnemonic and
   field decode for every instruction pair, including I-bit lower words (floats, not instructions), E-bit delay slot
   and 11-bit relative branches near 0xFFF/0x3FFF.
   *Check that can fail:* any disagreement is a decoder bug or a data word; the result is publishable only when zero
   unexplained disagreements remain. Keep the VU side as disassembly; no public tool decompiles VU code.
8. **Fence off VU0 macro-mode and MMI islands from C-level comparison.** Mark functions containing COP2 or MMI
   encodings as assembly islands for m2c/Ghidra comparisons (rac1 blocks "VU0 cluster" and SIMD/COP2 bodies from C),
   and record the PS2 float differences (no NaN/Inf/denormals, round toward zero) in the claim limits of any
   behavioural statement.
   *Check that can fail:* count how many islands exist and how many have callers outside islands; if islands are
   large, the fence hides most of the renderer and the claim limit must say so.
9. **Type recovery order for FR2:** middleware first (check asset chunk stamps and strings for RenderWare/CRI; the
   public RenderWare 3.7.0.2 source is the example of verbatim recovery), SDK structs second, field-access inference
   last, with an `unkNNN` naming rule and a "named/typed/documented" count like Persona 4's.
   *Check that can fail:* if no RenderWare or CRI chunk magic or library string exists in the corpus, drop the
   middleware branch.
10. **Control-set discipline for any new "code vs data" heuristic.** Require measured rates on known code and on known
    data, as `verify_text_denominator.py` already does, and withdraw a heuristic if known code scores in the same
    range as data (the WoS repo's entry-point case).
    *Check that can fail:* run the shape filter on the ELF entry region and on a known data table; if their rates
    overlap, the filter cannot be used as a classifier.

## Unverified leads and blocked sources

Unverified leads (not reproduced; present only as someone's claim):

- Whether FR2 was built with SN ProDG, Sony ee-gcc 2.9x/2.96 or something else is unknown. All "SN/ProDG" statements
  above come from other games. The RetroReversing symbol list had no FR2 entry in the fetched text; that list is
  community maintained and old.
- SDK version inference from `PsII` strings and module banners such as `PsIImcman   2020` is a community inference
  (RetroReversing; also used as a regex by ps2kit). The scanner source confirms the stamp format, not the mapping to an
  SDK release.
- `gmi-forge`'s claim that a VIF/VU1 program can be run offline to rebuild meshes is a plan at milestone M0. It would also
  require writing an emulator component, which conflicts with this project's "no emulator" scope unless the owner
  accepts an in-repo interpreter run only on extracted bytes.
- PS2Recomp README says Ghidra boundaries take priority; a community workbench observed the union with the recompiler's
  own heuristic winning for one title (Jev: contradicted at 0.85, confidence 0.77, flagged `review`). Treat as
  one user's observation until reproduced.
- `PS2Recomp #165` links on EE/VU float quirks (fobes.dev, gregorygaines.com, eefloat, DobieStation) were not fetched.
- `.user_section*` sections as an unit-boundary signal (step 3) is my hypothesis; no public source describes them.
- The sce-symbol-scanner database coverage for FR2's SDK era and region is unknown (built mostly from Japanese
  debug-info titles per the PS2Recomp README).
- `ps2-recomp-Agent-SKILL` (hkmodd) and other "AI skill" repos surfaced by search were deliberately not read; they
  are instruction-bearing text aimed at agents.
- GT3/GT4 decompilation: no public repo found (search-limited).

Blocked sources: none. No `jev_screen` result reached `review` or `block`. The PCSX2 `GSRendererSW.cpp` LOD excerpt was
not read, per the instruction. Sources not used as evidence: EQAI (asset injector, off-topic).

## Still unresearched or unverified (coordinator wrap-up)

- Not fetched or read: ps2dev toolchain internals, PCSX2 `IopModuleNames.cpp`, Ghidra FunctionID/BSim primary docs
  (only the maintainer's statement in issue 112 was used), OpenGOAL `docs/scratch` VU1 notes and level extractor,
  chaoticgd `wrench` source (README only), rac1 `SIBLING_DECOMPS.md`, Persona 4 `docs/compiler-floors.md`, sh2-proto
  deeper docs, the sce-symbol-scanner `SymbolScanner.kt` thresholds, and the ps2kit `gs.py`/`vif.py` source.
- Nothing here was run against the FR2 ELF; every "next step" check is untested and its outcome unknown.
- Several sources are LLM-assisted or single-author projects (sh2-proto, ps2recomp-workbench, WoS findings, ps2kit);
  their numbers are author-reported.
- Jev screens cover bounded excerpts, not whole repositories or later revisions.

## Reproducibility notes

- All repository claims have a revision in the table. Issue text was fetched with `gh api repos/<repo>/issues/<n>` and
  `.../comments` on 2026-10-04; issues can change after that date.
- Jev calls: 42 `jev_screen`, 1 `jev_rerank` (28 candidates; top four: spimdisasm 0.91, ps2recomp-export 0.88,
  ghidra-ee-patterns 0.88, rac1-decomp-triage 0.87, then ps2kit 0.83), 1 `jev_verify` (20 claims: 15 verified, 4
  contradicted (planted), 1 unsupported (planted), 4 returned `review`).
