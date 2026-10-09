#!/usr/bin/env python3
"""Check draft publication text against what its cited references say today.

A draft body that cites an external URL, a commit revision, or a pull-request
state is only as accurate as those references. This tool gates the moment
before such text is published: it never edits anything and never approves
content. It is deliberately separate from `repository_hygiene.py`, which checks
already-tracked repository files, because a draft is untracked and mutable.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT = 15
MAX_URLS = 20
UNMERGED_WINDOW = 120


def revisions(text: str) -> list[str]:
    """Full 40-hex commit identifiers, excluding 64-hex digests and URL paths.

    A 40-hex token inside a URL names a remote object, not a commit in this
    repository, so URLs are stripped before the scan.
    """
    return re.findall(
        r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", re.sub(r"https?://\S+", "", text)
    )


def urls(text: str) -> list[str]:
    found = re.findall(r'https?://[^\s)\]<>"\']+', text)
    seen, unique = set(), []
    for url in found:
        url = url.rstrip(".,;:")
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def unmerged_claims(text: str) -> list[int]:
    """Issue numbers asserted as unmerged, each with its own context window."""
    claims = []
    for match in re.finditer(r"#(\d+)", text):
        window = text[match.end() : match.end() + UNMERGED_WINDOW].lower()
        if "not merged" in window or "is not merged" in window:
            claims.append(int(match.group(1)))
    return sorted(set(claims))


def resolve_revision(root: Path, revision: str) -> bool:
    """A cited identifier may name a commit or a tree; either resolves."""
    for kind in ("commit", "tree"):
        result = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", revision + "^{" + kind + "}"],
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True
    return False


def fetch(url: str) -> int:
    """Return the HTTP status, or 0 when the request itself failed."""
    for method in ("HEAD", "GET"):
        try:
            request = Request(
                url, method=method, headers={"User-Agent": "fr2-publish-gate"}
            )
            with urlopen(request, timeout=TIMEOUT) as response:
                return response.status
        except OSError:
            # URLError is an OSError; try the next method, then report failure.
            continue
    return 0


def pr_state(number: int) -> str:
    """Report the tracker state for one number; caller treats failure as unknown."""
    result = subprocess.run(
        ["gh", "pr", "view", str(number), "--json", "state", "--jq", ".state"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.stdout.strip() or "unknown"


def check_body(path: Path, root: Path, *, offline: bool, pr_lookup=None) -> dict:
    """One draft: every reference must resolve, and no merged PR may be called unmerged."""
    if not path.is_file():
        return {
            "path": str(path),
            "status": "incomplete",
            "reason": "draft body is absent: " + str(path),
        }
    text = path.read_text()
    findings, skipped = [], []
    for revision in revisions(text):
        if not resolve_revision(root, revision):
            findings.append(
                {
                    "kind": "unresolved_revision",
                    "value": revision,
                    "detail": "revision does not resolve in this repository",
                }
            )
    if offline:
        skipped.append("external_url_check")
        skipped.append("pull_request_state_check")
    else:
        for url in urls(text)[:MAX_URLS]:
            status = fetch(url)
            if not 200 <= status < 400:
                findings.append(
                    {
                        "kind": "unreachable_url",
                        "value": url,
                        "detail": "HTTP status " + str(status)
                        if status
                        else "request failed",
                    }
                )
        lookup = pr_lookup or (lambda _root, number: pr_state(number))
        for number in unmerged_claims(text):
            state = lookup(root, number)
            if state == "unknown":
                skipped.append("pull_request_state_check:" + str(number))
            elif state == "MERGED":
                findings.append(
                    {
                        "kind": "stale_merge_claim",
                        "value": "#" + str(number),
                        "detail": "text asserts unmerged while the tracker reports MERGED",
                    }
                )
    return {
        "path": str(path),
        "status": "fail" if findings else "pass",
        "findings": findings,
        "skipped": skipped,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--body",
        type=Path,
        action="append",
        required=True,
        help="Draft body to check; repeat for several drafts",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository whose revisions resolve; defaults to this checkout",
    )
    parser.add_argument(
        "--output", type=Path, help="Write a bounded receipt instead of only printing"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip network and tracker checks; deterministic local checks only",
    )
    args = parser.parse_args(argv)
    results = []
    for path in args.body:
        try:
            results.append(check_body(path, args.root, offline=args.offline))
        except (OSError, subprocess.SubprocessError) as error:
            results.append(
                {
                    "path": str(path),
                    "status": "incomplete",
                    "reason": type(error).__name__ + ": " + str(error),
                }
            )
    statuses = {row["status"] for row in results}
    exit_code = 2 if "incomplete" in statuses else 1 if "fail" in statuses else 0
    report = {
        "schema": "fr2-publish-gate/v1",
        "offline": args.offline,
        "drafts": len(results),
        "status": {0: "pass", 1: "fail", 2: "incomplete"}[exit_code],
        "results": results,
    }
    print(json.dumps(report, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
