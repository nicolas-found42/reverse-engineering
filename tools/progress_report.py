#!/usr/bin/env python3
"""Export pinned structural load-image accounting as objdiff Report v2.

This command cannot import a receipt or award match/completion credit. Only
completion.py validates fresh source builds. Unattributed ranges carry both
mixed and unresolved categories; those category totals overlap.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from evidence_common import Invalid
from matching_ranges import boundary_provenance
from recorded_decisions import read_decisions

ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = 'notes/evidence/fr2-progress/structural-ledger.json'
LEDGER_SHA256 = '7de5d5f22987e82afbecfc7e2d6287d565727b727b4a62137b65f56314762ba1'
HISTORICAL_PATH = 'notes/evidence/fr2-completion/20261008-continuation-summary.json'
CATEGORIES = (('game-owned', 'Game-owned'), ('mixed', 'Mixed'),
              ('substitute', 'Substitute'), ('unresolved', 'Unresolved'))
BYTE_FIELDS = ('total_code', 'matched_code', 'total_data', 'matched_data',
               'complete_code', 'complete_data')
COUNT_FIELDS = ('total_functions', 'matched_functions', 'total_units', 'complete_units')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def empty_measures() -> dict:
    return {**dict.fromkeys(BYTE_FIELDS, '0'), **dict.fromkeys(COUNT_FIELDS, 0)}


def aggregate(units: list[dict]) -> dict:
    return {**{k: str(sum(int(u['measures'][k]) for u in units)) for k in BYTE_FIELDS},
            **{k: sum(u['measures'][k] for u in units) for k in COUNT_FIELDS}}


def validate_ledger(snapshot: dict) -> None:
    if snapshot.get('status') != 'pass':
        raise Invalid('structural inventory did not pass')
    ledger = snapshot['details']
    if ledger['matched_bytes'] != 0 or ledger['substitute_bytes'] != 0:
        raise Invalid('structural inventory cannot earn matching/substitute credit')
    measured = sum(r['length'] for a in ledger['artifacts'] for r in a['ranges'])
    if measured != ledger['file_backed_bytes'] + ledger['zero_fill_bytes']:
        raise Invalid('load-image byte conservation failed')
    owned = 0
    for artifact in ledger['artifacts']:
        previous = -1
        for row in artifact['ranges']:
            address, length = row['address'], row['length']
            if length <= 0 or address < previous:
                raise Invalid('overlapping or empty load-image ranges')
            previous = address + length
            classification = row['classification']
            if classification == 'game_owned':
                if (artifact['artifact'] != 'EE' or row['section'] != '.text'
                        or address != 0x001D1800 or length != 60):
                    raise Invalid('ownership exceeds the recorded ADR-0005 split')
                owned += length
            elif classification != 'mixed_unresolved':
                raise Invalid('unsupported load-image attribution')
    if owned != 60 or ledger['game_owned_bytes'] != owned:
        raise Invalid('owned denominator disagrees with ADR-0005')
    if ledger['unresolved_bytes'] != measured - owned:
        raise Invalid('unresolved-byte conservation failed')


def build_report(snapshot: dict) -> dict:
    validate_ledger(snapshot)
    units = []
    for artifact in snapshot['details']['artifacts']:
        bases = {}
        for row in artifact['ranges']:
            if row['section'] is not None:
                bases.setdefault(row['section'], row['address'])
        for row in artifact['ranges']:
            categories = (['game-owned'] if row['classification'] == 'game_owned'
                          else ['mixed', 'unresolved'])
            name = row['section'] or '<unmapped-load-image>'
            code = name in ('.text', '.vutext', '.init', '.fini') or name.startswith('.text.')
            measures = empty_measures()
            measures['total_code' if code else 'total_data'] = str(row['length'])
            measures['total_units'] = 1
            item = {'name': name, 'size': str(row['length']),
                    'metadata': {'virtual_address': str(row['address'])}}
            if row['section'] is not None:
                item['address'] = str(row['address'] - bases[row['section']])
            metadata = {'complete': False, 'auto_generated': True,
                        'module_name': artifact['artifact'], 'progress_categories': categories}
            if row.get('build_unit'):
                metadata['source_path'] = row['build_unit']
            units.append({'name': f"{artifact['artifact']}/{name}/{row['address']:08x}",
                          'measures': measures, 'sections': [item], 'functions': [],
                          'metadata': metadata})
    categories = [{'id': cid, 'name': name,
                   'measures': aggregate([u for u in units if cid in u['metadata']['progress_categories']])}
                  for cid, name in CATEGORIES]
    return {'version': 2, 'measures': aggregate(units), 'units': units, 'categories': categories}


def outputs(root: Path = ROOT) -> dict[str, str]:
    read_decisions(root)
    path = root / LEDGER_PATH
    if not path.is_file() or digest(path) != LEDGER_SHA256:
        raise Invalid('structural ledger is missing or its recorded pin changed')
    snapshot = json.loads(path.read_text())
    for name, expected in snapshot['source_pins'].items():
        source = root / name
        if not source.is_file() or digest(source) != expected:
            raise Invalid('structural ledger source binding changed: ' + name)
    # The boundary's own cross-file identities remain independently checked.
    if root == ROOT:
        boundary_provenance()
    report = build_report(snapshot)
    history = root / HISTORICAL_PATH
    provenance = {'schema': 'fr2-progress-provenance/v1', 'authority': snapshot['authority'],
                  'ledger_path': LEDGER_PATH, 'ledger_sha256': digest(path),
                  'source_pins': snapshot['source_pins'], 'reproduce': snapshot['command'],
                  'report_match_credit': 0, 'report_completion_credit': 0,
                  'total_load_image_bytes': snapshot['details']['file_backed_bytes'] + snapshot['details']['zero_fill_bytes'],
                  'game_owned_bytes': snapshot['details']['game_owned_bytes'],
                  'unresolved_bytes': snapshot['details']['unresolved_bytes'],
                  'historical_summary': {'path': HISTORICAL_PATH, 'sha256': digest(history),
                                         'authority': 'archived result; not a fresh build verification'},
                  'limits': ['This is a structural section/range inventory, not a function census.',
                             'No game-wide match percentage or fuzzy score is emitted.',
                             'Mixed and unresolved categories overlap; do not add their totals.',
                             'Non-code measures include zero-fill and unmapped load-image bytes.',
                             'The archived 60-byte compiler result is separate from zero fresh match credit.']}
    return {'progress/report.json': json.dumps(report, indent=2) + '\n',
            'progress/provenance.json': json.dumps(provenance, indent=2) + '\n'}


if __name__ == '__main__':
    for name, text in outputs().items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    print('Generated structural Report v2: zero fresh match/completion credit')
