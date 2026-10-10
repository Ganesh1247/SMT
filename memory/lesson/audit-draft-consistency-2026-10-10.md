---
name: audit-draft-consistency-2026-10-10
description: Parallel authors diverged on score rule and topology; audit gave G1 FAIL, G2 COND, G3 FAIL, G4 FAIL
type: lesson
scope: project
status: active
updated: 2026-10-10
---
Report: delivery/G3-solution-design/audit-draft-consistency.md. Root cause: authors worked from different inputs while three Founder decisions were open (score gate, ADR-0002 A vs B, REQ-007 mutation follow-ups). **Why:** parallel dispatch before decisions multiplies divergence. **How to apply:** resolve Founder decisions BEFORE fanning out authors; give all authors the same decision record; re-sync plan s3/s11, test-strategy s5, contracts C1-C7, threat model after decisions.
