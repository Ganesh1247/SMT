<!-- STATUS: DRAFT -->
# Architecture Overview: Crucible (Part A proof-of-skill platform)

Owner: principal-architect | Gate: G3 | Version: 0.1 | Date: 2026-10-10 | Reviewer: staff-code-reviewer and security-engineer, then compliance-auditor

Inputs (none FINAL yet; see Assumptions): delivery/G0-intake/final-solution-approach.md (DRAFT 0.1); delivery/G0-intake/curated-pitch-content.md (DRAFT 0.2); delivery/G4-delivery-plan/delivery-plan.md (DRAFT 0.1, provisional REQ and SLICE IDs); delivery/G4-delivery-plan/implementation-plan.md (DRAFT 0.1); delivery/G3-solution-design/contracts/ (README.md, six `*.schema.json` files, hash-canonicalisation.md).
Decisions: [ADR-0001 stack](../decisions/adr/ADR-0001-stack.md) (Proposed); [ADR-0002 three systems](../decisions/adr/ADR-0002-three-systems.md) (Proposed, needs Founder approval, conflicts with rule 7).

> Crucible is a working name. Nothing here claims that scores predict hiring outcomes; every estimate is labelled experimental (contracts invariant 9).

## 1. Context and quality attributes

### System context
```
 Learner ──> learner-ui ──> [ Sandbox ]  tasks, assessment, probes, Level 4, progression
                 │              │  EvidenceEvent (append, idempotent)
                 │              v
                 └────────> [ Trust ]  system of record: ledger, estimates, profile, consent, review, assessor audit
                                ^  SharedEvidenceQueryRequest / Response (grant-filtered)
 Recruiter ──> hr-ui ──> [ HR Portal ]  roles, coverage and gaps, evidence viewer
 External (simulated): Nyeras course completion -> Sandbox; NxtMove job role -> HR Portal (synthetic data, D5)
 External (optional): AI provider behind FeedbackProvider port in Sandbox (D3); stub by default
```
- **Trust is the system of record** for evidence events, grants, estimates, appeals and assessor reports. Nothing else stores or alters them.
- **The HR Portal never calls the Sandbox** and receives nothing without an active ShareGrant (contracts/README.md).
- Whether the three systems are three processes or three bounded-context groups in one process is ADR-0002. This document's baseline is ADR-0002 Option B (rule-7 compliant); module boundaries, data ownership and contracts are identical under Option A.

### Ranked quality attributes (targets are *Proposed*)
| Rank | Attribute | Target and measure | Driven by |
|---|---|---|---|
| 1 | Integrity and provenance | Any change to any stored event fails `GET /ledger/verify` at the altered entry; every criterion result carries task, task version, rubric, rubric version, seed, submission hash, method and date | REQ-008, F21, contracts invariants 1, 11 |
| 2 | Privacy and consent | Query without an active grant returns an empty result indistinguishable from "learner does not exist"; revoke effective on the next query; no names, emails or phones in any contract | NFR-003, REQ-016, invariants 3, 7, 15 |
| 3 | Sandbox safety | Learner SQL cannot write, attach, read files, load extensions or run past the step budget (indicative 2 s wall-clock equivalent); 100% of the escape suite refused | R1, REQ-002, ADR-0001 FF-1 |
| 4 | Grader robustness and honesty | Embedded instructions never change a score and are logged; invariance report per rubric version lists categories tested and failures; every AI-judged result labelled with confidence and `model_ref` | REQ-004, REQ-011, F04-F06, invariant 4 |
| 5 | Demo reliability | Full demo path runs from a clean checkout with no network, using the stub AI adapter | R3, SLICE-018 |
| 6 | Accessibility and fairness | Keyboard-operable UIs; text alternative for every non-text step; no time limit on probes; no time or speed feature in any score; axe check with no serious violations | NFR-004, F17, F23 |
| 7 | Modifiability | Zero boundary violations in architecture tests; infrastructure swappable behind ports | NFR-002, rule 7 |
| 8 | Performance (demo scale) | Evaluation of one submission under 3 s p95 on a laptop excluding AI calls; recruiter query under 1 s for up to 50 candidates | Demo usability; result cap in query response schema |

