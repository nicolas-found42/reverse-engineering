# Ford Racing 2 EE toolchain: what the ELF proves, and what is obtainable

Research date: 2026-10-05. Static/offline only: no SDK or game file downloaded, nothing built or run. Adds to
`notes/research/ps2-github-decompilation-practices.md` (Q3) and `notes/research/ps2-tooling-and-techniques-survey-2026-10.md`
(Section A), and does not repeat them. Measurements below were made this session on
`games/ford-racing-2/extracted/SLES_517.05` (SHA-256 21671121…bea95) with a local ELF/instruction scan (Python, no
disassembler run); every external claim has a URL.

## Findings

1. **The ELF carries no game-compiler stamp.** There is no `.comment`, `.symtab` or `.strtab`; `.mdebug.eabi64` is empty.
   Raw-string scan of the whole file returns **0** hits for `Metrowerks`, `SN Systems`, `ProDG`, `ee-gcc`, `ee-ld`,
   `dvp-elf-as`, `MW MIPS`. The only compiler-adjacent strings are 10 Sony `PsII…` library stamps and the game's own
   `../fr2/source/*.c` `__FILE__` paths. (`tools/sdk_stamps.py`, `notes/evidence/fr2-source-map/sdk-stamps-result.json`.)

2. **`e_flags = 0x20924001`**: `EF_MIPS_ARCH_2` (0x20000000) plus machine `0x00920000` (R5900/EE), ABI64 bit clear. This
   is the same EE tag ICO must preserve (`tools/binutils-2.10-ee.patch` backports it "so the inputs' `e_flags` mach bits
   0x00920000 survive the link"). It identifies the target, not the compiler.

3. **`.reginfo`** is a `MIPS_REGINFO` (0x70000006) section; `ri_gp_value = 0x00295d70`, matching the repo's pinned gp
   (`notes/evidence/fr2-gp-context/README.md`). No compiler identity.

4. **Callee-saved spills are `sd`/`ld`, not `sq`/`lq`**, ~15:1, in every executable section: `.text` LD 15158 / SD 13487
   vs SQ 876 / LQ 812; all sections summed LD 15985 / SD 14899 vs SQ 1044 / LQ 940. rac1-decomp reports that retail's
   `text` segment spills with `sq`/`lq` while `core_text` spills with `sd`/`ld`, and that its SN GCC 2.95.3 v1.14 emits
   the `sd`/`ld` layout ([rac1 TOOLCHAIN](https://github.com/Lynder063/rac1-decomp/blob/main/docs/TOOLCHAIN.md),
   `docs/TOOLCHAIN.md` on the default branch). So FR2's code uses the `sd`/`ld` compiler style, not SN's `sq`/`lq` one.

5. **No Sony/SN `ps2eeas` short-loop padding.** rac1's `tools/ps2eeas_nops.py` documents that SN's assembler pads every
   loop shorter than six instructions before its backward branch and inserts a `nop` between an FP compare and a
   following `bc1` ("191 of 191" sites), while GNU `as` does neither. Measured in FR2 `.text`: of 99 short backward
   loops (<6 instructions) only 12 (12.1 %) contain any `nop` and only 4 have a `nop` immediately before the branch; and
   of 1,405 `bc1` sites, 1,209 have an FP compare **directly adjacent** (no `nop`) versus 2 separated by a `nop`. That is
   the **GNU `as` behaviour**, the opposite of SN `ps2eeas`. This is the strongest single discriminator found: it argues
   FR2 was **not** built with SN ProDG, but with a Sony/Cygnus GNU `ee-gcc`/`ee-as` toolchain. (Counts are from one
   approximate loop detector; the direction, not the exact figure, is the claim.)

6. **libgcc fingerprint present but not version-specific.** libgcc's 256-byte `__clz_tab` (`longlong.h`, used by the MIPS
   `__divdi3`/`__udivdi3` in `libgcc2.c`) occurs **4×** in `.rodata` at `0x28cba8 / 0x28cca8 / 0x28cda8 / 0x28cea8`
   (0x100 apart). A MIPS64 64-bit-divide libgcc was linked, consistent with any Sony `ee-gcc` 2.9/2.95/2.96 libgcc;
   it does not separate them. FR2 uses `DIV`/`DIVU`/`DIV1` (47/43/4 in the saved inventory,
   `notes/evidence/fr2-integer-division/README.md`), not an inlined libgcc divide.

7. **SDK library revision ≈ 2.5.5, from the stamps.** Nine libraries are stamped 2500–2550: `libkernl 2550`, `libgraph
   /libdma/libpad/libscf/libmpeg/libipu 2500`, `libcdvd/libsdr 2530`, `libmc 2540`; the IOP side (`ioman`, `mcman`,
   `sysclib`, …) is uniformly 2550 and the disc ships `IOPRP255.IMG` (`sdk-stamps-result.json`). RetroReversing's
   documented reading rule is "a string of the form 'PSII* 2720' … Replace 2720 with the version number you want, e.g
   272 is 2.7.2" ([PS2 Official SDK](https://www.retroreversing.com/ps2-official-sdk), updated 2026-08-09), so 2550 =
   **SDK 2.5.5**, 2540 = 2.5.4, 2530 = 2.5.3, 2500 = 2.5.0. Stamps date the *libraries*, not the game compiler
   (`sdk-stamps-result.json` "claim_limits"), and no Sony-authored version→date table was found in public sources.

8. **ICO proves the recipe (and its inputs).** `nathanialf/ico` is a byte-exact PAL rebuild; its `tools/setup.sh`
   fetches **ee-gcc 2.9-991111-01** (game + libc/libm/libgcc, via its bundled `ee-as`) and **ee-gcc 2.96** (only its
   bundled **SCE 2.10-ee-001003-1** assembler, for SDK archives) from `decompme/compilers` releases; links with **GNU ld
   2.10** (`--target=mipsel-elf`, patched for the R5900 machine and `.DVP.overlay.*`) and assembles VU1 with **`dvp-as`**
   from ps2dev `binutils-gdb` branch `dvp-v2.45.1` commit `3eb45ea37f0efd498d1de3cf9562de07197aefa8`
   ([docs/BUILDING.md](https://github.com/nathanialf/ico/blob/main/docs/BUILDING.md),
   [tools/compile_c.sh](https://github.com/nathanialf/ico/blob/main/tools/compile_c.sh)). ICO deliberately does **not**
   use Sony's `ee-ld`; MAIN.MAP is used only for symbol names and TU order (`tools/gen_pal_symbol_addrs.py`), because
   ICO's PAL disc shipped `MAIN.MAP`/`SRCFILE.TXT`/`TRFILE.TXT`
   ([config/ico.pal.yaml](https://github.com/nathanialf/ico/blob/main/config/ico.pal.yaml)). **FR2's disc ships none of
   those** (no reference file in the repo corpus), so that shortcut is unavailable.

9. **Obtainable toolchains** (all primary):
   - `decompme/compilers` release tarballs, PS2 platform: `ee-gcc2.9-990721`, `ee-gcc2.9-991111`, `…-991111a`,
     `…-991111b-r4`, `…-991111-01`, `…-991111-01-dtls13010`, `ee-gcc2.96`, `ee-gcc2.95.2-273a`, `…-2.95.2-274`,
     `…-2.95.3-107/114/136`, `ee-gcc3.2-030210-beta2/030926/040921`, `iop-gcc2.8.1`, `iop-gcc2.95.2-102`, and 20+
     `mwcps2-*` (2.3-991202 … 3.0.1b210-060308)
     ([values.yaml](https://github.com/decompme/compilers/blob/main/values.yaml),
     [platforms/ps2](https://github.com/decompme/compilers/tree/main/platforms/ps2)).
   - SN ProDG mirrors, cloned by rac1-decomp ([README](https://github.com/Lynder063/rac1-decomp/blob/main/README.md)):
     [AngheloAlf/SN-Systems-ProDG_for_PS2_2.0](https://github.com/AngheloAlf/SN-Systems-ProDG_for_PS2_2.0) (GCC 2.95.2
     SN v2.73a), [..._3.01](https://github.com/AngheloAlf/SN-Systems-ProDG_for_PS2_3.01) (GCC 2.95.3 SN v1.36),
     [sce_ps2_sdk_24](https://github.com/AngheloAlf/sce_ps2_sdk_24) (GCC 2.95.2 SN v2.74 + 2.95.3 SN v1.14). These are
     third-party mirrors of commercial software.
   - Sony `ee-ld`: **not** in decompme (it ships compilers only) and in no public tarball; obtainable only from an SDK
     leak. ICO sidestepped it with GNU ld 2.10 from `https://ftp.gnu.org/gnu/binutils/binutils-2.10.tar.gz`.
   - `dvp-as` (DVP/VU1 assembler) and libgcc source: ps2dev `binutils-gdb` `dvp-v2.45.1` @ `3eb45ea3` (already built by
     this repo per the survey note) and GCC's own `libgcc2.c`/`fp-bit.c` (rac1 rebuilds libgcc from GCC source).

10. **What is pinned vs not.** Pinned from primary evidence: target = R5900/EE (`e_flags`); assembler family = GNU `as`,
    not SN `ps2eeas` (finding 5); compiler family = Sony/Cygnus GNU `ee-gcc`; SDK libraries ≈ 2.5.5 (finding 7);
    matching-decomp inputs obtainable from public sources (finding 9). **Not** pinned: the exact `ee-gcc` id.

## What is still unknown

- **The exact `ee-gcc` id** (2.9-991111-01 vs 2.95.x vs 2.96 vs 3.2-*): not readable from any metadata; it needs a
  probe — compile a known FR2 function under each decomp.me id and diff bytes (the method ICO/rac1 use). No public
  source resolves it for FR2.
- **Whether game objects and SDK archives used a different compiler/assembler pair**, as in ICO (2.9 game vs SCE 2.10
  SDK) and rac1 (SN 2.95.3 vs Sony 2.9): untested here; a per-region spill/erratum boundary was not measured.
- **The exact SDK release label/date for stamp 2550**: no Sony-authored public table; the 2.5.5 reading rests on
  community documentation and the `IOPRP255.IMG` filename.
- **Which linker and patches produced the final ELF** (Sony `ee-ld` vs GNU ld): the ELF alone does not say. ICO needs
  GNU ld 2.10 plus two patches and still cannot reproduce one `.bss` and seven autogenerated overlay names
  (`config/link.pal.ld` "What the link still does not give the file"); FR2's eight `.DVP.overlay.*` sections
  (name hashes `0xf75a9b76`, `0x1d855a55`) would need the same treatment.
- **MWCC is not fully excluded**: the `sd`/`ld` spill style and GNU-`as` erratum behaviour favour GNU `ee-gcc`, but zero
  `Metrowerks`/`MW MIPS` strings is weak evidence for a stripped binary. `mwcps2-*` ids exist and could be probed.
- **A symbol oracle**: no `MAIN.MAP`/`SRCFILE.TXT` exists for FR2; whether the USA beta (`SLUS_207.88`) carries
  symbols/DWARF is an unverified lead (`notes/research/ps2-tooling-and-techniques-survey-2026-10.md`).
- **The 3.2-era GCC**: FR2 is a 2003 PAL title; `ee-gcc3.2-0309*` cannot be excluded on the ELF alone.
