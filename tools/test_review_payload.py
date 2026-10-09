"""Controls for bounded reviews, intact diffs and separate claim authorities."""
import unittest
from review_payload import capacity, claim_packets, encoded_size, partition


class ReviewPayloadTests(unittest.TestCase):
    def test_partitions_preserve_every_raw_diff(self):
        files = [{'path': str(i), 'diff': '@@ -1 +1 @@\n-old\n+' + 'new' * 60} for i in range(6)]
        packets = partition(files, 'request', 'actual tests', 600)
        self.assertGreater(len(packets), 1)
        self.assertEqual([x for p in packets for x in p['files']], files)
        self.assertTrue(all(encoded_size(p) <= 600 for p in packets))

    def test_oversized_hunk_is_refused_without_truncation(self):
        with self.assertRaisesRegex(ValueError, 'intact file'):
            partition([{'path': 'large.py', 'diff': 'x' * 1000}], 'request', '', 600)

    def test_empty_diff_has_no_review_packets(self):
        self.assertEqual(partition([], 'request', '', 600), [])

    def test_individual_authorities_keep_individual_evidence(self):
        records = [{'authority': x, 'claim': x + ' fact', 'evidence': [{'id': x, 'text': x + ' evidence'}]}
                   for x in ['structural', 'compiler']]
        packets = claim_packets(records, 600)
        self.assertEqual(len(packets), 2)
        self.assertEqual(packets[0]['evidence'][0]['id'], 'structural')
        with self.assertRaisesRegex(ValueError, 'needs'):
            claim_packets([{'claim': 'unsupported'}], 600)

    def test_invalid_provider_budget_fails(self):
        with self.assertRaises(ValueError):
            capacity({'context_tokens': 100, 'template_reserve_tokens': 50, 'output_reserve_tokens': 50})


if __name__ == '__main__':
    unittest.main()