Availability beyond a single demo machine is not a target for the MVP.

## 2. Module map (bounded contexts)

Modules are named after business capabilities. Python packages use underscores. Owners follow implementation-plan.md section 1. Each backend module has `domain/`, `application/`, `infrastructure/` and `api/`.

### Group `sandbox` (learner assessment)
| Module | Responsibility | Owner | Public api surface | Depends on (api only) | Data owned |
|---|---|---|---|---|---|
| `competency` | Versioned competencies, rubrics and criteria for one role (two competencies); publishes the ID registry | Dev 1 | `get_rubric(id, version)`, `list_competencies()`; registry export to `contracts` | none | Competency, Rubric, RubricVersion, Criterion |
| `tasks` | Task families and levels, per-learner seed generator, dataset builder, hidden checks, read-only SQL runner (`QueryRunner` port) | Dev 1 | `GET /tasks/{id}`, `POST /submissions`; internal `run_query(seed, sql)`, `run_hidden_checks(...)` | `competency` | TaskDefinition, TaskVersion, Seed, Submission (text plus SHA-256), HiddenCheck |
| `assessment_core` | Deterministic evaluator, criterion results with method, rationale, confidence; row-level diff feedback | Dev 1 | `evaluate(submission_id)`; `POST /evaluate?test=true` for the audit suite | `tasks`, `competency`, `ai_adapter`, `trust_client` | CriterionResult (local working copy until acknowledged by Trust) |
| `probes` | Predict-the-output probe on altered data: generates the altered table, executes the learner's own query, compares with the prediction | Dev 3 | `create_probe(submission_id)`, `answer_probe(...)` | `tasks`, `trust_client` | Probe, ProbeAnswer |
| `ai_adapter` | `FeedbackProvider` port; stub adapter and one real adapter; delimited untrusted input; structured output only | Dev 3 | `judge(criterion, submission_text) -> {rationale, confidence, model_ref}` | `competency` | Response cache keyed by input hash (no learner identity) |
| `level4` | Scripted adaptive text session (D4); mutation follow-up generated from the learner's own query (three hand-written mutation types); adapted query checked against a hidden check | Dev 3 | `start_session`, `next_turn`, `submit_adaptation` | `tasks`, `ai_adapter`, `trust_client` | Level4Session, Turn |
| `progression` | Level state machine L1-L4, saved progress, retry on a fresh seed, attempt history | Dev 1 | `GET /progress/{learner}`; `record_level_outcome` | `tasks`, `trust_client` | LearnerProgress, Attempt |
| `integrity` | Answer fingerprints across seeds; review flags that never lower a score | Dev 1 | `fingerprint(submission_id)` | `tasks`, `trust_client` | Fingerprint |
| `trust_client` | Outbox: builds EvidenceEvents, assigns idempotency keys, delivers to Trust, retries | Dev 1 | `append_event(event)` | `trust.ledger` api (in-process under ADR-0002 B; HTTP under A) | OutboxItem |

