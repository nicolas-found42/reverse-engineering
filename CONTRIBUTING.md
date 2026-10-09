# Contributing

This repository contains tools, evidence measurements and hand-written
reconstruction for Ford Racing 2 PAL, serial SLES-517.05. Start with the
[glossary](GLOSSARY.md), [decisions](docs/README.md), [tool index](tools/README.md)
and [evidence index](notes/evidence/INDEX.md).

Use Python 3.10 or newer for repository tools. They use the standard library.
The optional RE utilities and MCP runtimes are installed separately; see
[local RE setup](docs/RE-SETUP.md). Use only open-source tooling under
[ADR-0003](docs/adr/0003-open-source-only.md).

Use your own legally obtained, unchanged corpus in the ignored `games/` paths.
Validate its identities with the corpus tools; never upload a disc, executable,
extracted asset, SDK object, memory dump or decompiler-generated source. See
[LEGAL](docs/LEGAL.md) for the permitted tracked material. In a first PR, disclose
whether the work used third-party source or leaked/proprietary material; do not
paste that material into the issue or PR.

A source unit is finished only within its measured boundary: record the source
and evidence identities, compile/link with the stated toolchain, run the exact
byte gate and its negative controls, and retain the immutable receipt. A saved
function or approximate match grants no matching credit. The original compiler
remains unresolved; a passing exploratory candidate is a bounded probe.

```sh
tools/install_hooks.sh
python3 tools/repository_hygiene.py generate
python3 tools/validate.py --staged
```

Stage new files before regenerating indexes: the generators index Git's tracked
and staged paths, not ignored or unrelated untracked files. Include the generated
outputs in the same commit. Use the [style guide](docs/STYLE.md) for claims and
reproduction commands. Keep incomplete work explicit in the
[reconstruction/drafts convention](reconstruction/README.md).

`validate.py` runs IP, metadata freshness, Ruff and tests; `--staged` materializes
the exact index with CI's documented local-input exclusions. Without a snapshot
flag it checks the working tree and runs the available local tests. Full output
and JSON counts/skip reasons stay in ignored validation receipts. The runtime
[maintenance commands](docs/agents/re-setup-maintenance.md) and bounded
[review inputs](docs/agents/review-payloads.md) are maintained separately.

The installed pre-push hook checks newly introduced commit snapshots for IP
violations and metadata freshness. It is an opt-in guard rail and `--no-verify`
can bypass it; CI repeats the portable checks. The separate full local command is
[documented here](docs/RE-SETUP.md#full-local-verification) and requires the corpus
and toolchain inputs. Its incomplete result is retained as incomplete.
