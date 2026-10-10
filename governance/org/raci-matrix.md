# RACI Matrix

R = Responsible (does the work) · A = Accountable (owns the outcome) · C = Consulted · I = Informed · F = Founder approves

| Activity | Chief of Staff | product-owner | principal-architect | research-analyst | ux-architect | backend-engineer | frontend-engineer | platform-engineer | quality-engineer | security-engineer | staff-code-reviewer | compliance-auditor | technical-writer | process-improvement-engineer |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G0 Project brief | R | A | C | C | I | I | I | I | I | I | I | I | I | I |
| G1 Discovery research | C | A | C | R | C | I | I | I | I | I | I | I | I | I |
| G2 PRD and metrics | C | R/A | C | C | C | I | I | I | C | C | I | I | I | I |
| G3 UX flows | C | C | C | C | R/A | C | C | I | C | C | I | I | I | I |
| G3 Architecture + ADRs | C | C | R/A | I | C | C | C | C | C | C | I | I | I | I |
| G3 Threat model | C | I | C | I | I | C | C | C | I | R/A | I | I | I | I |
| G4 Delivery plan | R | C | A | I | C | C | C | C | C | I | I | I | I | I |
| G4 Test strategy | C | C | C | I | I | I | I | I | R/A | C | I | I | I | I |
| G5 Slice implementation | C | I | C | I | C | R | R | C | C | C | I | I | I | I |
| G5 Slice verification | I | I | I | I | I | I | I | I | R | C | R | I | I | I |
| G6 Assurance audit | C | I | I | I | I | I | I | I | R | R | C | R/A | I | I |
| G7 Release | R | C | C | I | I | C | C | R | C | C | I | C | R | I |
| G8 Runbooks and operations | C | I | C | I | I | I | I | R/A | C | C | I | I | R | I |
| Retrospective and rule proposals | C | C | C | C | C | C | C | C | C | C | C | C | C | R/A |

**F (Founder approval)** is required on every gate close, every ADR with cross-module or stack impact, every scope change, and every change under `.claude/` or `governance/` proposed by the Improver.
