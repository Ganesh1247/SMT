---
name: record-adr
description: Create an Architecture Decision Record with alternatives, trade-offs and consequences. Use for any costly-to-reverse decision - stack, data store, module boundary, integration style, dependency, distribution.
---
# Record ADR

Owner: `principal-architect`. Template: `platform/templates/adr.md`. Output: `delivery/decisions/adr/ADR-NNNN-<slug>.md` (NNNN = next number, zero-padded).

## Steps
1. State the decision and the forces: requirements and quality attributes it must satisfy, constraints.
2. List >=2 real alternatives (include "do nothing" where valid) with pros, cons and cost to reverse.
3. Decide; give the reasoning tied to the forces. Note consequences (positive, negative, follow-up work) and the fitness function or test that will keep the decision honest.
4. Status: Proposed -> Accepted (after Founder approval for stack or cross-module impact) -> Superseded by ADR-NNNN.
5. Link the ADR from the architecture overview and the dependency register.

Never edit an accepted ADR's decision; supersede it with a new one.
