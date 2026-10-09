# Local static RE setup

For repeatable runtime checks, candidate builds, activation and native discovery,
use the [maintenance workflow](agents/re-setup-maintenance.md).

The shared launchers are `tools/re_mcp.py` and `tools/re_tool.py`. Ignored
`.scratch/re-setup/config.json` records machine paths and `.scratch/re-setup/ghidra-token`
holds the dedicated local token with mode 0600. Client entries contain only the
Python executable and shared launcher arguments; they do not contain the token
or provider API keys. Unrelated client servers are retained.

The 2026-10-08 installation uses Ghidra 12.1.4, EE:Reloaded v2.1.38, PyGhidra
3.1.0, rabbitizer 1.16.2, objdiff-cli 3.8.2, ccc/stdump and radare2 6.2.4 with
r2mcp. Ghidra native components were built for Apple Silicon using Java 21.
The source builds and version/hash receipts are retained under ignored
`.scratch/setup-2026-10-08/`. Utility wrappers are installed under `~/.local/bin`.
No repository Python dependency was added. Rabbitizer is a library: use the
isolated `re-python` interpreter rather than assuming `uvx rabbitizer` is a CLI.

The Ghidra MCP bridge remains bethington v6.0.0, rebuilt against Ghidra 12.1.4 with the local file-scope patch described below.
All three clients register `ghidra`, `rea` (pinned to 5.0.0), and `radare2` through
shared launchers. Ghidra serves authenticated HTTP only on `127.0.0.1:8090`,
with stdio bridges to the clients. File operations are contained to the local
Documents directory, program selectors are required, and arbitrary MCP scripts
are explicitly disabled. The project-folder scope `/` permits the contents of
an explicitly opened Ghidra project; it does not restrict the project to one
subfolder. Static database-editing tools remain available. This is not an
all-tools read-only Ghidra configuration.

r2mcp uses stdio with read-only `-R`, sandbox `-s`, and `-n -N` to avoid ambient
plugins, startup commands and prompts. Its read-only flag limits the advertised
surface; the sandbox is the separate process/filesystem restriction. Dynamic
PCSX2/game integration is outside this setup. No target is automatically opened
and no login/boot service is installed. The original 12.1.3 distribution is
retained for rollback.

Existing running agent sessions can retain their original tool catalog. Fresh
sessions read the updated configuration; tool discovery does not itself prove
that an analysis call succeeded. The [validation receipt](../notes/evidence/fr2-re-setup/README.md) records synthetic
analysis and authority rejection controls separately from discovery.

```sh
python3 tools/re_mcp.py status
objdiff-cli --version
stdump --help
r2 -v
rea doctor --provider ghidra
```

`tools/configure_re_clients.py` registers the existing local installation. It
uses the native Claude/Codex commands and atomically updates OMP's native MCP
JSON. It does not install runtime packages or create credentials. Ghidra tokens
are passed in child environments, never arguments or tracked files. Keep the
private token and runtime files out of external review payloads.

REA's scoped `doctor --provider ghidra` passes. Its audit-wide doctor still reports
missing optional proprietary engines and labels the shared wrapper registration
as configuration drift because it expects its own direct command. Native client
connections and the actual configured launches are tested independently; running
`rea setup` can overwrite the shared registration.

## Local bridge compatibility patch

[The Apache-2.0 patch](../tools/patches/README.md) applies file-root resolution to
GhidraMCP 6.0.0's headless project-open and archive-restore paths. The upstream
source checkout is preserved; the patched extension was built in an ignored
source copy. The launcher pins the reviewed patch and installed extension JAR,
refusing a missing or replaced runtime identity. Rebuild and revalidate when
changing the host version or patch.

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

Stop only the managed new backend with `python3 tools/re_mcp.py stop`. The path-only
local configuration can select a previously validated installation. Rebuild the
MCP Java extension against the selected Ghidra host; its extension properties
must match that version. Revalidate authentication and synthetic analysis before
switching client entries. Preserve existing projects and unpublished analysis.

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
