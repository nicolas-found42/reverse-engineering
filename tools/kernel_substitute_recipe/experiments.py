#!/usr/bin/env python3
"""Run consumer boundary controls and mutations of a real linked substitute output."""
import argparse
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from evidence_common import Incomplete, Invalid, identity, write_result
from kernel_substitutes import SOURCE, verify_outputs
from ps2_executables import parse_elf


def check(game: Path, linked: Path, work: Path):
    work.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='controls-', dir=work))
    code = SOURCE.read_text()
    substitutions = {
        'positive': None,
        'reversed_semaphore_condition': ('remaining == 0', 'remaining != 0'),
        'wrong_cache_operation': ('FlushCache(0)', 'FlushCache(2)'),
        'reversed_dma_source': ('transfer.src = source;\n    transfer.dest = destination;',
                                'transfer.src = destination;\n    transfer.dest = source;'),
        'missing_poll': ('while (sceSifDmaStat(transaction) >= 0) {}', '(void)transaction;'),
        'zero_size_submitted': ('size <= 0', 'size < 0'),
    }
    host = []
    for name, replacement in substitutions.items():
        source = staging / (name + '.c')
        if replacement and code.count(replacement[0]) != 1:
            raise Invalid('mutation no longer binds one source expression')
        source.write_text(code.replace(*replacement) if replacement else code)
        executable = staging / name
        command = ['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined',
                   '-I', str(SOURCE.parent), str(source),
                   str(Path(__file__).with_name('host_controls.c')), '-o', str(executable)]
        compiled = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if compiled.returncode:
            raise Invalid('host mutation did not compile: ' + name, {'stderr': compiled.stderr})
        run = subprocess.run([str(executable)], cwd=staging, capture_output=True, text=True, timeout=10)
        (staging / (name + '.stderr')).write_text(run.stderr)
        if (run.returncode == 0) != (name == 'positive'):
            raise Invalid('host mutation outcome differs: ' + name)
        host.append({'case': name, 'compile_exit': 0, 'exit_code': run.returncode,
                     'expected': 'pass' if name == 'positive' else 'fail',
                     'source': identity(source), 'command': command})
    retail, original = (game / 'extracted/SLES_517.05').read_bytes(), linked.read_bytes()
    verify_outputs(retail, original)
    elf = parse_elf(original)
    index, section = next((i, s) for i, s in enumerate(elf['sections']) if s['name'] == '.text.FlushCache')
    controls = []
    for name in ('changed_wrapper', 'missing_wrapper', 'shifted_wrapper', 'uncalled_interface',
                 'changed_consumer_preserving_calls'):
        changed = bytearray(original)
        if name == 'changed_wrapper':
            changed[section['offset']] ^= 1
        elif name == 'missing_wrapper':
            # Remove the required named section without giving remaining bytes credit.
            strings = elf['sections'][elf['strings_section']]
            changed[strings['offset'] + section['name_offset'] + 1] = ord('x')
            struct.pack_into('<I', changed, elf['section_offset'] + index * 40 + 8, 0)
            struct.pack_into('<I', changed, elf['section_offset'] + index * 40 + 20, 0)
        elif name == 'shifted_wrapper':
            struct.pack_into('<I', changed, elf['section_offset'] + index * 40 + 12, section['address'] + 4)
        elif name == 'uncalled_interface':
            consumer = next(s for s in elf['sections'] if s['name'] == '.text.fr2_dma_copy')
            changed[consumer['offset']:consumer['offset'] + consumer['size']] = bytes(consumer['size'])
        else:
            consumer = next(s for s in elf['sections'] if s['name'] == '.text.fr2_dma_copy')
            for offset in range(consumer['offset'], consumer['offset'] + consumer['size'], 4):
                word, = struct.unpack_from('<I', changed, offset)
                if word >> 26 not in (2, 3):
                    struct.pack_into('<I', changed, offset, 0)
        expected = 'incomplete' if name == 'missing_wrapper' else 'fail'
        try:
            verify_outputs(retail, bytes(changed))
        except Incomplete:
            actual = 'incomplete'
        except Invalid:
            actual = 'fail'
        else:
            actual = 'pass'
        if actual != expected:
            raise Invalid('linked mutation outcome differs: ' + name)
        controls.append({'case': name, 'status': actual, 'expected': expected})
    return {'authority': 'host_model_and_static_output_controls', 'matched_bytes': 0,
            'host_cases_per_execution': 90, 'host': host, 'linked_controls': controls,
            'linked': identity(linked), 'host_compiler': shutil.which('cc'),
            'guest_observations': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('linked', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    return write_result(args.output, 'kernel-substitute-controls',
                        lambda: check(args.game, args.linked, args.output),
                        [SOURCE, Path(__file__), Path(__file__).with_name('host_controls.c'), args.linked])


if __name__ == '__main__':
    raise SystemExit(main())
