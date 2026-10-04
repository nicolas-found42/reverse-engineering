"""Tests for bounded IRX import/export tables and corpus provenance."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from evidence_common import Incomplete, Invalid
import ps2_irx as subject
from verify_irx import verify_corpus


def table_text() -> bytes:
    imports = struct.pack("<III8s", subject.IMPORT_MAGIC, 0, 0x0101, b"loadcore")
    imports += struct.pack("<II", 0x03E00008, (9 << 26) | 6)
    imports += struct.pack("<II", 0, 0)
    exports = struct.pack("<III8s", subject.EXPORT_MAGIC, 0, 0x0100, b"demo\0\0\0\0")
    exports += struct.pack("<II", 0x120, 0)
    return imports + exports


def minimal_elf(text: bytes) -> bytes:
    """Small ELF32 MIPS IRX with .text and .iopmod sections."""
    data = bytearray(52)
    data[:16] = b"\x7fELF\x01\x01\x01" + bytes(9)
    # ELF header: ET 0xff80, EM_MIPS, section table at 52.
    struct.pack_into("<HHIIIIIHHHHHH", data, 16,
                     0xFF80, 8, 1, 0, 0, 52, 0, 52, 0, 0, 40, 5, 4)
    names = b"\0.text\0.iopmod\0.shstrtab\0"
    shoff = 52
    data.extend(bytes(5 * 40))
    text_offset = len(data)
    data.extend(text)
    mod_offset = len(data)
    data.extend(struct.pack("<IIIIIIH", 0x100, 0x120, 0, len(text), 0, 0, 0x0101) + b"test\0")
    names_offset = len(data)
    data.extend(names)
    struct.pack_into("<10I", data, shoff + 40, 1, 1, 6, 0, text_offset, len(text), 0, 0, 4, 0)
    struct.pack_into("<10I", data, shoff + 80, 7, subject.SHT_IOPMOD, 0, 0, mod_offset, 31, 0, 0, 4, 0)
    struct.pack_into("<10I", data, shoff + 160, 15, 3, 0, 0, names_offset, len(names), 0, 0, 1, 0)
    struct.pack_into("<H", data, 16 + 50, 4)  # e_shstrndx
    return bytes(data)


class IrxParserTests(unittest.TestCase):
    def test_import_and_export_tables_preserve_offsets_and_numeric_indices(self):
        result = subject.parse_irx(minimal_elf(table_text()))
        self.assertEqual(result["module"]["name"], "test")
        self.assertEqual(result["imports"][0]["library"], "loadcore")
        self.assertEqual(result["imports"][0]["version"], 0x0101)
        self.assertEqual(result["imports"][0]["links"][0]["index"], 6)
        self.assertEqual(result["exports"][0]["library"], "demo")
        self.assertEqual(result["exports"][0]["links"], [{"offset": 0x120}])
        self.assertEqual(result["counts"], {"import_libraries": 1, "import_stubs": 1,
                                             "export_libraries": 1, "export_links": 1})

    def test_unterminated_import_and_export_tables_fail_closed(self):
        bad_import = struct.pack("<III8sII", subject.IMPORT_MAGIC, 0, 1, b"loadcore", 0x03E00008, 0x24000001)
        bad_export = struct.pack("<III8sI", subject.EXPORT_MAGIC, 0, 1, b"demo\0\0\0\0", 0x120)
        for text in (bad_import, bad_export):
            with self.subTest(text=text[:4]), self.assertRaises(Invalid):
                subject.parse_irx(minimal_elf(text))

    def test_bad_library_name_and_import_opcode_fail_closed(self):
        payload = bytearray(minimal_elf(table_text()))
        text_offset = subject.parse_elf(bytes(payload))["sections"][".text"]["offset"]
        payload[text_offset + 12 : text_offset + 20] = b"bad/name"
        with self.assertRaises(Invalid):
            subject.parse_irx(bytes(payload))

    def test_import_stub_and_terminator_encodings_are_exact(self):
        mutations = [
            (20, 0x08000008),  # not `jr $ra`
            (24, 0x24200006),  # LI has nonzero rs
            (28, 0x00000001),  # partial nonzero terminator pair
            (8, 0x00010001),   # high version bits are outside the 16-bit field
        ]
        for offset, word in mutations:
            payload = bytearray(minimal_elf(table_text()))
            text_offset = subject.parse_elf(bytes(payload))["sections"][".text"]["offset"]
            struct.pack_into("<I", payload, text_offset + offset, word)
            with self.subTest(offset=offset), self.assertRaises(Invalid):
                subject.parse_irx(bytes(payload))
        payload = bytearray(minimal_elf(table_text()))
        text_offset = subject.parse_elf(bytes(payload))["sections"][".text"]["offset"]
        struct.pack_into("<I", payload, text_offset + 24, 0x08000006)
        with self.assertRaises(Invalid):
            subject.parse_irx(bytes(payload))

    def test_out_of_bounds_section_and_bad_iopmod_are_rejected(self):
        original = minimal_elf(table_text())
        bad_section = bytearray(original)
        # Section 1 .text file offset is at section-header offset + 16.
        struct.pack_into("<I", bad_section, 52 + 40 + 16, len(original) + 1)
        with self.assertRaises(Invalid):
            subject.parse_irx(bytes(bad_section))
        bad_module = bytearray(original)
        # The .iopmod payload's declared text bytes must agree with the .text section.
        parsed = subject.parse_elf(bytes(bad_module))
        mod_offset = parsed["sections"][".iopmod"]["offset"]
        struct.pack_into("<I", bad_module, mod_offset + 12, 0xFFFFFFF0)
        with self.assertRaises(Invalid):
            subject.parse_irx(bytes(bad_module))

    def test_table_scan_ignores_unaligned_magic_bytes(self):
        text = b"x" + table_text()
        imports, exports = subject.parse_tables(text)
        self.assertEqual(imports, [])
        self.assertEqual(exports, [])

    def test_nonzero_reserved_word_fails_closed_at_table_magic(self):
        text = bytearray(table_text())
        struct.pack_into("<I", text, 4, 1)
        with self.assertRaises(Invalid):
            subject.parse_tables(bytes(text))

    def test_wrong_elf_machine_is_rejected(self):
        payload = bytearray(minimal_elf(table_text()))
        struct.pack_into("<H", payload, 18, 3)  # EM_386
        with self.assertRaises(Invalid):
            subject.parse_irx(bytes(payload))

    def test_zero_sized_sections_do_not_read_outside_file(self):
        data = bytearray(minimal_elf(table_text()))
        # Section 3 is an empty optional section; its file offset has no payload semantics.
        struct.pack_into("<I", data, 52 + 3 * 40 + 16, 0xFFFFFFFF)
        struct.pack_into("<I", data, 52 + 3 * 40 + 20, 0)
        self.assertEqual(subject.parse_elf(bytes(data))["sections"][".iopmod"]["size"], 31)


class IrxVerifierTests(unittest.TestCase):
    def make_inputs(self, root: Path):
        payload = minimal_elf(table_text())
        (root / "IRX").mkdir()
        standalone_rows = []
        candidates = []
        for index in range(9):
            name = f"S{index}.IRX"
            standalone = root / "IRX" / name
            standalone.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            standalone_rows.append({"path": f"IRX/{name}", "elf": {
                "type": 0xFF80, "machine": 8, "bytes": len(payload), "sha256": digest}})
            candidates.append({"file": f"IRX/{name}", "offset": 0, "file_bytes": len(payload),
                               "sha256": digest, "type": 0xFF80, "machine": 8, "valid_header": True})

        module_names = [f"M{i:02d}" for i in range(15)]
        rows = [(b"RESET", 0, 0), (b"ROMDIR", 0, 304), (b"EXTINFO", 0, 0)]
        rows.extend((name.encode(), 0, len(payload)) for name in module_names)
        directory = b"".join(struct.pack("<10sHI", name, ext, size) for name, ext, size in rows)
        directory += bytes(16)
        image = bytearray(directory)
        embedded_rows = []
        for name in module_names:
            offset = len(image)
            image.extend(payload)
            digest = hashlib.sha256(payload).hexdigest()
            embedded_rows.append({"name": name, "offset": offset, "bytes": len(payload), "sha256": digest})
            while len(image) % 16:
                image.append(0)
        image_path = root / "IRX" / "IOPRP255.IMG"
        image_path.write_bytes(image)
        image_digest = hashlib.sha256(image).hexdigest()
        candidates.extend({"file": "IRX/IOPRP255.IMG", "offset": row["offset"],
                           "file_bytes": len(image), "sha256": image_digest,
                           "type": 0xFF80, "machine": 8, "valid_header": True}
                          for row in embedded_rows)
        source_root = root.resolve()
        inventory = {
            "root": str(source_root),
            "elf_magic_candidates": candidates,
        }
        boundaries = {"standalone": standalone_rows, "modules": embedded_rows,
                      "bytes": len(image), "sha256": image_digest}
        inv = root / "inventory.json"; inv.write_text(json.dumps(inventory))
        bound = root / "boundaries.json"; bound.write_text(json.dumps(boundaries))
        return inv, bound

    def test_exact_standalone_bounds_and_hashes_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "disc"
            root.mkdir()
            inv, bounds = self.make_inputs(root)
            result = verify_corpus(root, inv, bounds)
            self.assertEqual(result["module_count"], 24)
            self.assertEqual(result["standalone_count"], 9)
            self.assertEqual(result["romdir_module_count"], 15)

    def test_hash_mismatch_fails_and_missing_input_is_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "disc"; root.mkdir()
            inv, bounds = self.make_inputs(root)
            value = json.loads(inv.read_text()); value["elf_magic_candidates"][0]["sha256"] = "0" * 64
            inv.write_text(json.dumps(value))
            with self.assertRaises(Invalid):
                verify_corpus(root, inv, bounds)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "disc"; root.mkdir()
            inv, bounds = self.make_inputs(root)
            (root / "IRX/S0.IRX").unlink()
            with self.assertRaises(Incomplete):
                verify_corpus(root, inv, bounds)

    def test_inventory_byte_count_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "disc"; root.mkdir()
            inv, bounds = self.make_inputs(root)
            value = json.loads(inv.read_text())
            value["elf_magic_candidates"][0]["file_bytes"] += 1
            inv.write_text(json.dumps(value))
            with self.assertRaises(Invalid):
                verify_corpus(root, inv, bounds)

    def test_embedded_candidate_offset_must_match_romdir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "disc"; root.mkdir()
            inv, bounds = self.make_inputs(root)
            value = json.loads(inv.read_text())
            embedded = next(row for row in value["elf_magic_candidates"]
                            if row["file"].endswith("IOPRP255.IMG"))
            embedded["offset"] += 4
            inv.write_text(json.dumps(value))
            with self.assertRaises(Invalid):
                verify_corpus(root, inv, bounds)

    def test_standalone_identity_must_match_boundary_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "disc"; root.mkdir()
            inv, bounds = self.make_inputs(root)
            value = json.loads(bounds.read_text())
            value["standalone"][0]["elf"]["sha256"] = "0" * 64
            bounds.write_text(json.dumps(value))
            with self.assertRaises(Invalid):
                verify_corpus(root, inv, bounds)


if __name__ == "__main__":
    unittest.main()
