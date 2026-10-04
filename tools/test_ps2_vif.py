import struct
import unittest
from pathlib import Path

from evidence_common import Incomplete, Invalid
from ps2_vif import parse_chain, public_chain
from verify_vif import EXECUTABLE_SHA256, verify


def mpg(instruction_index: int, count: int) -> int:
    return 0x4a000000 | ((count & 0xff) << 16) | instruction_index


def chain_fixture(*, first_command=None, tag_vif0=0, body=None, qwc=None,
                  end_words=(0x70000000, 0, 0, 0)):
    first_command = mpg(0, 1) if first_command is None else first_command
    body = (bytes(range(8)) + struct.pack('<I', 0) + struct.pack('<I', mpg(1, 1))
            + bytes(range(16, 24)) + bytes(8)) if body is None else body
    if len(body) % 16:
        raise ValueError('fixture body must be qword aligned')
    qwc = len(body) // 16 if qwc is None else qwc
    packet = struct.pack('<4I', 0x10000000 | qwc, 0, tag_vif0, first_command) + body
    return packet + struct.pack('<4I', *end_words)


class VifParserTest(unittest.TestCase):
    def test_bounded_cnt_nop_mpg_end_and_exact_payloads(self):
        parsed = parse_chain(chain_fixture(), 0x1000)
        self.assertEqual(parsed['qwc'], 2)
        self.assertEqual(parsed['end_tag_address'], 0x1030)
        self.assertEqual([(x['instruction_index'], x['instruction_pairs'], x['bytes'])
                          for x in parsed['chunks']], [(0, 1, 8), (1, 1, 8)])
        self.assertEqual(parsed['chunks'][0]['payload'], bytes(range(8)))
        self.assertEqual(parsed['chunks'][1]['payload'], bytes(range(16, 24)))
        self.assertEqual(parsed['nop_count'], 4)

    def test_zero_num_means_256_pairs(self):
        payload = bytes(2048)
        packet = chain_fixture(first_command=mpg(12, 0), body=payload)
        parsed = parse_chain(packet, 0x2000)
        self.assertEqual(parsed['chunks'][0]['instruction_pairs'], 256)
        self.assertEqual(parsed['chunks'][0]['vu_byte_address'], 96)
        self.assertEqual(parsed['chunks'][0]['bytes'], len(payload))

    def test_refuses_without_tte_or_for_non_cnt_or_unsupported_flags(self):
        with self.assertRaises(Incomplete):
            parse_chain(chain_fixture(), 0x1000, tte=False)
        mutations = [
            (0, 0x20000000, Incomplete),  # NEXT
            (0, 0x90000003, Incomplete),  # IRQ flag
            (4, 0x20, Incomplete),        # external CNT pointer
        ]
        original = chain_fixture()
        for offset, value, error in mutations:
            changed = bytearray(original); struct.pack_into('<I', changed, offset, value)
            with self.subTest(offset=offset, value=value), self.assertRaises(error):
                parse_chain(bytes(changed), 0x1000)

    def test_refuses_unsupported_vif_flags_commands_and_end_profiles(self):
        for command in (0x80000000 | mpg(0, 1), 0x50000000, 0x4b000000):
            with self.subTest(command=hex(command)), self.assertRaises(Incomplete):
                parse_chain(chain_fixture(first_command=command), 0x1000)
        bad_end = chain_fixture(end_words=(0x70000000, 0, 1, 0))
        with self.assertRaises(Incomplete):
            parse_chain(bad_end, 0x1000)
        # The first TTE word is consumed before any payload body. It cannot
        # itself be MPG because the following TTE word would then be payload.
        with self.assertRaises(Incomplete):
            parse_chain(chain_fixture(tag_vif0=mpg(0, 1)), 0x1000)
        with self.assertRaises(Incomplete):
            parse_chain(chain_fixture(first_command=0), 0x1000)

    def test_refuses_bad_packet_alignment_reserved_tag_bits_and_non_end_tag(self):
        packet = chain_fixture()
        for changed, exception in (
            (packet[:24], Invalid),
            (packet + bytes(16), Invalid),
            (packet[:16] + packet[16:-16] + struct.pack('<4I', 0x60000000, 0, 0, 0), Incomplete),
        ):
            with self.subTest(exception=exception.__name__), self.assertRaises(exception):
                parse_chain(changed, 0x1000)
        for offset, value in ((0, 0x10010002), (0, 0x10000000), (4, 4)):
            changed = bytearray(packet); struct.pack_into('<I', changed, offset, value)
            expected = Incomplete if offset == 0 and value == 0x10010002 else Invalid if value == 0x10000000 else Incomplete
            with self.subTest(offset=offset, value=hex(value)), self.assertRaises(expected):
                parse_chain(bytes(changed), 0x1000)
        with self.assertRaises(Invalid):
            parse_chain(packet, 0x1001)

    def test_rejects_empty_mpg_stream_and_mpg_extent_past_vu_memory(self):
        with self.assertRaises(Incomplete):
            parse_chain(chain_fixture(first_command=0, body=bytes(16)), 0x1000)
        with self.assertRaises(Invalid):
            parse_chain(chain_fixture(first_command=mpg(2047, 2), body=bytes(16)), 0x1000)

    def test_public_chain_never_exposes_payload_bytes(self):
        public = public_chain(parse_chain(chain_fixture(), 0x1000))
        self.assertNotIn('payload', public['chunks'][0])
        self.assertIn('payload_sha256', public['chunks'][0])

    def test_refuses_malformed_qwc_destination_payload_overrun_and_unknown_data(self):
        with self.assertRaises(Invalid):
            parse_chain(chain_fixture(qwc=1), 0x1000)
        with self.assertRaises(Invalid):
            parse_chain(chain_fixture(first_command=mpg(2048, 1)), 0x1000)
        with self.assertRaises(Invalid):
            parse_chain(chain_fixture(first_command=mpg(0, 3), body=bytes(16)), 0x1000)
        # Unknown body words are not treated as padding after a complete payload.
        body = bytes(range(8)) + b'\x01\x02\x03\x04' + bytes(4)
        with self.assertRaises(Incomplete):
            parse_chain(chain_fixture(body=body), 0x1000)


class VifStaticMappingTest(unittest.TestCase):
    def test_pinned_game_has_eight_exact_overlay_matches_and_no_extras(self):
        executable = Path(__file__).resolve().parents[1] / 'games/ford-racing-2/extracted/SLES_517.05'
        if not executable.is_file():
            self.skipTest('private pinned game executable is not present in this checkout')
        result = verify(executable.read_bytes())
        self.assertEqual(result['executable_sha256'], EXECUTABLE_SHA256)
        self.assertEqual((result['overlay_count'], result['transfer_count'], result['matched_count']), (8, 8, 8))
        self.assertEqual(result['unmatched_overlay_count'], 0)
        self.assertEqual(result['total_instruction_pairs'], 1698)
        self.assertEqual(result['total_transferred_bytes'], 13584)
        self.assertEqual([x['channel'] for x in result['matches']].count('VIF1'), 7)
        self.assertEqual([x['channel'] for x in result['matches']].count('VIF0'), 1)
        self.assertTrue(all(x['exact_bytes_match'] for x in result['matches']))
        self.assertTrue(all(x['exact_file_offset_match'] and x['exact_load_address_match']
                            for x in result['matches']))
        self.assertFalse(result['whole_game_execution_or_render_proven'])

    def test_wrong_executable_identity_is_incomplete(self):
        with self.assertRaises(Incomplete):
            verify(b'not the pinned executable')


if __name__ == '__main__':
    unittest.main()
