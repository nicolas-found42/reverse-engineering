#!/usr/bin/env python3
"""Read fixed repository decisions; reject changed pins and caller-supplied scope."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from evidence_common import Invalid

ROOT = Path(__file__).resolve().parent.parent
TABLE_PINS = {'flags.tsv': '8831fbab1f06b947faf542b1d299662cd47e800aaca82ffaf8b86a403997c248', 'not_functions.txt': '4aba80c3673f8fd6e062b337cac7e62cb4821f28232b3652de77567eedef1e57', 'sections.tsv': '3642008adbe537b2124e81fbbfa4ee1a2fd4bd322a6d7ab43e288841d49da29a', 'units.tsv': '2ce335a435466ef40cc9c6967e00221ae6e3f7fe984aaa3b7f8fcf22771b66f5'}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_decisions(root: Path = ROOT) -> dict:
    for name, expected in TABLE_PINS.items():
        path = root / 'config' / name
        if not path.is_file():
            raise Invalid('recorded decision table missing: ' + name)
        if digest(path) != expected:
            raise Invalid('recorded decision table pin changed: ' + name)
    def rows(name):
        with (root / 'config' / name).open(newline='') as stream:
            return list(csv.DictReader(stream, delimiter='\t'))
    sections, units, flags = rows('sections.tsv'), rows('units.tsv'), rows('flags.tsv')
    previous = {}
    for row in units:
        start, end = int(row['start'], 16), int(row['end_exclusive'], 16)
        if start >= end or start < previous.get(row['section'], 0):
            raise Invalid('invalid or overlapping recorded unit ranges')
        previous[row['section']] = end
        for field in ('source', 'decision', 'evidence'):
            path = root / row[field]
            if not path.is_file() or digest(path) != row[field + '_sha256']:
                raise Invalid('recorded unit provenance changed: ' + row[field])
    for row in flags:
        path = root / row['probe']
        if not path.is_file() or digest(path) != row['probe_sha256']:
            raise Invalid('compiler probe pin changed')
        probe = json.loads(path.read_text())
        candidate = next((x for x in probe['candidates'] if x['id'] == row['profile']), None)
        if candidate is None or candidate['flags'] != json.loads(row['flags_json']):
            raise Invalid('recorded compiler flags disagree with the probe')
    return {'sections': sections, 'units': units, 'flags': flags}


DECISIONS = read_decisions()
METADATA = tuple(x['section'] for x in DECISIONS['sections'] if x['scope'] == 'excluded')
GAME_OWNED_RANGES = tuple((x['section'], int(x['start'], 16), int(x['end_exclusive'], 16))
                          for x in DECISIONS['units'] if x['scope'] == 'game_owned')
