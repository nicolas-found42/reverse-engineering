## Agent skills

### Issue tracker

Issues and specs live in this repo’s public GitHub repository; use `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Use the single-context `GLOSSARY.md` and `docs/adr/` layout. See `docs/agents/domain.md`.

### Tests and review

Before publication, run `python3 tools/validate.py --staged`; use `tools/check.sh test_matching` for targeted tests. Review against `CODING_STANDARDS.md`; prepare semantic review inputs using `docs/agents/review-payloads.md`.

### Local RE runtime

For installation, upgrade, runtime controls or client discovery, use `docs/agents/re-setup-maintenance.md`.
