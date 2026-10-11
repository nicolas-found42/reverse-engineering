# Local static RE setup

The repository no longer ships RE launchers, a bootstrap, a doctor or client
registration (removed in `8b2ce53`; their last revision is `fcbf938`). Install the
analysis tools and register MCP servers with each client's own configuration,
outside this repository. Repository verification is in the
[maintenance workflow](agents/re-setup-maintenance.md).

## Recorded installation (2026-10-08)

This is a historical record of the machine this evidence was produced on, not a
procedure the repository can reproduce. It used Ghidra 12.1.4, EE:Reloaded
v2.1.38, PyGhidra 3.1.0, rabbitizer 1.16.2, objdiff-cli 3.8.2, ccc/stdump and
radare2 6.2.4 with r2mcp. Ghidra native components were built for Apple Silicon
using Java 21. The [validation receipt](../notes/evidence/fr2-re-setup/README.md)
records the version/hash observations and the synthetic analysis and authority
rejection controls, separately from tool discovery. Rabbitizer is a library, not a
CLI; use a Python interpreter that has it installed.

The Ghidra MCP bridge was bethington v6.0.0, rebuilt against Ghidra 12.1.4 with
the local patch below. The recorded configuration served the bridge on loopback
only with a local token, kept file operations inside the local Documents
directory, required program selectors and disabled arbitrary MCP scripts. Those
controls were enforced by the removed launchers; a new client registration must
re-establish and re-test them. Static database-editing tools remain available in
that bridge, so it is not a read-only configuration. r2mcp ran over stdio with
read-only `-R`, sandbox `-s` and `-n -N`; the read-only flag limits the advertised
surface and the sandbox is the separate process/filesystem restriction. Dynamic
PCSX2/game integration is outside this setup.

Existing agent sessions can retain their original tool catalog; fresh sessions
read updated configuration. Tool discovery does not itself prove that an analysis
call succeeded. Manual spot checks for the installed utilities:

```sh
objdiff-cli --version
stdump --help
r2 -v
rea doctor --provider ghidra
```

REA's scoped `doctor --provider ghidra` passed. Its audit-wide doctor reported
missing optional proprietary engines, and running `rea setup` can overwrite a
shared client registration.

## Local bridge compatibility patch

[The Apache-2.0 patch](../tools/patches/README.md) applies file-root resolution to
GhidraMCP 6.0.0's headless project-open and archive-restore paths. The upstream
source checkout is preserved; the patched extension was built in an ignored
source copy. No in-repo launcher pins the patch or the installed JAR any more, so
verify the installed extension against the patch yourself. Rebuild and revalidate
when changing the host version or patch.

## Reproduction and rollback

Official packages: [Ghidra 12.1.4](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build),
[EE v2.1.38](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/releases/tag/v2.1.38),
[objdiff v3.8.2](https://github.com/encounter/objdiff/releases/tag/v3.8.2),
[rabbitizer 1.16.2](https://pypi.org/project/rabbitizer/1.16.2/),
[PyGhidra 3.1.0](https://pypi.org/project/pyghidra/3.1.0/),
[ccc](https://github.com/chaoticgd/ccc), and
[r2mcp](https://github.com/radareorg/radare2-mcp).
ccc includes a GPL/LGPL GNU demangler alongside MIT/BSD components; do not label
the entire built utility MIT. Source checkout commits are recorded locally.

To roll back, select the previously validated installation in the client's own
configuration. Rebuild the MCP Java extension against the selected Ghidra host;
its extension properties must match that version. Revalidate authentication and
synthetic analysis before switching client entries. Preserve existing projects and
unpublished analysis. The original Ghidra 12.1.3 distribution was retained for
rollback.

## Full local verification

The push hook and CI run corpus-free IP, decision/evidence/index/link/report
checks. Full reconstruction verification is a separate local command using the
existing input paths on this machine:

```sh
python3 tools/completion.py games/ford-racing-2 \
  --assembler .scratch/mesh/codex-root/binutils-dvp-build/gas/as-new \
  --objdump .scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump \
  --compiler-tools /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output .scratch/full-completion
```

The aggregate uses independent fresh child receipts. Exit 2 means incomplete,
not success; it must not be used as an unconditional passing pre-push requirement.
This setup's checks do not establish full reconstruction or fresh compiler-match
credit. The [progress report](../progress/README.md) states its narrower authority.
