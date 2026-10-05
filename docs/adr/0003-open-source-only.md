# All tooling and all code must be completely open source

The owner set this as a hard constraint: **everything except the downloaded game corpus and PCSX2 must be completely open source.** No proprietary toolchain, no proprietary library object, no proprietary dependency may be used to build or reproduce the game.

Consequences, recorded so the target stays honest:

- SDK/library regions **cannot be byte-matched**: Sony's `.a` objects are proprietary and public matching decomps (ICO, rac1, BFM) link them. Those regions get an **open-source substitute** (ps2sdk, GPL) and are labelled **"substitute, not matched"**, never counted as matched.
- The ELF-hash **gate is scoped to game-owned sections**, not the whole ELF.
- If the game code itself was built with a **proprietary compiler** (Metrowerks MWCCPS2, SN ProDG), byte-exact game code is **unattainable under this constraint**. **Resolved 2026-10-05:** FR2's game code was built with **Sony/Cygnus GNU `ee-gcc`** (open source), not a proprietary compiler, so byte-exact game code *is* attainable. Evidence in `notes/research/fr2-toolchain-identification.md`. The exact `ee-gcc` id remains a probe, not an obstacle.

- **Toolchain choice follows from this constraint.** Only the GPL Cygnus `ee-gcc` builds from `decompme/compilers` are permitted for *matching*; the SN ProDG mirrors (`AngheloAlf/SN-Systems-ProDG_for_PS2_*`, `sce_ps2_sdk_24`) are third-party mirrors of proprietary software and are **excluded**, as is any Sony `ee-ld`. The linker is GNU ld (patched), as ICO uses.
- **The open-source foundation is ps2dev** (https://github.com/ps2dev): `ps2sdk` (Academic Free License 2.0) is the `substitute region` for the SDK; `ps2toolchain-dvp` and ps2dev `binutils-gdb` supply `dvp-as`; `ps2toolchain-iop` covers the IOP modules. **ps2dev's modern `ps2toolchain-ee` builds gcc 15.2.0 and is *not* the matching compiler** — matching uses the era `ee-gcc`.
