# Ford Racing 2 (PS2) — Reverse-Engineering Brief

> **SUPERSEDED (2026-10-03):** §5's FILES.HDR/FILES.DAT container hypothesis below is outdated.
> The validated format now lives in `tools/extract_tree.py` (proof: `notes/fs-tree.txt` — 1037 records,
> 48-segment partition verified; 990 files extracted, 604 zlib + 386 raw, zero failures).
> See `.scratch/HANDOFF-ford-racing-2-re.md` for the continuation state.

Scope: research findings, each claim with a source URL. Local disc facts come from
`games/ford-racing-2/ford-racing-2.bin` (MODE2/2352, 288,549 sectors) and the extractor output in
`games/ford-racing-2/extracted/` (see `notes/iso-file-table.txt`). "Local obs." marks a finding read
from those files, not a published source.

## 1. Release facts and serials

- Developer **Razorworks**, publisher **Empire Interactive** (EU) / **Gotham Games** (NA). PS2 NA release
  28 Oct 2003, EU 31 Oct 2003. Also PC, Xbox, Mac OS X.
  https://en.wikipedia.org/wiki/Ford_Racing_2
- Serials: **PAL `SLES-51705`** (CD, 1 data track, barcode 5017783012170, PAL multi-5)
  https://psxdatacenter.com/psx2/games2/SLES-51705.html ; **NTSC-U `SLUS-20788`**, CD, EXE date
  2003-09-11, internal serial `SLUS-20788` https://psxdatacenter.com/psx2/games2/SLUS-20788.html ,
  http://redump.org/disc/15603/
- Local disc is the **PAL** build: `SYSTEM.CNF` says `BOOT2=cdrom0:\SLES_517.05;1`, `VMODE=PAL`
  (local obs.; note the on-disc filename is `SLES_517.05` with an underscore, while the printed serial
  is `SLES-51705`).
- Razorworks: founded Aug 1996, based in Oxfordshire UK, an internal Empire Interactive studio (acquired
  Nov 2000), closed July 2008 after Empire's financial collapse (Empire into administration May 2009).
  It began with combat flight sims, then racing. https://gamia-archive.fandom.com/wiki/Razorworks ,
  https://www.mobygames.com/company/1788/razorworks/
- **Engine sharing: not directly documented.** No public source states the shared engine name. Circumstantial
  link: Razorworks built *Total Immersion Racing* (2002) before *Ford Racing 2* (2003), and Feral's Mac port
  partner Zonic had "previously brought Total Immersion Racing to the Macintosh" using "Razorworks' code"
  https://www.macworld.com/article/172954/fordracing2.html . *Ford Racing 3* (2004, SLUS_209.7) is a
  separate later title confirmed as Razorworks/Empire PS2
  https://32bits.substack.com/p/under-the-microscope-ford-racing-7a4 . No primary source confirms a named
  common engine across these — treat "shares tech" as plausible, unproven.

## 2. PS2 disc + executable boot chain

- `SYSTEM.CNF` requires, in order: `BOOT2` (full path to the executable), `VER` (title version), `VMODE`
  (`PAL`/`NTSC`). CD example `BOOT2 = cdrom0:\SCPS_110.04;1`. https://www.psdevwiki.com/ps2/System.cnf
  (Local file matches this format exactly.)
- The BOOT2 target is an **EE (Emotion Engine) main executable**: a MIPS **R5900** ELF. Local
  `SLES_517.05` confirms this: `ELF 32-bit LSB executable, MIPS, MIPS-III (SYSV), statically linked,
  stripped` (local obs.). EE = MIPS R5900 core with 128-bit MMI SIMD; IOP = MIPS R3000A (PSX-derived).
  https://www.copetti.org/writings/consoles/playstation-2/
- **IRX** = IOP Relocatable eXecutable — ELF objects that run on the IOP, export/import functions, and are
  loaded from EE code via `sceSifLoadModule` / `sceSifLoadStartModule` / `...Buffer` variants. Modules loaded
  at boot (e.g. SECRMAN) can only be replaced via an **IOPRP image** (`IOPRPxxx.IMG`, x = SDK version),
  usually in `MODULES/`, `IOP/` or `IRX/` folders. https://www.psdevwiki.com/ps2/IRX_Files
  IRX files are ELF-based; module name/version and imported/exported libraries are inspectable.
  https://github.com/frno7/iopmod
- **SIF** (Subsystem Interface) is the EE↔IOP link: two DMA channels SIF0 (IOP→EE) and SIF1 (EE→IOP) plus
  registers `MSCOM`/`SMCOM` (EE↔IOP mailboxes) and `MSFLAG`/`SMFLAG`, at EE side `1000F200h…1000F230h`
  https://psi-rockin.github.io/ps2tek/ . IOP-side `1D000000h…` SIF registers likewise. Local disc ships
  `IRX/IOPRP255.IMG` plus STREAM.IRX, LGDEV.IRX, LIBSD.IRX, MCMAN.IRX, MCSERV.IRX, PADMAN.IRX,
  SDRDRV.IRX, SIO2MAN.IRX, USBD.IRX (local obs.) — SDK 2.5.5 modules.

