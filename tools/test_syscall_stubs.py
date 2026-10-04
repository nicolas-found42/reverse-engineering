import unittest

from evidence_common import Invalid
from ps2_syscall_stubs import parse_syscall_header, scan_stubs
from test_text_denominator import BASE, JR_RA, NOP, elf_with
from test_text_references import addr, static_owning

SYSCALL = 0x0000000C


def li_v1(number):
    return 0x24030000 | (number & 0xFFFF)


def stub(number):
    return [li_v1(number), SYSCALL, JR_RA, NOP]


HEADER = """
#define __NR_SetGsCrt                 2
#define __NR_RFU060                   0x3c
#define __NR_SetupThread              __NR_RFU060 // alias
#define __NR_iWakeupThread            (-0x34)
/* block comment */
#define __SYSCALLNR_H__
"""


class ParseHeaderTest(unittest.TestCase):
    def test_numbers_hex_negative_and_aliases_are_read_without_choosing_between_aliases(self):
        table = parse_syscall_header(HEADER)
        self.assertEqual(table[2], ["SetGsCrt"])
        self.assertEqual(table[0x3C], ["RFU060", "SetupThread"])
        self.assertEqual(table[-0x34], ["iWakeupThread"])

    def test_unsupported_right_hand_side_is_invalid(self):
        with self.assertRaises(Invalid):
            parse_syscall_header("#define __NR_Bad (1 << 3)\n")

    def test_alias_of_an_unknown_name_is_invalid(self):
        with self.assertRaises(Invalid):
            parse_syscall_header("#define __NR_A __NR_Missing\n")


class ScanStubsTest(unittest.TestCase):
    def build(self, words, owned):
        data = elf_with(words)
        return data, static_owning(data, owned)

    def test_unowned_stub_gets_its_candidate_name(self):
        data, static = self.build([JR_RA, NOP] + stub(2), owned=range(2))
        result = scan_stubs(data, static, HEADER)
        self.assertEqual(result["stubs"], [{
            "address": f"{addr(2):08x}", "number": 2, "names": ["SetGsCrt"], "ownership": "unowned"}])
        self.assertEqual(result["summary"]["unowned"], 1)

    def test_stub_that_is_exactly_a_saved_function_is_owned(self):
        data, static = self.build(stub(2), owned=range(4))
        self.assertEqual(scan_stubs(data, static, HEADER)["stubs"][0]["ownership"], "saved_function")

    def test_stub_partly_inside_a_larger_function_is_reported_as_partial(self):
        data, static = self.build([JR_RA, NOP] + stub(2), owned=[0, 1, 2])
        self.assertEqual(scan_stubs(data, static, HEADER)["stubs"][0]["ownership"], "partial")

    def test_number_missing_from_the_header_has_no_names(self):
        data, static = self.build([JR_RA, NOP] + stub(99), owned=range(2))
        result = scan_stubs(data, static, HEADER)
        self.assertEqual(result["stubs"][0]["names"], [])
        self.assertEqual(result["summary"]["unknown_number"], 1)

    def test_aliased_number_is_counted_as_ambiguous(self):
        data, static = self.build([JR_RA, NOP] + stub(0x3C), owned=range(2))
        result = scan_stubs(data, static, HEADER)
        self.assertEqual(result["stubs"][0]["names"], ["RFU060", "SetupThread"])
        self.assertEqual(result["summary"]["ambiguous"], 1)

    def test_words_in_another_order_are_not_a_stub(self):
        data, static = self.build([JR_RA, NOP, li_v1(2), JR_RA, SYSCALL, NOP], owned=range(2))
        self.assertEqual(scan_stubs(data, static, HEADER)["stubs"], [])

    def test_result_states_its_limits(self):
        data, static = self.build([JR_RA, NOP] + stub(2), owned=range(2))
        result = scan_stubs(data, static, HEADER)
        self.assertEqual(BASE, 0x1000)
        self.assertTrue(any("original" in limit for limit in result["claim_limits"]))


class PinnedHeaderTest(unittest.TestCase):
    def repo(self, directory, text):
        import subprocess
        from pathlib import Path
        root = Path(directory)
        header = root / "ee/kernel/include/syscallnr.h"
        header.parent.mkdir(parents=True)
        header.write_text(text)
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin:/opt/homebrew/bin"}
        for args in (["init", "-q"], ["add", "."], ["commit", "-q", "-m", "x"]):
            subprocess.run(["git", "-C", str(root), *args], check=True, env=env, capture_output=True)
        commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
                                capture_output=True, text=True).stdout.strip()
        return root, header, commit

    def test_header_must_equal_the_pinned_git_object(self):
        import tempfile

        from ps2_syscall_stubs import read_pinned_header
        with tempfile.TemporaryDirectory() as directory:
            root, header, commit = self.repo(directory, HEADER)
            text, sha = read_pinned_header(root, commit)
            self.assertEqual(text, HEADER)
            self.assertEqual(len(sha), 64)
            with self.assertRaises(Invalid):
                read_pinned_header(root, "0" * 40)
            header.write_text(HEADER + "#define __NR_X 1\n")
            with self.assertRaises(Invalid):
                read_pinned_header(root, commit)
