"""Public child controls for complete scoped incoming and pointer domains."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from elf_fixture import Spec, build_elf
from evidence_common import sha256
import misc3d_aliases as aliases


def static_fixture(change=None, omit=()):
    """Hand-authored synthetic dependency/callback sites, not a retail export."""
    words = {}
    immediate = (
        (0x108bf8,35,2,2,0xa8c0), (0x108d64,35,7,7,0xa8c0),
        (0x108dec,35,3,3,0xa8c0), (0x108f04,35,3,3,0xa8c0),
        (0x1083a4,9,28,5,0xa8c0), (0x1083a8,9,0,4,1), (0x1083ac,9,5,2,4),
        (0x1083b8,43,5,0,0), (0x1083bc,43,6,4,0), (0x108478,9,28,3,0xa8c0),
        (0x10847c,9,0,2,1), (0x108480,43,3,2,0), (0x108488,43,3,0,4),
        (0x175594,9,5,5,0x5788), (0x1755b8,9,5,5,0x6300), (0x17584c,9,4,4,0x63a0),
        (0x178268,15,0,12,0x18), (0x178274,9,12,12,0x8650), (0x1782d4,43,29,12,0x28),
        (0x17f598,9,5,5,0xf700), (0x1cb598,9,22,6,0xc018), (0x1cb5cc,9,22,6,0xc018),
        (0x10cdc4,43,28,4,0x8fd0), (0x10cdc8,35,28,2,0x8fd0), (0x1081e4,9,0,5,1),
        (0x10b8ac,9,18,18,1), (0x10b8b4,10,18,2,2), (0x10c744,9,17,17,1),
        (0x10c74c,10,17,2,2), (0x1d1794,35,28,4,0xad5c), (0x1d1798,35,28,5,0xad60),
        (0x181fe0,9,18,17,1), (0x18200c,9,28,1,0xac90), (0x182028,43,16,2,0),
        (0x182078,10,18,2,2), (0x18207c,21,2,0,0xffda), (0x182d18,9,28,16,0xac90),
        (0x182d3c,35,16,4,0), (0x182c34,35,18,2,24), (0x182c38,6,2,0,17),
        (0x182c44,9,28,17,0xac90), (0x182c48,35,17,4,0), (0x182c50,9,17,17,4),
        (0x182c6c,9,16,16,1), (0x182c70,35,18,2,24), (0x182c78,21,2,0,0xfff5),
        (0x182c7c,35,17,4,0),
    )
    registers = (
        (0x108bf0,0,4,4,0,2), (0x108bf4,4,28,2,33,0),
        (0x108d60,4,28,7,33,0), (0x108de8,4,28,3,33,0), (0x108f00,4,28,3,33,0),
        (0x1083b4,2,0,6,45,0), (0x1763a8,5,0,16,45,0), (0x10cdd8,2,0,31,9,0),
        (0x1081bc,0,0,5,45,0), (0x10c384,17,0,5,45,0), (0x10c06c,4,0,17,45,0),
        (0x10b094,0,0,18,45,0), (0x10b098,18,0,4,45,0), (0x10b3d8,18,0,4,45,0),
        (0x10c6a8,0,0,17,45,0), (0x10c73c,17,0,4,45,0),
        (0x181f4c,0,0,18,45,0), (0x181ff4,0,18,16,0,2), (0x182010,1,16,16,33,0),
        (0x18203c,17,0,18,45,0), (0x182d08,4,0,18,45,0), (0x182d10,0,18,20,0,2),
        (0x182d1c,16,20,16,33,0), (0x182bdc,0,0,16,45,0), (0x182c74,16,2,2,42,0),
    )
    for site, op, base, register, value in immediate:
        words[site] = op << 26 | base << 21 | register << 16 | value
    for site, left, right, destination, function, shift in registers:
        words[site] = left << 21 | right << 16 | destination << 11 | shift << 6 | function
    references = []
    for site, opcode, target in ((0x1d3d64,3,0x1d1628), (0x1d17a0,2,0x1318a0),
                                 (0x10b09c,3,0x10c060), (0x175854,3,0x10cdc0)):
        words[site] = opcode << 26 | target >> 2
        if target == 0x1d1628:
            references.append({'from': f'{site:08x}', 'to': '001d1628', 'type': 'UNCONDITIONAL_CALL'})
    for entry, refs in aliases.RELATED_INCOMING.items():
        for site, kind in refs:
            if kind == 'UNCONDITIONAL_CALL':
                words[int(site,16)] = 3 << 26 | int(entry,16) >> 2
    words.update(change or {})
    for site in omit:
        words.pop(site)
    spans = []
    for site in sorted(words):
        if spans and spans[-1][0]+len(spans[-1][1]) == site:
            spans[-1][1].extend(struct.pack('<I',words[site]))
        else:
            spans.append((site,bytearray(struct.pack('<I',words[site]))))
    data = build_elf([Spec(f'.site{site:x}', bytes(payload), flags=6, address=site) for site,payload in spans])
    isolated = {'executable_sha256': sha256(data), 'language': 'r5900:LE:32:default',
                'domains': [{'start': f'{a:08x}', 'end_exclusive': f'{b:08x}',
                             'incoming': [r for r in references if a <= int(r['to'],16) < b]}
                            for a,b in aliases.DOMAINS],
                'related_entry_incoming': [{'entry': entry,'incoming': [{'from':site,'type':kind}for site,kind in refs]}
                                           for entry,refs in aliases.RELATED_INCOMING.items()],
                'gp_sum_saved_context': [{'site': site, 'saved_instruction_present': True}
                                         for site in ('00108bf4','00108d60','00108de8','00108f00')],
                'gp_constructor_saved_context': {'candidate_count': 5, 'unowned_sites': [], 'unlisted_sites': []}}
    return data,isolated


class AliasDomainControls(unittest.TestCase):
    def isolated(self, data, references=()):
        return {'executable_sha256': sha256(data), 'language': 'r5900:LE:32:default',
                'domains': [{'start': f'{a:08x}', 'end_exclusive': f'{b:08x}',
                             'incoming': [ref for ref in references if a <= int(ref['to'], 16) < b]}
                            for a, b in aliases.DOMAINS]}

    def run_child(self, data, isolated):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'game/extracted').mkdir(parents=True)
            (root/'game/extracted/SLES_517.05').write_bytes(data)
            path = root/'isolated.json'
            path.write_text(json.dumps(isolated))
            stream = StringIO()
            argv = ['aliases', str(root/'game'), str(path), '--output', str(root/'output')]
            with patch.object(sys, 'argv', argv), redirect_stdout(stream), \
                 patch.object(aliases, 'EE_CORPUS_SHA256', sha256(data)):
                code = aliases.main()
            receipt = json.loads(Path(json.loads(stream.getvalue())['result']).read_text())
            return code, receipt

    def test_interior_jump_is_reconciled_and_no_closure_is_awarded(self):
        word = 2 << 26 | 0x1d1454 >> 2
        data = build_elf([Spec('.text', struct.pack('<I', word), flags=6, address=0x1000)])
        isolated = self.isolated(data, [{'from': '00001000', 'to': '001d1454',
                                        'type': 'UNCONDITIONAL_JUMP'}])
        code, receipt = self.run_child(data, isolated)
        self.assertEqual(code, 2)
        self.assertEqual(receipt['details']['incoming_domain_status'], 'incomplete')
        self.assertEqual(receipt['details']['direct_transfers'][0]['to'], '001d1454')
        self.assertEqual(receipt['details']['computed_alias_status'], 'conditional_static')
        self.assertIn('open-world-indirect-and-runtime-addresses', receipt['details']['parent_required_unknown'])

    def test_derived_gp_index_records_an_actual_local_access_candidate(self):
        # input 293 -> 4 * 293 + GP - 0x5740 = 0x00290ac4.
        words = (0x24040125, 0x00042080, 0x009c1021, 0x8c42a8c0)
        data = build_elf([Spec('.text', struct.pack('<4I', *words), flags=6, address=0x1000)])
        code, receipt = self.run_child(data, self.isolated(data))
        self.assertEqual(code, 2)
        accesses = receipt['details']['locally_resolved_memory_candidates']
        self.assertEqual(accesses[0]['address'], '00290ac4')
        self.assertEqual(accesses[0]['site'], '0000100c')

    def test_unaligned_body_interior_pointer_is_retained(self):
        data = build_elf([Spec('.data', b'X'+struct.pack('<I', 0x1d184c), flags=3, address=0x2000)])
        code, receipt = self.run_child(data, self.isolated(data))
        self.assertEqual(code, 2)
        self.assertEqual(receipt['details']['all_byte_pointer_literals'][0]['site'], '00002001')
        self.assertFalse(receipt['details']['all_byte_pointer_literals'][0]['aligned'])

    def test_changed_saved_target_fails(self):
        data = build_elf([Spec('.text', struct.pack('<I', 2 << 26 | 0x1d1454 >> 2),
                               flags=6, address=0x1000)])
        isolated = self.isolated(data, [{'from': '00001000', 'to': '001d1458',
                                        'type': 'UNCONDITIONAL_JUMP'}])
        code, receipt = self.run_child(data, isolated)
        self.assertEqual(code, 1)
        self.assertIn('raw direct domain', receipt['diagnostics'][0])

    def test_missing_domains_are_incomplete(self):
        data = build_elf([Spec('.text', b'\0'*4, flags=6, address=0x1000)])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'game/extracted').mkdir(parents=True)
            (root/'game/extracted/SLES_517.05').write_bytes(data)
            stream = StringIO()
            with patch.object(sys, 'argv', ['aliases', str(root/'game'), str(root/'missing'),
                                            '--output', str(root/'output')]), \
                 patch.object(aliases, 'EE_CORPUS_SHA256', sha256(data)), redirect_stdout(stream):
                code = aliases.main()
            self.assertEqual(code, 2)
            self.assertIn('isolated incoming-reference evidence is absent', stream.getvalue())

    def test_complete_static_contract_pass_retains_conditional_parent_limits(self):
        data, isolated = static_fixture()
        code, receipt = self.run_child(data, isolated)
        self.assertEqual(code, 0, receipt['diagnostics'])
        self.assertEqual(receipt['details']['bounded_static_status'], 'pass')
        forms = receipt['details']['conditional_gp_aliases']['forms']
        self.assertEqual(forms[0]['conditions'][0]['ordinary_nonnegative_input'], 293)
        self.assertEqual(forms[1]['conditions'][0]['ordinary_nonnegative_input'], 1172)
        self.assertEqual(receipt['details']['new_attributed_match_bytes'], 0)

    def test_changed_conditional_stride_fails(self):
        data, isolated = static_fixture({0x108bf0: 0x000420c0})
        code, receipt = self.run_child(data, isolated)
        self.assertEqual(code, 1)
        self.assertIn('conditional GP alias equation differs', receipt['diagnostics'][0])

    def test_changed_constructor_stride_fails(self):
        data, isolated = static_fixture({0x182d10: 0x0012a0c0})
        code, receipt = self.run_child(data, isolated)
        self.assertEqual(code, 1)
        self.assertIn('GP derived UI equation/predicate differs', receipt['diagnostics'][0])

    def test_missing_callback_contract_site_remains_incomplete(self):
        data, isolated = static_fixture(omit=(0x1763a8,))
        code, receipt = self.run_child(data, isolated)
        self.assertEqual(code, 2)
        self.assertIn('required conditional alias/consumer instruction sites are absent', receipt['diagnostics'][0])


if __name__ == '__main__':
    unittest.main()
