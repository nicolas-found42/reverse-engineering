#!/usr/bin/env python3
"""Plan comments and a few renames for IOP module functions from relocation-exact facts.

Each comment lists what the static tables show: import calls (with the pinned SDK candidate name or "unnamed"), role
tags that every matching import adds (a function may have several), printable strings its code points at, the export
slot whose offset is the function entry, and the number of data pointers that name it. A function is renamed only when it
references exactly one string of the form "ERROR: <identifier>" and no other function claims the same name. Nothing here
claims what a function is. No module code is run.
"""
import argparse
import json
import re
from pathlib import Path

from evidence_common import Incomplete, write_result

NAME_TAGS = {
    'rpc_server': {'sceSifRegisterRpc', 'sceSifSetRpcQueue', 'sceSifRpcLoop'},
    'rpc_client': {'sceSifBindRpc', 'sceSifCallRpc'},
    'timer': {'AllocHardTimer', 'SetupHardTimer', 'StartHardTimer', 'SetTimerHandler', 'FreeHardTimer', 'SetAlarm', 'CancelAlarm'},
    'thread_control': {'CreateThread', 'StartThread', 'DeleteThread', 'TerminateThread', 'SleepThread', 'WakeupThread',
                       'ChangeThreadPriority', 'ExitThread', 'DelayThread'},
    'semaphore': {'CreateSema', 'WaitSema', 'SignalSema', 'iSignalSema', 'DeleteSema'},
    'sif_dma': {'sceSifSetDma', 'sceSifDmaStat', 'sceSifInit', 'sceSifInitRpc', 'sceSifCheckInit'},
    'interrupt_guard': {'CpuSuspendIntr', 'CpuResumeIntr'}}
LIBRARY_TAGS = {'usbd': 'usb', 'libsd': 'sound_driver', 'cdvdman': 'cd_driver', 'ioman': 'file_io',
                'sysmem': 'memory', 'sysclib': 'c_library'}
SELF_NAME = re.compile(r'ERROR: ([A-Za-z_][A-Za-z0-9_]*)\n?')


def _tags(imports: list[dict]) -> list[str]:
    names = {i['name'] for i in imports if i['name']}
    tags = [tag for tag, members in NAME_TAGS.items() if names & members]
    tags += sorted({LIBRARY_TAGS[i['library']] for i in imports if i['library'] in LIBRARY_TAGS})
    return tags


def _import_text(item: dict) -> str:
    if not item['name']:
        return f"{item['library']}#{item['index']} (unnamed)"
    if item.get('name_source') == 'module symbol table':
        return f"{item['name']} (read from the module symbol table)"
    return f"{item['name']} (candidate name from pinned SDK table)"


def _comment(function: dict, rename: str | None) -> str:
    lines = ['Static facts from relocation tables and import/export tables; no code was run.']
    if function['imports']:
        shown = ', '.join(_import_text(i) for i in function['imports'])
        lines.append('Calls imports: ' + shown + '.')
        tags = _tags(function['imports'])
        if tags:
            lines.append('Role tags from imports (all that match): ' + ', '.join(tags) + '.')
    procedure = function.get('procedure')
    if procedure:
        lines.append(f"Debug symbols place this procedure in object file {procedure['file']}, frame {procedure['frame_bytes']} bytes, size {procedure['size']} bytes.")
    if function['strings']:
        lines.append('References strings: ' + '; '.join(repr(s) for s in function['strings']) + '.')
    for slot in function['exported_as']:
        lines.append(f"Export slot {slot['index']} of library {slot['library']} points at this entry.")
    if function['data_pointer_references']:
        lines.append(f"{function['data_pointer_references']} data pointer(s) name this entry.")
    if rename:
        lines.append(f'Name {rename} comes from a self-naming error string; it is a candidate, not a recovered symbol.')
    lines.append('No identity claim.')
    return '\n'.join(lines)


def build_plan(profile: dict, module_sha: str) -> dict:
    if profile['module']['sha256'] != module_sha:
        raise ValueError('profile was built from a different module hash')
    claims: dict[str, list[str]] = {}
    for function in profile['functions']:
        names = {m[1] for s in function['strings'] if (m := SELF_NAME.fullmatch(s))}
        if len(names) == 1:
            claims.setdefault(next(iter(names)), []).append(function['entry'])
    default = {f['entry'] for f in profile['functions'] if f.get('name') in (None, f'FUN_{f["entry"]}')}
    renames = {entries[0]: name for name, entries in claims.items() if len(entries) == 1 and entries[0] in default}
    entries = []
    for function in profile['functions']:
        if not (function['imports'] or function['strings'] or function['exported_as'] or function['data_pointer_references']
                or function.get('procedure')):
            continue
        rename = renames.get(function['entry'])
        entry = {'entry': function['entry'], 'comment': _comment(function, rename)}
        if rename:
            entry['rename'] = rename
        entries.append(entry)
    return {'schema_version': 1, 'executable_sha256': module_sha, 'module': profile['module']['name'], 'entries': entries,
            'claim_limits': ['Comments restate static tables; role tags are import-derived hints, not identities.',
                             'Import names are candidates from pinned public SDK tables.',
                             'A rename needs one self-naming error string, no other claimant and a default current name.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    record = json.loads(args.profile.read_text())
    profile = record.get('details', record)
    plan = build_plan(profile, profile['module']['sha256'])
    if not plan['entries']:
        raise Incomplete('no function has any static fact to annotate', plan)
    args.output.write_text(json.dumps(plan, indent=1) + '\n')
    print(len(plan['entries']), 'entries', sum('rename' in e for e in plan['entries']), 'renames')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
