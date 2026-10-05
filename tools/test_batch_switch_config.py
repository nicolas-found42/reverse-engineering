import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import unittest

import test_pipeline_walker as fixtures
import seedlib

REPO = Path(__file__).resolve().parent.parent
PIPE = REPO / 'tools/ghidra/experimental/pipeline'


class BatchSwitchConfigTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=REPO / '.scratch', prefix='switch-config-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        with fixtures.SwitchWalkerTest().fixture():
            self.data = seedlib.elf
        executable = self.root / 'games/ford-racing-2/extracted/SLES_517.05'
        executable.parent.mkdir(parents=True)
        executable.write_bytes(self.data)
        self.export = self.root / 'export'
        (self.export / 'decompilation').mkdir(parents=True)
        (self.export / 'inventory.json').write_text(json.dumps({'functions':[], 'inventory_count':0}))
        (self.export / 'coverage.json').write_text(json.dumps({'blocks':[{'name':'.text',
            'undefined_ranges':[{'start':'00100000','end':'001000ff'}], 'unowned_instruction_ranges':[]}]}))
        (self.export / 'decompilation/manifest.json').write_text('{}')
        (self.root / 'seeds.json').write_text('["00100000"]')
        self.config = self.root / 'config.json'

    def run_script(self, name, *args):
        return subprocess.run([sys.executable, str(PIPE / name), *map(str,args)], cwd=self.root,
                              env={**os.environ, 'PYTHONPATH':str(REPO / 'tools')}, capture_output=True, text=True)

    def generate(self):
        run = self.run_script('make_batch_config.py', 'export', 'config.json', 'seeds.json')
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(self.config.read_text())

    def test_generator_carries_the_ordered_switch_pin_into_schema_two(self):
        config = self.generate()
        self.assertEqual(config['schema_version'], 2)
        self.assertEqual(len(config['seeds']), 1)
        self.assertEqual(config['seeds'][0]['jump_tables'][0]['targets'], ['00100024','0010002c'])

    def test_the_last_case_can_jump_back_to_a_shared_return(self):
        data = bytearray(self.data)
        struct.pack_into('<I', data, 0x1000+44, 2 << 26 | (0x100024 >> 2))
        (self.root / 'games/ford-racing-2/extracted/SLES_517.05').write_bytes(data)
        config = self.generate()
        self.assertEqual(len(config['seeds']), 1)
        self.assertEqual(config['seeds'][0]['end'], '00100034')

    def test_the_independent_checker_accepts_a_rederived_switch_pin(self):
        self.generate()
        run = self.run_script('check_batch_config_root.py', 'config.json', 'export', 'checked.json')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads((self.root / 'checked.json').read_text())['status'], 'pass')

    def test_the_independent_checker_rejects_changed_switch_pins(self):
        original = self.generate()
        mutations = {'count':1, 'table':'00250004', 'table_sha256':'0'*64,
                     'targets':['0010002c','00100024'], 'guard_site':'00100004', 'site':'00100018'}
        for key, value in mutations.items():
            config = copy.deepcopy(original)
            config['seeds'][0]['jump_tables'][0][key] = value
            self.config.write_text(json.dumps(config))
            with self.subTest(key=key):
                run = self.run_script('check_batch_config_root.py', 'config.json', 'export', 'checked.json')
                self.assertNotEqual(run.returncode, 0, run.stdout)
                self.assertFalse((self.root / 'checked.json').exists())

    def test_an_extra_unreached_switch_pin_is_rejected(self):
        config = self.generate()
        extra = copy.deepcopy(config['seeds'][0]['jump_tables'][0]);extra['site']='00100024'
        config['seeds'][0]['jump_tables'].append(extra)
        self.config.write_text(json.dumps(config))
        run = self.run_script('check_batch_config_root.py', 'config.json', 'export', 'checked.json')
        self.assertNotEqual(run.returncode, 0)

    def test_a_missing_pin_is_rejected(self):
        config = self.generate();config['seeds'][0]['jump_tables']=[]
        self.config.write_text(json.dumps(config))
        run = self.run_script('check_batch_config_root.py', 'config.json', 'export', 'checked.json')
        self.assertNotEqual(run.returncode, 0)

    def test_the_shared_return_candidate_also_passes_the_independent_check(self):
        self.test_the_last_case_can_jump_back_to_a_shared_return()
        run = self.run_script('check_batch_config_root.py', 'config.json', 'export', 'checked.json')
        self.assertEqual(run.returncode, 0, run.stderr)

    def test_the_checker_rejects_a_pin_whose_base_definition_can_be_skipped(self):
        config=self.generate()
        f=fixtures
        words=[f.beq(f.V0,f.V1,2),f.NOP,f.lui(f.AT,0x25),f.sltiu(f.V1,f.V0,2),f.beq(f.V1,0,6),f.sll(f.V1,f.V0,2),
               f.addu(f.AT,f.AT,f.V1),f.lw(f.V0,0,f.AT),f.NOP,f.jr(f.V0),f.NOP,f.jr(31),f.NOP]
        with f.SwitchWalkerTest().fixture(words=words,targets=[f.BASE+44,f.BASE+44]):data=seedlib.elf
        (self.root / 'games/ford-racing-2/extracted/SLES_517.05').write_bytes(data)
        config['baseline']['executable_sha256']=hashlib.sha256(data).hexdigest()
        row=config['seeds'][0]
        row.update(window_sha256=hashlib.sha256(data[0x1000:0x1034]).hexdigest(),first_word=f'{words[0]:08x}',
                   zero_words=['00100004','00100020','00100028','00100030'])
        row['jump_tables']=[{'site':'00100024','table':'00250000','guard_site':'0010000c','count':2,
                             'targets':['0010002c','0010002c'],'table_sha256':hashlib.sha256(bytes.fromhex('2c0010002c001000')).hexdigest()}]
        self.config.write_text(json.dumps(config))
        run=self.run_script('check_batch_config_root.py','config.json','export','checked.json')
        self.assertNotEqual(run.returncode,0)
        self.assertIn('switch instruction profile not rederived',run.stderr)
