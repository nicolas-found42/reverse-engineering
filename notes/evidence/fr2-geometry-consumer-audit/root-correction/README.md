# Object float cursor correction and disposition

Root independently traced the loader cursor and found the earlier four-byte mapping error before committing the verifier. The agent independently confirmed the correction. Current serialized offsets are `8,12,16,20`, mapping to runtime offsets `12,16,20,24`. At the first float load the pointer has advanced 12 bytes from the row base and the instruction reads -4, so the source is +8. Following loads advance by four bytes. The parser's row base follows the four-byte count word, matching the loader pointer at loop entry.

[The cursor regression](cursor-red.log) fails the old map. It derives effective source addresses from the pinned producer's increment/load sequence independently of the verifier constants. [Five corrected tests](focused-tests.log) pass, including NaN and both infinity encodings in each mapped field, ignored adjacent non-field bits, malformed/bounded spans, and archive-bound corpus. [Pyright](pyright.log) has zero errors, warnings, or informations. Earlier four passing tests and the 269-test full-suite log remain superseded; those passes did not prove source mapping.

[The corrected corpus receipt](corrected-corpus.json) checks all 56 models to exact EOF, 28,453 parser-derived rows and 113,812 consumed binary32 words. All are finite. It preserves the 54 loader68/two measured legacy60 distinction. [A separate real-asset mutation](corrected-anchor.json) changes only an in-memory first-row field at serialized +0x14 to quiet NaN, reports one nonfinite mapped word and failure, and rehashes the original file unchanged. No game code executes.

[Jev r075](r075-cursor-verification.json) erroneously verifies both mutually incompatible maps at low confidence 0.37 and 0.40. Original agent receipts also supported the old map. All judgments remain unchanged. Deterministic instruction arithmetic and the parser cursor establish the corrected mapping and contradict the earlier one; model confidence does not decide byte offsets. No unchanged question was retried for a favorable verdict.

The corrected producer/consumer interpretation is in [the provenance supplement](../object-float-provenance-01.md). Finiteness is an input invariant. It does not identify mesh planes, coordinate axes, angle units, or prove complete VU0/renderer behavior.

The [full Python suite](full-python-suite.log) passes all 270 tests in 43.054 seconds with the corrected mapping. This supersedes the earlier 269-test pass as current verification.
