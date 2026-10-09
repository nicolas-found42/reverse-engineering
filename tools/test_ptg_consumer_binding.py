"""EE consumer binding for PTG texture graphics (issue #28, AC20/AC24 criterion 2).

Seam: EE static consumer facts re-measured from the pinned PAL executable
(`games/ford-racing-2/extracted/SLES_517.05`) must equal the pins in
`notes/evidence/fr2-ptg-body-contracts/variant-census.json` ("consumer"
section). The binding is static only: it proves the EE texture-graphic
loader accepts `.psd`/`.ptg` requests and that every static EE
`GRAPHICS...PSD` request resolves (case-insensitively, extension swapped)
to a corpus `.ptg` file. It claims no palette, tile-pointer, descriptor,
upload, plane-decoding, or lifetime semantics; those stay unresolved.

Skips cleanly when the local corpus or executable is absent.
"""

import hashlib
import json
import re
import struct
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from corpus_binding import Baseline  # noqa: E402
from corpus_contract import corpus_identity  # noqa: E402
from ptg_profile import classify  # noqa: E402

CENSUS_PATH = REPO / "notes/evidence/fr2-ptg-body-contracts/variant-census.json"
GAME = REPO / "games/ford-racing-2"
ELF = GAME / "extracted" / "SLES_517.05"

SEG1_FILE, SEG1_VADDR, SEG1_SIZE = 0x1000, 0x100000, 0x11B188
SEG2_FILE, SEG2_VADDR, SEG2_SIZE = 0x11C200, 0x21B200, 0x753C7


def fo_of_v(v):
    if SEG1_VADDR <= v < SEG1_VADDR + SEG1_SIZE:
        return v - SEG1_VADDR + SEG1_FILE
    if SEG2_VADDR <= v < SEG2_VADDR + SEG2_SIZE:
        return v - SEG2_VADDR + SEG2_FILE
    return None


