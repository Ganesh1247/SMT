---
name: decompose-work
description: Break the approved design into ordered vertical slices with requirement links, owners, acceptance tests, risks and a critical path. Use at G4 and when re-planning.
---
# Decompose Work

Owner: `principal-architect` (with Chief of Staff). Template: `platform/templates/delivery-plan.md`. Output: `delivery/G4-delivery-plan/delivery-plan.md`.

## Steps
1. List modules from the architecture overview. A **slice** is the thinnest end-to-end increment (UI -> api -> domain -> persistence) that a user or test can observe.
2. For each slice: `SLICE-###`, title, REQ-IDs, module(s), owner role, acceptance tests (from PRD criteria), dependencies, estimate (S/M/L), risk.
3. Order: walking skeleton first (end-to-end thin path through CI), then highest-risk, then highest-value Must slices, then Should/Could.
4. Mark the critical path and parallelisable slices (different modules, no shared contracts in flux).
5. Add a risk register with mitigations and fallbacks; link to `delivery/state/open-risks.md`.
6. Confirm each Must requirement maps to >=1 slice; no slice lacks an acceptance test.
