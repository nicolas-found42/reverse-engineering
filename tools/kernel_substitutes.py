#!/usr/bin/env python3
"""Build the recorded kernel substitutes through actual reconstructed consumers.

This is a bounded prerequisite of AC11. Full EE/IOP substitute coverage remains
incomplete; no output from this command earns matching credit.
"""
import argparse
import json
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from judgment_contract import accepted
from ps2_executables import parse_elf

STUBS = {'SignalSema': (0x1eab80, 66), 'FlushCache': (0x1eade0, 100),
         'sceSifDmaStat': (0x1eaf00, 118), 'sceSifSetDma': (0x1eaf20, 119)}
CONSUMERS = {'fr2_dma_copy': 0x11b780, 'fr2_mfile_release': 0x20c940}
# Emitted by the fixed source/compiler/linker recipe; these are substitute integrity
# pins, never evidence of matching the original game-owned consumers.
BUILT_CONSUMERS = {
    'fr2_dma_copy': '20aa121b81875d40fa9a17eaf9ca4111c943a5876fb94e0105076ceb242a9e50',
    'fr2_mfile_release': '3fa1b0b9910e8770c1fd77728c6928a6a3849300b392a15326f6f637e61569a2',
}
TRANSFERS = {'fr2_dma_copy': [0x1eade0, 0x1eaf20, 0x1eaf00],
             'fr2_mfile_release': [0x1eab80]}
CELLS = {'sema': (0x24bad8, bytes(4)), 'marker': (0x24f8e0, b'\xff' * 4),
         'count': (0x24f8e4, bytes(4))}
ROOT = Path(__file__).resolve().parent.parent
RECIPE = ROOT / 'tools/kernel_substitute_recipe'
SOURCE = ROOT / 'reconstruction/ee/system/sdk_consumers.c'
SDK_COMMIT = '2c670453980fcc3fe46ead6399b730b12c8556eb'
TOOL_ARCHIVE_SHA256 = 'ed69330f235d421754196acf866f8590e5f92e8b92571f1c7e05e853900e7622'
IMAGE = 'sha256:10fd7468c52dd2c69367b434738d30ac6e9f5e9ece3ef58e2a1e09edb8b22263'
CORPUS_SHA256 = '216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95'
CONTRACT = ROOT / 'notes/evidence/fr2-ps2sdk-substitute/kernel-consumer-contract.json'
CONTRACT_SHA256 = 'eb398c70524a54e410a379d2a596abdacbc546ca3f0a4ebc7150fd0434f461dc'


def consumer_contract() -> dict:
    """Retained semantic review is source-bound and cannot alter numerical credit."""
    if not CONTRACT.is_file():
        raise Incomplete('kernel consumer contract missing')
    if identity(CONTRACT)['sha256'] != CONTRACT_SHA256:
        raise Invalid('recorded kernel consumer contract changed')
    contract = json.loads(CONTRACT.read_text())
    missing = []
    for name, expected in contract['files'].items():
        path = ROOT / name
        if not path.is_file():
            missing.append(name)
        elif identity(path)['sha256'] != expected:
            raise Invalid('kernel consumer source/evidence changed: ' + name)
    for judgment in contract['judgments']:
        accepted(judgment, judgment['claim'])
    if missing:
        raise Incomplete('kernel consumer source/evidence missing: ' + ', '.join(missing))
    return contract


def span(data: bytes, address: int, length: int) -> bytes:
    sections = [s for s in parse_elf(data)['sections'] if s['type'] == 1
                and s['flags'] & 2 and s['address'] <= address
                and address + length <= s['address'] + s['size']]
    if len(sections) != 1:
        raise Invalid('retail span must have one file-backed section')
    section, = sections
    offset = section['offset'] + address - section['address']
    return data[offset:offset + length]


