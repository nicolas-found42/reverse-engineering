"""Structure-only tests for the UI script grammar decoder.

Consumer binding is explicitly incomplete: there is no EE loader/consumer
address pinned in-repo (cf. notes/asset-loader-registry.json `interface-ui`
`unresolved`). The corpus-identity control below keeps #31 C4 honest.
"""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from corpus_contract import corpus_identity  # noqa: E402
from evidence_common import Incomplete  # noqa: E402
from ui_contracts import InvalidUI, parse_ui_script  # noqa: E402

GAME = REPO / "games/ford-racing-2"


class UiScriptGrammar(unittest.TestCase):
    def test_screen_with_button_block_parses(self):
        data = (
            b"\r\n:TYPE UI_TYPE_SCREEN\r\n:OBJECT_ID UI\\START.UI\r\n"
            b":STRETCH_GRAPHIC 1\r\n:TEXTURE_ENUM GRAPHICS\\GAME\\START.PSD\r\n"
            b"\r\n:S{*****>>>\r\n"
            b"\r\n\t:TYPE UI_TYPE_BUTTON\r\n\t:CLEAR 1\r\n\t:FONT 2\r\n"
            b"\t:OBJECT_ID BUTTON1\r\n"
            b"\t:POSITION_END 0.0 0.720833\r\n\t:POSITION_START 0.0 0.720833\r\n"
            b"\t:SIZE 1.0000 0.150000\r\n\t:TIME_LENGTH 0.800000\r\n"
            b"\r\n\t:TYPE UI_TYPE_TEXT\r\n\t:CLEAR 1\r\n"
            b"\t:FONT_COLOUR 64 64 64 255\r\n\t:OBJECT_ID VERSION\r\n"
            b"\t:POSITION_END 0.06 0.05\r\n\t:POSITION_START 0.06 0.05\r\n"
            b"\t:SIZE 1.0000 0.150000\r\n\t:TEXT_JUSTIFY 1\r\n"
            b"\t\r\n:E}*****<<<\r\n"
        )
        parsed = parse_ui_script(data)
        self.assertEqual(len(parsed.blocks), 1)
        self.assertEqual(parsed.blocks[0].records[0].tag, "S")
        self.assertEqual(parsed.blocks[0].records[-1].tag, "E")
        self.assertEqual(parsed.records[0].line_number, 2)

    def test_nested_blocks_and_commented_tags_parse(self):
        data = (
            b"// :TYPE UI_TYPE_GRAPHIC\r\n:TYPE UI_TYPE_SCREEN\r\n"
            b":S{*****>>>\r\n:TYPE UI_TYPE_BUTTON\r\n"
            b":S{*****>>>\r\n:TYPE UI_TYPE_TEXT\r\n:E}*****<<<\r\n"
            b":E}*****<<<\r\n"
        )
        parsed = parse_ui_script(data)
        self.assertEqual(len(parsed.blocks), 2)
        self.assertEqual(parsed.blocks[0].depth, 1)
        self.assertEqual(parsed.blocks[1].depth, 2)
        self.assertEqual(parsed.blocks[1].line_start, 5)

    def test_wrapped_value_continuation_joins(self):
        parsed = parse_ui_script(b":POSITION_START 0.5734375\r\n 0.585000\r\n")
        self.assertEqual(len(parsed.records), 1)
        self.assertEqual(parsed.records[0].tag, "POSITION_START")
        self.assertEqual(parsed.records[0].value, "0.5734375 0.585000")

    def test_bare_value_line_is_rejected(self):
        with self.assertRaises(InvalidUI):
            parse_ui_script(b"0.585000\r\n")

    def test_unbalanced_close_is_rejected(self):
        with self.assertRaises(InvalidUI):
            parse_ui_script(b":TYPE UI_TYPE_SCREEN\r\n:E}*****<<<\r\n")

    def test_unterminated_block_is_rejected(self):
        with self.assertRaises(InvalidUI):
            parse_ui_script(b":TYPE UI_TYPE_SCREEN\r\n:S{*****>>>\r\n")

    def test_changed_corpus_identity_is_incomplete(self):
        """Missing-corpus-identity control: no corpus, no UI grammar claim."""
        if (GAME / "extracted" / "FILES.HDR").is_file():
            self.assertEqual(corpus_identity(GAME)["profile"], "fr2-pal-sles-517.05")
            return
        with self.assertRaises(Incomplete):
            corpus_identity(GAME)

    def test_unchanged_corpus_ui_files_all_parse(self):
        from corpus_binding import Baseline

        try:
            baseline = Baseline(GAME)
        except Incomplete as exc:
            self.skipTest(f"local PAL corpus is absent: {exc}")
        entries = baseline.entries(".ui;1")
        self.assertEqual(len(entries), 45)
        failures = []
        for entry in entries:
            try:
                parse_ui_script(entry.load())
            except InvalidUI as exc:
                failures.append(f"{entry.path}: {exc}")
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
