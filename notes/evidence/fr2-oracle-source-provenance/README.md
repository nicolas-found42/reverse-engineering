# Oracle dependency source inventory continuation

This static inventory resolves a bounded part of #22; it does not qualify the
runtime required by AC25/AC26 or complete dependency acceptance for #5.
[The retained receipt](source-inventory.json) is a fresh execution of
`tools/oracle_dependency_sources.py` and passes its inventory scope. It assigns
zero game matching credit and explicitly retains `issue22_status: incomplete`.
No emulator or guest was launched.

The installed executable and four declared Qt/docking dylibs have the same
SHA-256 identities as their members of the official PCSX2 v2.6.3 macOS Qt
release. This binds these five installed members to that release, not every
transitive component or an independently reproduced build. The pinned SDK
source SPDX records 22,684 files; all 22,684 SHA1 records match the Qt Git
checkout at `90b845d15ffb97693dba527385db83510ebd121a` (v6.10.1).

The downloadable source archive initially left Git metadata absent and changed
`.tag` through export substitution. The actual Git checkout resolves those
records, including the literal `$Format:%H$` file. Archive/export comparison is
not used to silently omit records. The checker rejects empty, duplicate,
malformed, escaping and changed source records; missing records remain
incomplete. Available mismatches take precedence over unrelated missing
prerequisites. Public CLI controls exercise missing and changed inputs and retain
immutable receipts. A combined source-mismatch/missing-release regression
checks that independent branches cannot suppress each other's contradictions.

Primary upstream material retained locally:

- [PCSX2 v2.6.3 release](https://github.com/PCSX2/pcsx2/releases/tag/v2.6.3).
- [PCSX2 dependency recipe at the release commit](https://github.com/PCSX2/pcsx2/blob/bc8151d2a46d4aba039ea5580afbfc7bfcf6d730/.github/workflows/scripts/macos/build-dependencies.sh).
- [Qt 6.10.1 source archive](https://download.qt.io/archive/qt/6.10/6.10.1/submodules/qtbase-everywhere-src-6.10.1.tar.xz).
- [Qt source tag](https://github.com/qt/qtbase/tree/v6.10.1).
- [KDDockWidgets v2.4.0](https://github.com/KDAB/KDDockWidgets/releases/tag/v2.4.0).

Archive/recipe, installed member and SDK identities are in the receipt and fixed
checker profile. Downloads, full source, SDK files and binaries remain local.
The raw receipt is retained at
`.scratch/continuation-oracle-provenance/source-audit-reviewed/20261008T213957Z-ae6278e562bd4cf68c6564264ca4606a/result.json`.

Reproduce with the retained local inputs, into a new output directory:

```sh
python3 tools/oracle_dependency_sources.py \
  .scratch/continuation-oracle-provenance \
  /Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/oracle/qt-sdk \
  /Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/oracle/qtbase.7z \
  --output .scratch/oracle-source-inventory-new
```

Still required: complete installed dependency closure and component notices,
exact dependency build provenance, and separate strict window/display/audio/
focus lifecycle qualification. Upstream source availability and inventory
agreement do not establish those claims. The aggregate completion command
retains AC25/AC26 incomplete and does not consume this independent inventory as
behavioral evidence.