def verify_outputs(retail: bytes, linked: bytes) -> dict:
    """Public bounded output check; it alone cannot establish build provenance."""
    sections = {}
    elf = parse_elf(linked)
    allowed = {'.text.' + name for name in (*STUBS, *CONSUMERS)} | {
        '.data.fr2_mfile_' + name for name in CELLS}
    for section in elf['sections']:
        if section['name'] in sections:
            raise Invalid('duplicate linked section')
        sections[section['name']] = section
        if section['flags'] & 2 and section['size'] and section['name'] not in allowed:
            raise Invalid('unexpected allocated payload: ' + section['name'])
    missing, outputs = [], {}
    for name, (address, number) in STUBS.items():
        section = sections.get('.text.' + name)
        if section is None:
            missing.append(name)
            continue
        raw = linked[section['offset']:section['offset'] + section['size']]
        expected = struct.pack('<4I', 0x24030000 | number, 12, 0x03e00008, 0)
        if (section['address'] != address or section['type'] != 1
                or section['flags'] != 6 or raw != expected or span(retail, address, 16) != expected):
            raise Invalid(name + ' substitute output or reference differs')
        outputs[name] = {'address': f'{address:08x}', 'bytes': 16,
                         'sha256': sha256(raw), 'disposition': 'substitute, not matched'}
    for name, address in CONSUMERS.items():
        section = sections.get('.text.' + name)
        if section is None:
            missing.append(name)
        elif (section['address'] != address or section['type'] != 1
              or section['flags'] != 6 or not section['size']):
            raise Invalid(name + ' linked consumer layout differs')
        else:
            raw = linked[section['offset']:section['offset'] + section['size']]
            if len(raw) % 4:
                raise Invalid('consumer instruction alignment differs')
            transfers = []
            for offset in range(0, len(raw), 4):
                word, = struct.unpack_from('<I', raw, offset)
                if word >> 26 in (2, 3):
                    target = ((address + offset + 4) & 0xf0000000) | ((word & 0x3ffffff) << 2)
                    transfers.append(target)
            if transfers != TRANSFERS[name]:
                raise Invalid(name + ' consumer transfer bindings differ')
            if sha256(raw) != BUILT_CONSUMERS[name]:
                raise Invalid(name + ' consumer bytes differ from fixed source build')
    for name, (address, expected) in CELLS.items():
        section = sections.get('.data.fr2_mfile_' + name)
        if section is None:
            missing.append('mfile_' + name)
            continue
        raw = linked[section['offset']:section['offset'] + section['size']]
        if (section['address'] != address or section['type'] != 1
                or section['flags'] != 3 or raw != expected or span(retail, address, 4) != expected):
            raise Invalid('mfile_' + name + ' initialized cell differs')
    result = {'matched_bytes': 0, 'substitute_bytes': sum(r['bytes'] for r in outputs.values()),
              'outputs': outputs, 'ac11_status': 'incomplete',
              'claim_limits': ['Four kernel interfaces and two consumers only.',
                               'Consumer code and data remain uncredited.',
                               'No guest cache, DMA or semaphore behavior is observed.']}
    if missing:
        raise Incomplete('Required substitute output/interface missing: ' + ', '.join(missing), result)
    return result


