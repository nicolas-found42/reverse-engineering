"""Hand-written bounded STREAM 6.2 channel-volume batch contract.

Static framing check only: no game execution, source-match or audio credit.
Other subcommands are deliberately incomplete; unused transfer tail is opaque.
"""
import struct

from evidence_common import Incomplete, Invalid, sha256

TRANSFER_BYTES = 0x800
VERSION = 62


def _decode_volume_batch(data: bytes) -> dict:
    """Decode command-0 records whose subcommand is 2 (channel volume)."""
    if not isinstance(data, bytes) or len(data) != TRANSFER_BYTES:
        raise Invalid('STREAM transfer must contain exactly 2048 bytes')
    version, count = struct.unpack_from('<Hh', data)
    if version != VERSION:
        raise Invalid('STREAM static version must be 62')
    if count < 0 or count > (TRANSFER_BYTES - 4) // 4:
        raise Invalid('STREAM record count exceeds the bounded transfer')
    cursor, records = 4, []
    unsupported = []
    for index in range(count):
        if cursor + 4 > len(data):
            raise Invalid('STREAM record header exceeds transfer')
        command, length = struct.unpack_from('<Hh', data, cursor)
        cursor += 4
        if length < 0 or cursor + length * 2 > len(data):
            raise Invalid('STREAM record length exceeds transfer')
        args = struct.unpack_from('<' + 'H' * length, data, cursor)
        cursor += length * 2
        if command == 2:
            if length != 3:
                raise Invalid('channel-volume layout requires three halfwords')
            if args[0] >= 48:
                raise Invalid('channel-volume caller permits only channels 0..47')
            records.append(dict(zip(('channel', 'left', 'right'), args)))
        else:
            unsupported.append({'record': index, 'subcommand': command, 'halfwords': length})
    result = {'scope': 'STREAM command-0/channel-volume framing only',
              'version': version, 'record_count': count, 'records': records,
              'used_bytes': cursor, 'opaque_tail_bytes': len(data) - cursor,
              'unsupported_records': unsupported, 'runtime_observed': False}
    if unsupported:
        raise Incomplete('required STREAM subcommand contract is unresolved', result)
    if not records:
        raise Incomplete('no channel-volume record was checked', result)
    return result


def decode_volume_batch(data: bytes) -> dict:
    """Check the bounded record and retain packet identity on every disposition."""
    if not isinstance(data, bytes):
        raise Invalid('STREAM transfer must be immutable bytes')
    digest = sha256(data)
    try:
        result = _decode_volume_batch(data)
    except (Invalid, Incomplete) as exc:
        raise type(exc)(str(exc), {**exc.details, 'input_sha256': digest,
                                 'input_bytes': len(data)}) from exc
    return {**result, 'input_sha256': digest, 'input_bytes': len(data)}
