# Scoped linker claim verification

`jev-verification.json` retains the original judgment. Four claims were verified,
none contradicted or unsupported. The control/test claim requires review:
`supports=0.74`, `contradicts=0.25`, `says_nothing=0.01`, confidence `0.62`.
It was not retried with unchanged wording.

Direct deterministic inspection of `controls.json` and each raw child receipt
finds this exact map: positive exit 0; displaced_text, incorrect_alignment,
incorrect_nobits_size, incorrect_entry, incorrect_flags, wrong_relocation,
wrong_gnu_object_tag and wrong_gnu_carry exit 1; missing_provenance exit 2.
Each raw child's status agrees with its recorded exit. `checks.log` literally
contains `Ran 17 tests`, `OK`, `exit=0`, and Pyright's `0 errors, 0 warnings,
0 informations` with exit 0. This evidence addresses the judged uncertainty;
independent integration review should inspect those receipts and the log.

Reproduce the rule audit without rerunning the judgment:

```sh
python3 - <<'PY'
import json
from pathlib import Path
root = Path('notes/evidence/fr2-linker-layout-continuation')
rows = json.loads((root / 'controls.json').read_text())['details']['controls']
expected = {'positive': 0, 'displaced_text': 1, 'incorrect_alignment': 1,
    'incorrect_nobits_size': 1, 'incorrect_entry': 1, 'incorrect_flags': 1,
    'wrong_relocation': 1, 'wrong_gnu_object_tag': 1, 'wrong_gnu_carry': 1,
    'missing_provenance': 2}
assert {row['control']: row['exit'] for row in rows} == expected
for row in rows:
    child = json.loads(Path(row['receipt']).read_text())
    assert child['status'] == {0: 'pass', 1: 'fail', 2: 'incomplete'}[row['exit']]
print('expected control verdicts verified')
print((root / 'checks.log').read_text())
PY
```

No gate here claims full AC06, issue #9 or issue #5 completion. Whole-suite,
final-diff gate and independent Standards/Spec review remain integration work.
