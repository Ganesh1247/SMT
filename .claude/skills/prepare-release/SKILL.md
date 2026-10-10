---
name: prepare-release
description: Prepare a safe release - checklist, rollback plan, monitoring, release notes and Founder go/no-go. Use at G7.
---
# Prepare Release

Owner: `platform-engineer` with `technical-writer`. Templates: `release-checklist.md`, `release-notes.md`.

## Steps
1. Confirm G6 `approved` and no open Critical/High findings.
2. Complete the checklist: version/tag, changelog, migrations tested forward and back, config and secrets set in the target environment, CI green on the release commit, artefacts reproducible.
3. Rollback plan: trigger conditions, exact steps, data considerations, who decides; rehearse where feasible and record the result.
4. Observability: health check, key metrics, alerts with thresholds, log queries; confirm dashboards show data.
5. Release notes (user and operator), known issues, upgrade steps.
6. Present to Founder for explicit go/no-go; record in the checklist and gate log. Destructive or production actions require that approval.
