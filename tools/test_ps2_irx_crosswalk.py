"""Synthetic falsifiers for literal observed-module import/export candidates."""
import struct
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from evidence_common import Invalid
from test_ps2_irx import minimal_elf
from test_ps2_irx_relocations import build_irx
import ps2_irx_crosswalk as subject


def module(*, importing=False, library=b"demo", version=0x101,
           ordinal=1, targets=(0x80, 0x84)):
    magic = 0x41E00000 if importing else 0x41C00000
    text = struct.pack("<III8s", magic, 0, version, library)
    if importing:
        text += struct.pack("<IIII", 0x03E00008, 0x24000000 | ordinal, 0, 0)
    else:
        text += struct.pack("<" + "I" * (len(targets) + 1), *targets, 0)
    return minimal_elf(text.ljust(0x100, b"\0"))


def relocatable_module(*, importing=False, pointer_relocations=(20, 24), tail_target=0x80):
    text = struct.pack("<III8s", 0x41E00000 if importing else 0x41C00000,
                       0, 0x101, b"demo")
    text += (struct.pack("<IIII", 0x03E00008, 0x24000000, 0, 0) if importing
             else struct.pack("<III", 0, tail_target, 0))
    words = struct.unpack("<64I", text.ljust(0x100, b"\0"))
    return build_irx(words=words,
                     text_relocations=() if importing else tuple((at, 2) for at in pointer_relocations),
                     bss_relocations=(), load_memory_size=0x100, module_text=0x100, module_bss=0)


class CrosswalkTests(unittest.TestCase):
    def test_exact_tuple_and_byte_provenance(self):
        result = subject.crosswalk([("consumer", module(importing=True)),
                                    ("provider", module())])
        edge = result["edges"][0]
        self.assertEqual(result["counts"]["unique_candidate"], 1)
        self.assertEqual(edge["candidates"][0]["relative_target"], 0x84)
        self.assertEqual(edge["candidates"][0]["ordinal"], 1)
        self.assertEqual(edge["candidates"][0]["module_key"], "provider")
        self.assertEqual(len(edge["importer_sha256"]), 64)
        self.assertFalse(edge["runtime_binding_verified"])

    def test_library_version_and_ordinal_mutations_do_not_guess(self):
        for payload in (module(importing=True, library=b"other"),
                        module(importing=True, version=0x102),
                        module(importing=True, ordinal=2)):
            with self.subTest(payload=payload[:36]):
                result = subject.crosswalk([("consumer", payload),
                                            ("provider", module())])
                self.assertEqual(result["counts"]["no_candidate"], 1)
                self.assertEqual(result["edges"][0]["candidates"], [])

    def test_two_observed_providers_remain_ambiguous(self):
        result = subject.crosswalk([("consumer", module(importing=True)),
                                    ("provider-a", module()), ("provider-b", module())])
        self.assertEqual(result["counts"]["ambiguous_candidates"], 1)
        self.assertEqual(len(result["edges"][0]["candidates"]), 2)

    def test_duplicate_source_is_rejected(self):
        with self.assertRaises(Invalid):
            subject.crosswalk([("same", module()), ("same", module())])

    def test_unaligned_or_outside_export_target_is_rejected(self):
        for target in (0x81, 0x100, 0xFFFFFFFC):
            with self.subTest(target=target), self.assertRaises(Invalid):
                subject.crosswalk([("provider", module(targets=(target,)))])

    def test_nonzero_text_address_profile_is_rejected(self):
        payload = bytearray(module())
        struct.pack_into("<I", payload, 52 + 40 + 12, 0x1000)
        with self.assertRaises(Invalid):
            subject.crosswalk([("provider", bytes(payload))])

    def test_input_order_has_stable_candidate_output(self):
        inputs = [("z", module()), ("a", module()), ("c", module(importing=True))]
        self.assertEqual(subject.crosswalk(inputs), subject.crosswalk(list(reversed(inputs))))

    def test_verified_slice_drift_and_path_escape_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            original = module()
            (root / "provider").write_bytes(module(version=0x102))
            inventory, boundaries = root / "inventory.json", root / "boundaries.json"
            inventory.write_text("{}")
            boundaries.write_text("{}")
            row = {"source": "provider", "offset": 0, "bytes": len(original),
                   "sha256": hashlib.sha256(original).hexdigest()}
            for changes in ({}, {"source": "../outside"}):
                with self.subTest(changes=changes), patch.object(subject, "verify_corpus",
                        return_value={"modules": [{**row, **changes}]}), self.assertRaises(Invalid):
                    subject.corpus(root, inventory, boundaries)

    def test_input_inventory_change_during_verification_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            inventory, boundaries = root / "inventory.json", root / "boundaries.json"
            inventory.write_text("{}")
            boundaries.write_text("{}")

            def mutate(*args):
                boundaries.write_text('{"changed":true}')
                return {"modules": []}

            with patch.object(subject, "verify_corpus", side_effect=mutate), self.assertRaises(Invalid):
                subject.corpus(root, inventory, boundaries)

    def test_relocated_zero_export_is_pointer_and_unrelocated_zero_terminates(self):
        inputs = [("consumer", relocatable_module(importing=True)),
                  ("provider", relocatable_module())]
        self.assertEqual(subject.crosswalk(inputs)["export_entries"], 0)
        result = subject.crosswalk(inputs, synthetic_load_base=0x1000)
        self.assertEqual(result["export_entries"], 2)
        self.assertEqual(result["counts"]["unique_candidate"], 1)
        self.assertEqual(result["edges"][0]["candidates"][0]["relative_target"], 0)
        self.assertTrue(result["edges"][0]["candidates"][0]["pointer_relocation_verified"])

    def test_relocation_view_requires_nonzero_base_and_preserves_input(self):
        raw = relocatable_module()
        original = bytes(raw)
        with self.assertRaises(Invalid):
            subject.crosswalk([("provider", raw)], synthetic_load_base=0)
        first = subject.crosswalk([("provider", raw)], synthetic_load_base=0x1000)
        second = subject.crosswalk([("provider", raw)], synthetic_load_base=0x100000)
        self.assertEqual(first["export_entries"], second["export_entries"])
        self.assertEqual(raw, original)

    def test_wrapped_export_pointer_cannot_become_a_false_terminator(self):
        with self.assertRaises(Invalid):
            subject.crosswalk([("provider", relocatable_module(tail_target=0xFFFFF000))],
                              synthetic_load_base=0x1000)

    def test_unrelocated_nonzero_export_pointer_is_rejected_in_relocation_view(self):
        with self.assertRaises(Invalid):
            subject.crosswalk([("provider", relocatable_module(pointer_relocations=(20,)))],
                              synthetic_load_base=0x1000)


if __name__ == "__main__":
    unittest.main()