### Group `trust` (system of record)
| Module | Responsibility | Owner | Public api surface | Depends on (api only) | Data owned |
|---|---|---|---|---|---|
| `identity` | Pseudonymous learner IDs (`lrn_...`), organisations, roles, per-recipient candidate aliases, auth middleware | Dev 2 | `authenticate(request)`, `alias_for(learner, recipient)` | none | Learner pseudonym, Organisation, Credential reference (no secrets stored in files) |
| `ledger` | Append-only events, canonical hash per `hash-canonicalisation.md`, chain verification, normalise-on-append | Dev 2 | `POST /events`, `GET /ledger/verify`, internal `append`, `read_by_learner` | `identity` | LedgerEntry (EvidenceEvent plus ledger block) |
| `estimates` | Per-competency estimate with uncertainty band, recency widening, score gate rule; projection rebuilt from the ledger | Dev 2 | `estimate_for(learner, competency)` | `ledger` | EstimateProjection (derived, rebuildable) |
| `profile_api` | Learner-facing profile: band, method labels, understanding status, experimental label, no aggregate | Dev 2 | `GET /profile/{learner}` | `estimates`, `ledger`, `consent` | none (read model only) |
| `consent` | ShareGrants, revoke, scope checks; answers the grant-filtered shared-evidence query | Dev 2 | `POST /grants`, `DELETE /grants/{id}`, `POST /shared-evidence/query` | `identity`, `ledger`, `estimates` | ShareGrant, AccessLog (open item 6 in contracts README) |
| `review` | Appeals, uncertainty-ordered queue, reviewer decisions written as `review_decision` events | Dev 2 | `POST /appeals`, `/review/*` | `ledger`, `identity` | Appeal, ReviewItem |
| `assessor_audit` | Perturbation library (paraphrase, typo, filler, language style, injected instruction, requirement removed), runner, health report per rubric version | Dev 2 | `GET /assessor-reports`, `run_suite(rubric_version)` | Calls Sandbox `assessment_core` test-mode api only, never learner data | AssessorReport, PerturbationCase |

### Group `hr_portal` (recruiter)
| Module | Responsibility | Owner | Public api surface | Depends on (api only) | Data owned |
|---|---|---|---|---|---|
| `roles` | RoleRequirement CRUD, version increments on every edit | Dev 3 | `POST /roles`, `GET /roles/{id}` | `contracts` registry | RoleRequirement |
| `coverage` | Per candidate, per competency: `met`, `partly_met`, `not_met`, `no_evidence`; gaps and why-surfaced; never a combined score | Dev 3 | `coverage_for(role_id)` | `roles`, Trust `consent` api (shared-evidence query) | none persisted beyond a request cache |
| `evidence_viewer` | Candidate evidence page data from SharedEvidence, method labels, ledger head for receipt checks | Dev 3 | `evidence_for(candidate_ref, role_id)` | `coverage` | none |

### Shared published language and frontends
| Unit | Responsibility | Owner | Notes |
|---|---|---|---|
| `contracts` | The schema files in `delivery/G3-solution-design/contracts/`, copied into the product as a read-only package; generated competency, task and rubric ID registry (open item 5) | Dev 2 (changes need all three) | Contains data and validation only, no business logic. It is not a helper library. |
| `learner-ui` (React) | Task, feedback, probe, Level 4, profile, consent, appeal screens | Dev 1 | Calls Sandbox and Trust edges only |
| `hr-ui` (React) | Role setup, coverage and gaps, evidence page | Dev 3 | Calls HR Portal edge only; has no Sandbox base URL |

`assessor_audit` sits in `trust` because its reports are trust artefacts; it reaches the grader only through `assessment_core`'s test-mode api with synthetic inputs. **Open question Q7:** if the Founder approves ADR-0002 Option A, this is a cross-system call that must be authenticated.

## 3. Layering and dependency rules

| Layer | May depend on | Must not depend on |
|---|---|---|
| `domain/` | Standard library, own module's domain | FastAPI, SQLAlchemy, HTTP clients, other modules |
| `application/` | Own `domain/`; other modules' `api/` facades; ports it defines | Other modules' `domain/`, `application/`, `infrastructure/` |
| `infrastructure/` | Own `application/` ports, `domain/`; frameworks, database, SQL engine, AI SDK | Other modules' internals |
| `api/` | Own `application/`; `contracts` | Other modules' internals |

Additional rules
1. Cross-module access goes through `<module>.api` only (rule 7). Cross-group access goes through the target group's facade modules listed above.
2. `hr_portal` never imports or calls anything in `sandbox`.
3. Only `trust.ledger` writes ledger storage; no code path updates or deletes a ledger row.
4. Each group opens only its own database.
5. No module named `utils`, `common`, `helpers` or `shared`.

