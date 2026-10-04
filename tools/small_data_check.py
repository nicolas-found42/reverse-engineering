#!/usr/bin/env python3
"""Compare two exports around one guarded small-data typing transaction.

The transaction types globals and may mark literal-pool items constant. The listing must not change. Functions that never
touch a planned address must keep their pseudocode. When pool entries are marked constant, nearly all pool address tokens must vanish
from the pseudocode, because the decompiler then shows the stored value; a renamed global is not a constant. No game code is run.
"""
import json
import re
import sys
from pathlib import Path

ADDRESS_TOKEN = re.compile(r'(?<![0-9a-f])([0-9a-f]{8})(?![0-9a-f])')
COMMENT = re.compile(r'/\*.*?\*/', re.S)
REMAINING_LIMIT = 0.05


def pool_tokens(text: str, low: int, high: int) -> int:
    """Count 8-digit hex address tokens in the pool range, whatever name prefix the decompiler gives them."""
    return sum(low <= int(m[1], 16) <= high for m in ADDRESS_TOKEN.finditer(COMMENT.sub('', text).lower()))


def _names_planned_address(text: str, spans: list[tuple[int, int]]) -> bool:
    """True when the text has an 8-digit hex token inside any planned address span."""
    return any(low <= int(m[1], 16) < high for m in ADDRESS_TOKEN.finditer(text.lower()) for low, high in spans)


def _normal(text: str) -> str:
    return ''.join(COMMENT.sub('', text).split())


def compare_exports(plan: dict, old: Path, new: Path) -> dict:
    old, new = Path(old), Path(new)
    old_inv = json.loads((old / 'inventory.json').read_text())
    new_inv = json.loads((new / 'inventory.json').read_text())
    checks = []

    def check(name, ok, detail=None):
        checks.append({'check': name, 'passed': bool(ok), 'detail': detail})
    old_fn = {f['entry']: f for f in old_inv['functions']}
    new_fn = {f['entry']: f for f in new_inv['functions']}
    check('same function entries', set(old_fn) == set(new_fn), {'old': len(old_fn), 'new': len(new_fn)})
    drift = [e for e in old_fn if e in new_fn and any(old_fn[e].get(k) != new_fn[e].get(k)
                                                      for k in ('name', 'size', 'blocks', 'instructions'))]
    check('every function keeps size, blocks and instructions', not drift, drift[:10])
    touching = {e for entry in plan['entries'] for e in entry['functions']}
    spans = [(int(e['address'], 16), int(e['address'], 16) + e['size']) for e in plan['entries']]
    pool = plan.get('constant_pool')
    pools = [(int(pool['start'], 16), int(pool['end'], 16))] if pool else []
    before = after = 0
    kept = changed_touching = unlisted_touching = 0
    broken = []
    for entry in sorted(old_fn):
        po, pn = old / 'decompilation/functions' / f'{entry}.c', new / 'decompilation/functions' / f'{entry}.c'
        if not po.exists() or not pn.exists():
            broken.append(entry)
            continue
        old_text, new_text = po.read_text(errors='replace'), pn.read_text(errors='replace')
        for low, high in pools:
            before += pool_tokens(old_text, low, high)
            after += pool_tokens(new_text, low, high)
        same = _normal(old_text) == _normal(new_text)
        if entry in touching:
            changed_touching += not same
        elif same:
            kept += 1
        elif _names_planned_address(old_text, spans):
            unlisted_touching += 1
        else:
            broken.append(entry)
    check('functions that touch no planned address keep identical pseudocode', not broken,
          {'identical': kept, 'changed_or_missing': len(broken), 'changed_but_naming_a_planned_address': unlisted_touching,
           'examples': broken[:10]})
    rate = after / before if before else 0.0
    check('literal-pool reads become numeric constants', not pools or (before > 0 and rate <= REMAINING_LIMIT),
          {'before': before, 'after': after, 'remaining_rate': rate, 'limit': REMAINING_LIMIT})
    manifest = json.loads((new / 'decompilation/manifest.json').read_text())
    check('new manifest reports every function generated',
          manifest['failed'] == 0 and manifest['generated'] == manifest['inventory_count'],
          {'generated': manifest['generated'], 'failed': manifest['failed']})
    return {'schema_version': 1, 'status': 'pass' if all(c['passed'] for c in checks) else 'fail',
            'plan_entries': len(plan['entries']), 'functions_touching_planned_addresses': len(touching),
            'touching_functions_changed': changed_touching, 'unlisted_functions_naming_a_planned_address': unlisted_touching, 'pool_tokens_before': before, 'pool_tokens_after': after,
            'check_count': len(checks), 'passed_count': sum(c['passed'] for c in checks), 'checks': checks,
            'scope': 'data types and one memory flag in the project copy; no original name, type or behavior claim'}


def main() -> int:
    if len(sys.argv) != 5:
        print('usage: small_data_check.py PLAN OLD_EXPORT NEW_EXPORT OUT_JSON', file=sys.stderr)
        return 2
    result = compare_exports(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]), Path(sys.argv[3]))
    Path(sys.argv[4]).write_text(json.dumps(result, indent=1) + '\n')
    print(result['status'], result['passed_count'], '/', result['check_count'])
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
