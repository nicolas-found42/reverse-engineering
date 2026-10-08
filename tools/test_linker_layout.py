"""Public ELF fixture controls for GNU placement, relocation and zero-fill."""
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from linker_layout import CELL, TEXT, check, verify_outputs, verify_relocations
from evidence_common import Incomplete, Invalid
from elf_fixture import Spec, build_elf
from ps2_executables import parse_elf


def output_fixture():
    text = bytearray(60)
    words = {0: 0x8f83ad54, 0x18: 0x3c040028, 0x1c: 0x3c060028,
             0x20: 0x248431a8, 0x24: 0x24c63320, 0x28: 0x0c041622}
    for at, word in words.items():
        struct.pack_into('<I', text, at, word)
    data = bytearray(build_elf([
        Spec(TEXT, bytes(text), flags=6, address=0x1d1800, alignment=8),
        Spec('.fr2_file', bytes(29), flags=2, address=0x2831a8, alignment=8),
        Spec('.fr2_message', bytes(55), flags=2, address=0x283320, alignment=8),
        Spec(CELL, kind=8, flags=3, address=0x290ac4, size=4, alignment=4),
    ], entry=0x1d1800))
    rows = parse_elf(bytes(data))['sections'][1:5]
    program_offset = len(data)
    for row in rows:
        file_size = 0 if row['type'] == 8 else row['size']
        permissions = 4 | (2 if row['flags'] & 1 else 0) | (1 if row['flags'] & 4 else 0)
        data.extend(struct.pack('<8I', 1, row['offset'], row['address'], row['address'],
                                file_size, row['size'], permissions, 8 if row['type'] != 8 else 4))
    struct.pack_into('<I', data, 28, program_offset)
    struct.pack_into('<H', data, 44, 4)
    return bytes(data)


def object_fixture():
    code = bytearray(60)
    words = {0: 0x8f830000, 0x18: 0x3c040000, 0x1c: 0x3c060000,
             0x20: 0x24840000, 0x24: 0x24c60000, 0x28: 0x0c000000}
    for at, word in words.items():
        struct.pack_into('<I', code, at, word)
    names = b'\0misc3d_db_id\0report_error\0'
    # Symbols 1,2: undefined externals; symbols 3,4: section symbols.
    symbols = bytes(16) + struct.pack('<IIIBBH', 1, 0, 4, 17, 0, 0)
    symbols += struct.pack('<IIIBBH', 14, 0, 0, 18, 0, 0)
    symbols += struct.pack('<IIIBBH', 0, 0, 0, 3, 0, 2)
    symbols += struct.pack('<IIIBBH', 0, 0, 0, 3, 0, 3)
    relocations = b''.join(struct.pack('<II', at, (symbol << 8) | kind) for at, symbol, kind in
                          [(0,1,7),(0x18,3,5),(0x20,3,6),(0x1c,4,5),(0x24,4,6),(0x28,2,4)])
    data = bytearray(build_elf([Spec(TEXT,bytes(code),flags=6),
                              Spec('.fr2_file',bytes(29)), Spec('.fr2_message',bytes(55)),
                              Spec('.symtab',symbols,kind=2,flags=0),
                              Spec('.strtab',names,kind=3,flags=0),
                              Spec('.rel.text',relocations,kind=9,flags=0)]))
    struct.pack_into('<H',data,16,1)
    table = struct.unpack_from('<I',data,32)[0]
    struct.pack_into('<I',data,table+4*40+24,5)
    struct.pack_into('<I',data,table+4*40+36,16)
    struct.pack_into('<II',data,table+6*40+24,4,1)
    struct.pack_into('<I',data,table+6*40+36,8)
    return bytes(data)


def mutate_section(data, name, field, value):
    elf = parse_elf(data)
    index = next(i for i,s in enumerate(elf['sections']) if s.get('name') == name)
    changed = bytearray(data)
    struct.pack_into('<I',changed,elf['section_offset']+index*40+field,value)
    return bytes(changed)


