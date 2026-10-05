#!/usr/bin/env python3
"""Per-function facts for an IOP IRX, taken from exact relocation sites and the module's own tables.

For each saved function this lists the import stubs it calls (a `jump` relocation aimed at a stub, so no data-flow
guess), the printable strings its `lui`/`addiu` pairs point at, the export slots whose offset is the function entry,
and how many data pointers name the entry. Import names are candidates from the pinned SDK tables, never original
symbols. No module code is run.
"""
import argparse
import json
import re
from pathlib import Path

from evidence_common import Incomplete, write_result
import ecoff_mdebug
import iop_references
import iop_symbols
import ps2_executables
import ps2_irx
import ps2_irx_catalog

PRINTABLE = re.compile(rb'[\x20-\x7e\t\r\n]{5,}\x00')
STRING_LIMIT = 90


def _function_of(inventory: dict) -> dict[int, str]:
    return {int(i['address'], 16): f['entry'] for f in inventory['functions'] for i in f['instructions']}


def build_profile(inventory: dict, refs: list[dict], imports: list[dict], exports: list[dict], image: bytes,
                  procedures: list[dict] | None = None) -> dict:
    owner = _function_of(inventory)
    stubs = {i['stub_text_offset']: i for i in imports}
    entries = {int(f['entry'], 16): f['entry'] for f in inventory['functions']}
    profile = {f['entry']: {'entry': f['entry'], 'name': f.get('name'), 'imports': [], 'strings': [], 'exported_as': [],
                            'data_pointer_references': 0, 'procedure': None} for f in inventory['functions']}
    seen_imports: dict[str, set] = {entry: set() for entry in profile}
    for ref in refs:
        function = owner.get(ref['site'])
        if ref['kind'] == 'jump' and function and ref['target'] in stubs:
            stub = stubs[ref['target']]
            key = (stub['library'], stub['index'])
            if key not in seen_imports[function]:
                seen_imports[function].add(key)
                row = {'library': stub['library'], 'index': stub['index'], 'name': stub.get('candidate_name')}
                if stub.get('name_source'):
                    row['name_source'] = stub['name_source']
                profile[function]['imports'].append(row)
        elif ref['kind'] == 'hi_lo' and function and ref['target'] < len(image):
            match = PRINTABLE.match(image, ref['target'])
            if match:
                text = match.group()[:-1].decode('latin-1')[:STRING_LIMIT]
                if text not in profile[function]['strings']:
                    profile[function]['strings'].append(text)
        elif ref['kind'] == 'word' and function is None and ref['target'] in entries:
            profile[entries[ref['target']]]['data_pointer_references'] += 1
    for procedure in procedures or []:
        entry = entries.get(procedure['linked_address'])
        if entry is not None:
            profile[entry]['procedure'] = {'file': procedure['file'], 'frame_bytes': procedure['frame_bytes'],
                                          'size': procedure['size']}
    unmatched = 0
    for table in exports:
        for index, link in enumerate(table['links']):
            entry = entries.get(link['offset'])
            if entry is None:
                unmatched += 1
            else:
                profile[entry]['exported_as'].append({'library': table['library'], 'index': index})
    functions = [profile[f['entry']] for f in inventory['functions']]
    return {'functions': functions,
            'summary': {'functions': len(functions),
                        'calling_imports': sum(bool(f['imports']) for f in functions),
                        'calling_named_imports': sum(any(i['name'] for i in f['imports']) for f in functions),
                        'with_strings': sum(bool(f['strings']) for f in functions),
                        'exported': sum(bool(f['exported_as']) for f in functions),
                        'with_debug_procedure': sum(f['procedure'] is not None for f in functions),
                        'export_offsets_without_function': unmatched}}


def _symbol_evidence(data: bytes, annotations: list[dict]) -> tuple[list[dict], list[dict], dict]:
    """Observed stub names and linked debug procedures, with the agreement counts against the SDK catalog."""
    elf = ps2_executables.parse_elf(data)
    if not any(s.get('name') == '.symtab' and s['size'] > 16 for s in elf['sections']):
        return annotations, [], {'symbols': 0}
    symbols = iop_symbols.read_symbols(data)
    observed = iop_symbols.stub_names([a['stub_text_offset'] for a in annotations], symbols)
    confirmed = contradicted = newly = 0
    merged = []
    for annotation in annotations:
        name = observed.get(annotation['stub_text_offset'])
        if name is None:
            merged.append(annotation)
            continue
        candidate = annotation.get('candidate_name')
        confirmed += candidate == name
        contradicted += candidate not in (None, name)
        newly += candidate is None
        merged.append({**annotation, 'candidate_name': name, 'name_source': 'module symbol table'})
    evidence = {'symbols': len(symbols), 'stubs_named_by_symbols': len(observed), 'catalog_confirmed': confirmed,
                'catalog_contradicted': contradicted, 'newly_named': newly}
    section = next((s for s in elf['sections'] if s.get('name') == '.mdebug'), None)
    procedures: list[dict] = []
    if section is not None:
        debug = ecoff_mdebug.parse_mdebug(data[section['offset']:section['offset'] + section['size']], file_base=section['offset'])
        linked = iop_symbols.link_procedures(debug['procedures'], symbols)
        procedures = linked['procedures']
        text = next(x for x in elf['sections'] if x.get('name') == '.text')
        frames = iop_symbols.frame_agreement(procedures, data[text['offset']:text['offset'] + text['size']])
        evidence.update({'debug_procedures': len(procedures), 'debug_files': debug['files'], 'frame_check': frames,
                         'file_address_offsets': linked['file_offsets'], 'size_disagreements': linked['size_disagreements']})
    return merged, procedures, evidence


def profile_module(irx: Path, inventory: Path, catalog: dict) -> dict:
    data = irx.read_bytes()
    parsed = ps2_irx.parse_irx(data)
    annotations = ps2_irx_catalog.annotate_irx(data, catalog, source=str(irx))['import_annotations']
    annotations, procedures, evidence = _symbol_evidence(data, annotations)
    elf = ps2_irx.parse_elf(data)['elf']
    load = elf['programs'][1]
    image = data[load['offset']:load['offset'] + load['file_size']]
    result = build_profile(json.loads(inventory.read_text()), iop_references.reference_sites(data),
                           annotations, parsed['exports'], image, procedures)
    result['module'] = {'name': parsed['module']['name'], 'sha256': parsed['sha256']}
    result['symbol_evidence'] = evidence
    result['claim_limits'] = ['Import names are candidates from pinned public SDK tables unless marked as read from the module symbol table.',
                              'Strings and calls come from relocation sites; unrelocated references are not seen.',
                              'Debug procedure facts (file, frame, size) come from the module symbol tables, not from recovered source.',
                              'No function identity, behavior or source is claimed.']
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--irx', type=Path, required=True)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/iop-function-profile'))
    args = parser.parse_args()

    def action() -> dict:
        result = profile_module(args.irx, args.inventory, json.loads(args.catalog.read_text()))
        if not result['functions']:
            raise Incomplete('inventory has no functions', result)
        return result
    return write_result(args.output, 'iop-function-profile', action, [args.irx, args.inventory, args.catalog])


if __name__ == '__main__':
    raise SystemExit(main())
