"""Bind installed compiler components to members of their pinned release archive."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tarfile

from evidence_common import Incomplete, identity
from compiler_probe_recipe.build import DISTRIBUTIONS


def bind_packages(manifest: dict, tool_root: Path) -> list[dict]:
    rows = []
    for candidate in manifest['candidates']:
        name = candidate['id']
        archive_name, expected_hash = DISTRIBUTIONS[name]
        archive = tool_root / archive_name
        if not archive.is_file() or identity(archive)['sha256'] != expected_hash:
            raise Incomplete(f'pinned candidate archive is missing or changed: {name}')
        installed_root = tool_root / 'candidates' / name
        tools = {'driver': candidate['compiler_executable'], **candidate.get('tool_files', {})}
        members = {}
        with tarfile.open(archive) as package:
            for role, file in tools.items():
                path = Path(file)
                if not path.is_relative_to(installed_root):
                    continue  # GNU binutils substitution is separately hashed in phase_tools.
                member_name = path.relative_to(installed_root).as_posix()
                try:
                    stream = package.extractfile(member_name)
                except (KeyError, tarfile.TarError) as exc:
                    raise Incomplete(f'candidate package member unavailable: {name}/{member_name}') from exc
                if stream is None or not path.is_file():
                    raise Incomplete(f'candidate package component missing: {name}/{member_name}')
                with stream:
                    archived = hashlib.sha256(stream.read()).hexdigest()
                installed = identity(path)
                if installed['sha256'] != archived:
                    raise Incomplete(f'installed candidate differs from archive: {name}/{member_name}')
                members[role] = {'member': member_name, **installed}
        rows.append({'candidate': name, 'archive': archive_name, 'sha256': expected_hash, 'members': members,
                     'source_disposition': 'Exact corresponding source/notices remain unresolved under #21.'})
    return rows