class LinkerLayout(unittest.TestCase):
    def test_positive_loadable_layout(self):
        result = verify_outputs(output_fixture())
        self.assertEqual(result['entry'], '001d1800')
        self.assertEqual(result['matched_bytes'], 0)
        self.assertEqual(result['sections'][-1]['file_bytes'], 0)

    def test_missing_program_headers_is_incomplete(self):
        fixture = build_elf([Spec(TEXT, bytes(60), flags=6, address=0x1d1800),
                            Spec(CELL,kind=8,flags=3,address=0x290ac4,size=4,alignment=4)],entry=0x1d1800)
        with self.assertRaisesRegex(Incomplete,'PT_LOAD'):
            verify_outputs(fixture)

    def test_section_placement_alignment_storage_controls(self):
        for section, field, value in [(TEXT,12,0x1d1804),(TEXT,32,4),
                                      (CELL,12,0x290ac8),(CELL,20,8),(CELL,4,1)]:
            with self.subTest(section=section,field=field,value=value):
                with self.assertRaises(Invalid):
                    verify_outputs(mutate_section(output_fixture(),section,field,value))

    def test_wrong_entry_and_machine_flags(self):
        for offset, value, pattern in [(24,0x1d183c,'entry'),(36,0x20924000,'e_flags')]:
            bad = bytearray(output_fixture()); struct.pack_into('<I',bad,offset,value)
            with self.assertRaisesRegex(Invalid,pattern):
                verify_outputs(bytes(bad))

    def test_load_mapping_permissions_and_nobits_controls(self):
        for index, field, value, pattern in [(0,16,59,'file position'),(0,24,4,'permissions'),
                                            (0,28,3,'congruence'),(3,16,4,'NOBITS')]:
            bad = bytearray(output_fixture()); program = parse_elf(bytes(bad))['program_offset']
            struct.pack_into('<I',bad,program+index*32+field,value)
            with self.assertRaisesRegex(Invalid,pattern):
                verify_outputs(bytes(bad))

    def test_missing_section_is_incomplete(self):
        data = mutate_section(output_fixture(),'.fr2_message',0,0)
        with self.assertRaisesRegex(Incomplete,'section missing'):
            verify_outputs(data)

    def test_missing_section_does_not_hide_known_layout_contradiction(self):
        data = mutate_section(output_fixture(),'.fr2_message',0,0)
        data = mutate_section(data,CELL,12,0x290ac8)
        with self.assertRaisesRegex(Invalid,'address/size/storage/flags'):
            verify_outputs(data)

    def test_positive_relocation_replay(self):
        result = verify_relocations(object_fixture(),output_fixture())
        self.assertEqual([r['kind'] for r in result['records']],[7,5,6,5,6,4])
        self.assertEqual(result['matched_bytes'],0)

    def test_wrong_linked_relocation_has_located_diagnostic(self):
        for at in (0,0x18,0x1c,0x20,0x24,0x28):
            data = bytearray(output_fixture()); row = parse_elf(bytes(data))['sections'][1]
            data[row['offset']+at] ^= 1
            with self.subTest(offset=at):
                with self.assertRaisesRegex(Invalid,fr'\+{at:#x} \(vaddr'):
                    verify_relocations(object_fixture(),bytes(data))

    def test_unknown_relocation_is_incomplete(self):
        data = bytearray(object_fixture()); row = parse_elf(bytes(data))['sections'][6]
        data[row['offset']+4] = 99
        with self.assertRaisesRegex(Incomplete,'unsupported relocation kind 99'):
            verify_relocations(bytes(data),output_fixture())

    def test_missing_provenance_is_incomplete_before_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('linker_layout.DECISION',Path(tmp)/'absent.json'):
                with self.assertRaisesRegex(Incomplete,'decision is missing'):
                    check(Path(tmp),Path(tmp))


