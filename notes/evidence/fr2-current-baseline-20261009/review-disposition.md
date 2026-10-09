# Independent PR42 review disposition

## Standards

One consequential P1 finding persists: candidate discovery can accept an existing same-token backend and does not bind candidate instance identity. The documented claim cannot exceed the check. Failed token cleanup and partial client registration restoration are P2 followups; stale PID activation refusal is P3 maintenance friction. No Fowler heuristic alone warrants a finding. The earlier review-capacity allegation was not reproduced as a hard violation; template reserve remains an explicitly documented assumption. All 24 original reviewed file-diff hashes bind to the actual PR. Exact-head targeted checks pass 42 tests with zero failures/errors/skips/exclusions.

## Spec

The five retrospective candidates are substantially implemented, but candidate verification and failure cleanup remain incomplete. The spec promises a separate managed backend and temporary-token cleanup; synthetic controls show shared discovery inherits the bootstrap candidate profile on port8090, and start accepts an authenticated existing backend without candidate-instance identity. A mocked failed doctor leaves the bootstrap token placeholder. A mocked clang failure also leaves the doctor placeholder because its cleanup try/finally begins afterwards. These sustain the consequential #43 findings; no actual runtime or credential was accessed.

Fresh targeted checks pass: 42 tests, zero failures/errors/skips/exclusions. They do not exercise these counterexamples. Immutable Git snapshot validation, explicit optional dependency exclusions, bounded raw-diff preparation, pinned primary installation inputs and accurately limited native client discovery otherwise match the requested scope.

Independent packet dispositions: 1 accepted with linked limits; 2 and 3 require changes; 4 accepted with the candidate-identity limit; 5 accepted; 6 requires the missing controls; 7 accepted. The scoped validate.py gate is accepted for its exact snapshot-validation scope and truthful reported historical receipts, but its original escalation and every original distribution remain intact; scoped acceptance cannot resolve packet2/3.

Activation restores the machine configuration as documented; partial client registration rollback remains an additional limitation. It is not treated as failure of that narrower statement. No unintended game completion, corpus exposure or spec expansion is introduced. PR42 already merged; this review supplies disposition and actionable follow-up, not retrospective automatic approval.

Standards: one consequential hard candidate-verification finding, three lifecycle/diagnostic followups. Spec: candidate isolation and cleanup remain incomplete, including the doctor early-failure path; other bounded maintenance scope accepted. Original escalations stand with independent dispositions. PR42 is already merged; issue43 carries concrete repairs and remains open.