## 3. Current tools that actually work (2024–2026)

- **Ghidra Emotion Engine: Reloaded** (chaoticgd) — maintained (last commit Aug 2026, supports Ghidra 12.1.3).
  Disassembles/decompiles EE-specific ISA (MMI, VU0 macro), recovers types from `.mdebug` (STABS),
  imports PCSX2 savestates, exports VU programs. https://github.com/chaoticgd/ghidra-emotionengine-reloaded
  (supersedes the older beardypig `ghidra-emotionengine`, per its README.)
- **PCSX2 built-in debugger** — documented, first-class, intended for patch/reverse-engineering work; open
  via `Debug → Open Debugger`. https://github.com/PCSX2/pcsx2-net-www/blob/main/docs/advanced/debugger.md
- **ps2dev toolchain** — `ps2toolchain-ee` builds EE (R5900) GCC/binutils (e.g. `ee-objdump`/`ee-gcc`);
  PS2SDK provides EE/IOP libraries and `sdk/tools`. https://github.com/ps2dev/ps2toolchain-ee ,
  https://github.com/ps2dev/ps2sdk
- **iopmod** — `iopmod-info` parses IRX metadata (module name/version, imported/exported libraries) without
  loading; `iopmod-link` builds IRX. Last active Dec 2024. https://github.com/frno7/iopmod (Also
  `ps2homebrew/ps2-unpacker`, early-alpha ELF emulation loader: https://github.com/ps2homebrew/ps2-unpacker .)
- **Symbol recovery** — `chaoticgd/ccc` parses PS2 debug symbols (`.mdebug`, `.sndata`).
  https://github.com/chaoticgd/ccc
- **ISO extraction (macOS, no 7z needed)** — `pycdlib` (pure-Python ISO9660; 1.21.0 released Sep 2026, active).
  https://github.com/clalancette/pycdlib . This is a MODE2/2352 raw `.bin`: ISO9660 logical sector =
  user-data of each 2352-byte raw sector, so extraction needs a raw-sector reader (the repo's
  `tools/ps2iso.py`/`iso_walk.py` already do this) rather than plain pycdlib on the `.bin`.
