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

### Pre-push snapshot isolation

The normal `tools/hooks/pre-push` hook resolves the pushing worktree, then runs
`tools/pre_push.py` to validate introduced commits. Git reads use the explicit
source path with `git -C`; temporary snapshot initialization, indexing and
IP/hygiene validation run with every inherited `GIT_*` environment override
removed. This includes repository/worktree/common-directory, index, object and
alternate-object paths, and environment-supplied Git configuration. Other
environment variables and ordinary on-disk Git configuration remain available.
The snapshot's Git subprocesses discover its own repository from its path.

```sh
tools/check.sh test_pre_push
```

The controls use disposable synthetic repositories and local bare remotes.
Direct `materialize`/commit-selection tests inject linked-worktree and unrelated
repository overrides. Separate real `git push` tests execute the normal hook
from both primary and linked worktrees, accept a valid snapshot, and reject a
forbidden tracked payload, a stale hygiene index, or a missing required checker.
They compare source configuration, both indexes, refs, file bytes/modes and Git
status before and after. A POSIX process-group interruption during a synthetic
waiting validator tests cancellation of a real linked-worktree push. These are
local hook tests; direct `validate.py` success alone does not prove a hook ran,
and these controls make no claim about a hosted remote or other platforms.

The IP and hygiene checks still run on the committed snapshot, including tracked
ignored files. This environment boundary does not change corpus/compiler gates
or the separately tracked candidate runtime and credential lifecycle.
