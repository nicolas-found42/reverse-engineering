import struct
import unittest

from ecoff_mdebug import parse_mdebug
from evidence_common import Invalid

ST_PROC, ST_END, ST_FILE, ST_GLOBAL, ST_STATIC_PROC = 6, 8, 11, 1, 14
SC_TEXT, SC_UNDEFINED, SC_NIL = 1, 6, 0


def symr(iss, value, st, sc, index=0):
    return struct.pack("<IIi", iss, value, st | (sc << 6) | (index << 12))


def pdr(adr, isym, regmask=0, regoffset=0, frameoffset=0, framereg=29, pcreg=31):
    return struct.pack("<IIIIIIIIiHHIII", adr, isym, 0, regmask, regoffset, 0, 0, 0, frameoffset, framereg, pcreg, 0, 0, 0)


def build(files, externals, ss_ext=b"\0"):
    """files: list of dict(name, adr, symbols=[(iss, value, st, sc, index)], procs=[(adr, isym, regmask, frame)], ss=bytes)"""
    ss = b""; sym = b""; pd = b""; fd = b""
    for f in files:
        issbase = len(ss)
        block = f["ss"]
        ss += block
        isymbase = len(sym) // 12
        for s in f["symbols"]:
            sym += symr(*s)
        ipdfirst = len(pd) // 52
        for p in f["procs"]:
            pd += pdr(p[0], p[1], regmask=p[2], frameoffset=p[3])
        fd += struct.pack("<IIIIIIIIIIHHIIIIIII", f["adr"], f["name_off"], issbase, len(block), isymbase, len(f["symbols"]),
                          0, 0, 0, 0, ipdfirst, len(f["procs"]), 0, 0, 0, 0, 0, 0, 0)
    ext = b"".join(struct.pack("<I", 0) + symr(*e) for e in externals)
    header_size = 96
    off = header_size
    cb_pd = off; off += len(pd)
    cb_sym = off; off += len(sym)
    cb_ss = off; off += len(ss)
    cb_ssext = off; off += len(ss_ext)
    cb_fd = off; off += len(fd)
    cb_ext = off; off += len(ext)
    header = struct.pack("<HH23I", 0x7009, 0,
                         0, 0, 0, 0, 0, len(pd) // 52, cb_pd, len(sym) // 12, cb_sym, 0, 0, 0, 0,
                         len(ss), cb_ss, len(ss_ext), cb_ssext, len(files), cb_fd, 0, 0, len(externals), cb_ext)
    return header + pd + sym + ss + ss_ext + fd + ext


FILE = {"name": "m.c", "adr": 0x100, "name_off": 0, "ss": b"m.c\0main\0helper\0",
        "symbols": [(0, 0x100, ST_FILE, SC_TEXT, 0), (4, 0x100, ST_PROC, SC_TEXT, 0), (4, 0x40, ST_END, SC_TEXT, 1),
                    (9, 0x140, ST_STATIC_PROC, SC_TEXT, 0), (9, 0x20, ST_END, SC_TEXT, 3)],
        "procs": [(0x100, 1, 0x80000000, 32), (0x140, 3, 0, 0)]}


class ParseTest(unittest.TestCase):
    def setUp(self):
        blob = build([FILE], [(1, 0x100, ST_PROC, SC_TEXT)], ss_ext=b"\0main\0")
        self.result = parse_mdebug(blob)

    def test_files_have_names_and_addresses(self):
        self.assertEqual([(f["name"], f["address"]) for f in self.result["files"]], [("m.c", 0x100)])

    def test_procedures_take_name_address_size_and_frame_from_their_symbols(self):
        procs = {p["name"]: p for p in self.result["procedures"]}
        self.assertEqual(procs["main"]["address"], 0x100)
        self.assertEqual(procs["main"]["size"], 0x40)
        self.assertEqual(procs["main"]["frame_bytes"], 32)
        self.assertEqual(procs["main"]["saved_register_mask"], 0x80000000)
        self.assertEqual(procs["main"]["file"], "m.c")
        self.assertEqual(procs["helper"]["address"], 0x140)
        self.assertEqual(procs["helper"]["size"], 0x20)
        self.assertEqual(procs["helper"]["static"], True)
        self.assertEqual(procs["main"]["static"], False)

    def test_external_symbols_get_names_from_the_external_string_table(self):
        self.assertEqual(self.result["externals"], [{"name": "main", "value": 0x100, "symbol_type": 6, "storage_class": 1, "file_index": 0}])

    def test_header_counts_are_reported(self):
        self.assertEqual(self.result["header"]["procedures"], 2)
        self.assertEqual(self.result["header"]["files"], 1)


class RejectTest(unittest.TestCase):
    def test_bad_magic(self):
        blob = bytearray(build([FILE], []))
        blob[0:2] = b"\x00\x00"
        with self.assertRaises(Invalid):
            parse_mdebug(bytes(blob))

    def test_a_region_past_the_end_of_the_data(self):
        blob = build([FILE], [])
        with self.assertRaises(Invalid):
            parse_mdebug(blob[:-8])

    def test_a_procedure_symbol_index_out_of_range(self):
        bad = dict(FILE, procs=[(0x100, 99, 0, 0)])
        with self.assertRaises(Invalid):
            parse_mdebug(build([bad], []))


if __name__ == "__main__":
    unittest.main()
