import struct
import unittest

from ip_rails import violations


def elf(machine=8, flags=0x20924001, kind=2) -> bytes:
    header = bytearray(52)
    header[:16] = b"\x7fELF\x01\x01\x01" + bytes(9)
    struct.pack_into("<HHIIIIIHHHHHH", header, 16, kind, machine, 1, 0x100008, 52, 0, flags, 52, 32, 0, 40, 0, 0)
    return bytes(header)


class PathRuleTest(unittest.TestCase):
    def test_boot_executable_names_and_sony_artifact_extensions_are_refused(self):
        for path in ("SLES_517.05", "games/x/SLUS_207.88", "IRX/LIBSD.IRX", "lib/libkernl.a", "build/main.o",
                     "dump/disc.iso", "extracted/FILES.DAT", "games/ford-racing-2/ford-racing-2.bin"):
            self.assertTrue(violations(path, b"text"), path)

    def test_ordinary_repository_paths_pass(self):
        for path in ("tools/matching_diff.py", "docs/LEGAL.md", "games/ford-racing-2/ford-racing-2.cue",
                     "notes/evidence/fr2-static-recovery/results/sections.json"):
            self.assertEqual(violations(path, b"ordinary text\n"), [], path)


class BypassTest(unittest.TestCase):
    def test_case_and_missing_dot_do_not_evade_the_path_rules(self):
        for path in ("x.ISO", "lib/X.Irx", "SLES_51705", "dump/Disc.IMG"):
            self.assertTrue(violations(path, b"text"), path)

    def test_a_mips_elf_is_refused_even_with_zeroed_flags_or_a_late_stamp(self):
        self.assertTrue(violations("t.dat", elf(flags=0)))
        blob = b"\x80" * 9000 + b"PsIIlibkernl2550"
        self.assertTrue(violations("t.dat", blob))


class ContentRuleTest(unittest.TestCase):
    def test_an_ee_elf_is_refused_whatever_its_name(self):
        found = violations("tools/innocent.dat", elf())
        self.assertTrue(any("ELF" in reason for reason in found), found)

    def test_a_mips_object_with_the_ee_machine_bits_is_refused(self):
        self.assertTrue(violations("x.bin.txt", elf(kind=1, flags=0x00920000)))

    def test_an_elf_for_another_machine_is_not_a_ps2_artifact(self):
        self.assertEqual(violations("tools/helper", elf(machine=62, flags=0)), [])

    def test_a_sony_library_stamp_in_a_binary_blob_is_refused(self):
        blob = b"\0\1\2" + b"PsIIlibkernl2550" + b"\0"
        self.assertTrue(any("Sony" in reason for reason in violations("tools/blob", blob)))

    def test_a_stamp_literal_in_text_source_is_allowed(self):
        source = b'data = b"PsIIlibkernl2550"  # test fixture\n'
        self.assertEqual(violations("tools/test_sdk_stamps.py", source), [])


class TreeScanTest(unittest.TestCase):
    def repo(self, files):
        import subprocess, tempfile
        from pathlib import Path
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        for name, data in files.items():
            (root / name).write_bytes(data)
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        return root

    def test_a_tracked_ee_elf_is_found_even_though_the_hook_never_saw_it(self):
        from ip_rails import tracked_violations
        root = self.repo({"ok.txt": b"fine\n", "notes.dat": elf()})
        self.assertEqual(sorted(tracked_violations(root)), ["notes.dat"])

    def test_a_clean_tree_has_no_violations(self):
        from ip_rails import tracked_violations
        self.assertEqual(tracked_violations(self.repo({"ok.txt": b"fine\n"})), {})


if __name__ == "__main__":
    unittest.main()
