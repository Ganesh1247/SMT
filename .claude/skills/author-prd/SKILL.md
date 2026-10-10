---
name: author-prd
description: Produce a Product Requirements Document and success metrics from G0 and G1 inputs. Use for G2 product definition or when requirements must be revised under change control.
---
# Author PRD

Owner: `product-owner`. Templates: `platform/templates/prd.md`, `success-metrics.md`. Output: `delivery/G2-product-definition/`.

## Steps
1. Read `project-brief.md`, `market-and-user-research.md`, `feasibility-assessment.md`.
2. Fill the PRD: problem, users, goals, non-goals, scope, functional requirements (`REQ-###`, MoSCoW, acceptance criteria in Given/When/Then), non-functional requirements with numeric thresholds, assumptions, dependencies, release criteria, open questions.
3. Fill success-metrics: metric, baseline, target, measurement method, owner, review date. Include at least one adoption, one quality and one performance metric.
4. Self-check: every requirement testable; every Must traces to a G1 finding; no technology prescriptions; non-goals explicit.
5. Set `<!-- STATUS: DRAFT -->`; independent review sets FINAL.

## Change control after approval
Record changes in the PRD change log with reason, impact on design/plan/tests, and Founder approval. Re-open affected gates.
