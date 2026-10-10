<!-- STATUS: DRAFT -->
# ADR-0002: Sandbox, HR Portal and Trust as three separately deployable systems in one repository

Owner: principal-architect | Date: 2026-10-10 | Reviewer: staff-code-reviewer, then compliance-auditor | **Decision maker: Founder**

Inputs: delivery/G4-delivery-plan/implementation-plan.md (three-system design, section 2 and 10); delivery/G4-delivery-plan/delivery-plan.md; delivery/G3-solution-design/contracts/README.md (producer/consumer table, invariants 14-16); CLAUDE.md rule 7. Architecture context: delivery/G3-solution-design/architecture-overview.md.

## Status
**Proposed. Requires explicit Founder approval.** It conflicts with a constitutional rule (see below) and must not be treated as accepted by any agent, including the Chief of Staff. Until the Founder decides, the architecture overview treats Option B as the working baseline because it is rule-compliant; both options share the same module boundaries and contracts, so the choice does not block G3 module design.

## The conflict, stated explicitly
CLAUDE.md hard rule 7: "Product code is a modular monolith: modules interact only through each module's `api/` surface." The principal-architect mandate adds: "Distribute only when an ADR proves the need."

The implementation plan (version 0.1) assumes three systems (Sandbox, HR Portal, Trust), each its own process with its own HTTP API, started by one compose command, and talking over the network using the files in `delivery/G3-solution-design/contracts/`. Three independently deployable services is a distributed system, not a modular monolith. Adopting Option A therefore either needs a recorded exception to rule 7 approved by the Founder, or a change proposal to the constitution under the `self-improve` process. A profile may not weaken rule 7 (CLAUDE.md, Profiles).

This ADR does not resolve the conflict by itself. It lays out the options so the Founder can decide.

## Context and forces
| Force | Source |
|---|---|
| Trust must be the system of record for evidence, grants and estimates | contracts/README.md (producer/consumer table) |
| The HR portal never calls the Sandbox and receives nothing without an active ShareGrant | contracts/README.md; NFR-003 |
| Trust never sees recruiter thresholds; the query carries competency IDs only | contracts invariant 14 |
| `recipient_id` must equal the authenticated organisation | contracts invariant 16 |
| Three developers work in parallel, each owning one area, with a rotation for verification | implementation-plan.md section 1 |
| 24-hour clock; integration and environment problems are the most common cause of demo failure | delivery-plan.md R4; hackathon profile |
| Pitch narrative: a separate trust layer the recruiter can rely on | curated-pitch-content.md section 4 (Trust layer) |
| Rule 7 and the "simplest that satisfies" principle | CLAUDE.md; architect mandate |

## Options considered

