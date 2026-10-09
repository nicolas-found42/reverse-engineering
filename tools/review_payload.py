#!/usr/bin/env python3
"""Build bounded raw-diff review packets and individual claim/evidence packets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from repository_hygiene import GENERATED

ROOT = Path(__file__).resolve().parent.parent
# Conservative byte upper bound, including JSON escaping. Reserve provider prompt/output separately.
DEFAULT_BUDGET = {'context_tokens': 32000, 'template_reserve_tokens': 10000, 'output_reserve_tokens': 4096}


def encoded_size(value):
    return len(json.dumps(value, ensure_ascii=False).encode())


def capacity(budget: dict) -> int:
    if set(budget) != set(DEFAULT_BUDGET) or any(type(x) is not int or x < 0 for x in budget.values()):
        raise ValueError('Budget must contain nonnegative integer context/template/output token counts')
    limit = budget['context_tokens'] - budget['template_reserve_tokens'] - budget['output_reserve_tokens']
    if limit < 512:
        raise ValueError('Provider budget leaves too little input capacity')
    return min(limit, 50000)


def partition(files: list[dict], request: str, tests: str, limit: int) -> list[dict]:
    packets = []
    packet = {'request': request, 'files': []}
    if tests:
        packet['tests'] = tests
    for file in files:
        proposed = dict(packet, files=packet['files'] + [file])
        if encoded_size(proposed) > limit or len(proposed['files']) > 16:
            if packet['files']:
                packets.append(packet)
            packet = {k: v for k, v in packet.items() if k != 'files'}
            packet['files'] = [file]
            if encoded_size(packet) > limit:
                raise ValueError('An intact file diff exceeds the provider budget: ' + file['path'])
        else:
            packet = proposed
    if packet['files']:
        packets.append(packet)
    return packets


def claim_packets(records: list[dict], limit: int) -> list[dict]:
    packets = []
    for record in records:
        if set(record) != {'claim', 'authority', 'evidence'} or not record['authority']:
            raise ValueError('Each claim needs exactly claim, authority and evidence fields')
        if not isinstance(record['claim'], str) or not 0 < len(record['claim']) <= 2000:
            raise ValueError('Claim is missing or exceeds the tool claim limit')
        evidence = record['evidence']
        if not isinstance(evidence, list) or not evidence or len(evidence) > 16:
            raise ValueError('Each claim needs 1..16 evidence items')
        if any(set(x) != {'id', 'text'} or not all(isinstance(v, str) and v for v in x.values()) for x in evidence):
            raise ValueError('Evidence needs nonempty id and text strings')
        packet = {'claims': [record['claim']], 'evidence': evidence}
        if encoded_size(packet) > limit:
            raise ValueError('Claim evidence exceeds the provider budget: ' + record['authority'])
        packets.append(packet)
    return packets


def build(root: Path, base: str, staged: bool, request: str, tests: str, records: list[dict], budget: dict):
    revision = subprocess.check_output(['git', '-C', str(root), 'rev-parse', '--verify',
                                        '--end-of-options', base + '^{commit}'], text=True).strip()
    command = ['git', '-C', str(root), 'diff', '--no-ext-diff', '--no-textconv']
    if staged:
        command.append('--cached')
    names = subprocess.check_output(command + ['--name-only', '-z', revision, '--']).split(b'\0')
    files, excluded, sources = [], [], []
    for raw in names:
        if not raw:
            continue
        path = raw.decode()
        diff = subprocess.check_output(command + [revision, '--', path]).decode()
        if path in GENERATED:
            excluded.append({'path': path, 'reason': 'generated; validated by repository_hygiene',
                             'raw_diff_sha256': hashlib.sha256(diff.encode()).hexdigest()})
            continue
        files.append({'path': path, 'diff': diff})
        if path.endswith(('.py', '.sh', '.java')) or path.startswith('tools/hooks/'):
            sources.append(path)
    limit = capacity(budget)
    reviews = partition(files, request, tests, limit)
    claims = claim_packets(records, limit)
    manifest = {'schema': 'fr2-review-payload/v1', 'base': base, 'base_revision': revision, 'staged': staged,
                'budget': budget, 'maximum_payload_bytes': limit,
                'reviewed_paths': [x['path'] for x in files], 'excluded': excluded,
                'source_paths': sources, 'review_packets': len(reviews), 'claim_packets': len(claims),
                'claim_authorities': [x['authority'] for x in records],
                'limits': ['No judgment is made by the builder; retain all resulting review dispositions.',
                           'Byte count is a conservative token upper bound; provider template reserve must be calibrated.',
                           'Full file diffs are preserved; oversized files fail instead of being truncated.']}
    return manifest, reviews, claims


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--base', default='origin/main')
    parser.add_argument('--staged', action='store_true')
    parser.add_argument('--request-file', required=True, type=Path)
    parser.add_argument('--tests-file', type=Path, help='Bounded actual output excerpt, not the full log')
    parser.add_argument('--claims-file', type=Path)
    parser.add_argument('--budget-file', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    budget = json.loads(args.budget_file.read_text()) if args.budget_file else DEFAULT_BUDGET
    records = json.loads(args.claims_file.read_text()) if args.claims_file else []
    manifest, reviews, claims = build(args.root, args.base, args.staged, args.request_file.read_text(),
                                     args.tests_file.read_text() if args.tests_file else '', records, budget)
    args.output.mkdir(parents=True, exist_ok=False)
    for kind, packets in [('review', reviews), ('claim', claims)]:
        for i, packet in enumerate(packets, 1):
            (args.output / f'{kind}-{i:03}.json').write_text(json.dumps(packet, indent=2) + '\n')
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'reviews': len(reviews), 'claims': len(claims), 'excluded': len(manifest['excluded']),
                      'maximum_payload_bytes': manifest['maximum_payload_bytes'], 'output': str(args.output)}))


if __name__ == '__main__':
    main()
