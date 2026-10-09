# Bounded semantic review inputs

Run deterministic validation before preparing a review. Keep raw output in
ignored receipts and select the actual summary needed for a claim. The builder
never calls a model or changes a review disposition.

```sh
python3 tools/review_payload.py --staged --base origin/main \
  --request-file .scratch/review-request.txt \
  --tests-file .scratch/review-test-excerpt.txt \
  --claims-file .scratch/review-claims.json \
  --output .scratch/review-packets
```

`review-*.json` contain raw per-file diffs for `jev_review`. `claim-*.json` contain
one claim and its evidence for `jev_verify`. The manifest pins the base commit,
accounts for reviewed/excluded paths and lists changed source paths for scoped
semantic searches. Generated outputs are excluded by the existing hygiene
generator's file list, with raw-diff hashes; changed tests remain included.
An individual file that cannot fit intact fails locally rather than being cut.

The claim input is an array of records:

```json
[
  {
    "authority": "structural-report",
    "claim": "The structural report awards zero fresh matching credit.",
    "evidence": [{"id": "structural-measures", "text": "Actual bounded command output goes here."}]
  }
]
```

Use separate records for independent authorities, such as a structural inventory
and a fresh compiler receipt. Evidence is required, kept with its claim and never
silently truncated. A caller supplies real output; the builder does not certify it.

The default provider context is 32,000 tokens, as listed for
[Jev 1.13](https://openrouter.ai/typesafe/jev-1.13/), checked 2026-10-08. The builder
reserves 10,000 tokens for templates and 4,096 for output, and bounds the serialized
payload by UTF-8 bytes as a conservative token upper bound. Use `--budget-file`
with `context_tokens`, `template_reserve_tokens` and `output_reserve_tokens` when
the provider or template differs. Template reserve is a local policy assumption;
it is not an observed provider token count. Tool-level file/claim limits also apply.

Read every packet's disposition. An operational error remains an error; a
well-formed escalation stands. Retain all results and any human disposition.
Use source paths from the manifest for source-security searches, and handle
`jgrep` exit 2 as an error, never as a clean search result.
