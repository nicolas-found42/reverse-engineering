# Modern Python tooling for a stdlib-only PS2 reverse-engineering repository

*Survey date: 2026-10-08. Written from a background research pass; every tool-behavior claim cites its primary source.*

## Scope and method

This survey compares uv, Ruff, ty, and pytest configuration with this repository's stdlib-only and unittest-canonical constraints. Tool behavior below is grounded in each project's official documentation or source repository. GitHub configuration examples, curated lists, Q&A, Reddit, and YouTube are reported only as practice or opinion signals; they are not treated as tool specifications. This follows the neighboring surveys' separation of short findings, source-backed claims, and source/access limitations ([tooling survey](ps2-tooling-and-techniques-survey-2026-10.md), [public-Q&A survey](ps2-forum-qa-reverse-engineering-practice.md)).

## Executive recommendation

Keep `tools/check.sh` and `tools/run_tests.py` as the required test path: the script selects Python 3.10 or newer and invokes the custom `unittest` runner, while CI calls that script on Python 3.12 ([check.sh](../../tools/check.sh), [run_tests.py](../../tools/run_tests.py), [CI workflow](../../.github/workflows/ci.yml)). The project metadata has an empty dependency list and explicitly describes the tooling as stdlib-only; ADR-0003 requires open-source tools and dependencies ([pyproject.toml](../../pyproject.toml), [ADR-0003](../../docs/adr/0003-open-source-only.md)).

