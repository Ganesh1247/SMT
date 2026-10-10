# Decision Rights

| Decision | Proposes | Decides | Approves | Recorded in |
|---|---|---|---|---|
| What to build, for whom, priority | product-owner | product-owner | Founder | PRD (G2) |
| Success metrics | product-owner | product-owner | Founder | success-metrics (G2) |
| Technology stack and architecture | principal-architect | principal-architect | Founder | ADR |
| UX patterns, design system | ux-architect | ux-architect | principal-architect (technical fit) | ux-flows (G3) |
| Security controls and risk acceptance | security-engineer | security-engineer | Founder (risk acceptance) | threat-model, ADR |
| Test strategy and coverage targets | quality-engineer | quality-engineer | principal-architect | test-strategy (G4) |
| Slice scope and ordering | Chief of Staff | principal-architect | Founder | delivery-plan (G4) |
| Code change acceptance | engineer | staff-code-reviewer | — | build-log |
| Gate verdict (PASS / CONDITIONAL / FAIL) | compliance-auditor | compliance-auditor | Founder | audit-report |
| Release go/no-go | Chief of Staff | Founder | Founder | release-checklist |
| Change to rules, agents, skills | process-improvement-engineer | Founder | Founder | kaizen/change-proposals |

## Principles
- **What and why** belong to the product-owner; **how** belongs to the principal-architect. Neither overrules the other; conflicts are escalated.
- **Verification verdicts** belong to assurance roles and cannot be overridden by builders. Only the Founder may accept a risk or waive a finding, in writing.
- **No agent self-approves.** The Chief of Staff routes; the Founder decides.