def check(game: Path, sdk_work: Path) -> dict:
    """Always compile fresh from Git source, never consume an installed SDK object."""
    initial = {'matched_bytes': 0, 'ac11_status': 'incomplete'}
    contract = consumer_contract()
    executable = game / 'extracted/SLES_517.05'
    sdk_work = sdk_work.resolve()
    sdk = sdk_work / 'pinned-src'
    archive = sdk_work / 'toolchain/ps2dev-ubuntu-24.04-arm.tar.gz'
    missing = [str(path) for path in (executable, sdk / '.git', archive) if not path.exists()]
    if missing:
        raise Incomplete('Required corpus/SDK inputs missing: ' + ', '.join(missing), initial)
    retail = executable.read_bytes()
    if sha256(retail) != CORPUS_SHA256 or identity(archive)['sha256'] != TOOL_ARCHIVE_SHA256:
        raise Invalid('corpus or permitted tool archive identity differs', initial)
    for row in contract['retail_ranges']:
        raw = span(retail, int(row['entry'], 16), row['verified_instruction_bytes'])
        if sha256(raw) != row['corpus_instruction_sha256']:
            raise Invalid('recorded consumer/reference range differs', initial)
    source_paths = ['LICENSE', 'ee/kernel/src/kernel.S', 'ee/kernel/include', 'common/include']
    def invoke(argv, *, cwd=None, timeout=30, log=None):
        try:
            run = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Incomplete('substitute build command unavailable: ' + type(exc).__name__, initial) from exc
        if log is not None:
            log.with_suffix('.stdout').write_bytes(run.stdout)
            log.with_suffix('.stderr').write_bytes(run.stderr)
        if run.returncode:
            raise Invalid('substitute build command failed',
                          {**initial, 'argv': argv, 'stderr': run.stderr.decode(errors='replace')[-4000:]})
        return run.stdout
    observed = invoke(['git', '-C', str(sdk), 'rev-parse', 'HEAD']).decode().strip()
    if observed != SDK_COMMIT:
        raise Invalid('pinned ps2sdk revision differs', initial)
    invoke(['git', '-C', str(sdk), 'diff', '--exit-code', 'HEAD', '--', *source_paths])
    observed_image = invoke(['docker', 'image', 'inspect', IMAGE, '--format', '{{.Id}}']).decode().strip()
    if observed_image != IMAGE:
        raise Invalid('substitute build image identity differs', initial)
    staging = Path(tempfile.mkdtemp(prefix='kernel-substitutes-', dir=sdk_work))
    (staging / 'sdk').mkdir()
    source_archive = staging / 'sdk-source.tar'
    source_archive.write_bytes(invoke(['git', '-C', str(sdk), 'archive', SDK_COMMIT, *source_paths]))
    invoke(['tar', '-xf', str(source_archive), '-C', str(staging / 'sdk')])
    public_inputs = [SOURCE, SOURCE.with_suffix('.h'), RECIPE / 'consumer.ld', RECIPE / 'build.sh']
    for path in public_inputs:
        shutil.copyfile(path, staging / path.name)
    argv = ['docker', 'run', '--rm', '--platform', 'linux/arm64', '--network', 'none',
            '-v', str(archive.parent) + ':/toolchain:ro', '-v', str(staging) + ':/out',
            IMAGE, 'sh', '/out/build.sh']
    invoke(argv, timeout=240, log=staging / 'build')
    linked = staging / 'consumer.elf'
    outputs = verify_outputs(retail, linked.read_bytes())
    if (staging / 'undefined.txt').read_text().strip():
        raise Invalid('linked game consumer has unresolved symbols', outputs)
    outputs.update(build_directory=str(staging), command=argv,
                   consumer_contract=identity(CONTRACT), semantic_judgments=contract['judgments'],
                   sdk={'commit': SDK_COMMIT, 'source_archive': identity(source_archive),
                        'license': identity(staging / 'sdk/LICENSE'),
                        'files': {p.relative_to(staging / 'sdk').as_posix(): identity(p)
                                  for p in (staging / 'sdk').rglob('*') if p.is_file()}},
                   build_image=IMAGE, tool_archive=identity(archive),
                   sources={str(path.relative_to(ROOT)): identity(path) for path in public_inputs},
                   artifacts={p.name: identity(p) for p in staging.iterdir() if p.is_file()},
                   compiler_version=(staging / 'compiler-version.txt').read_text(),
                   tool_identities=(staging / 'tools.sha256').read_text(),
                   runtime_packages=(staging / 'runtime-packages.txt').read_text(),
                   runtime_licenses={p.name: identity(p)
                                     for p in (staging / 'runtime-notices').iterdir()})
    (staging / 'receipt.json').write_text(json.dumps(outputs, indent=2) + '\n')
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('sdk_work', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    def action():
        try:
            return check(args.game, args.sdk_work)
        except (Incomplete, Invalid) as exc:
            exc.details.setdefault('matched_bytes', 0)
            exc.details.setdefault('ac11_status', 'incomplete')
            raise
    inputs = [Path(__file__), SOURCE, SOURCE.with_suffix('.h'), CONTRACT,
              RECIPE / 'consumer.ld', RECIPE / 'build.sh', RECIPE / 'Dockerfile']
    return write_result(args.output, 'kernel-substitutes', action,
                        [path for path in inputs if path.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
