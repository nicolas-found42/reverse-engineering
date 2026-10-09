"""Independent synthetic instruction controls for computed GP constructor aliases."""
import struct
import unittest

from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, Invalid
from misc3d_loader_recipe import constructor_aliases as constructors, ui_aliases
from ps2_executables import parse_elf


def fixture(words):
    data = build_elf([Spec('.text', struct.pack('<' + 'I' * len(words), *words), flags=6, address=0x1000)])
    return data, parse_elf(data)['sections']


class ConstructorControls(unittest.TestCase):
    def test_derived_index_preserves_possible_overlap_outside_initial_address(self):
        data, sections = fixture((9 << 26 | 28 << 21 | 16 << 16 | 0xac90,
                                  16 << 21 | 4 << 16 | 16 << 11 | 33,
                                  35 << 26 | 16 << 21 | 2 << 16,
                                  31 << 21 | 8, 0))
        result = constructors.observe(data, sections, {'candidate_count': 1, 'unowned_sites': [], 'unlisted_sites': []})
        row = result['constructors'][0]
        self.assertFalse(row['initial_address_is_scoped'])
        memory = next(use for use in row['uses'] if use['kind'] == 'memory-address')
        self.assertEqual(memory['base_constant'], '00290a00')
        self.assertEqual(memory['conditions'][0]['delta_low_word_candidates'], list(range(193, 200)))
        self.assertIn('register_4_low_word', memory['delta'])
        self.assertEqual(row['prefix_stop'], 'control transfer after its delay slot')
        self.assertIn('not an absence proof', row['disposition'])

    def test_stored_pointer_and_call_boundaries_remain_may_alias(self):
        data, sections = fixture((9 << 26 | 28 << 21 | 4 << 16 | 0xac90,
                                  43 << 26 | 29 << 21 | 4 << 16 | 16,
                                  3 << 26 | 0x2000 >> 2, 0))
        result = constructors.observe(data, sections, {'candidate_count': 1, 'unowned_sites': ['00001000'], 'unlisted_sites': []})
        row = result['constructors'][0]
        self.assertEqual(result['raw_unowned_count'], 1)
        self.assertEqual([escape['kind'] for escape in row['escapes']], ['stored-derived-value', 'control-or-call-boundary'])
        self.assertIn('conditional if executed', row['instruction_status'])

    def test_missing_saved_context_remains_incomplete(self):
        data, sections = fixture((9 << 26 | 28 << 21 | 4 << 16 | 0xac90,))
        with self.assertRaisesRegex(Incomplete, 'saved-instruction context is absent'):
            constructors.observe(data, sections)

    def test_conditional_overwrite_retains_prior_pointer_possibility(self):
        data, sections = fixture((9 << 26 | 28 << 21 | 16 << 16 | 0xac90,
                                  4 << 21 | 5 << 16 | 16 << 11 | 10,
                                  35 << 26 | 16 << 21 | 2 << 16))
        row = constructors.observe(data, sections, {'candidate_count': 1})['constructors'][0]
        self.assertEqual([use['kind'] for use in row['uses']], ['conditional-derived-value', 'memory-address'])
        self.assertIn('conditional move', row['uses'][1]['delta'])

    def test_hi_lo_flow_is_explicit_unresolved_escape(self):
        data, sections = fixture((9 << 26 | 28 << 21 | 16 << 16 | 0xac90,
                                  16 << 21 | 4 << 16 | 24,
                                  2 << 11 | 18))
        row = constructors.observe(data, sections, {'candidate_count': 1})['constructors'][0]
        self.assertEqual(row['prefix_stop'], 'unresolved HI/LO register effects')
        self.assertEqual(row['escapes'][0]['kind'], 'unsupported-register-effects')

    def test_saved_denominator_cannot_hide_candidate(self):
        data, sections = fixture((9 << 26 | 28 << 21 | 4 << 16 | 0xac90,))
        with self.assertRaisesRegex(Invalid, 'denominator differs'):
            constructors.observe(data, sections, {'candidate_count': 0, 'unowned_sites': [], 'unlisted_sites': []})

    def test_known_real_ui_scope_missing_is_incomplete(self):
        data, sections = fixture((9 << 26 | 28 << 21 | 4 << 16 | 0xac90,))
        result = ui_aliases.known_ui_table_contract(data, sections)
        self.assertEqual(result['status'], 'incomplete')
        self.assertIn('00182010', result['missing_sites'])


if __name__ == '__main__':
    unittest.main()
