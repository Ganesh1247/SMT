<!-- STATUS: DRAFT -->
# Implementation Plan: sessions, phases and modules (Crucible, 3 developers)

Owner: principal-architect (drafted by Chief of Staff) | Gate: G4 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer, then compliance-auditor
Inputs: delivery/G4-delivery-plan/delivery-plan.md; profiles/hackathon-24h/timeline.md; three-system design (chat, 2026-10-10)

> Planning draft. `product/` is locked until G3 and G4 are approved. Assumes: three systems (Sandbox, HR Portal, Trust) pending ADR-0002; SQL/analytics ladder; three developers; text Level 4. Effort figures are indicative. Hours are on the 24-hour event clock.

## 1. Teams, systems and ownership

| Dev | Primary system | Modules owned |
|---|---|---|
| Dev 1 | System 1 Sandbox | `tasks`, `assessment-core`, `progression`, `integrity`, `learner-ui`, `trust-client` |
| Dev 2 | System 3 Trust | `ledger`, `estimates`, `profile-api`, `consent`, `review`, `assessor-audit`, `identity`, `contracts` |
| Dev 3 | System 2 HR Portal + intelligence | `roles`, `coverage`, `evidence-viewer`, `hr-ui`, plus in Sandbox: `probes`, `ai-adapter`, `level4` |

**Verification rotation (rule 2):** Dev 1's work is verified by Dev 2, Dev 2's by Dev 3, Dev 3's by Dev 1.

## 2. Module catalogue

| System | Module | Contains | Contract surface |
|---|---|---|---|
| Sandbox | `tasks` | Seed generator, dataset schema, hidden checks, read-only query runner with timeout, level and task definitions | `GET /tasks/{id}`, `POST /submissions` |
| Sandbox | `assessment-core` | Deterministic evaluator, criterion results, row-level diff feedback | internal api, `POST /evaluate?test=true` |
| Sandbox | `probes` | Predict-output probe generator and checker | internal api |
| Sandbox | `ai-adapter` | Delimited-input AI feedback, label, stub fallback | internal api |
| Sandbox | `level4` | Scripted adaptive session, mutation follow-up generator and checker | internal api |
| Sandbox | `progression` | Level state machine, saved progress, gated score update, retry | `GET /progress/{learner}` |
| Sandbox | `integrity` | Answer fingerprints, review flags | internal api |
| Sandbox | `trust-client` | Event outbox with retry, signing | calls Trust `POST /events` |
| Sandbox | `learner-ui` | Task, feedback, probe, Level 4, profile, consent, appeal screens | consumes Sandbox and Trust apis |
| Trust | `contracts` | JSON schemas: EvidenceEvent, ShareGrant, SharedEvidence, RoleRequirement | shared package |
| Trust | `identity` | Pseudonymous IDs, service keys, roles | auth middleware |
| Trust | `ledger` | Append-only events, hash chain, verify | `POST /events`, `GET /ledger/verify` |
| Trust | `estimates` | Skill estimate and band, recency | internal api |
| Trust | `profile-api` | Profile projection for the learner | `GET /profile/{learner}` |
| Trust | `consent` | Grants, revoke, scope checks | `POST/DELETE /grants` |
| Trust | `review` | Appeals, uncertainty-ordered queue, decisions | `POST /appeals`, `/review/*` |
| Trust | `assessor-audit` | Perturbation library, test runner, health report | `GET /assessor-reports` |
| HR Portal | `roles` | Role requirement CRUD | `POST /roles` |
| HR Portal | `coverage` | Matches requirements against shared evidence, coverage and gaps, why-surfaced | internal api |
| HR Portal | `evidence-viewer` | Candidate evidence page data | internal api |
| HR Portal | `hr-ui` | Role setup, results, evidence page | consumes HR and Trust apis |

## 3. Module maturity scale

| Level | Name | Meaning |
|---|---|---|
| M0 | Stub | Returns fixed, contract-valid data |
| M1 | Skeleton | Happy path works end to end |
| M2 | Core | Acceptance tests pass, errors handled |
| M3 | Complete | Edge cases, evidence recorded, reviewed |

## 4. Phases at a glance

