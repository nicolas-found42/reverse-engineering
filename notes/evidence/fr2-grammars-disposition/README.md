# #31 grammars disposition (incremental, 2026-10-09)

Committed this run: `tools/ui_contracts.py` + `tools/test_ui_contracts.py`
(`4580acdb41f7ecd00df3eb6fe1d2cf8282f95e2e`, green: 8 tests) plus regenerated
`tools/README.md` index (`e46174a7cd0db9717886f44cd63ff38964a3d212`).

Resolve the cited revisions and prove the merge base with:

```sh
git cat-file -t 4580acd
git cat-file -t e46174a
git merge-base --is-ancestor 05a685a HEAD && echo "05a685a is an ancestor of HEAD"
python3 tools/publish_gate.py --body notes/evidence/fr2-grammars-disposition/README.md
```

Run the decoder contract tests with:

```sh
sh tools/check.sh test_ui_contracts
```

Reproduce the corpus UI measurements (45/45 parse, 32 distinct tags,
6-deep maximum block nesting, balanced everywhere) on the pinned PAL corpus
(`corpus_id`
`e69a2afbd6db606d166e40bae32c436691e134722ad153200859961a5f517dab`)
with:

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "tools")
from pathlib import Path
from corpus_binding import Baseline
from ui_contracts import parse_ui_script
entries = Baseline(Path("games/ford-racing-2")).entries(".ui;1")
tags, depth, failures = set(), 0, []
for e in entries:
    try:
        parsed = parse_ui_script(e.load())
    except Exception as exc:
        failures.append(str(exc))
        continue
    tags |= set(parsed.tags) | {rec.tag for rec in parsed.records}
    for b in parsed.blocks:
        depth = max(depth, b.depth)
print("ui files parsed:", len(entries) - len(failures), "/", len(entries))
print("distinct tags:", len(tags), "max block depth:", depth)
PY
```

## Catalog status

- Family catalog remains extension-only (archive traversal), per Impl31Grammars survey.
- DONE: configuration grammar (16-file PAL `.cfg` set, prior work).
- DONE NOW: UI script grammar — `:DIRECTIVE` grammar shared with ASCII text family;
  6-deep maximum block nesting, balanced everywhere; 45/45 corpus `.ui` files
  parse with 32 distinct tags (measured by the commands above; consumer tag
  coverage stays unresolved until a loader binds the tags). Bounded static
  decoder only; runtime loading/selection/rendering unresolved.
- INCOMPLETE: text/data (`.dat`), audio playback, geometry-body, PTG-body,
  texture palette/mip, and other unclassified families. Each lacks a bounded
  decoder + consumer contract and blocks completion (incomplete, not pass).

## Falsifiers for the remaining families

- A family is complete only with: supported profile + consumer contract bound to
  concrete consumer/reference evidence + corpus profile, or a measured
  opaque/passthrough case with documented consumer behavior.
- Counter-evidence that reopens a DONE family: a corpus file the decoder rejects,
  a consumer tag/path with no pinned code anchor, or contradictory/silent sources
  treated as supported.

No corpus bytes committed. Remaining families explicitly deferred to a later run.