| Option | Pros | Cons | Cost to reverse |
|---|---|---|---|
| **A. Three separately deployable systems in one repository** (as proposed in the implementation plan). Three FastAPI processes, three databases, network calls using the contracts, service keys between them, compose file to start all three | Isolation is physical: the HR process holds no Sandbox address or credentials, so "HR never calls Sandbox" is true by construction; Trust's data cannot be reached except through its HTTP API; a convincing story that Trust is independent; each developer can run and restart their own system; a crash in the SQL runner cannot take down Trust | **Violates rule 7** unless an exception is approved; three times the scaffolding, configuration, health checks and CI jobs; service-to-service auth must be built (keys, signing in `trust-client`); network failure modes appear (timeouts, retries, outbox, partial failure) and need tests; local demo depends on three processes starting cleanly; debugging across process boundaries is slower; end-to-end tests are slower and flakier | Medium: merging back to one process is already listed as a contingency (implementation plan section 10), provided module `api/` boundaries hold |
| **B. Modular monolith with the same three module groups; run as three processes only if needed** (recommended). One codebase and one deployable unit. Top-level bounded-context groups `sandbox`, `trust`, `hr_portal` each contain the modules from the module map, each with `domain/application/infrastructure/api`. Cross-group calls go through the target group's `api/` facades, which accept and return the contract shapes. Each group owns its own database file. The same codebase can start any group alone (`--context=trust`) so a split into processes is a configuration change, not a rewrite | **Complies with rule 7**; one scaffold, one CI pipeline, one start command; no network failure modes in the critical path; the contracts are still enforced at the group facades and validated against the schema files; separate database files keep data ownership physical; architecture tests enforce "HR never imports Sandbox" and "only Trust writes the ledger"; the split option keeps Option A's main benefit available if a real need appears | Isolation is logical, not physical: a careless import could cross a boundary (mitigated by import-linter tests that fail the build); a crash in the SQL runner could affect the whole process (mitigated by the runner's step budget, and by running the `sandbox` group as its own process if that risk materialises); the "independent Trust" story is weaker in the pitch unless the facade and separate database are shown | Low: moving to Option A later means adding an HTTP adapter behind each existing facade |
| C. Single module set with no system grouping (plain monolith of ~20 modules) | Least structure | Loses the Trust and HR boundaries the contracts rely on; "HR never calls Sandbox" becomes a convention only | Medium |

## Cost and benefit of A versus B (indicative, 3 developers, 24 hours)

| Item | A: three systems | B: modular monolith | Difference |
|---|---|---|---|
| Scaffold, configuration, health endpoints | 3 apps | 1 app with 3 groups | about 1 to 1.5 developer-hours more for A |
| Service-to-service auth (keys, signing, rejection tests) | Required | Not required in-process; `recipient_id` still checked against the authenticated organisation at the Trust facade | about 1 to 2 developer-hours more for A |
| Outbox, retries, idempotency | Required and tested over the network | Idempotency key still honoured (contract invariant 10); outbox can be a direct in-process call with the same interface | about 1 developer-hour more for A |
| End-to-end test runtime and flakiness | Higher | Lower | Demo risk higher for A |
| Isolation strength | Physical | Logical, enforced by tests | Benefit to A |
| Fault isolation of the SQL runner | Yes | Only if `sandbox` is split out | Benefit to A, available to B on demand |
| Constitution compliance | Needs Founder exception or constitution change | Compliant | Benefit to B |

Estimated net cost of A: about 3 to 4.5 developer-hours on a budget of roughly 48 build hours (3 developers x 16 hours, H6 to H22), plus higher integration risk at H8 and H12 checkpoints. These are estimates, not measurements.

## Decision (proposed, not accepted)
The principal-architect recommends **Option B**: one modular monolith, with `sandbox`, `trust` and `hr_portal` as top-level bounded-context groups, separate database files per group, the contract files enforced at the group facades, and the ability to run any group as its own process if fault isolation or a hosted demo requires it.

Reason: B satisfies every force in the table above that A satisfies, except physical isolation, and it does so within rule 7 and at lower cost and risk. Physical isolation is not required by any Must requirement; the privacy and integrity requirements (NFR-003, REQ-008, REQ-016) are met by the facades, the grant check in Trust and the architecture tests.

If the Founder prefers **Option A** (for example, for the pitch narrative or to let each developer run their own service), the Founder must also approve an explicit, recorded exception to rule 7 for this project, scoped to these three systems, with internal modules inside each system still following rule 7. In that case the Chief of Staff records the exception in the gate log and, if it is to persist beyond this project, raises a change proposal.

If the Founder and product-owner disagree with the architect on this, it goes to `delivery/decisions/escalations/`.

## Consequences
If B is approved
- The implementation plan's ownership by system stays as is; "system" reads as "bounded-context group".
- `trust-client` keeps its interface (append event with idempotency key) but its MVP adapter is an in-process call to `trust.ledger.api`. An HTTP adapter is written only if `trust` is split out.
- Service keys are not needed for in-process calls; organisation and learner authentication at the HTTP edge are still needed.
- The contingency "merge Trust modules into the Sandbox process" (implementation plan section 10) becomes the default rather than a fallback.

If A is approved
- Rule 7 exception recorded before SLICE-001; compose file, three CI jobs and service-key handling added to SLICE-001 scope (likely S grows to M).
- Network failure tests added to SLICE-004 and SLICE-015.

Either way
- Module boundaries, contracts, data ownership and fitness tests in the architecture overview are identical.

## Fitness function / verification
| ID | Check | Applies to |
|---|---|---|
| AT-02 | No module in `hr_portal` imports any `sandbox` package; HR configuration contains no Sandbox address | A and B |
| AT-04 | Only `trust.ledger` writes ledger storage; ledger rows cannot be updated or deleted | A and B |
| AT-01 | Cross-module imports go to `<module>.api` only | A and B (inside each system for A) |
| AT-12 | Each bounded-context group opens only its own database file or connection | B |
| AT-13 | Each group starts alone (`--context=<group>`) and passes its health check | B (keeps the split option real) |
| AT-14 | Service-to-service calls without a valid key are rejected | A only |
