"""Controls for discovery schema, missing evidence fields, links and stale outputs."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evidence_common import Invalid
from repository_hygiene import ROOT, broken_links, check, evidence_entry, validate_schema


class RepositoryHygieneTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ROOT / 'tools/schemas/recomp-v1.json').read_text())
        self.metadata = json.loads((ROOT / '.recomp.json').read_text())

    def test_positive_discovery_metadata(self):
        validate_schema(self.metadata, self.schema, self.schema)

    def test_unknown_fields_and_invalid_types_fail(self):
        self.metadata['claimed_percent'] = 100
        with self.assertRaisesRegex(Invalid, 'unknown property'):
            validate_schema(self.metadata, self.schema, self.schema)
        del self.metadata['claimed_percent']
        self.metadata['type'] = 'complete'
        with self.assertRaises(Invalid):
            validate_schema(self.metadata, self.schema, self.schema)

    def test_missing_maintainer_name_fails(self):
        self.metadata['maintainers'] = [{'link': 'https://example.com'}]
        with self.assertRaisesRegex(Invalid, 'required'):
            validate_schema(self.metadata, self.schema, self.schema)

    def test_unknown_schema_validation_keyword_fails(self):
        with self.assertRaisesRegex(Invalid, 'unsupported schema'):
            validate_schema('value', {'unsupportedLimit': 1}, {})

    def test_incomplete_evidence_fields_remain_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('# Evidence\nNo command or pin established.\n')
            entry = evidence_entry('README.md', root)
            self.assertEqual(len(entry['missing']), 3)
            self.assertEqual(entry['commands'], [])

    def test_command_and_hash_are_copied_with_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pin = 'a' * 64
            (root / 'README.md').write_text('# Evidence\n```sh\npython3 probe.py\n```\nSHA-256 ' + pin + '\n')
            entry = evidence_entry('README.md', root)
            self.assertEqual(entry['commands'], ['python3 probe.py'])
            self.assertEqual(entry['sha256_mentions'][0]['value'], pin)
            self.assertEqual(entry['sha256_mentions'][0]['line'], 5)

    def test_broken_link_fails_but_code_example_is_not_a_link(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('[Missing](missing.md)\n```md\n[Example](not-real.md)\n```\n')
            self.assertEqual(broken_links(root, ['README.md']), ['README.md: missing.md'])

    def test_stale_generated_output_is_rejected(self):
        with patch('repository_hygiene.generated_outputs', return_value={'missing-generated.md': 'required'}):
            self.assertTrue(any('stale' in error for error in check()))


if __name__ == '__main__':
    unittest.main()
