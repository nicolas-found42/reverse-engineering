"""Synthetic public controls; real corpus source acceptance stays separate."""
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, Invalid, sha256
import misc3d_loader as loader
from misc3d_loader_recipe.source_build import compare
from misc3d_loader_recipe import source_build


def fixture():
    groups = [(0x1d1408, loader.LOADER_RANGES), (0x11ed90, ((0x11ed90, 0x11ed94),)),
              (0x124f58, ((0x124f58, 0x124f5c),)), (0x125068, ((0x125068, 0x12506c),))]
    stores = dict(zip((0x1d1460, 0x1d14a4, 0x1d14b8, 0x1d14cc, 0x1d14d4),
                      (0x290ac4, 0x290acc, 0x290ac8, 0x290ad0, 0x290ad4)))
    specs, functions, fresh = [], [], []
    for entry, ranges in groups:
        instructions = []
        for start, end in ranges:
            data = bytearray(end-start)
            for site in range(start, end, 4):
                word = ((0x2b << 26) | (28 << 21) | (2 << 16) | ((stores[site]-loader.GP)&0xffff)) if site in stores else 0
                struct.pack_into('<I',data,site-start,word)
                instructions.append({'address':f'{site:08x}', 'bytes':struct.pack('<I',word).hex()})
            specs.append(Spec('.range'+str(start),bytes(data),flags=6,address=start))
        functions.append({'entry':f'{entry:08x}', 'size':len(instructions)*4,'instructions':instructions})
        fresh.append({'entry':f'{entry:08x}', 'bytes':len(instructions)*4,
                      'ranges':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}'}for a,b in ranges], 'incoming':[]})
    data=build_elf(specs)
    common={'executable_sha256':sha256(data),'language':'r5900:LE:32:default'}
    return data,{**common,'functions':functions},{**common,'functions':fresh}


class LoaderObservationTests(unittest.TestCase):
    def setUp(self):
        self.data,self.inventory,self.isolated=fixture()
        self.digest=patch.object(loader,'EE_CORPUS_SHA256',sha256(self.data))
        self.digest.start()
        self.addCleanup(self.digest.stop)

    def test_positive_noncontiguous_scope_excludes_envelope(self):
        result=loader.observe(self.data,self.inventory,self.isolated)
        spans=result['body_ranges']['001d1408']
        self.assertEqual(sum(row['bytes']for row in spans),536)
        self.assertEqual(len(spans),6)
        self.assertEqual(result['new_attributed_match_bytes'],0)

    def test_missing_dependency_is_incomplete(self):
        self.inventory['functions'].pop()
        with self.assertRaisesRegex(Incomplete,'required saved/isolated function missing'):
            loader.observe(self.data,self.inventory,self.isolated)

    def test_missing_dependency_cannot_hide_available_body_contradiction(self):
        self.inventory['functions'].pop()
        self.isolated['functions'][0]['ranges'].pop(0)
        with self.assertRaisesRegex(Invalid,'isolated function body differs'):
            loader.observe(self.data,self.inventory,self.isolated)

    def test_raw_instruction_contradiction_fails(self):
        self.inventory['functions'][0]['instructions'][0]['bytes']='01000000'
        with self.assertRaisesRegex(Invalid,'instruction differs'):
            loader.observe(self.data,self.inventory,self.isolated)

    def test_isolated_incoming_domain_cannot_invent_caller(self):
        self.isolated['functions'][0]['incoming']=[{'from':'00100000','type':'UNCONDITIONAL_CALL'}]
        with self.assertRaisesRegex(Invalid,'incoming calls differ'):
            loader.observe(self.data,self.inventory,self.isolated)

    def test_duplicate_ownership_cannot_hide_in_size(self):
        self.inventory['functions'][0]['instructions'].append(self.inventory['functions'][0]['instructions'][0])
        with self.assertRaisesRegex(Invalid,'duplicate instruction ownership'):
            loader.observe(self.data,self.inventory,self.isolated)


class TerminalOutputTests(unittest.TestCase):
    def fixtures(self):
        retail=build_elf([Spec('.text',b'ABCDEFGH',flags=6,address=0x12c218)])
        linked=build_elf([Spec('.text.fr2_misc3d_loader_terminal',b'ABCDEFGH',flags=6,address=0x12c218)])
        return retail,linked

    def test_positive_has_no_new_ownership_credit(self):
        result=compare(*self.fixtures())
        self.assertEqual(result['candidate_byte_identical_bytes'],8)
        self.assertEqual(result['new_attributed_match_bytes'],0)

    def test_shifted_layout_fails(self):
        retail,_=self.fixtures()
        changed=build_elf([Spec('.text.fr2_misc3d_loader_terminal',b'ABCDEFGH',flags=6,address=0x12c21c)])
        with self.assertRaisesRegex(Invalid,'address/size/bytes differ'):
            compare(retail,changed)

    def test_absent_section_is_incomplete(self):
        retail,_=self.fixtures()
        with self.assertRaisesRegex(Incomplete,'section is absent'):
            compare(retail,build_elf([Spec('.text',b'ABCDEFGH',flags=6,address=0x12c218)]))


class LoaderSourceTests(unittest.TestCase):
    def test_real_source_obeys_synthetic_service_contracts(self):
        with tempfile.TemporaryDirectory()as temp:
            result=loader.source_contract(Path(temp))
        self.assertEqual(result['exit_code'],0)
        self.assertIn('6 scenarios',result['stdout'])

    def test_changed_source_fails_exact_state_pattern(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp)
            changed=root/'changed.c'
            changed.write_text(loader.SOURCE.read_text().replace('*flags |= 32ULL;', '*flags |= 16ULL;'))
            with self.assertRaisesRegex(Invalid,'call/state contract failed'):
                loader.source_contract(root,changed)

    def test_missing_decision_is_incomplete(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp)
            with patch.object(loader,'DECISION',root/'missing.json'):
                with self.assertRaisesRegex(Incomplete,'recorded decision is absent'):
                    loader.check(root/'game',root/'missing-inventory',root/'missing-isolated',root/'host')

    def test_existing_source_identity_change_outranks_absent_inputs(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp)
            changed=root/'changed.c'
            changed.write_text('void fr2_misc3d_load(void) {}')
            with patch.object(loader,'SOURCE',changed):
                with self.assertRaisesRegex(Invalid,'input identity differs.*source'):
                    loader.check(root/'game',root/'missing-inventory',root/'missing-isolated',root/'host')


class TerminalProvenanceTests(unittest.TestCase):
    def test_missing_corpus_and_tool_root_are_incomplete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(Incomplete, 'retail executable is absent'):
                source_build.provenance(root/'game', root/'tools')

    def test_available_bad_corpus_outranks_absent_tools(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'game/extracted').mkdir(parents=True)
            (root/'game/extracted/SLES_517.05').write_bytes(b'contradictory executable')
            with self.assertRaisesRegex(Invalid, 'executable identity differs'):
                source_build.provenance(root/'game', root/'tools')

    def test_changed_source_identity_outranks_absent_corpus(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            changed = root/'changed.c'
            changed.write_text('void fr2_misc3d_set_optional_object(void *object) {}')
            with patch.object(source_build, 'SOURCE', changed):
                with self.assertRaisesRegex(Invalid, 'source/recipe identity differs'):
                    source_build.provenance(root/'game', root/'tools')

class TerminalStagingTests(unittest.TestCase):
    def test_named_stage_is_fresh_and_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = source_build.prepare_stage(root, 'repro-first')
            self.assertEqual(first, root/'misc3d-loader-terminal-repro-first')
            first.joinpath('stale.o').write_text('stale')
            second = source_build.prepare_stage(root, 'repro-first')
            self.assertEqual(second, first)
            self.assertFalse(second.joinpath('stale.o').exists())

    def test_unnamed_stage_stays_unique(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertNotEqual(source_build.prepare_stage(root), source_build.prepare_stage(root))