def code_words(data):
    code = data[SEG1_FILE : SEG1_FILE + SEG1_SIZE]
    return struct.unpack("<%dI" % (len(code) // 4), code[: len(code) // 4 * 4])


def function_span(data, entry_vaddr):
    start = fo_of_v(entry_vaddr)
    for off in range(start, start + 0x2000, 4):
        if struct.unpack("<I", data[off : off + 4])[0] == 0x03E00008:
            return start, off + 8
    raise AssertionError(f"no jr ra terminator after {entry_vaddr:#x}")


def lui_addiu_targets(words):
    """All (code_file_off, target_vaddr) lui/addiu pairs in the code segment."""
    pairs = []
    n = len(words)
    for i, w in enumerate(words):
        if (w >> 26) == 15:
            rt, hi = (w >> 16) & 0x1F, w & 0xFFFF
            for j in range(i + 1, min(i + 9, n)):
                w2 = words[j]
                if (
                    (w2 >> 26) == 9
                    and ((w2 >> 16) & 0x1F) == rt
                    and ((w2 >> 21) & 0x1F) == rt
                ):
                    simm = w2 & 0xFFFF
                    if simm >= 0x8000:
                        simm -= 0x10000
                    pairs.append((SEG1_FILE + 4 * i, (hi << 16) + simm))
                    break
    return pairs


def static_psd_requests(data):
    """Non-format `GRAPHICS...PSD` request strings (raw bytes, in order)."""
    out = []
    for m in re.finditer(rb"GRAPHICS", data):
        raw = data[m.start() : m.start() + 64].split(b"\x00")[0]
        try:
            s = raw.decode("ascii")
        except UnicodeDecodeError:
            continue
        if s == "GRAPHICS" or "%" in s or s.endswith("\\") or len(s) > 60:
            continue
        out.append(s)
    return out


class PtgConsumerBinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (GAME / "extracted" / "FILES.HDR").is_file() or not ELF.is_file():
            raise unittest.SkipTest("local PAL corpus or executable is absent")
        cls.census = json.loads(CENSUS_PATH.read_bytes())
        if "consumer" not in cls.census:
            raise unittest.SkipTest("census has no consumer section yet")
        cls.data = ELF.read_bytes()
        cls.words = code_words(cls.data)
        cls.baseline = Baseline(GAME)

    def test_executable_identity_matches_pin(self):
        pinned = self.census["consumer"]["executable"]
        self.assertEqual(hashlib.sha256(self.data).hexdigest(), pinned["sha256"])
        self.assertEqual(
            corpus_identity(GAME)["profile"], self.census["corpus_profile"]
        )

    def test_loader_function_bytes_match_pin(self):
        pinned = self.census["consumer"]["loader"]
        start, end = function_span(self.data, int(pinned["entry"], 16))
        blob = self.data[start:end]
        self.assertEqual(len(blob) // 4, pinned["words"])
        self.assertEqual(hashlib.sha256(blob).hexdigest()[:16], pinned["sha16"])
        # Entry prologue anchor: addiu sp,sp,-0x30; lui v0,0x23.
        self.assertEqual(blob[:8].hex(), pinned["prologue_hex"])

    def test_extension_comparators_match_pin(self):
        pinned = self.census["consumer"]["extension_check"]
        fo = fo_of_v(int(pinned["psd_string_vaddr"], 16))
        self.assertEqual(self.data[fo : fo + 8], b"psd\x00\x00\x00\x00\x00")
        self.assertEqual(self.data[fo + 8 : fo + 16], b"ptg\x00\x00\x00\x00\x00")

    def test_caller_count_matches_pin(self):
        entry = int(self.census["consumer"]["loader"]["entry"], 16)
        callers = [
            SEG1_FILE + 4 * i
            for i, w in enumerate(self.words)
            if (w >> 26) == 3 and (w & 0x3FFFFFF) * 4 == entry
        ]
        self.assertEqual(len(callers), self.census["consumer"]["callers"])

    def test_every_static_request_resolves_to_corpus_ptg(self):
        requests = static_psd_requests(self.data)
        self.assertEqual(len(requests), self.census["consumer"]["static_requests"])
        names = {e.path for e in self.baseline.entries(".ptg;1")}
        lower = {n.lower(): n for n in names}
        profiles = {}
        for s in requests:
            arch = "/" + s.replace("\\", "/") + ";1"
            ptg = arch[:-5] + "ptg;1"
            hit = lower.get(ptg.lower())
            self.assertIsNotNone(hit, f"EE request has no corpus file: {s}")
            path = GAME / "extracted" / "files" / hit.lstrip("/")
            profile = classify(path.read_bytes())["profile"]
            profiles[profile] = profiles.get(profile, 0) + 1
        self.assertEqual(profiles, self.census["consumer"]["resolved_profiles"])

    def test_ui_init_function_bytes_match_pin(self):
        pinned = self.census["consumer"]["ui_init"]
        start, end = function_span(self.data, int(pinned["entry"], 16))
        blob = self.data[start:end]
        self.assertEqual(len(blob) // 4, pinned["words"])
        self.assertEqual(hashlib.sha256(blob).hexdigest()[:16], pinned["sha16"])

    def test_wrong_extension_requests_have_no_corpus_file(self):
        """Negative control: a non-psd/ptg extension resolves to nothing."""
        names = {e.path for e in self.baseline.entries(".ptg;1")}
        lower = {n.lower(): n for n in names}
        requests = static_psd_requests(self.data)
        sample = requests[0].replace(".PSD", ".XYZ")
        arch = "/" + sample.replace("\\", "/") + ";1"
        xyz = arch[:-5] + "xyz;1"
        self.assertNotIn(xyz.lower(), lower)
        # And the loader's own comparators only accept psd/ptg.
        fo = fo_of_v(
            int(self.census["consumer"]["extension_check"]["psd_string_vaddr"], 16)
        )
        window = self.data[fo : fo + 32]
        self.assertNotIn(b"xyz", window)


if __name__ == "__main__":
    unittest.main()
