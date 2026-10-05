#!/usr/bin/env python3
"""Compare two exports around one guarded program-wide gp context change.

The EE executable sets gp once (`move gp,a0` in the entry routine, a0 = 0x295d70) and the ELF
.reginfo records the same value. Without a gp value Ghidra prints each gp-relative global as an
offset name (`uGpffff9118`, `&gp0xffffa920`). With the value set, the same operand must show the
absolute address gp+offset. This check keeps the listing unchanged, requires that functions
without gp names keep their pseudocode, that no gp names remain, and that the addresses the new
pseudocode shows match the addresses predicted from the old offsets. No game code is run.
"""
import json
import re
import sys
from pathlib import Path

GP = 0x295D70
GP_NAME = re.compile(r'\b[a-zA-Z]{1,6}Gp([0-9a-f]{8})\b|\bgp0x([0-9a-f]+)\b')
COMMENT = re.compile(r'/\*.*?\*/', re.S)
MISMATCH_LIMIT = 0.05


def predicted_address(offset: int) -> int:
    return (GP + (offset - (1 << 32 if offset >= 1 << 31 else 0))) & 0xFFFFFFFF


def gp_names(text: str) -> list[int]:
    return [int(m[1] or m[2], 16) for m in GP_NAME.finditer(text)]


def _normal(text: str) -> str:
    return ''.join(COMMENT.sub('', text).split())


def _mentions(text: str, address: int) -> bool:
    lowered = text.lower()
    return f'{address:08x}' in lowered or f'0x{address:x}' in lowered


def compare_exports(old: Path, new: Path) -> dict:
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
    before = after = 0
    kept_without_gp = changed_without_gp = 0
    unchanged_bad, still_named, mismatched, resolved = [], [], [], 0
    for entry in sorted(old_fn):
        po, pn = old / 'decompilation/functions' / f'{entry}.c', new / 'decompilation/functions' / f'{entry}.c'
        if not po.exists() or not pn.exists():
            unchanged_bad.append(entry)
            continue
        old_text, new_text = po.read_text(errors='replace'), pn.read_text(errors='replace')
        names, remaining = gp_names(old_text), gp_names(new_text)
        before += len(names)
        after += len(remaining)
        if not names:
            if _normal(old_text) == _normal(new_text):
                kept_without_gp += 1
            else:
                changed_without_gp += 1
                unchanged_bad.append(entry)
            continue
        if remaining:
            still_named.append(entry)
            continue
        wanted = {predicted_address(o) for o in names}
        if all(_mentions(new_text, a) for a in wanted):
            resolved += 1
        else:
            mismatched.append(entry)
    with_gp = resolved + len(mismatched) + len(still_named)
    check('functions without gp names keep identical pseudocode', not unchanged_bad,
          {'identical': kept_without_gp, 'changed': changed_without_gp, 'examples': unchanged_bad[:10]})
    check('no gp-relative names remain', after == 0, {'before': before, 'after': after, 'functions_still_named': still_named[:10]})
    rate = len(mismatched) / with_gp if with_gp else 0.0
    check('resolved addresses match the gp prediction', rate <= MISMATCH_LIMIT and not still_named,
          {'functions_with_gp_names': with_gp, 'all_predicted_addresses_shown': resolved,
           'mismatched': len(mismatched), 'mismatch_rate': rate, 'limit': MISMATCH_LIMIT, 'examples': mismatched[:10]})
    manifest = json.loads((new / 'decompilation/manifest.json').read_text())
    check('new manifest reports every function generated',
          manifest['failed'] == 0 and manifest['generated'] == manifest['inventory_count'],
          {'generated': manifest['generated'], 'failed': manifest['failed']})
    return {'schema_version': 1, 'status': 'pass' if all(c['passed'] for c in checks) else 'fail',
            'gp_value': f'{GP:08x}', 'gp_names_before': before, 'gp_names_after': after,
            'functions_with_gp_names_before': with_gp, 'check_count': len(checks),
            'passed_count': sum(c['passed'] for c in checks), 'checks': checks,
            'scope': 'decompiler context only; no identity, behavior or original-name claim'}


def main() -> int:
    if len(sys.argv) != 4:
        print('usage: gp_context_check.py OLD_EXPORT NEW_EXPORT OUT_JSON', file=sys.stderr)
        return 2
    result = compare_exports(Path(sys.argv[1]), Path(sys.argv[2]))
    Path(sys.argv[3]).write_text(json.dumps(result, indent=1) + '\n')
    print(result['status'], result['passed_count'], '/', result['check_count'])
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
