#!/usr/bin/env python3
"""Real source/layout/provenance controls, retained separately from acceptance."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evidence_common import Incomplete, Invalid, identity, write_result
import misc3d_loader as loader
from misc3d_loader_recipe import source_build
from ps2_executables import parse_elf

BUILD_ARTIFACTS = ('object', 'prepared', 'linked', 'comparison')


def compare_builds(first: dict, second: dict) -> dict:
    """Two clean builds in separate fresh directories must agree byte for byte."""
    report = {'artifacts': {}, 'identical': True}
    for name in BUILD_ARTIFACTS:
        try:
            one, two = first['artifacts'][name], second['artifacts'][name]
        except (KeyError, TypeError) as error:
            raise Incomplete('reproducibility comparison requires artifact ' + name) from error
        same = one['sha256'] == two['sha256'] and one['bytes'] == two['bytes']
        report['artifacts'][name] = {'first_sha256': one['sha256'],
                                     'second_sha256': two['sha256'], 'identical': same}
        report['identical'] = report['identical'] and same
    if first.get('compiler') != second.get('compiler'):
        raise Invalid('clean rebuilds disagree on the recorded compiler identity')
    report['build_directories_differ'] = (
        first['artifacts']['linked']['path'] != second['artifacts']['linked']['path'])
    if not report['identical']:
        raise Invalid('clean rebuilds produced different credited bytes', report)
    return report


def detect_drift(first: dict, changed: dict) -> dict:
    """A changed source build must differ, or the rebuild comparison is vacuous."""
    try:
        one, two = first['artifacts']['linked'], changed['artifacts']['linked']
    except (KeyError, TypeError) as error:
        raise Incomplete('drift detection requires the linked artifacts') from error
    if one['sha256'] == two['sha256']:
        raise Invalid('reproducibility comparison cannot detect a changed source build')
    return {'first_linked_sha256': one['sha256'],
            'changed_linked_sha256': two['sha256'], 'drift_detected': True}


def controls(game: Path, tool_root: Path, inventory: Path, isolated: Path, output: Path) -> dict:
    output.mkdir(parents=True,exist_ok=False)
    results = {}

    def record(name, action):
        folder=output/name
        code=write_result(folder,'misc3d-loader-control-'+name,action,[])
        receipt=next(folder.glob('*/result.json'))
        results[name]={'exit_code':code,'receipt':{'path':str(receipt),**identity(receipt)}}
        return json.loads(receipt.read_text())

    positive=record('real_terminal_source',lambda:source_build.source_build(game,tool_root))
    changed=output/'changed-terminal.c'
    changed.write_text(source_build.SOURCE.read_text().replace('misc3d_optional_object = object;','misc3d_optional_object = 0;'))
    record('changed_terminal_source',lambda:source_build.source_build(game,tool_root,changed))
    record('host_source',lambda:loader.source_contract(output/'host-positive'))
    changed_loader=output/'changed-loader.c'
    changed_loader.write_text(loader.SOURCE.read_text().replace('*flags |= 32ULL;','*flags |= 16ULL;'))
    record('changed_host_source',lambda:loader.source_contract(output/'host-negative',changed_loader))
    if positive['status']=='pass':
        linked_path=Path(positive['details']['artifacts']['linked']['path'])
        data=bytearray(linked_path.read_bytes())
        rows=parse_elf(bytes(data))['sections']
        index=next(i for i,s in enumerate(rows) if s['name']=='.text.fr2_misc3d_loader_terminal')
        table=struct.unpack_from('<I',data,32)[0]
        stride=struct.unpack_from('<H',data,46)[0]
        struct.pack_into('<I',data,table+index*stride+12,0x12c21c)
        shifted=output/'shifted-terminal.elf';shifted.write_bytes(data)
        record('changed_terminal_layout',lambda:source_build.compare((game/'extracted/SLES_517.05').read_bytes(),bytes(data)))
    record('static_positive',lambda:loader.observe((game/'extracted/SLES_517.05').read_bytes(),json.loads(inventory.read_text()),json.loads(isolated.read_text())))
    record('full_frontier',lambda:loader.check(game,inventory,isolated,output/'frontier-host'))
    with patch.object(loader,'DECISION',output/'missing-decision.json'):
        record('missing_provenance',lambda:loader.check(game,inventory,isolated,output/'missing-host'))
    stale=output/'stale-isolated.json'
    value=json.loads(isolated.read_text());value['functions'][0]['ranges'].pop(0)
    stale.write_text(json.dumps(value)+'\n')
    record('stale_provenance',lambda:loader.check(game,inventory,stale,output/'stale-host'))
    record('contradiction_over_missing',lambda:loader.check(game,output/'missing-inventory.json',stale,output/'contradiction-host'))
    record('reproducibility',lambda:compare_builds(
        source_build.source_build(game,tool_root,stage_name='repro-first'),
        source_build.source_build(game,tool_root,stage_name='repro-second')))

    def drift():
        real=source_build.source_build(game,tool_root)
        changed=output/'changed-terminal-drift.c'
        changed.write_text(source_build.SOURCE.read_text().replace(
            'misc3d_optional_object = object;','misc3d_optional_object = 0;'))
        try:
            source_build.source_build(game,tool_root,changed)
        except Invalid as error:
            return detect_drift(real,error.details)
        raise Invalid('changed source build unexpectedly matched the retail terminal bytes')

    record('reproducibility_drift_detected',drift)
    expected={'real_terminal_source':0,'changed_terminal_source':1,'host_source':0,
              'changed_host_source':1,'changed_terminal_layout':1,'static_positive':0,
              'full_frontier':2,'missing_provenance':2,'stale_provenance':1,
              'contradiction_over_missing':1,'reproducibility':0,
              'reproducibility_drift_detected':0}
    failures=[name for name,code in expected.items() if results.get(name,{}).get('exit_code')!=code]
    summary={'scope':'Executed real source, isolated static and two-clean-build reproducibility controls; full loader/alias acceptance remains incomplete.',
             'results':results,'expected_exit_codes':expected,'failures':failures,
             'public_inputs':{name:identity(path)for name,path in [('controls',Path(__file__)),('loader',Path(loader.__file__)),('source_recipe',Path(source_build.__file__)),('decision',loader.DECISION)]}}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game',type=Path);parser.add_argument('tool_root',type=Path)
    parser.add_argument('inventory',type=Path);parser.add_argument('isolated',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=controls(args.game,args.tool_root,args.inventory,args.isolated,args.output)
    print(json.dumps({'failures':result['failures'],'summary':str(args.output/'summary.json')}))
    return 1 if result['failures'] else 0


if __name__=='__main__':
    raise SystemExit(main())