### Architecture fitness tests (specification for `product/architecture-tests/`; to be written in SLICE-001, not here)
| ID | Test | Tooling |
|---|---|---|
| AT-01 | Imports across modules target `<module>.api` only | import-linter contracts |
| AT-02 | `hr_portal.*` imports nothing from `sandbox.*`; HR and hr-ui configuration contain no Sandbox address | import-linter plus config test |
| AT-03 | `domain/` packages import no framework, ORM or HTTP library | import-linter forbidden contract |
| AT-04 | Only `trust.ledger.infrastructure` references the ledger table; a `BEFORE UPDATE/DELETE` trigger raises; test attempts both | pytest |
| AT-05 | Every contract example passes `validate_examples.py`; boundary handlers validate payloads against the schema files and reject unknown fields | pytest in CI |
| AT-06 | Ledger reproduces the `canonical_hash.py` test vector; tampering with entry n is reported at n | pytest |
| AT-07 | No package named `utils`, `common`, `helpers`, `shared` | pytest (filesystem scan) |
| AT-08 | Shared-evidence query with no active grant returns an empty result with no total, count or reason; revoked grant returns empty on the next query | pytest (cross-group) |
| AT-09 | Sandbox escape suite (ADR-0001 FF-1) | pytest |
| AT-10 | Secret scan clean | pre-commit and CI |
| AT-11 | Claim guard: UI strings and API responses contain no `rank`, `overall_score`, `hire_recommendation` or wording that claims hiring prediction | pytest string scan plus schema |
| AT-12, AT-13 | Database isolation per group; each group starts alone (ADR-0002 Option B) | pytest |

## 4. Data model

Shapes that cross a boundary are defined only in the contract files; this section names ownership and consistency, it does not redefine them.

| Entity | Owner module | Contract file (if shared) | Consistency |
|---|---|---|---|
| Competency, Rubric(Version), Criterion | `sandbox.competency` | IDs only, via registry (pattern in `evidence-event.schema.json`) | Immutable versions; edit creates a new version |
| TaskDefinition, TaskVersion, Seed, HiddenCheck | `sandbox.tasks` | IDs only | Immutable versions; seeds deterministic |
| Submission (text and SHA-256) | `sandbox.tasks` | `submission_ref` hash only (invariant 2) | Text never leaves the Sandbox in an event |
| CriterionResult, Probe, Level4Session, LearnerProgress, Attempt, Fingerprint | Sandbox modules as listed | Emitted as `evidence-event.schema.json` | Local state is working data; the fact of record is the ledger event |
| OutboxItem | `sandbox.trust_client` | `evidence-event.schema.json` | At-least-once delivery; `idempotency_key` deduplicates (invariant 10) |
| LedgerEntry | `trust.ledger` | `evidence-event.schema.json` plus ledger block; hashing per `hash-canonicalisation.md` | Strictly sequential append in one transaction (sequence allocation and hash together); normalised values stored (rule 9 of the hash document) |
| EstimateProjection | `trust.estimates` | Exposed in `shared-evidence.schema.json` band fields | Derived from ledger; rebuildable; never edited directly |
| ShareGrant | `trust.consent` | `share-grant.schema.json` | Strong: checked on every query; `expires_at` required |
| AccessLog | `trust.consent` | Not yet specified (contracts open item 6) | Append-only |
| Appeal, ReviewItem | `trust.review` | Decisions as `review_decision` events | Queue ordered by uncertainty |
| AssessorReport | `trust.assessor_audit` | Not shared with HR in MVP | Versioned per rubric version |
| Learner pseudonym, Organisation, candidate alias | `trust.identity` | `learner_id`, `recipient_id`, `candidate_ref` patterns in the schemas | Alias derivation open (contracts open item 3) |
| RoleRequirement | `hr_portal.roles` | `role-requirement.schema.json` | Version increments on every edit |
| Coverage result | `hr_portal.coverage` | Not persisted | Computed per request from SharedEvidence; thresholds never leave HR (invariant 14) |

**Score gate.** `sandbox.progression` controls which level a learner may attempt. `trust.estimates` decides when a competency estimate moves, using `level_outcome` events in the ledger, so the score rule is enforced in the system of record. Which levels must pass before the estimate moves is open (Q3).

## 5. Integration contracts