| Phase | Hours | Event stage | Goal | Exit gate |
|---|---|---|---|---|
| **P0** Decide and design | 0-6 | Rounds 1 and 2 | G0-G4 approved; contracts specified | Founder approvals at H2 and H6 |
| **P1** Foundations | 6-12 | Build, mentor checkpoint | Three systems running; first end-to-end event | Walking skeleton green in CI |
| **P2** Core path | 12-16 | Round 3 | Learner path through Level 3 with probe, ledger, band | Working prototype with test evidence |
| **P3** Differentiate and prove | 16-22 | Hardening | Level 4, assessor audit, consent, appeals, validation | Code freeze at H22 |
| **P4** Demo and defend | 22-24 | Round 4 | Demo, evidence pack, defence | Demo delivered |

## 5. Module maturity by phase

| Module | End P1 (H12) | End P2 (H16) | End P3 (H22) |
|---|---|---|---|
| `contracts` | M3 | M3 | M3 |
| `identity` | M1 | M2 | M3 |
| `tasks` | M2 | M2 | M3 |
| `assessment-core` | M1 | M2 | M3 |
| `probes` | M0 | M2 | M3 |
| `ai-adapter` | M0 | M1 | M3 |
| `level4` | M0 | M0 | M2 |
| `progression` | M0 | M2 | M3 |
| `integrity` | M0 | M1 | M2 |
| `trust-client` | M1 | M2 | M3 |
| `ledger` | M2 | M3 | M3 |
| `estimates` | M1 | M2 | M3 |
| `profile-api` | M1 | M2 | M3 |
| `consent` | M0 | M1 | M3 |
| `review` | M0 | M0 | M2 |
| `assessor-audit` | M0 | M1 | M3 |
| `roles` | M1 | M2 | M3 |
| `coverage` | M0 | M1 | M3 |
| `evidence-viewer` | M0 | M1 | M3 |
| `learner-ui` | M1 | M2 | M3 |
| `hr-ui` | M0 | M1 | M2 |

## 6. Session plan

Each session is about two hours. Each starts with a 10-minute sync and ends with a 15-minute integration check and a build-log entry. Every second session runs the rubric scoring pass from the hackathon profile.

### Phase P0: Decide and design (H0-6)

| Session | Hours | Objective | Dev 1 | Dev 2 | Dev 3 | Exit check |
|---|---|---|---|---|---|---|
| **S1** | 0-2 | Round 1 submission and decisions | Review brief and approach; draft the seeded dataset schema | Draft EvidenceEvent and ShareGrant schemas on paper | Draft role requirement examples and coverage rules | G0 approved; D1-D6 answered |
| **S2** | 2-4 | G1 and G2 one-pagers | Write 3 seeded task variants and hidden checks on paper | Draft estimate and band parameters; list ledger fields | Draft probe and mutation types; draft AI feedback rubric | REQ list and MVP cut line FINAL |
| **S3** | 4-6 | G3 design and G4 plan | Sandbox safety checklist; stack setup notes | Contracts spec and auth model; ADR-0002 input | Level 4 session script outline | G3 and G4 approved at H6 |

Work in P0 produces documents under `delivery/`, never files under `product/`.

### Phase P1: Foundations (H6-12)

| Session | Hours | Objective | Dev 1 (Sandbox) | Dev 2 (Trust) | Dev 3 (HR + intelligence) | Exit check |
|---|---|---|---|---|---|---|
| **S4** | 6-8 | Scaffold, contracts, stubs | Repo layout, CI, health endpoints, DB migration (SLICE-001) | `contracts/` schemas, Trust stub, service keys | HR portal shell, role form against Trust stub | CI green; three stubs run via one compose command |
| **S5** | 8-10 | First module cores *(mentor checkpoint)* | Seed generator, query runner, one hidden check (SLICE-003) | Ledger append and verify, hash chain (SLICE-005) | Role CRUD, coverage skeleton on stub data | Seed determinism test; tamper test fails verification |
| **S6** | 10-12 | First end-to-end event | Evaluator, row diff, `trust-client` outbox (SLICE-004) | Estimates v1 and profile-api (SLICE-006) | Evidence viewer reading real `SharedEvidence` from Trust | One submission becomes an event, then a profile, then HR view |

