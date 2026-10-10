# delivery/ - Artifact Layer

One folder per gate. Artifacts are created from `platform/templates/` and tracked by status marker (`TEMPLATE` -> `DRAFT` -> `FINAL`).

| Folder | Gate | Owner | Required artifacts |
|---|---|---|---|
| `state/` | - | Chief of Staff | `lifecycle-state.yaml`, `gate-log.md`, `open-risks.md` |
| `G0-intake/` | G0 | product-owner | project-brief |
| `G1-discovery/` | G1 | research-analyst | market-and-user-research, feasibility-assessment |
| `G2-product-definition/` | G2 | product-owner | prd, success-metrics |
| `G3-solution-design/` | G3 | principal-architect | ux-flows, architecture-overview, threat-model, dependency-register (+ ADRs) |
| `G4-delivery-plan/` | G4 | principal-architect | delivery-plan, test-strategy |
| `G5-build-log/` | G5 | engineers | build-log |
| `G6-assurance-audit/` | G6 | compliance-auditor | audit-report, test-report, security-review (+ `gate-audits/`) |
| `G7-release/` | G7 | platform-engineer | release-checklist, release-notes |
| `G8-operations/` | G8 | platform-engineer | runbook, operations-review |
| `decisions/adr/` | - | principal-architect | ADR-NNNN-*.md |
| `decisions/escalations/` | - | any role | ESC-NNNN-*.md |

Authoritative criteria: `governance/gates/`. Check readiness: `python platform/scripts/gate_check.py <gate>`.
