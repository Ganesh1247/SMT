# Definition of Done

## Artifact (any document)
- Created from the matching `platform/templates/` file; status marker changed from `TEMPLATE` to `DRAFT`, then `FINAL`.
- Owner named; upstream inputs referenced; open questions listed, not hidden.
- Reviewed by someone other than the author.

## Work slice (code)
- Linked to a requirement ID in the PRD and a task in the delivery plan.
- Tests written first (red → green → refactor); all tests pass.
- No module-boundary violations; no new dependency without a dependency-policy entry.
- Security checklist items for the slice satisfied; no secrets.
- Accessibility acceptance criteria met for UI slices.
- Independent review by `staff-code-reviewer` with no open blocking findings.
- Entry appended to `delivery/G5-build-log/build-log.md` with evidence (test output, screenshots).

## Gate
- Every artifact listed in `governance/gates/<gate>.yaml` exists, is `FINAL`, and `python platform/scripts/gate_check.py` passes.
- `compliance-auditor` verdict recorded as PASS or CONDITIONAL (with owners and dates).
- Founder approval recorded in the state file.

## Release
- All gates up to G6 approved; release checklist complete; rollback tested or documented; runbook current; monitoring in place.