Keep the narrow Ruff rule selection. Use uv only as an optional way to invoke isolated command-line tools, not as a new dependency-management workflow for this repository. Keep pytest optional: it can run existing `unittest.TestCase` tests, but the project runner has custom skip behavior that should remain authoritative ([pytest unittest integration](https://docs.pytest.org/en/stable/how-to/unittest.html), [run_tests.py](../../tools/run_tests.py)). Treat ty as an optional local type-checking experiment while it remains beta and before its diagnostics have been reviewed ([ty version policy](https://github.com/astral-sh/ty#version-policy)).

## Current repository state

- `pyproject.toml` declares `requires-python = ">=3.10"`, `dependencies = []`, a pytest configuration scoped to `tools`, Ruff targeting Python 3.10 with an explicit narrow selection, and a ty environment table ([pyproject.toml](../../pyproject.toml)).
- `tools/check.sh` searches for Python 3.10 or newer and delegates to `tools/run_tests.py`; the runner uses `unittest.TestLoader`, exposes the repository root and `tools/` on `sys.path`, discovers `test_*.py`, and retains special whole-suite behavior for missing optional imports and CI-only local-input skips ([check.sh](../../tools/check.sh), [run_tests.py](../../tools/run_tests.py)).
- CI has a dedicated IP-rails job and a test job; the latter installs Python 3.12 and runs `tools/check.sh`. It does not install or invoke uv, Ruff, ty, or pytest ([CI workflow](../../.github/workflows/ci.yml)).
- The existing pytest settings are configuration only; pytest is not listed in project dependencies and is not the runner used by CI ([pyproject.toml](../../pyproject.toml), [CI workflow](../../.github/workflows/ci.yml)).
- The ty key lives under `[tool.ty.environment]`, which is the documented location; if omitted, ty infers its Python version from the minimum in `project.requires-python` ([ty configuration reference](https://docs.astral.sh/ty/reference/configuration/#python-version)).

## Tool findings

### uv

- uv manages Python projects, dependencies, lockfiles, project environments, and command execution. Project commands such as `uv run` keep the lockfile and environment synchronized; the project guide describes creating `.venv` and `uv.lock` when a project command is first run ([uv projects guide](https://docs.astral.sh/uv/guides/projects/), [uv lock and sync](https://docs.astral.sh/uv/concepts/projects/sync/)).
- `uv add` edits dependency metadata. uv distinguishes published project dependencies from local development `dependency-groups`; the `dev` group is synced by default ([uv dependency guidance](https://docs.astral.sh/uv/concepts/projects/dependencies/), [uv lock and sync](https://docs.astral.sh/uv/concepts/projects/sync/)). That is useful for normal packaged projects, but adding Ruff, ty, or pytest to a development group would introduce third-party packages into this repository's otherwise empty dependency set.
- `uvx` / `uv tool run` invokes a tool in an isolated temporary environment. uv's docs recommend `uv run` instead when a tool must import an installed project; they note that a flat project which does not need installation can use `uvx` ([uv tools guide](https://docs.astral.sh/uv/guides/tools/)). **Recommendation:** if contributors choose to use uv locally, `uvx ruff check tools` avoids adding Ruff to project metadata. `uvx ty check tools` can be tried as an advisory check, but local import resolution and diagnostics must be reviewed before treating it as a gate ([uv tools guide](https://docs.astral.sh/uv/guides/tools/), [ty type-checking guide](https://docs.astral.sh/ty/type-checking/)).
- Do not make `uv run` or a new `uv.lock` part of the required test path unless the project intentionally adopts uv-managed environments. The existing shell script already selects Python and the CI workflow invokes it directly ([check.sh](../../tools/check.sh), [CI workflow](../../.github/workflows/ci.yml)); uv's automatic project lock/sync behavior is documented above ([uv lock and sync](https://docs.astral.sh/uv/concepts/projects/sync/)).
- uv's upstream repository supplies Apache-2.0 and MIT license texts, consistent with the repository's open-source requirement ([uv Apache license](https://github.com/astral-sh/uv/blob/main/LICENSE-APACHE), [uv MIT license](https://github.com/astral-sh/uv/blob/main/LICENSE-MIT), [ADR-0003](../../docs/adr/0003-open-source-only.md)).

### Ruff

- Ruff supports configuration in `pyproject.toml` and provides both `ruff check` and `ruff format` ([configuration](https://docs.astral.sh/ruff/configuration/), [linter](https://docs.astral.sh/ruff/linter/), [formatter](https://docs.astral.sh/ruff/formatter/)).
- Ruff explicitly recommends an explicit `lint.select`, starting with a small set and expanding by rule family; it advises using `ALL` with discretion because upgrades can enable new rules ([Ruff rule selection guidance](https://docs.astral.sh/ruff/linter/#rule-selection)). The repository has a narrow, explicit selection and a comment to expand deliberately, so keep it instead of importing a broad template ([pyproject.toml](../../pyproject.toml)).
- `ruff format` writes formatted code by default; `ruff format --check` checks without writing ([Ruff formatter](https://docs.astral.sh/ruff/formatter/#ruff-format)). Do not run an unreviewed whole-tree formatter or `ruff check --fix` without diff review. If formatter adoption is separately approved, first inspect the diff and use `--check` for a non-writing gate ([Ruff formatter](https://docs.astral.sh/ruff/formatter/#ruff-format)).
- Ruff's upstream license is MIT ([Ruff LICENSE](https://github.com/astral-sh/ruff/blob/main/LICENSE)).

### ty

- ty is an Astral type checker and language server; its upstream README currently identifies it as beta, uses `0.0.x` versioning, and warns that it has no stable API and may break between versions ([ty README/version policy](https://github.com/astral-sh/ty#version-policy)). Its README says Python 3.10 and later are officially supported ([ty README](https://github.com/astral-sh/ty#which-python-versions-does-ty-support)).
- If `python-version` is omitted, ty first looks at `project.requires-python` and uses its minimum version. If an explicit value is needed, the documented TOML location is `[tool.ty.environment]` ([ty configuration reference](https://docs.astral.sh/ty/reference/configuration/#python-version)).
- ty supports rule severities and line-level, rule-specific suppression comments, including for false positives; prefer a narrow, named suppression over globally silencing rules ([ty rule configuration](https://docs.astral.sh/ty/reference/configuration/#rules), [ty suppression guide](https://docs.astral.sh/ty/suppression/)).
- **Recommendation:** do not gate CI on an unpinned beta checker. First run it locally against `tools/`, review the initial findings (current baseline: 173 diagnostics, unreviewed), and only consider an exact version pin and CI gate after the project explicitly decides to adopt it ([ty version policy](https://github.com/astral-sh/ty#version-policy), [ty file selection](https://docs.astral.sh/ty/type-checking/#file-selection)). ty's upstream license is MIT ([ty LICENSE](https://github.com/astral-sh/ty/blob/main/LICENSE)).

### pytest

- pytest is a third-party package: its official getting-started guide instructs users to install it with `pip install -U pytest` ([pytest installation guide](https://docs.pytest.org/en/stable/getting-started.html#install-pytest)). Python's `unittest` is part of the standard library ([Python `unittest` docs](https://docs.python.org/3/library/unittest.html)).
- pytest collects `unittest.TestCase` subclasses and their test methods out of the box, so a pytest run can be an optional alternate runner without rewriting those tests. pytest documents that the `load_tests` protocol is unsupported, and that fixture injection, parametrization, and custom hooks do not work inside `unittest.TestCase` classes ([pytest unittest integration](https://docs.pytest.org/en/stable/how-to/unittest.html)).
- pytest's good-practice guide recommends `importlib` import mode for new projects and documents the `pythonpath` setting for adding repository paths ([pytest good practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html), [pytest import mechanisms](https://docs.pytest.org/en/stable/explanation/pythonpath.html), [pythonpath reference](https://docs.pytest.org/en/stable/reference/reference.html#confval-pythonpath)). The repo configures `testpaths = ["tools"]`, test file/class/function patterns, `pythonpath = ["tools", "."]`, and `importmode = "importlib"` ([pyproject.toml](../../pyproject.toml)).
- `importlib` mode does not alter `sys.path` to import test modules and avoids requiring unique test-module names, but test modules cannot import one another as helpers; pytest recommends placing reusable helpers outside the tests directory ([pytest import mechanisms](https://docs.pytest.org/en/stable/explanation/pythonpath.html#import-modes)). Keep the current paths aligned with the repository's `tools/` layout instead of copying a `src/` example.
- pytest can coexist with unittest tests, but replacing `tools/check.sh` with pytest would not automatically reproduce this repository's custom optional-import and CI-local-input skipping policy ([pytest unittest integration](https://docs.pytest.org/en/stable/how-to/unittest.html), [run_tests.py](../../tools/run_tests.py)). **[INFERENCE]** Keep pytest as an optional developer convenience, not the canonical CI runner, unless the custom skip semantics are explicitly recreated and reviewed. pytest is MIT-licensed ([pytest LICENSE](https://github.com/pytest-dev/pytest/blob/main/LICENSE)).
- Measured with this repository's adopted configuration (2026-10-08): `pytest tools/ --import-mode=importlib` collects 761 tests with no errors and runs **754 passed, 7 skipped, 1,203 subtests passed in ~116 s**; `tools/conftest.py` mirrors `run_tests.py`'s optional-`typesafe_sdk` skip at collection time. The canonical `PYTHON=... tools/check.sh` run on the same tree reports OK (735 unittest tests, the documented local-inputs skip); both runners agree green on the same tree.

## GitHub and curated-list practice signals

- pytest's own GitHub suite exercises `unittest.TestCase` cases through pytest's test harness, which is a concrete example of compatibility testing ([pytest `testing/test_unittest.py`](https://github.com/pytest-dev/pytest/blob/main/testing/test_unittest.py)).
- GitHub projects configure `pythonpath` according to their layout: pytest-django uses `"."` and `tests`, while Apache Airflow's mypy subproject uses `"src"` and `tests` ([pytest-django `pyproject.toml`](https://github.com/pytest-dev/pytest-django/blob/main/pyproject.toml), [Airflow `pyproject.toml`](https://github.com/apache/airflow/blob/main/dev/mypy/pyproject.toml)). These are examples, not values to copy; this repository's current `tools` and root paths match its flat module imports ([run_tests.py](../../tools/run_tests.py), [pyproject.toml](../../pyproject.toml)).
- Curated lists place Ruff and ty in `vinta/awesome-python`'s Code Analysis section, uv/Ruff/ty in `ritwiktiwari/awesome-python-rs`, and both pytest and standard-library unittest in `cleder/awesome-python-testing` ([awesome-python](https://github.com/vinta/awesome-python), [awesome-python-rs](https://github.com/ritwiktiwari/awesome-python-rs), [awesome-python-testing](https://github.com/cleder/awesome-python-testing)). These are discovery/curation signals, not evidence that all tools fit this repository.

## Community signals and source limits

- Stack Overflow's `unittest vs pytest` discussion contains competing opinions on unittest classes and pytest fixtures; treat it as an example of developer preference, not a current recommendation ([Stack Overflow question](https://stackoverflow.com/questions/27954702/unittest-vs-pytest)). A Ruff setup question illustrates confusion around which lint rules are enabled by default; the current Ruff docs, not a 2023 answer, are the authority ([Ruff setup Q&A](https://stackoverflow.com/questions/76885582/setting-up-ruff-python-linter), [Ruff rule selection](https://docs.astral.sh/ruff/linter/#rule-selection)).
- ty Q&A includes reports of false positives and requests for line suppression, and a separate question about project-wide checks including scratch/untracked files ([ty suppression Q&A](https://stackoverflow.com/questions/79628526/how-to-make-ty-ignore-a-single-line-in-a-source-file), [untracked-file Q&A](https://stackoverflow.com/questions/79873711/exclude-untracked-files-from-ty-check)). These are individual adoption experiences; use ty's official suppression and file-selection documentation for any response ([ty suppression guide](https://docs.astral.sh/ty/suppression/), [ty type checking](https://docs.astral.sh/ty/type-checking/)).
- Search-index snippets surfaced an r/Python comparison thread asking about Ruff+ty versus Ruff+Pyrefly and another thread whose snippet reports a user's false-positive concern ([comparison thread](https://www.reddit.com/r/Python/comments/1uf2eoz/ruff_ty_vs_ruff_pyrefly_which_type_checking_stack/), [false-positive thread](https://www.reddit.com/r/Python/comments/1rrz3kx/what_hidden_gem_python_modules_do_you_use_and_why/)). Reddit page extraction returned a bot/human-verification page, so these snippets are not a full comment review and should not be generalized to the subreddit.
- Searches targeting Python testing/tooling in r/ReverseEngineering did not produce a usable thread about pytest/Ruff/ty adoption; Reddit's direct search extraction also returned only a gated shell ([scoped Reddit search](https://www.reddit.com/r/ReverseEngineering/search/?q=python%20pytest&restrict_sr=1)). This is a search limitation, not evidence that the community has no such practices.
- The YouTube video by Corey Schafer has auto-generated captions for a uv workflow and covers project setup, lock/sync, `uv run`, and isolated `uvx` tool use ([video](https://www.youtube.com/watch?v=AMdG7IjgSPM)). Talk Python's episode with Astral's Charlie Marsh and Carl Meyer has a transcript/manual subtitles and provides an interview-era account of uv, Ruff, and ty ([video](https://www.youtube.com/watch?v=XVwpL_cAvrw), [transcript](https://talkpython.fm/episodes/show/506/ty-astrals-new-type-checker-formerly-red-knot.vtt)). A 2026 workflow tutorial transcript advocates uv, Ruff, pytest, and development dependency groups, but its auto-captions include the incorrect claim that pytest is in the standard library; the official pytest installation page disproves that ([video/transcript](https://www.youtube.com/watch?v=ShjFPBDFjZ8), [pytest install docs](https://docs.pytest.org/en/stable/getting-started.html#install-pytest)). Treat videos as creator practice signals, not authoritative setup instructions.

## Recommended configuration

The following retains the project metadata and tool settings as adopted on 2026-10-08; it adds no third-party dependencies and keeps pytest as an optional runner ([pyproject.toml](../../pyproject.toml), [ADR-0003](../../docs/adr/0003-open-source-only.md)).

```toml
[project]
requires-python = ">=3.10"
dependencies = []

[tool.ruff]
target-version = "py310"

[tool.ruff.lint]
select = ["F", "E9"]

[tool.pytest.ini_options]
testpaths = ["tools"]
python_files = ["test_*.py"]
python_classes = ["*Tests", "Test*"]
python_functions = ["test_*"]
pythonpath = ["tools", "."]
addopts = "--import-mode=importlib"

[tool.ty.environment]
python-version = "3.10"
```

`addopts` carries the import-mode flag because pytest 9 accepts no `importmode`/`import_mode` ini key (an unknown ini key is only a warning, silently weakening the config). Importlib mode is load-bearing: with the default prepend mode, pytest cannot collect the two same-basename test modules (`tools/test_argb1555_candidate.py` and `tools/ghidra/experimental/test_argb1555_candidate.py`). `tools/conftest.py` additionally mirrors `run_tests.py`'s optional-dependency skip at collection time via `collect_ignore` for `test_research_jev_battery.py` when `typesafe_sdk` is absent ([pytest import mechanisms](https://docs.pytest.org/en/stable/explanation/pythonpath.html#import-modes), [run_tests.py](../../tools/run_tests.py)).

No `[dependency-groups].dev` or uv project section is needed for the recommended setup: uv development groups install packages, while `uvx` provides optional isolated tool invocations ([uv dependency groups](https://docs.astral.sh/uv/concepts/projects/dependencies/), [uv tools guide](https://docs.astral.sh/uv/guides/tools/)).

## What not to adopt

- Do not replace `tools/check.sh`/unittest with pytest or rewrite tests to pytest style: pytest already runs `TestCase`, while this repository's runner has behavior not provided by simply changing the command ([run_tests.py](../../tools/run_tests.py), [pytest unittest integration](https://docs.pytest.org/en/stable/how-to/unittest.html)).
- Do not add pytest, Ruff, or ty to `[project.dependencies]` or a development group under the current stdlib-only constraint; invoke optional CLI tools outside the project dependency graph if desired ([pyproject.toml](../../pyproject.toml), [ADR-0003](../../docs/adr/0003-open-source-only.md), [uv dependency groups](https://docs.astral.sh/uv/concepts/projects/dependencies/)).
- Do not turn `uv run` into a required command merely to run checks; uv project commands manage a lock and environment, unlike the current direct Python selector ([uv projects guide](https://docs.astral.sh/uv/guides/projects/), [check.sh](../../tools/check.sh)).
- Do not enable Ruff `ALL`, widen the rule set wholesale, auto-fix, or format the whole repository without a separate baseline/diff review; Ruff recommends staged rule selection and documents that formatting writes files by default ([Ruff linter](https://docs.astral.sh/ruff/linter/#rule-selection), [Ruff formatter](https://docs.astral.sh/ruff/formatter/#ruff-format), [pyproject.toml](../../pyproject.toml)).
- Do not require an unpinned ty beta check in CI or silence broad rule families to hide its first-pass findings; ty's version policy warns of breaking changes, and its docs support targeted suppression ([ty version policy](https://github.com/astral-sh/ty#version-policy), [ty suppression guide](https://docs.astral.sh/ty/suppression/)).
- Do not copy generic tutorials' dependency groups, test plugins, pre-commit hooks, or pytest workflow wholesale: they are not necessary to satisfy the current canonical test path, and some tutorial transcript details are inaccurate ([uv dependency groups](https://docs.astral.sh/uv/concepts/projects/dependencies/), [2026 workflow video](https://www.youtube.com/watch?v=ShjFPBDFjZ8), [CI workflow](../../.github/workflows/ci.yml)).

## Source/access notes

Official docs and first-party project repositories were used for behavior, supported settings, and licensing. Search snippets were used only to locate community discussions; Reddit's direct content was gated, and some YouTube captions were automatic. No claim about Reddit community-wide practice is made from those snippets.
