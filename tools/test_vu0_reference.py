"""Tests for the bounded VU0 0x268 arithmetic model and source guard."""
from __future__ import annotations

import dataclasses
import hashlib
import math
import struct
import unittest
from pathlib import Path

from tools.vu import vu268_reference as model
from tools.vu import vu268_source_guard as guard

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ELF = REPO_ROOT / "games/ford-racing-2/extracted/SLES_517.05"


def _fixture():
    source_offset = 64
    data = bytearray(source_offset + guard.PINNED_CONTRACT.overlay_bytes)
    for pair, _name, lower_word in guard.PINNED_CONTRACT.loi_words:
        # The upper word is only used here to exercise the LOI flag check. Other
        # opcodes are covered by the pinned whole-span digest on the real file.
        struct.pack_into("<II", data, source_offset + pair * 8,
                         lower_word, 0x80000000 | pair)
    source = bytes(data[source_offset:source_offset + guard.PINNED_CONTRACT.overlay_bytes])
    span_start = source_offset + guard.PINNED_CONTRACT.span_start_pair * 8
    span_end = source_offset + guard.PINNED_CONTRACT.span_end_pair_exclusive * 8
    contract = dataclasses.replace(
        guard.PINNED_CONTRACT,
        executable_sha256=hashlib.sha256(data).hexdigest(),
        overlay_source_offset=source_offset,
        overlay_sha256=hashlib.sha256(source).hexdigest(),
        span_sha256=hashlib.sha256(data[span_start:span_end]).hexdigest(),
    )
    inventory = {
        "executable_sha256": contract.executable_sha256,
        "overlays": [{
            "index": contract.overlay_index,
            "name": contract.overlay_name,
            "load_address": contract.overlay_load_address,
            "vu_byte_address": contract.overlay_vma,
            "source_section": contract.overlay_source_section,
            "source_offset": source_offset,
            "bytes": contract.overlay_bytes,
            "instruction_pairs": contract.overlay_pairs,
            "sha256": contract.overlay_sha256,
        }],
    }
    return bytes(data), inventory, contract


def _refresh_identity(data: bytes, inventory: dict, contract: guard.GuardContract,
                      *, refresh_span: bool = False):
    source_offset = inventory["overlays"][0]["source_offset"]
    source = data[source_offset:source_offset + contract.overlay_bytes]
    span_start = source_offset + contract.span_start_pair * 8
    span_end = source_offset + contract.span_end_pair_exclusive * 8
    inventory = {**inventory, "executable_sha256": hashlib.sha256(data).hexdigest(),
                 "overlays": [dict(inventory["overlays"][0])]}
    inventory["overlays"][0]["sha256"] = hashlib.sha256(source).hexdigest()
    contract = dataclasses.replace(
        contract,
        executable_sha256=hashlib.sha256(data).hexdigest(),
        overlay_sha256=hashlib.sha256(source).hexdigest(),
        span_sha256=(hashlib.sha256(data[span_start:span_end]).hexdigest()
                     if refresh_span else contract.span_sha256),
    )
    return inventory, contract


class VU268ModelTest(unittest.TestCase):
    def test_exact_loi_values_are_source_bit_patterns(self):
        expected = {name: bits for _, name, bits in guard.PINNED_CONTRACT.loi_words
                    if name != "minus_inv_tau_again"}
        self.assertEqual(model.LOI_BITS, expected)
        self.assertEqual(struct.unpack("<I", struct.pack("<f", model.load_i("pi_over_2")))[0],
                         0x3FC90FDB)

    def test_sweeps_and_negative_controls(self):
        result = model.evaluate_suite()
        self.assertEqual(result["sweeps"]["period_0_to_2pi"]["samples"], 20001)
        self.assertLess(result["sweeps"]["period_0_to_2pi"]["max_sin_error"], 1.1e-6)
        self.assertLess(result["sweeps"]["period_0_to_2pi"]["max_cos_error"], 9.0e-7)
        self.assertLess(result["sweeps"]["signed_small"]["max_sin_error"], 2.2e-6)
        self.assertLess(result["sweeps"]["wide_100"]["max_sin_error"], 1.9e-5)
        self.assertEqual(result["random_range"]["samples"], 10000)
        self.assertEqual(len(result["quarter_turn_boundaries"]), 51)
        self.assertGreater(result["rounding_negative_control"]["nearest_sin_error"], 0.1)
        self.assertLess(result["rounding_negative_control"]["vu_round0_sin_error"], 1.0e-7)
        self.assertTrue(result["other_lane_negative_control_equal"])
        x, y = model.run(0.73)[0][:2]
        self.assertLess(abs(x - math.sin(0.73)), 3e-6)
        self.assertLess(abs(y - math.cos(0.73)), 3e-6)


