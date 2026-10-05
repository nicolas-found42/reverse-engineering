# Coding standards

Read during review, not implementation. Mechanical rules live in checks (`tools/check.sh`, `tools/ip_rails.py --tree`, CI), not here.

## Claims match evidence

- Every measured number in an ADR, evidence README or issue comment names the committed command that reproduces it. A number with no command is a finding.
- A claim is no stronger than the code enforces: a heuristic guard is described as a heuristic, with its bypasses (opt-in hook, `--no-verify`, repacked containers).
- A pass is a bounded claim. "Identical bytes" is not "matched"; nothing approximate is counted as matched ([ADR-0005](docs/adr/0005-game-owned-sdk-boundary.md)).

## Gates cannot be steered by their caller

- Scope, thresholds and denominators come from a recorded decision in the repo, never from an argument or input file of the check they govern.

## Tests

- Each check ships a positive fixture, a negative control that must fail, and an incomplete case. Build ELF fixtures with `tools/elf_fixture.py`.
