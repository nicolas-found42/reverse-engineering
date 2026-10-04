import struct
import unittest
from pathlib import Path
import tempfile

from evidence_common import Incomplete, Invalid
import ps2_executables as subject
from verify_executables import inventory


def elf():
    data = bytearray(96)
    data[:16] = b'\x7fELF\x01\x01\x01' + bytes(9)
    struct.pack_into('<HHIIIIIHHHHHH', data, 16,
                     0xFF80, 8, 1, 0, 52, 0, 1, 52, 32, 1, 40, 0, 0)
    struct.pack_into('<8I', data, 52, 1, 84, 0, 0, 12, 16, 5, 4)
    return bytes(data)


def romdir():
    module = elf()
    entries = [(b'RESET', 0, 0), (b'ROMDIR', 0, 80),
               (b'EXTINFO', 0, 0), (b'TEST', 0, len(module))]
    return b''.join(struct.pack('<10sHI', *r) for r in entries) + bytes(16) + module


class ExecutablesTest(unittest.TestCase):
    def test_valid_iop_elf_and_bss_memory(self):
        result = subject.parse_elf(elf())
        self.assertEqual(result['machine'], 8)
        self.assertEqual(result['programs'][0]['file_size'], 12)
        self.assertEqual(result['programs'][0]['memory_size'], 16)

    def test_truncated_table_and_segment_rejected(self):
        for data in (elf()[:51], elf()[:82], elf()[:95]):
            with self.assertRaises(Invalid):
                subject.parse_elf(data)

    def test_memory_size_must_cover_file_size(self):
        data = bytearray(elf())
        struct.pack_into('<I', data, 52 + 20, 8)
        with self.assertRaises(Invalid):
            subject.parse_elf(bytes(data))

    def test_unsupported_encoding_and_extended_sections_incomplete(self):
        for at, value in ((4, 2), (5, 2)):
            data = bytearray(elf()); data[at] = value
            with self.assertRaises(Incomplete):
                subject.parse_elf(bytes(data))
        data = bytearray(elf()); struct.pack_into('<H', data, 50, 0xFFFF)
        with self.assertRaises(Incomplete):
            subject.parse_elf(bytes(data))

    def test_romdir_exact_module_and_hash(self):
        result = subject.parse_romdir(romdir())
        self.assertEqual(len(result['modules']), 1)
        self.assertEqual(result['modules'][0]['offset'], 80)
        self.assertEqual(result['modules'][0]['bytes'], 96)
        self.assertEqual(result['logical_end'], 176)

    def test_romdir_bounds_and_names_rejected(self):
        variants = [romdir()[:-1]]
        bad = bytearray(romdir()); struct.pack_into('<I', bad, 48 + 12, 9999); variants.append(bytes(bad))
        bad = bytearray(romdir()); bad[48:58] = b'../escape\0'; variants.append(bytes(bad))
        bad = bytearray(romdir()); bad[64] = 1; variants.append(bytes(bad))
        for data in variants:
            with self.assertRaises(Invalid):
                subject.parse_romdir(data)

    def test_no_elf_magic_length_guess(self):
        data = bytearray(romdir()); data[164:168] = b'\x7fELF'
        result = subject.parse_romdir(bytes(data))
        self.assertEqual(len(result['modules']), 1)
        self.assertEqual(result['modules'][0]['bytes'], 96)

    def test_zero_size_sections_do_not_claim_payload(self):
        data = bytearray(elf() + bytes(80))
        struct.pack_into('<I', data, 32, 96)
        struct.pack_into('<H', data, 48, 2)
        struct.pack_into('<10I', data, 136, 0, 1, 0, 0, 999999, 0, 0, 0, 1, 0)
        self.assertEqual(subject.parse_elf(bytes(data))['sections'][1]['size'], 0)
        struct.pack_into('<I', data, 136 + 20, 1)
        with self.assertRaises(Invalid):
            subject.parse_elf(bytes(data))

    def test_inventory_coverage_and_unknown_magic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'module.IRX').write_bytes(elf())
            (root / 'reboot.IMG').write_bytes(romdir())
            self.assertEqual(inventory(root)['executable_count'], 2)
            (root / 'unclassified.dat').write_bytes(b'prefix\x7fELFunknown')
            with self.assertRaises(Incomplete) as caught:
                inventory(root)
            self.assertEqual(caught.exception.details['unclassified_elf_magic'][0]['offset'], 6)

    def test_real_disc_boundaries(self):
        root = Path(__file__).resolve().parent.parent / 'games/ford-racing-2/extracted'
        if not root.is_dir():
            self.skipTest('local game payload is unavailable')
        embedded = subject.parse_romdir((root / 'IRX/IOPRP255.IMG').read_bytes())
        self.assertEqual(len(embedded['modules']), 15)
        self.assertEqual(embedded['logical_end'], embedded['bytes'])
        for path in (root / 'IRX').glob('*.IRX'):
            self.assertEqual(subject.parse_elf(path.read_bytes())['machine'], 8)


if __name__ == '__main__':
    unittest.main()
