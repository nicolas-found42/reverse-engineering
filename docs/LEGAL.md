# What may and may not be committed

The tooling and reconstruction source in this repository are MIT licensed (`LICENSE`, [ADR-0004](adr/0004-license-and-ip-rails.md)). The game is not part of the repository.

## May be tracked

- Tooling, tests, ADRs, glossary and research notes.
- Evidence results (hashes, offsets, counts and measurements) derived from the corpus.
- Reconstruction source written by hand for this project.
- The disc image cue sheet (`games/ford-racing-2/ford-racing-2.cue`).

## Never committed

- The PS2 boot executable (`SLES_517.05`) or any PS2 ELF, and the disc image or its extracted contents (`FILES.HDR`, `FILES.DAT`, `extracted/`).
- IOP modules (`*.IRX`) and Sony SDK objects or libraries (`*.a`, `*.o`).
- Raw dumps, generated C or assembly produced from the corpus, memory cards and saves.
- Any file carrying a Sony SDK library stamp (`PsII…`) in binary form.

`tools/ip_rails.py` enforces this on the staged blobs, and CI runs `tools/ip_rails.py --tree` over every tracked file, so a skipped hook is still caught. Enable it with `git config core.hooksPath tools/hooks`. `.gitignore` keeps the same paths out of `git status`. The hook is a guard rail, not a licence review: a refusal means stop and ask, not rename the file.

The corpus and PCSX2 are the two named exceptions to "completely open source" ([ADR-0003](adr/0003-open-source-only.md)); neither is redistributed.
