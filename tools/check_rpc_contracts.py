#!/usr/bin/env python3
"""Check the fixed PAL STREAM volume child and retain unresolved parent scope."""
import argparse
import json
from pathlib import Path
import struct

from evidence_common import Incomplete, Invalid, sha256, write_result
from iop_symbols import read_symbols
from ps2_executables import parse_elf
from rpc_contracts import decode_volume_batch

PROFILE_PATH = Path(__file__).with_name('rpc_profile.json')
PROFILE = json.loads(PROFILE_PATH.read_text())
EE_TARGETS = {0x1ed0f0: 'bind-candidate', 0x1ed2c0: 'call-candidate'}
PARENT_GAPS = [
    'Other EE RPC candidates require service/client and IOP dispatch binding.',
    'Indirect calls and data-carried dispatch domains are not reconciled.',
    'Other STREAM subcommands and the 0x224-byte shared records remain unresolved.',
    'Reply layout, callback extent, concurrent ownership and shared-buffer lifetime remain unresolved.',
    'Other IOP module handlers and DMA/shared-memory domains remain unresolved.',
]


def scan_calls(data: bytes, targets: dict[int, str]) -> dict:
    """Inventory instruction-shaped JAL candidates; never assert decoding/reachability."""
    elf = parse_elf(data)
    direct, indirect = [], []
    for section in elf['sections']:
        if section['type'] != 1 or not section['flags'] & 4:
            continue
        if section['address'] % 4 or section['size'] % 4:
            raise Invalid('executable section is not word aligned')
        for offset in range(0, section['size'], 4):
            at = section['address'] + offset
            word = struct.unpack_from('<I', data, section['offset'] + offset)[0]
            if word >> 26 == 3:
                target = ((at + 4) & 0xf0000000) | ((word & 0x3ffffff) << 2)
                if target in targets:
                    direct.append({'site': at, 'target': target, 'domain': targets[target]})
            elif word >> 26 == 0 and word & 63 == 9:
                indirect.append(at)
    return {'direct_candidates': direct, 'indirect_instruction_candidates': indirect,
            'claim': 'aligned executable words only; no reachability or exhaustive protocol claim'}


def check_static_binding(ee: bytes, stream: bytes) -> dict:
    """Bind fresh raw bytes to the committed static profile; accept no supplied receipt."""
    images = {'ee': ee, 'stream': stream}
    for name, data in images.items():
        if sha256(data) != PROFILE[name + '_sha256']:
            raise Invalid(name + ' static profile identity mismatch')
    ranges = []
    for row in PROFILE['ranges']:
        data = images[row['artifact']]
        elf = parse_elf(data)
        matches = [s for s in elf['sections'] if s['type'] == 1 and
                   s['address'] <= row['address'] and
                   row['address'] + row['bytes'] <= s['address'] + s['size']]
        if len(matches) != 1:
            raise Invalid('missing caller/handler file-backed binding')
        section = matches[0]
        offset = section['offset'] + row['address'] - section['address']
        if sha256(data[offset:offset + row['bytes']]) != row['sha256']:
            raise Invalid('stale caller/handler range evidence')
        ranges.append(row)
    symbols = {s['name']: s for s in read_symbols(stream)}
    for name, address in [('ProcessEECommand', 0xd410), ('sce_adpcm_loop', 0xd494),
                          ('AdpcmSetParam', 0x11d44)]:
        if name not in symbols or symbols[name]['value'] != address:
            raise Invalid('missing IOP handler symbol binding: ' + name)
    objects = {name: {'address': symbols[name]['value'], 'bytes': symbols[name]['size']}
               for name in ('rpc_arg', 'aret', 'StreamBuffer')}
    return {'symbol_objects': objects, 'profile': PROFILE['profile'], 'raw_identities': {n: sha256(d) for n, d in images.items()}, 'ranges': ranges,
            'ee_candidates': scan_calls(ee, EE_TARGETS),
            'service_id': 0x12345, 'rpc_command': 0,
            'static_version': 62, 'runtime_registration': 'unobserved',
            'runtime_load_base': None, 'parent_status': 'incomplete', 'parent_gaps': PARENT_GAPS}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ee', required=True, type=Path)
    parser.add_argument('--stream', required=True, type=Path)
    parser.add_argument('--packet', type=Path, help='local 2048-byte command-0 input; never published')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()

    def action():
        # Evaluate known identities before missing packet so contradictions win.
        ee = args.ee.read_bytes()
        if sha256(ee) != PROFILE['ee_sha256']:
            raise Invalid('ee static profile identity mismatch')
        static = check_static_binding(ee, args.stream.read_bytes())
        if args.packet is None:
            raise Incomplete('required channel-volume packet observation/control is absent', static)
        try:
            raw_packet = args.packet.read_bytes()
            packet = decode_volume_batch(raw_packet)
        except (Incomplete, Invalid) as exc:
            raise type(exc)(str(exc), {'static': static, 'packet': exc.details}) from exc
        return {'scope': 'fixed PAL STREAM channel-volume framing child only',
                'static': static, 'packet': packet,
                'claim_limits': 'Host framing validation, not IOP execution or full handoff acceptance.'}

    inputs = [PROFILE_PATH, *[Path(__file__).with_name(name) for name in
              ('check_rpc_contracts.py', 'rpc_contracts.py', 'iop_symbols.py',
               'ps2_executables.py', 'evidence_common.py')]]
    # Do not let absent optional input suppress a known static contradiction.
    return write_result(args.output, 'STREAM channel-volume contract', action, inputs)


if __name__ == '__main__':
    raise SystemExit(main())
