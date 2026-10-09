# Static RE runtime maintenance

Use these commands for runtime verification, installation and client discovery.
They use synthetic inputs and issue no model prompt. The repository's Python
tools remain stdlib-only; PyGhidra, rabbitizer and MCP packages live in the
separate installed environment.

## Verify

```sh
python3 tools/re_mcp.py status
python3 tools/re_doctor.py --discovery
python3 tools/re_client_discovery.py --output .scratch/native-discovery
```

Status reports observed health, schema authentication and installed JAR/patch
identity, alongside configured policy. It fails when an observation fails; it
does not label script policy as behaviorally verified.

The doctor starts a separate managed backend on an available loopback port and
uses a temporary synthetic project below `Documents/RE-Toolchain/doctor`.
It checks decompilation, required selectors, script rejection, create/open and
archive input/output boundaries, authentication, EE P-code and rabbitizer.
Projects are outside dot-prefixed directories; the utility Python runs with
`-I` so the repository's `tools/ghidra` directory cannot shadow Java packages.
Receipts/logs are ignored under `.scratch/re-doctor`; temporary token copies
are removed after the owned backend is stopped. The current analysis project
is not opened, closed or saved by this doctor.

`--discovery` initializes the three shared stdio launchers separately. Native
discovery uses Claude's existing entries and isolated Codex/omp profiles built
from the shared launcher arguments. Those isolated profiles prove native client
compatibility, not the contents of the user's global Codex/omp registrations.
OMP handles `/mcp test` locally and must report `agentInvoked: false`; the literal
unused model placeholder is not a provider credential. No provider environment
or existing auth file is copied into either isolated profile.

## Build a candidate

```sh
python3 tools/re_bootstrap.py
python3 tools/re_bootstrap.py --apply
```

The default command prints a plan. `--apply` checks macOS ARM64, Java 21 and the
installed git/clang/cmake/make/mvn/pkg-config/uv/npx commands. The versioned
`tools/re_install_manifest.json` records distribution digests, source commits,
primary Python package versions and the reviewed compatibility patch. Changes
to those pins require a new doctor receipt. Transitive Python/build dependencies
are resolved by their upstream packages; this is not a bit-identical build claim.

Each run creates a new ignored installation and preserves the previous one.
Downloads are hash-checked; source caches are cloned at the pinned commit.
`--cache PATH` reuses matching downloads/source checkouts, and `--java-home PATH`
selects a Java 21 runtime explicitly. Builds use Ghidra's bundled Gradle wrapper,
extensions under `Ghidra/Extensions`, an isolated settings directory and Python
environment, and explicit install prefixes for both radare2 and r2mcp.

The candidate must pass ccc's tests, the doctor and shared stdio discovery before
it is successful. Build output stays in numbered logs and `result.json` records
success or failure. Failed candidates never replace the active configuration.

## Activate during a maintenance window

`--apply --activate` requests activation after the candidate passes. Activation
refuses to interrupt a running managed backend or replace unrelated utility
wrappers. It saves private `rollback-config.json`, atomically selects the new
machine configuration, registers shared launchers and installs utility wrappers.
Registration failure restores the previous machine configuration. Existing
client sessions may retain their old catalog; verify fresh sessions.

Saving an analysis project and deciding when to close it precede an activation
that would restart its backend. The existing `re_mcp.py stop` command identifies
the owned launcher before stopping its process group. Candidate verification
does not require this activation window.

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