class VU268SourceGuardSeamTest(unittest.TestCase):
    def test_accepts_exact_mutation_fixture(self):
        data, inventory, contract = _fixture()
        result = guard.verify_source_bytes(data, inventory, contract=contract)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["instruction_span_bytes"], 200)
        self.assertTrue(result["model_LOI_table_matches_source_bits"])

    def test_rejects_wrong_executable_identity(self):
        data, inventory, contract = _fixture()
        wrong = dataclasses.replace(contract, executable_sha256="0" * 64)
        with self.assertRaisesRegex(guard.SourceGuardError, "executable SHA-256"):
            guard.verify_source_bytes(data, inventory, contract=wrong)

    def test_rejects_wrong_overlay_mapping(self):
        for field, changed_value in (("vu_byte_address", 8),
                                     ("source_offset", 65),
                                     ("load_address", guard.PINNED_CONTRACT.overlay_load_address + 8),
                                     ("name", ".DVP.overlay.wrong"),
                                     ("source_section", ".wrong")):
            with self.subTest(field=field):
                data, inventory, contract = _fixture()
                inventory["overlays"][0][field] = changed_value
                with self.assertRaisesRegex(guard.SourceGuardError, field):
                    guard.verify_source_bytes(data, inventory, contract=contract)

    def test_rejects_wrong_pair_span_bytes(self):
        data, inventory, contract = _fixture()
        changed = bytearray(data)
        changed[contract.overlay_source_offset + contract.span_start_pair * 8 + 4] ^= 1
        inventory, dynamic_contract = _refresh_identity(bytes(changed), inventory, contract)
        with self.assertRaisesRegex(guard.SourceGuardError, "pair 77..101 source bytes"):
            guard.verify_source_bytes(bytes(changed), inventory, contract=dynamic_contract)

    def test_rejects_wrong_loi_bits_even_if_mutated_span_is_rehashed(self):
        data, inventory, contract = _fixture()
        changed = bytearray(data)
        offset = contract.overlay_source_offset + 78 * 8
        struct.pack_into("<I", changed, offset, 0x3FC90FDA)
        inventory, dynamic_contract = _refresh_identity(bytes(changed), inventory, contract,
                                                        refresh_span=True)
        with self.assertRaisesRegex(guard.SourceGuardError, "pair 78 LOI lower-word bits"):
            guard.verify_source_bytes(bytes(changed), inventory, contract=dynamic_contract)

    def test_rejects_model_constant_disagreement(self):
        data, inventory, contract = _fixture()
        wrong_model = dict(model.LOI_BITS)
        wrong_model["pi_over_2"] ^= 1
        with self.assertRaisesRegex(guard.SourceGuardError, "model LOI bit table"):
            guard.verify_source_bytes(data, inventory, model_bits=wrong_model, contract=contract)


@unittest.skipUnless(PRIVATE_ELF.is_file(),
                     "private Ford Racing 2 executable is unavailable; synthetic guard mutation tests still run")
class VU268PrivateSourceIntegrationTest(unittest.TestCase):
    def test_local_executable_matches_pinned_overlay_span_and_loads(self):
        result = guard.verify_executable(PRIVATE_ELF)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["instruction_span_sha256"],
                         guard.PINNED_CONTRACT.span_sha256)
        self.assertEqual(len(result["loads"]), 11)


if __name__ == "__main__":
    unittest.main()
