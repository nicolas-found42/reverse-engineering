# Static RE setup reliability

This records implementation and bounded verification of the five retrospective
candidates: an isolated runtime doctor, explicit optional-test exclusions,
canonical Git snapshot validation, a pinned candidate installer, and bounded
raw-diff review preparation.

The source review base is `717f78df689be4e16ddc891b2def18cbda3ce79d`.
The tested staged code tree is `f0d0013f456ec4ba0485ff6353c2222d59b899f0`;
the final commit also adds these receipts and refreshes generated indexes.
The primary install manifest SHA-256 is
`a7fe7cb8629182653daf72d135b6b146e11dbcdd16e5e3662533f9b451d3bac3`.

## Observed results

[verification.json](verification.json) retains actual structured results:

- Exact staged snapshot: IP, hygiene, Ruff and tests passed; 785 tests run,
  zero failures/errors, 33 skipped tests and three excluded modules.
- Working tree: the same checks passed; 803 tests run, zero failures/errors,
  one skipped test and one excluded optional `typesafe_sdk` module.
- Targeted positive, negative and incomplete controls: 42 tests passed.
  Unexpected imports and repository import typos remain errors; only the
  recorded module/dependency pair may be excluded during discovery.
- A real fresh macOS ARM64 candidate build succeeded without activation.
  ccc CTest passed; the candidate doctor passed ten analysis/rejection controls
  and shared stdio discovery of Ghidra, REA and radare2.
- Nine native discovery checks succeeded. Claude used its existing entries;
  Codex and omp used isolated profiles made from the shared launchers. This
  proves native compatibility, not their live global registration contents.
- Two source-only semantic searches returned exit 1 with no matches: secret
  logging, and replacing the active installation before candidate verification.
  Those results are advisory searches, not proof of absence.

Synthetic analysis/discovery issued no model prompt and required no retail
corpus. These results do not establish game runtime compatibility or full
reconstruction completion. Primary distribution/source/package pins are
recorded; transitive Python/build dependencies remain upstream resolved.
The existing active installation remains in use. The maintained `re-doctor`
wrapper was installed separately; candidate activation was not requested.

## Reproduce

Run from the repository root with the build prerequisites described in
[runtime maintenance](../../../docs/agents/re-setup-maintenance.md). Select
fresh output/destination directories for subsequent runs.

```sh
python3 tools/validate.py --staged --output .scratch/reliability-reproduce/staged
python3 tools/validate.py --output .scratch/reliability-reproduce/local
tools/check.sh test_re_doctor test_re_bootstrap test_re_mcp test_run_tests test_review_payload test_validate test_pre_push
python3 tools/re_bootstrap.py --apply --cache .scratch/setup-2026-10-08 --destination .scratch/reliability-reproduce/candidate
python3 tools/re_doctor.py --discovery --output .scratch/reliability-reproduce/doctor
python3 tools/re_client_discovery.py --output .scratch/reliability-reproduce/native
```

The recorded original candidate is `.scratch/reliability/bootstrap-candidate-6`.
Its full numbered build logs, doctor logs and native transcripts stay ignored.
This committed receipt contains no authentication token, provider credential,
retail corpus bytes or generated decompiler source. The repository tools remain
stdlib-only; external analysis packages live in the separate installation.

## Review disposition

[review.json](review.json) binds every reviewed raw file diff to its SHA-256,
the exact base, packet membership, and complete retained judgment records.
The builder produced seven packets within its conservative 17,904-byte input
capacity; two generated navigation indexes were checked deterministically.
All seven calls completed without truncation and returned advisory `escalate`;
their `safe_to_apply` values range from 0.15 to 0.48. No escalation was retried.

The independent factual verifications are recorded separately. Four original
completion claims were verified with confidence 0.82–1.00. The later local-test
claim was `verified` with confidence 0.72 and action `review`; the deterministic
JSON retains its actual counts. The scoped final completion gate covers
`validate.py` and its changed tests: its three factual claims were verified,
while patch review escalated with `safe_to_apply: 0.48`. That scoped judgment
does not override any of the seven earlier dispositions. Human review remains
required before merge under the invoked Jev policy.

Review preparation uses the committed builder and documented request/test
files, with full intact hunks and a separate evidence authority per claim:

```sh
python3 tools/review_payload.py --base 717f78df689be4e16ddc891b2def18cbda3ce79d --staged --request-file .scratch/reliability/review-request.txt --tests-file .scratch/reliability/review-tests.txt --claims-file .scratch/reliability/completion-claims.json --output .scratch/reliability-reproduce/review
```

This command prepares inputs; it makes no judgment and does not silently drop
oversized files. Review payloads and local logs remain independent authorities;
neither is compiler evidence for target reconstruction.