class GnuPackages(unittest.TestCase):
    def test_binds_archives_and_installed_package_members(self):
        import io
        import tarfile
        from evidence_common import identity, sha256
        from linker_layout_recipe.packages import bind
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); archive_root=root/'gnu-linker-provenance'; archive_root.mkdir()
            tool=root/'mips-linux-gnu-ld'; tool.write_bytes(b'public synthetic linker')
            stream=io.BytesIO()
            with tarfile.open(fileobj=stream,mode='w:xz') as package:
                info=tarfile.TarInfo('./usr/bin/mips-linux-gnu-ld.bfd')
                info.size=tool.stat().st_size
                package.addfile(info,io.BytesIO(tool.read_bytes()))
            payload=stream.getvalue()
            header=f'{"data.tar.xz/":<16}{0:<12}{0:<6}{0:<6}{100644:<8}{len(payload):<10}`\n'.encode()
            path=archive_root/'fixture.deb';path.write_bytes(b'!<arch>\n'+header+payload+(b'\n' if len(payload)%2 else b''))
            decision={'archives':{'fixture.deb':{'identity':identity(path),'url':'fixture'}},
                      'binary_package':'fixture.deb','package_members':{'mips-linux-gnu-ld':
                      {'path':'./usr/bin/mips-linux-gnu-ld.bfd','identity':identity(tool)}},
                      'tool_files':{'mips-linux-gnu-ld':identity(tool)},'source_lineage':'fixture'}
            self.assertEqual(bind(root,decision)['package_members']['mips-linux-gnu-ld']['sha256'],sha256(tool.read_bytes()))
            tool.write_bytes(b'altered linker')
            with self.assertRaisesRegex(Invalid,'installed tool differs'):
                bind(root,decision)
            path.unlink()
            with self.assertRaisesRegex(Incomplete,'archive is missing'):
                bind(root,decision)

    def test_malformed_ar_is_invalid(self):
        from linker_layout_recipe.packages import ar_members
        for data in (b'bad',b'!<arch>\ntruncated'):
            with self.assertRaises(Invalid): ar_members(data)

    def test_missing_archive_does_not_hide_changed_archive(self):
        from evidence_common import identity
        from linker_layout_recipe.packages import bind
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'gnu-linker-provenance').mkdir()
            path = root/'gnu-linker-provenance'/'changed.tar'; path.write_bytes(b'original')
            decision = {'archives': {'missing.tar': {'identity': identity(path)},
                                     'changed.tar': {'identity': identity(path)}}}
            path.write_bytes(b'changed')
            with self.assertRaisesRegex(Invalid, 'archive identity differs'):
                bind(root, decision)


class NativeGnuFixture(unittest.TestCase):
    def test_missing_linker_tool_cannot_hide_available_changed_tool(self):
        from linker_layout import check
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'mips-linux-gnu-objcopy').write_bytes(b'changed required tool')
            with self.assertRaisesRegex(Invalid, 'tool identity differs.*objcopy'):
                check(root / 'game', root)

    def fixture(self):
        data = bytearray(build_elf([
            Spec('.text.gnu_fixture',struct.pack('<5I',0x3c080011,0x25088004,0,0,0),flags=6,address=0x100000),
            Spec('.gnu_fixture_data',bytes(4),flags=3,address=0x108004,alignment=4),
            Spec('.gnu_fixture_bss',kind=8,flags=3,address=0x108008,size=4,alignment=4)],entry=0x100000))
        rows = parse_elf(bytes(data))['sections'][1:4]
        program_offset = len(data)
        for row in rows:
            file_size = 0 if row['type']==8 else row['size']
            data.extend(struct.pack('<8I',1,row['offset'],row['address'],row['address'],
                                    file_size,row['size'],5 if row['flags']==6 else 6,4))
        struct.pack_into('<I',data,28,program_offset); struct.pack_into('<H',data,44,3)
        obj = bytearray(build_elf([]));struct.pack_into('<H',obj,16,1)
        return bytes(obj),bytes(data)

    def test_native_fixture_positive(self):
        from linker_layout_recipe.fixture import verify
        obj,linked = self.fixture()
        self.assertEqual(verify(obj,linked)['output_flags'],'20924001')

    def test_native_fixture_wrong_machine_tag_and_relocation(self):
        from linker_layout_recipe.fixture import verify
        obj,linked = self.fixture()
        wrong = bytearray(obj);struct.pack_into('<I',wrong,36,0x20923001)
        with self.assertRaisesRegex(Invalid,'flags differ'): verify(bytes(wrong),linked)
        wrong = bytearray(linked); row = parse_elf(linked)['sections'][1];wrong[row['offset']] ^= 1
        with self.assertRaisesRegex(Invalid,'carry relocation differs'): verify(obj,bytes(wrong))

    def test_native_fixture_missing_section(self):
        from linker_layout_recipe.fixture import verify
        obj,linked = self.fixture()
        wrong=mutate_section(linked,'.gnu_fixture_bss',0,0)
        with self.assertRaisesRegex(Incomplete,'section missing'): verify(obj,wrong)


if __name__ == '__main__':
    unittest.main()
