# Handoff Contracts

Each role consumes named artifacts and produces named artifacts. A handoff is valid only if the
inputs are `FINAL` (or `DRAFT` where stated) and the outputs are written to disk before the agent
returns. Agents return a summary of ≤150 words: what was produced, paths, open questions, risks.

| Role | Consumes | Produces | Path |
|---|---|---|---|
| product-owner | project-brief, research, feasibility | prd, success-metrics | delivery/G2-product-definition/ |
| research-analyst | project-brief | market-and-user-research, feasibility-assessment | delivery/G1-discovery/ |
| ux-architect | prd | ux-flows (flows, IA, design-system tokens, a11y criteria) | delivery/G3-solution-design/ |
| principal-architect | prd, ux-flows, feasibility | architecture-overview, ADRs | delivery/G3-solution-design/, delivery/decisions/adr/ |
| security-engineer | prd, architecture-overview | threat-model, (G6) security-review | delivery/G3-solution-design/, delivery/G6-assurance-audit/ |
| quality-engineer | prd, architecture-overview | test-strategy (G4), test-report (G6) | delivery/G4-delivery-plan/, delivery/G6-assurance-audit/ |
| Chief of Staff + principal-architect | all G2–G3 artifacts | delivery-plan (slices, order, owners) | delivery/G4-delivery-plan/ |
| backend-engineer / frontend-engineer | one approved slice, ux-flows, ADRs | code in product/, build-log entry with evidence | product/, delivery/G5-build-log/ |
| staff-code-reviewer | slice diff, build-log entry | review verdict appended to the build-log entry | delivery/G5-build-log/ |
| compliance-auditor | all artifacts of the gate, state | audit-report (PASS/CONDITIONAL/FAIL) | delivery/G6-assurance-audit/ |
| platform-engineer | architecture-overview, release-checklist | CI/CD, release-notes inputs, runbook | platform/ci/, delivery/G7-release/, delivery/G8-operations/ |
| technical-writer | any FINAL artifact | release-notes, user/ops docs | delivery/G7-release/, delivery/G8-operations/ |
| knowledge-curator | memory/, gate-log, retrospectives | compacted memory, rebuilt INDEX.md, token report | memory/ |
| process-improvement-engineer | gate-log, build-log, audit-reports | retrospective, lessons, change proposals | kaizen/ |

## Artifact status markers
First line of every artifact: `<!-- STATUS: TEMPLATE | DRAFT | FINAL -->`. `gate_check.py` fails on `TEMPLATE`.
Only the owning role sets `DRAFT`; `FINAL` is set after independent review.