| Flow | Producer | Consumer | Contract | Endpoint or call |
|---|---|---|---|---|
| Record evidence | `sandbox.trust_client` (and `trust.review` for decisions) | `trust.ledger` | `evidence-event.schema.json`; hash per `hash-canonicalisation.md` | `POST /events` (or in-process `ledger.api.append` under ADR-0002 B) |
| Verify ledger | Any caller with auditor role | `trust.ledger` | Ledger block in `evidence-event.schema.json` | `GET /ledger/verify` |
| Grant and revoke | Learner via `learner-ui` | `trust.consent` | `share-grant.schema.json` | `POST /grants`, `DELETE /grants/{id}` |
| Recruiter evidence query | `hr_portal.coverage` | `trust.consent` | `shared-evidence-query-request.schema.json`, `shared-evidence-query-response.schema.json`, `shared-evidence.schema.json` | `POST /shared-evidence/query` |
| Role definition | Recruiter via `hr-ui` | `hr_portal.roles` | `role-requirement.schema.json` | `POST /roles` |
| Learner profile | `learner-ui` | `trust.profile_api` | Internal read model (not a shared contract) | `GET /profile/{learner}` |
| Grader audit | `trust.assessor_audit` | `sandbox.assessment_core` | Internal test-mode api, synthetic inputs only | `POST /evaluate?test=true` |
| Simulated Nyeras / NxtMove | Seed scripts | `sandbox.progression`, `hr_portal.roles` | Synthetic fixtures (D5) | Adapter ports; no real integration |

**Versioning.** Every contract carries `schema_version` (`0.1`). Breaking changes create a new version and need all three developers (contracts/README.md). Hashing is versioned by its domain string (`crucible-evidence-event-v1`); old entries verify under their own version. Internal module APIs are versioned implicitly by the repository; they are not public.

## 6. Deployment topology

| Aspect | Baseline (ADR-0002 Option B, pending Founder) | If ADR-0002 Option A is approved |
|---|---|---|
| Deployable units | One backend process with three bounded-context groups; two static frontends | Three backend processes plus two frontends, one compose command |
| Databases | Three SQLite files: `sandbox`, `trust`, `hr_portal` (ADR-0001) | Same three files, one per process |
| Learner SQL engine | In-memory `sqlite3`, new connection per run, inside the `sandbox` group | Same, inside the Sandbox process |
| Inter-group calls | In-process `api/` facades, contract-validated | HTTP with service keys from environment variables |
| Split on demand | Any group runs alone with `--context=<group>` | Not applicable |

Environments: local development, CI (tests, architecture tests, contract examples, secret scan, accessibility), and the demo machine (local, offline-capable with the stub AI adapter). No cloud hosting is assumed (Q5). Scaling beyond demo load is out of scope; the path is PostgreSQL per group and a process per group.

## 7. Technology choices
| Choice | ADR |
|---|---|
| FastAPI on Python 3.12, Pydantic v2 | ADR-0001 |
| SQLite per bounded-context group via SQLAlchemy and Alembic; PostgreSQL-portable | ADR-0001 |
| Standard-library `sqlite3`, read-only, in-memory, step-budgeted, for learner SQL (D1) | ADR-0001 |
| `FeedbackProvider` port with stub adapter and one configurable real adapter (D3) | ADR-0001 |
| React + TypeScript + Vite, separate `learner-ui` and `hr-ui` | ADR-0001 |
| One modular monolith vs three deployables | ADR-0002 (Proposed) |
| Explicit-field-list hash canonicalisation | `contracts/hash-canonicalisation.md` (an ADR should be recorded for it; Q8) |

## 8. Cross-cutting concerns