**Mentor checkpoint (H8-10):** report built, working, broken, cut.

### Phase P2: Core path (H12-16)

| Session | Hours | Objective | Dev 1 | Dev 2 | Dev 3 | Exit check |
|---|---|---|---|---|---|---|
| **S7** | 12-14 | Levels and probe | Progression L1-L3, gated score, saved progress (SLICE-009) | Consent grants and `shared-evidence` query with scope rule | Predict-output probe generator and checker (SLICE-007) | Gated score test; no-grant-returns-nothing test |
| **S8** | 14-16 | Round 3 review readiness | Retry on fresh seed, attempt history (SLICE-013); learner UI flow | Profile API polish; band behaviour tests | AI adapter v1 with stub fallback (SLICE-008) | Full learner path L1-L3 runs; test output captured |

**Round 3 evidence:** requirement-to-feature map, passing tests, honest "built / partial / cut" list.

### Phase P3: Differentiate and prove (H16-22)

| Session | Hours | Objective | Dev 1 | Dev 2 | Dev 3 | Exit check |
|---|---|---|---|---|---|---|
| **S9** | 16-18 | Level 4 and appeals | Integrity fingerprints and flags (SLICE-014) | Review queue and appeal decision events (SLICE-016) | Level 4 scripted session, mutation follow-up (SLICE-010) | Follow-up derived from learner's code is checked; appeal recorded |
| **S10** | 18-20 | Prove the grader and failure cases | Learner UI: probe, Level 4, consent, appeal screens | Assessor audit suite and health report (SLICE-011) | Failure cases scripted (SLICE-012); coverage and why-surfaced complete | Invariance report generated; both failure cases run |
| **S11** | 20-22 | Validate and freeze | Fix defects from verification | Validation pack: benchmark agreement, seed-copy detection (SLICE-017) | Recruiter relevance test; usability test notes | **Code freeze at H22**; evidence pack drafted |

### Phase P4: Demo and defend (H22-24)

| Session | Hours | Objective | All devs |
|---|---|---|---|
| **S12** | 22-24 | Demonstration and defence | Run the demo script on a clean start; backup recording ready; defence notes (what is built, what is stubbed, what we do not claim); only critical-bug fixes |

## 7. Integration checkpoints

| When | Check | Owner |
|---|---|---|
| H8 | Stubs for all three systems running with agreed contracts | Dev 2 |
| H12 | Real event Sandbox to Trust to HR view | Dev 1 and Dev 2 |
| H16 | Learner path L1-L3 with probe, band, consent respected | All |
| H20 | Level 4, appeals and assessor report integrated | All |
| H22 | Code freeze; demo script passes from clean start | Dev 3 |

## 8. Cross-system acceptance tests

1. A recruiter query for a learner with no grant returns nothing.
2. Changing any stored event fails ledger verification.
3. Revoking a grant removes access on the next query.
4. The gated score does not change until all required levels pass.
5. An instruction embedded in a written answer does not change the score and is logged.
6. A correct answer that fails the probe shows "understanding unconfirmed" and keeps the output score.

## 9. Working rules

- One folder per system plus `contracts/`; changes to `contracts/` need all three developers.
- One branch per slice; merge to main at least every two hours; CODEOWNERS names owner and verifier.
- Tests are written first; every slice adds a build-log entry with evidence.
- No secrets in files; service keys come from environment variables.
- Dependencies are declared in the dependency register before use.
- If a module is behind at a phase boundary, apply the cut line from the delivery plan; never present a stub as working.

## 10. Contingencies

| Trigger | Response |
|---|---|
| Contracts not agreed by H8 | Dev 2 freezes a minimal version; extend later |
| Sandbox runner unsafe or slow at H10 | Fixed query set, no free-form SQL |
| Level 4 behind at H18 | Static follow-ups, labelled as scripted |
| Trust service unstable at H20 | Merge Trust modules into the Sandbox process, keeping the `api/` boundary |
| Any dev unavailable | Move their Should-tier modules to the cut line |

## 11. What this plan does not do
It does not authorise any file under `product/`, and it does not replace the PRD or the architecture overview. Module and slice IDs remain provisional until those are FINAL.
