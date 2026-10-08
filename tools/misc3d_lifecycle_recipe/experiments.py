#!/usr/bin/env python3
"""Retain safe sizes and identities from private exploratory objects, never credit."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence_common import identity
from matching_sections import sections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stages', type=Path, nargs='+')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for stage in args.stages:
        obj = stage / 'lifecycle.o'
        rows.append({'stage': str(stage), 'source': identity(stage / 'lifecycle.c'),
                     'object': identity(obj),
                     'code_section_sizes': {name: section.size for name, section in sections(obj.read_bytes()).items()
                                            if name.startswith('.text.fr2_misc3d_')},
                     'link_script': identity(stage / 'candidate.ld')})
    result = {'schema_version': 1, 'command': sys.argv, 'experiments': rows,
              'claim_limit': 'Post-hoc identity/size measurements only. Compiler flags were exploratory; no source-output acceptance or ownership credit follows. Full private sources and objects remain local.'}
    args.output.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