| Concern | Approach |
|---|---|
| Authentication | Learner and recruiter sessions at the HTTP edge (demo-grade, pseudonymous); `recipient_id` must equal the authenticated organisation (invariant 16); service keys only under ADR-0002 A; all keys from environment variables |
| Authorisation | Deny by default; object-level checks (a learner sees only their own profile and grants; a recruiter sees only grant-covered evidence); reviewer sees work without identity beyond review need; auditor sees ledger and reports, not raw submissions |
| Untrusted input | Learner SQL only through the read-only engine; written answers passed to AI as delimited data, never as instructions; all boundary payloads validated against schema files; unknown fields rejected |
| Logging | Structured logs with request IDs; never log submission text, tokens or keys; security events (rejected query, grant denial, injection detected, ledger verify failure) logged |
| Configuration | Environment variables only; a checked-in example file lists names without values |
| Error handling | Generic errors to clients; detailed errors in logs; outbox retries with backoff; a failed AI call degrades to "AI feedback unavailable", never to a fabricated result |
| Observability | Health endpoint per group; ledger verify as an operational check; counts of outbox backlog and AI fallbacks |
| Accessibility | Keyboard-operable, visible focus, text alternatives, no timers on probes or Level 4, axe checks in CI (NFR-004) |
| Responsible claims | Experimental label on every estimate; no aggregate, rank or hire field (schema-enforced, AT-11); integrity flags never lower a score; probe failure reads "understanding unconfirmed", never "misconduct" |

## 9. Requirement coverage

Provisional REQ and SLICE IDs from delivery-plan.md.

| REQ | Pri | Module(s) | Slice(s) |
|---|---|---|---|
| REQ-001 | Must | `sandbox.competency` | 002 |
| REQ-002 | Must | `sandbox.tasks`, `sandbox.assessment_core` | 003, 004 |
| REQ-003 | Must | `sandbox.assessment_core` | 004 |
| REQ-004 | Must | `sandbox.ai_adapter`, `sandbox.assessment_core` | 008 |
| REQ-005 | Must | `sandbox.probes` | 007 |
| REQ-006 | Must | `sandbox.progression`, `trust.estimates` (gate rule) | 009 |
| REQ-007 | Must | `sandbox.level4` | 010 |
| REQ-008 | Must | `trust.ledger`, `sandbox.trust_client` | 005 |
| REQ-009 | Must | `trust.estimates` | 006 |
| REQ-010 | Must | `trust.profile_api`, `learner-ui` | 006 |
| REQ-011 | Must | `trust.assessor_audit`, `sandbox.assessment_core` (test mode) | 011 |
| REQ-012 | Must | `sandbox.probes`, `sandbox.ai_adapter`, `trust.profile_api` | 012 |
| REQ-013 | Must | Validation pack (quality; uses `assessor_audit`, `integrity`, `coverage`) | 017 |
| REQ-014 | Should | `sandbox.integrity` | 014 |
| REQ-015 | Should | `trust.review` | 016 |
| REQ-016 | Should | `trust.consent`, `hr_portal.roles`, `hr_portal.coverage`, `hr_portal.evidence_viewer` | 015 |
| REQ-017 | Should | `sandbox.progression`, `sandbox.tasks` | 013 |
| REQ-018 to REQ-021 | Could | `tasks`, `probes`, `roles`, `level4` | 019, (none), 020, 021 |
| NFR-001 | Must | All; CI secret scan (AT-10) | 001 |
| NFR-002 | Must | All; AT-01 to AT-07 | 001 |
| NFR-003 | Must | `trust.identity`, `trust.consent` (AT-08) | 015 (grant enforcement must exist by 006, see Q6) |
| NFR-004 | Must | `learner-ui`, `hr-ui`, `probes`, `level4` | 018 |

Gaps found: REQ-019 (plain-English probe) has no slice; NFR-003's grant check is scheduled in SLICE-015 (Should tier, on the cut line) although NFR-003 is Must (Q6).

## 10. Risks and fallbacks

