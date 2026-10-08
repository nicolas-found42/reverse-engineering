#!/usr/bin/env python3
"""Run one fresh GNU build and retained artifact/provenance negative controls."""
from __future__ import annotations
import argparse
from pathlib import Path
import struct
import sys
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS))
import linker_layout
from evidence_common import Invalid, identity, write_result
from ps2_executables import parse_elf
from linker_layout_recipe.fixture import verify as verify_fixture


def execute(game: Path, tool_root: Path, output: Path) -> dict:
    built = linker_layout.check(game,tool_root)
    source = Path(built['artifacts']['linked_with_entry']['path'])
    original = source.read_bytes()
    object_data = Path(built['artifacts']['accessor_prepared_object']['path']).read_bytes()
    rows = parse_elf(original)['sections']
    section_table = parse_elf(original)['section_offset']
    text_index = next(i for i,s in enumerate(rows) if s.get('name') == linker_layout.TEXT)
    cell_index = next(i for i,s in enumerate(rows) if s.get('name') == linker_layout.CELL)
    changes = [('displaced_text',section_table+text_index*40+12,0x1d1804),
               ('incorrect_alignment',section_table+text_index*40+32,4),
               ('incorrect_nobits_size',section_table+cell_index*40+20,8),
               ('incorrect_entry',24,0x1d183c),
               ('incorrect_flags',36,0x20924000)]
    controls = []
    def record(name, action, artifact=None):
        destination = output / name
        code = write_result(destination,'gnu-linker-control-'+name,action,
                            [Path(__file__),Path(linker_layout.__file__),linker_layout.DECISION,
                             Path(__file__).with_name('packages.py'),Path(__file__).with_name('fixture.py')])
        receipt = next(destination.glob('*/result.json'))
        controls.append({'control':name,'exit':code,'receipt':str(receipt),
                         'receipt_identity':identity(receipt),
                         'artifact':{'path':str(artifact),**identity(artifact)} if artifact else None})
        return code
    def positive():
        return built
    if record('positive',positive,source) != 0:
        raise Invalid('fresh positive GNU linker control failed')
    for name,offset,value in changes:
        data = bytearray(original)
        struct.pack_into('<I',data,offset,value)
        artifact = source.with_name(name+'.elf'); artifact.write_bytes(data)
        if record(name,lambda data=bytes(data): linker_layout.verify_outputs(data),artifact) != 1:
            raise Invalid('GNU linker negative control was not rejected: '+name)
    wrong = bytearray(original)
    wrong[rows[text_index]['offset']] ^= 1  # relocated GPREL16 low bit
    artifact = source.with_name('wrong_relocation.elf'); artifact.write_bytes(wrong)
    if record('wrong_relocation',lambda: linker_layout.verify_relocations(object_data,bytes(wrong)),artifact) != 1:
        raise Invalid('wrong relocation negative control was not rejected')
    fixture = built['gnu_machine_fixture']['artifacts']
    fixture_object = Path(fixture['fixture.o']['path']).read_bytes()
    fixture_elf = Path(fixture['fixture.elf']['path']).read_bytes()
    wrong_tag = bytearray(fixture_object); struct.pack_into('<I',wrong_tag,36,0x20923001)
    artifact = source.with_name('wrong_gnu_object_tag.o'); artifact.write_bytes(wrong_tag)
    if record('wrong_gnu_object_tag',lambda:verify_fixture(bytes(wrong_tag),fixture_elf),artifact) != 1:
        raise Invalid('wrong native GNU object tag control was not rejected')
    wrong_carry = bytearray(fixture_elf)
    fixture_text = next(s for s in parse_elf(fixture_elf)['sections'] if s.get('name') == '.text.gnu_fixture')
    wrong_carry[fixture_text['offset']] ^= 1
    artifact = source.with_name('wrong_gnu_relocation.elf'); artifact.write_bytes(wrong_carry)
    if record('wrong_gnu_carry',lambda:verify_fixture(fixture_object,bytes(wrong_carry)),artifact) != 1:
        raise Invalid('wrong native GNU carry relocation control was not rejected')
    def missing():
        with patch('linker_layout.DECISION',source.parent/'absent-decision.json'):
            return linker_layout.check(game,tool_root)
    if record('missing_provenance',missing) != 2:
        raise Invalid('missing GNU linker provenance control was not incomplete')
    return {'controls':controls,'matched_bytes':0,'ac06_status':'incomplete',
            'claim_limits':['Artifact mutations are checker controls, not compiler-generated outputs.',
                            'Fresh positive executes the actual compiler and GNU linker.',
                            'The fixed accessor scope does not prove full-image layout.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game',type=Path); parser.add_argument('tool_root',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    return write_result(args.output/'summary','gnu-linker-layout-controls',
                        lambda:execute(args.game,args.tool_root,args.output),[Path(__file__),linker_layout.DECISION])

if __name__ == '__main__':
    raise SystemExit(main())
