# Relationship Map

How artifacts, roles and gates depend on each other. `platform/scripts/trace.py` checks these links mechanically
by scanning for IDs (`REQ-###`, `SLICE-###`, `ADR-####`).

## Artifact dependency chain (downstream consumes upstream)
```
project-brief (G0)
  -> market-and-user-research, feasibility (G1)
     -> PRD + success-metrics (G2)            defines REQ-###
        |-> ux-flows (G3)                     REQ -> flow -> screen
        |-> architecture-overview + ADRs (G3) REQ -> module
        |     |-> threat-model (G3)           boundary -> threat -> mitigation
        |     '-> dependency-register (G3)
        '-> test-strategy (G4)                REQ -> test level
              delivery-plan (G4)              REQ -> SLICE-###
                 -> build-log (G5)            SLICE -> code + tests + review
                    -> test-report (G6)       REQ -> test -> result
                    -> security-review (G6)   threat -> verified mitigation
                       -> audit-report (G6) -> release (G7) -> runbook, ops review (G8)
```

## Change impact (what must be revisited when X changes)
| Changed artifact | Re-check |
|---|---|
| project-brief | everything downstream |
| PRD | ux-flows, architecture, threat-model, delivery-plan, test-strategy, build-log, test-report |
| ux-flows | delivery-plan (UI slices), build-log, test-report |
| architecture / ADR | threat-model, dependency-register, delivery-plan, build-log |
| threat-model | build-log, security-review |
| delivery-plan | build-log, test-report |
| any approved gate artifact | that gate re-opens; all later approved gates become suspect until re-audited |

Run `python platform/scripts/trace.py impact <artifact>`.

## Role relationships
| Role | Produces for | Consumes from | Verified by |
|---|---|---|---|
| research-analyst | product-owner | brief | compliance-auditor |
| product-owner | ux-architect, principal-architect, quality-engineer | research | compliance-auditor |
| ux-architect | frontend-engineer, quality-engineer | PRD | principal-architect (fit), auditor |
| principal-architect | engineers, security-engineer, platform-engineer | PRD, ux-flows | auditor, Founder |
| security-engineer | engineers, auditor | architecture | auditor |
| engineers | quality-engineer | slice, ux-flows, ADRs | quality-engineer -> staff-code-reviewer |
| quality-engineer | auditor | PRD, strategy, code | auditor |
| platform-engineer | technical-writer | architecture, audit | auditor |
| compliance-auditor | Founder | all gate artifacts | Founder |
| process-improvement-engineer | Founder | telemetry, audits, retros, memory | Founder |
| knowledge-curator | all roles | memory, retros | process-improvement-engineer |

## Rules
- Nothing downstream may be FINAL while an upstream artifact it depends on is changed and not re-reviewed.
- Every Must REQ must appear in: architecture (module), delivery-plan (slice), test-report (result).
- IDs referenced downstream but not defined in the PRD are orphans and fail the audit.
