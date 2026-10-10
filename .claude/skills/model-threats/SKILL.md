---
name: model-threats
description: Build a STRIDE threat model with data classification, trust boundaries, abuse cases and mitigations traced to requirements or slices. Use at G3 and whenever architecture changes materially.
---
# Model Threats

Owner: `security-engineer`. Template: `platform/templates/threat-model.md`. Output: `delivery/G3-solution-design/threat-model.md`.

## Steps
1. Inventory assets and classify data (public, internal, confidential, restricted).
2. Draw the data-flow description: actors, processes, stores, flows; mark trust boundaries.
3. For each boundary crossing, evaluate STRIDE: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege.
4. Write abuse cases for the top user journeys (misuse by authenticated and anonymous actors).
5. For each threat: likelihood, impact, rating, mitigation, owner, and the requirement/slice/test that proves the mitigation.
6. Record residual risk; risk acceptance requires Founder sign-off.

Align with `governance/policies/security-policy.md`.
