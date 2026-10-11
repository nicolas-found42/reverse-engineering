# Repository verification and maintenance

Use these commands to verify the repository. They use synthetic inputs and issue
no model prompt. The repository's Python tools remain stdlib-only. The RE runtime
launchers, bootstrap, doctor and client registration were removed (`8b2ce53`); see
[RE-SETUP](../RE-SETUP.md) for the recorded installation and what that removal
leaves to each client's own configuration.

`tools/re_rpc.py` (bounded stdlib JSON-RPC transport) and `tools/re_static_probe.py`
(PyGhidra/EE and rabbitizer probe on generated R5900 bytes) remain as building
blocks; neither is wired to a launcher. `tools/re_install_manifest.json` and
`tools/patches/` are retained pins and patch for the recorded installation, with
no in-repo consumer.

## Repository checks

```sh
python3 tools/validate.py
python3 tools/validate.py --staged
python3 tools/validate.py --revision HEAD
```

All three run the existing IP, hygiene, Ruff and test checks. Snapshots contain
the exact Git file set, including previously tracked ignored files; symlinks,
traversal and `export-ignore` omissions are refused. Snapshot runs use CI's
explicit local-input exclusions. `--quick` omits tests and records that narrower
scope. Full logs and structured results are retained, with bounded console output.
Full corpus/compiler completion remains the separate command in
[RE-SETUP](../RE-SETUP.md#full-local-verification).