- **VU disassembly** — PCSX2 ships a VU1/VU micro disassembler
  (https://github.com/PCSX2/pcsx2/blob/master/pcsx2/DebugTools/DisVU1Micro.cpp); the VU instruction set is
  documented in the official VU manual http://lukasz.dk/files/vu-instruction-manual.pdf .

## 4. PS2 asset formats relevant to this era

- **VAG / ADS audio** — VAG is 4-bit mono ADPCM sample data (SPU/SPU2).
  http://justsolve.archiveteam.org/wiki/VAG_(PlayStation) . Modern convert tool:
  https://github.com/eurotools/es-ps2-vag-tool . Inside PSS, audio is the **"SS2"/SShd** stream
  (PCM16 BE/LE or SPU2-ADPCM). https://rewiki.miraheze.org/wiki/PlayStation_PSS_Video
- **PSS video** — PS2 "PlayStation Stream": big-endian MPEG-2 program stream with an `SShd` audio header
  (`SShd` signature, struct size 24, type 0/1/2, sample rate, channels, 512-byte interleave) plus `SSbd`
  body, private_stream_1 audio packets and MPEG program end code `00 00 01 B9`.
  https://rewiki.miraheze.org/wiki/PlayStation_PSS_Video
- **Textures** — PS2 GS pixel-storage modes `PSMCT32`, `PSMT8` (8-bit indexed, 4 px/word), `PSMT4` (4-bit
  indexed, 8 px/word), `PSMCT16`, etc.; TM2 (`TIM2` magic) is the common PS2 texture container carrying GS
  TEX/CLUT registers.
  https://openkh.dev/common/tm2.html
- **VIF/VU1** — VIF decompresses/streams vector data and uploads VU microprograms; command encoding is
  documented. https://psi-rockin.github.io/ps2tek/ (VIF Commands section),
  https://ps2dev.github.io/ps2sdk/vif__codes_8h.html
- **Compression** — no single PS2-standard archive compression exists; titles use zlib/deflate, custom
  LZSS, or DMC on a per-game basis. Community databases: the XeNTaX wiki (now largely archived/offline,
  https://archive.org/details/wiki-wikixentaxcom_202305 ) and the maintained
  https://github.com/VelocityRa/awesome-game-file-format-reversing index.
- **Ford Racing 2 specifically: no public format/modding documentation found.** The series' documented RE
  is for *Ford Racing 3* (cheat-code RE via Ghidra EE:
  https://32bits.substack.com/p/under-the-microscope-ford-racing-7a4 ) and *Ford Racing Off Road* PC
  (`widberg/fror-research`, ImHex `.hexpat` patterns for its PC container formats):
  https://github.com/widberg/fror-research . Neither documents FR2's PS2 archive.

## 5. Razorworks/Empire-era archive tooling

- **No public tool for Ford Racing 2's archive was found.** Searches for the actual container names
  (`FILES.HDR`/`FILES.DAT`) returned no parser, docs or wiki page. State clearly: no public documentation
  found.
- Local observation of the container (not published anywhere found): a **`FILES.HDR` index (29,428 B) +
  `FILES.DAT` data blob (334,641,152 B)** pair (local obs., `extracted/`). `FILES.HDR` begins with a u32
  word (`0x30`) then a table of little-endian `(size, offset)` pairs, mixing chained runs with `0xFFFFFFFF`
  sentinel/terminator entries (990 of them), followed by a name table. Named groups observed: `3DDATA`,
  `ANIMS`, `DATA`, `FONT`, `GRAPHICS`, `LANGUAGE`, `PHYSICS`, `SOUNDS`, `TRACKS`, plus per-vehicle entries
  suffixed `.PS2;1` (`49COUPE.PS2;1`, `COBRA.PS2;1`, `FORDGT.PS2;1`, `F150.PS2;1`, …) and `debug.ps2;1`,
  `misc.ps2;1` (local obs., `tools/hdr_analyze.py`). This is an **unverified working hypothesis**, not a
  documented format.
- By contrast, sibling-era PS2 racing archives *are* documented — e.g. Genki's GUT archives
  https://github.com/igor-cizd777/GUTArchiveTools (Genki GUT archives, PS2 racers). Useful only as format-reading
  technique reference, not for FR2.

## 6. Recommended RE workflow and PS2-specific pitfalls

Ordering for a raw MODE2/2352 `.bin`:

1. **Extraction** — parse the raw-sector stream to ISO9660 (2352→2048 user-data); the repo's
   `tools/ps2iso.py` already walks the PVD/file table (`notes/iso-file-table.txt`). No 7z needed.
2. **`SYSTEM.CNF`** — read `BOOT2` to identify the EE ELF (`SLES_517.05` here) and `VMODE`.
3. **EE ELF into Ghidra** — load with ghidra-emotionengine-reloaded; run the STABS analyzer only if
   `.mdebug` exists (this binary is **stripped**, so expect none — local obs.), then Auto-Analyze.
4. **IOP IRX inspection** — run `iopmod-info` on each `IRX/*.IRX` and on `IOPRP255.IMG` to enumerate
   modules/libraries; correlate with EE `sceSifLoadModule*` call sites.
5. **Asset cataloging** — census the `FILES.HDR` index (names, sizes, offsets); scan `FILES.DAT` for
   magic signatures (`SShd`/`SSbd`/PSS, `TIM2`, `VAG`, `Vag`/`SCEI`, MPEG start codes) before decompressing.
6. **Selective decompression** — only on slices whose size is suspiciously small relative to their header
   or that fail to parse; test zlib first, then LZSS, then DMC.

PS2-specific pitfalls:
- **Two CPUs, two address spaces.** EE virtual/physical map (KUSEG 0–7FFFFFFF, KSEG0 80000000, KSEG1
  A0000000…; RAM `00000000`/`20000000` uncached; IOP RAM `1C000000`, BIOS `1FC00000`, scratchpad
  `70000000`) https://psi-rockin.github.io/ps2tek/ . Never confuse EE and IOP pointers.
- **TLB / MIPS addresses.** MIPS ELF entries and pointers are frequently `0x0010xxxx`/`0x8xxxxxxx`-style
  virtual addresses; KSEG0/KSEG1 aliases must be normalized, and the MIPS-R5900 constant-reference analyzer
  in the Ghidra plugin exists precisely to fix such references.
- **VU microcode is separate from MIPS.** VU0/VU1 code lives in dedicated memories (`11000000h`/`11008000h`)
  and is uploaded via VIF; VU programs are not visible as EE functions. The plugin can export VU programs,
  and PCSX2 `DisVU1Micro` disassembles them.
- **Static stripping.** Stripped EE ELF → no symbols; expect to rely on string xrefs and PCSX2 savestates
  for dynamic grounding (the Ghidra plugin imports PCSX2 savestates, but modern PCSX2 savestates use zstd:
  set savestate compression to Deflate64 or disable zstd — see the plugin README).

## Open questions / unknown

- **No documented name of the Razorworks engine**, and no primary source confirming Ford Racing 2 shares
  code/format with Total Immersion Racing or Ford Racing 3 (only a Mac-porting anecdote).
- **No public documentation of FR2's `FILES.HDR`/`FILES.DAT` container** — the structure in §5 is a local
  hypothesis from one disc, unvalidated against other dumps or the PC version.
- **No confirmed per-asset format list for FR2** (which files are VAG/ADS, PSS, TIM2, or which compression
  is used); the on-disc `.PS2` vehicle files are named but not parsed.
- **Exact disc identity unverified**: local dump is 288,549 sectors, while the Redump USA entry records
  304,291 sectors for `SLUS-20788`; the PAL `SLES-51705` Redump entry/hash was not retrieved to confirm a
  byte-match. Track count is 1 data track in both cases.
- **IOPRP255.IMG internal module set not enumerated** (romman/ROMIMG referenced but not run).
- Whether FR2's PC/PS2 share container formats is unverified.
