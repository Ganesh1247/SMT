---
name: gate-drafts-g1-g4-written
description: Parallel authors drafted G1-G4 artifacts; open Founder decisions and threat-model contract changes pending
type: decision
scope: project
status: active
updated: 2026-10-10
---
Written 2026-10-10 (all DRAFT, unaudited): G1 feasibility-assessment, G2 prd + success-metrics, G3 architecture-overview + ux-flows + threat-model, G4 test-strategy, ADR-0001 stack (Proposed), ADR-0002 three-systems (Proposed). Architect recommends ADR-0002 option B (modular monolith, rule 7); Founder earlier asked for three separate systems = option A needs rule-7 exception. Threat model critical: no learner auth, unsafe SQL execution; contract changes C1-C7 recommended, not yet applied. Feasibility: cut live video, stub Level 4 mutation follow-ups, band illustrative. PRD adds REQ-022/023, NFR-005..007; delivery-plan coverage needs update. **How to apply:** Founder decisions first (ADR-0002, score gate Q3, AI provider, L4 mode), then apply C1-C7, then G0 approval.