| ID | Risk | Mitigation | Fallback |
|---|---|---|---|
| R1 | Sandbox escape or runaway query | ADR-0001 engine controls; AT-09 | Fixed query set, no free-form SQL |
| R2 | Level 4 overruns | Scripted text session, three mutation types | Static follow-ups labelled "scripted" |
| R3 | AI provider unavailable or unreliable | Stub adapter; cached outputs; deterministic-first | Deterministic path only, stated in the demo |
| R11 | ADR-0002 not decided by H6 | Baseline B keeps the same boundaries, so build can start either way | Start as B; split later only if approved |
| R12 | Contract drift between Pydantic models and schema files | Schema files authoritative; AT-05 | Freeze contracts at H8 (implementation plan contingency) |
| R13 | Ledger concurrency (two appends race for a sequence) | Single-writer transaction around sequence allocation and hash | Serialise appends through one worker |
| R14 | Pseudonymous IDs re-identified via `candidate_ref` reuse across recipients | Per-recipient alias (contracts open item 3) | Same alias for MVP, recorded as a known limitation |
| R15 | SQLite dialect surprises learners | Task text says "SQLite SQL"; tasks avoid missing functions | Provide a function reference card |
| R16 | Hash chain read as proof of truth | State the limit from hash-canonicalisation.md in the demo and profile | Remove the claim |

## 11. Assumptions and open questions

### Assumptions (used in this design; wrong ones change it)
| # | Assumption | Basis | Effect if wrong |
|---|---|---|---|
| A1 | Ladder language is SQL/analytics (D1) | Delivery plan D1 | Python ladder needs a container sandbox; ADR-0001 engine option 4; SLICE-003 grows to L |
| A2 | AI provider is behind an adapter with a stub fallback (D3) | Delivery plan D3 | None structurally; REQ-004 ships stub-labelled if no provider |
| A3 | Level 4 is a scripted adaptive text session for MVP (D4) | Delivery plan D4 | Voice or video adds media handling and retention rules (REQ-021) |
| A4 | Nyeras and NxtMove are simulated with synthetic data (D5) | Delivery plan D5 | Real integration needs adapters and data agreements |
| A5 | Three developers in three streams (D2) | Implementation plan | Fewer people: apply the cut line |
| A6 | Upstream artifacts (approach, pitch, plans) reflect intended scope although none is FINAL and no PRD, ux-flows or feasibility assessment exists yet | Inputs list | REQ mapping and quality targets need re-checking against the FINAL PRD |
| A7 | Demo runs on a local machine, offline-capable | Delivery plan R3 | Hosted demo pushes toward PostgreSQL and HTTP split (ADR-0002 A) |

### Open questions
| # | Question | Owner | Needed by |
|---|---|---|---|
| Q1 | ADR-0002: one modular monolith (B, recommended, rule-7 compliant) or three deployables (A, needs a recorded rule-7 exception)? | Founder | Before SLICE-001 (H6) |
| Q2 | D3: which AI provider, budget, and is sending learner written answers to a third party acceptable (data processing terms, retention)? Until answered, only the stub runs | Founder | Before SLICE-008 (H14) |
| Q3 | Score gate: does the estimate move after Levels 1-3 (REQ-006 wording) or only after all four levels (pitch, "score rule")? And is a scripted Level 4 session recorded with method `live_screening` or `probe`? | Founder with product-owner | Before SLICE-009 (H12) |
| Q4 | Is `submission_excerpt` allowed in SharedEvidence for the MVP (contracts open item 4)? | Founder | Before SLICE-015 |
| Q5 | Is a hosted demo required, or is a local machine acceptable? | Founder | H6 |
| Q6 | NFR-003 is Must but its grant enforcement sits in SLICE-015 on the cut line; propose moving the grant check and AT-08 into SLICE-006 so consent can never be cut | product-owner and Chief of Staff | G4 approval |
| Q7 | Under ADR-0002 A, `assessor_audit` (Trust) calls Sandbox test mode across systems; acceptable, or move `assessor_audit` to the Sandbox and publish reports to Trust? | principal-architect, after Q1 | H16 |
| Q8 | Record the hash canonicalisation decision as its own ADR (currently decided inside a contracts document) | principal-architect | G3 review |
| Q9 | How the competency, task and rubric ID registry reaches the HR portal without calling the Sandbox (proposed: generated read-only file in `contracts`) | Dev 1 and Dev 2 | H8 |
| Q10 | REQ-019 has no slice | product-owner | G4 approval |

### Follow-up artifacts not produced here
`delivery/G3-solution-design/dependency-register.md`, `platform/quality-commands.json` for this stack, and the G3 threat model (security-engineer) are still required for G3.
