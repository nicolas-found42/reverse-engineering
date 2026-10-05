#!/usr/bin/env python3
"""Count readability and consistency measures over exported decompiler C.

The measures are plain counts that a type, signature or naming improvement
should move: how many `undefined*` types remain, how many `$gp`-relative
operands the decompiler left unresolved, which decompiler warnings occur, how
many call sites pass as many arguments as the callee's header declares, and how
many functions carry a name other than the default. They come from text and are
matched with regular expressions, so header parse failures are reported rather
than hidden. A better count is not a correct type or a recovered source. No game
code is run.
"""
import argparse
import collections
import re
from pathlib import Path

from evidence_common import Incomplete, write_result

COMMENT = re.compile(r'/\*.*?\*/', re.DOTALL)
UNDEFINED = re.compile(r'\bundefined[0-9]*\b')
GP_TOKEN = re.compile(r'\bgp0x[0-9a-f]+|\b[a-zA-Z]{1,6}Gp[0-9a-f]{8}\b')
WARNING = re.compile(r"WARNING: ([^\n]*?)(?: '| \*/|$)", re.MULTILINE)
HEADER_NAME = re.compile(r'(\w+)\s*\(([^)]*)\)$', re.DOTALL)
CALL = re.compile(r'\b([A-Za-z_]\w*)\(')
DEFAULT_NAME = re.compile(r'(?:FUN_[0-9a-f]{8}|entry)$')


def _split_arguments(text: str) -> list[str]:
    parts, depth, current = [], 0, ''
    for char in text:
        depth += (char == '(') - (char == ')')
        if char == ',' and depth == 0:
            parts.append(current)
            current = ''
        else:
            current += char
    return [p for p in parts + [current] if p.strip()]


def _header(text: str) -> tuple[str, int] | None:
    lines = text.splitlines()
    opening = next((i for i, line in enumerate(lines) if line.strip() == '{'), None)
    if opening is None:
        return None
    header = ' '.join(COMMENT.sub('', '\n'.join(lines[:opening])).split())
    match = HEADER_NAME.search(header)
    if not match:
        return None
    params = [p for p in _split_arguments(match[2]) if p.strip() != 'void']
    return match[1], len(params)


def _body(text: str) -> str:
    start = text.find('\n{')
    return text[start:] if start >= 0 else text


def measure_directory(directory: Path) -> dict:
    texts = {path.name: path.read_text(errors='replace') for path in sorted(directory.glob('*.c'))}
    headers: dict[str, int] = {}
    named = failures = 0
    for text in texts.values():
        parsed = _header(text)
        if parsed is None:
            failures += 1
            continue
        headers[parsed[0]] = parsed[1]
        named += not DEFAULT_NAME.match(parsed[0])
    warnings: collections.Counter = collections.Counter()
    undefined = gp_tokens = gp_functions = 0
    arity: collections.Counter = collections.Counter()
    differences: collections.Counter = collections.Counter()
    for text in texts.values():
        undefined += len(UNDEFINED.findall(COMMENT.sub('', text)))
        found = len(GP_TOKEN.findall(text))
        gp_tokens += found
        gp_functions += bool(found)
        warnings.update(m[1].strip() for m in WARNING.finditer(text))
        body = COMMENT.sub('', _body(text))
        for call in CALL.finditer(body):
            name = call[1]
            if name not in headers:
                arity['unknown_callee'] += name.startswith('FUN_')
                continue
            depth, at = 1, call.end()
            while at < len(body) and depth:
                depth += (body[at] == '(') - (body[at] == ')')
                at += 1
            given = len(_split_arguments(body[call.end():at - 1]))
            if given == headers[name]:
                arity['match'] += 1
            else:
                arity['mismatch'] += 1
                differences[str(given - headers[name])] += 1
    return {'functions': len(texts), 'header_parse_failures': failures, 'named_functions': named,
            'undefined_type_tokens': undefined, 'gp_unresolved': {'tokens': gp_tokens, 'functions': gp_functions},
            'warnings': dict(warnings),
            'call_arity': {'match': arity['match'], 'mismatch': arity['mismatch'],
                           'unknown_callee': arity['unknown_callee'],
                           'mismatch_by_difference': dict(differences)},
            'whole_game_decompiled': False,
            'claim_limits': [
                'Counts come from exported pseudocode text matched with regular expressions; see header_parse_failures.',
                'Call arity compares argument count with the callee header, which the decompiler itself inferred.',
                'A better count is not a correct type, signature or recovered source.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--functions', type=Path, required=True, help='export decompilation/functions directory')
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/decompilation-quality'))
    args = parser.parse_args()

    def action() -> dict:
        result = measure_directory(args.functions)
        if not result['functions']:
            raise Incomplete('no exported function files were found', result)
        return result
    return write_result(args.output, 'decompilation-quality', action, [])


if __name__ == '__main__':
    raise SystemExit(main())
