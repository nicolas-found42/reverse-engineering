"""Exercise the pinned GNU assembler's native R5900 tag and linker HI/LO carry."""
from __future__ import annotations
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

from evidence_common import Incomplete, Invalid, identity
from ps2_executables import parse_elf

RECIPE = Path(__file__).resolve().parent


def verify(object_data: bytes, linked_data: bytes) -> dict:
    obj, elf = parse_elf(object_data), parse_elf(linked_data)
    if obj['type'] != 1 or elf['type'] != 2 or obj['flags'] != 0x20924001 or elf['flags'] != 0x20924001:
        raise Invalid('GNU fixture object/output R5900 machine/flags differ')
    if elf['entry'] != 0x100000:
        raise Invalid('GNU fixture entry differs')
    sections = {s.get('name', ''): s for s in elf['sections']}
    for name, address, size, kind in [('.text.gnu_fixture',0x100000,20,1),
                                     ('.gnu_fixture_data',0x108004,4,1),
                                     ('.gnu_fixture_bss',0x108008,4,8)]:
        if name not in sections:
            raise Incomplete('GNU fixture section missing: '+name)
        row = sections[name]
        if (row['address'],row['size'],row['type']) != (address,size,kind):
            raise Invalid('GNU fixture placement/storage differs: '+name)
        loads = [p for p in elf['programs'] if p['type'] == 1 and p['virtual_address'] <= address
                 and address+size <= p['virtual_address']+p['memory_size']]
        if len(loads) != 1:
            raise Invalid('GNU fixture PT_LOAD coverage differs: '+name)
        load = loads[0]; relative = address-load['virtual_address']
        if kind == 8:
            if relative < load['file_size']:
                raise Invalid('GNU fixture NOBITS overlaps load payload')
        elif row['offset'] != load['offset']+relative or relative+size > load['file_size']:
            raise Invalid('GNU fixture PT_LOAD file mapping differs: '+name)
    text = sections['.text.gnu_fixture']
    high, low = struct.unpack_from('<II',linked_data,text['offset'])
    if (high,low) != (0x3c080011,0x25088004):
        raise Invalid('GNU fixture HI16/LO16 carry relocation differs')
    return {'machine':8,'object_flags':'20924001','output_flags':'20924001','entry':'00100000',
            'hi_lo_carry_target':'00108004','zero_fill_bytes':4,'matched_bytes':0,
            'claim_limit':'Authored public fixture assembled with native GNU r5900 support; not retail code'}


def build(tool_root: Path, decision: dict) -> dict:
    stage = Path(tempfile.mkdtemp(prefix='gnu-machine-fixture-',dir=tool_root))
    for name in ('fixture.s','fixture.ld'):
        path = RECIPE/name
        if identity(path) != decision['fixture_inputs'][name]:
            raise Invalid('GNU machine fixture source identity differs: '+name)
        shutil.copyfile(path,stage/name)
    wrapper = Path(__file__).resolve().parents[1]/'compiler_probe_recipe/docker-linux-exec.sh'
    prefix = ['/bin/bash',str(wrapper),str(tool_root)]
    commands = [[*prefix,'mips-linux-gnu-as','-EL','-march=r5900','-mabi=eabi','-no-pad-sections',
                 '-o',str(stage/'fixture.o'),str(stage/'fixture.s')],
                [*prefix,'mips-linux-gnu-ld','-m','elf32ltsmip','-T',str(stage/'fixture.ld'),
                 '-o',str(stage/'fixture.elf'),str(stage/'fixture.o')]]
    for command in commands:
        try:
            result = subprocess.run(command,capture_output=True,text=True,timeout=120)
        except (OSError,subprocess.TimeoutExpired) as exc:
            raise Incomplete(f'GNU fixture invocation unavailable: {exc}') from exc
        if result.returncode:
            raise Invalid('GNU fixture invocation failed',{'command':command,'stderr':result.stderr[-2000:]})
    contract = verify((stage/'fixture.o').read_bytes(),(stage/'fixture.elf').read_bytes())
    return {'contract':contract,'commands':commands,'artifacts':
            {name:{'path':str(stage/name),**identity(stage/name)} for name in
             ('fixture.s','fixture.ld','fixture.o','fixture.elf')}}
