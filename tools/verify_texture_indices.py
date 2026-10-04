#!/usr/bin/env python3
"""Verify bounded model level-zero indexed texture upload interpretations."""
import argparse
from collections import Counter
from pathlib import Path

from corpus_binding import Baseline
from evidence_common import Incomplete, Invalid, sha256, write_result
from ps2_container import parse
from ps2_texture_indices import decode_indices


def check_corpus(game: Path) -> dict:
    baseline = Baseline(game)
    files, failures, counts, profiles = [], [], Counter(), Counter()
    expected = baseline.entries('.ps2;1')
    for entry in expected:
        data = entry.load()
        try:
            textures = parse(data)['textures']['items']
            rows = []
            for texture in textures:
                if texture['format'] not in (3, 4):
                    continue
                pixels = decode_indices(data, texture)
                packed = bool(int(texture['descriptor_field'], 16) & 256)
                counts[str(texture['format'])] += 1
                profiles[f"format{texture['format']}:{'packed' if packed else 'linear'}"] += 1
                rows.append({'name': texture['name'], 'format': texture['format'],
                             'width': texture['width'], 'height': texture['height'],
                             'packed_upload': packed, 'index_bytes': len(pixels),
                             'indices_sha256': sha256(pixels)})
            files.append({'path': entry.path, 'sha256': sha256(data), 'textures': rows})
        except (Invalid, ValueError) as exc:
            failures.append(f'{entry.path}: {exc}')
    return {'provenance': baseline.provenance, 'models': len(expected),
            'indexed_images': sum(counts.values()), 'formats': dict(sorted(counts.items())),
            'upload_profiles': dict(sorted(profiles.items())), 'file_results': files,
            'claim_limits': 'Level-zero index interpretation under the static model upload contract only; no palette color, mip, renderer, original function or hardware execution equivalence claim.',
            'failures': failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/texture-indices'))
    args = parser.parse_args()

    def run():
        if not args.game.is_dir():
            raise Incomplete('game corpus directory is absent')
        return check_corpus(args.game)

    return write_result(args.output, 'texture-indices:corpus', run, [])


if __name__ == '__main__':
    raise SystemExit(main())
