<!-- STATUS: DRAFT -->
# Delivery Plan: Crucible (Part A)

Owner: principal-architect (drafted by Chief of Staff) | Gate: G4 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer, then compliance-auditor
Inputs: delivery/G0-intake/final-solution-approach.md; delivery/G0-intake/curated-pitch-content.md; delivery/G0-intake/part-a-detailed-breakdown.md; profiles/hackathon-24h/timeline.md; high-level system design (chat, 2026-10-10)

> Status: PLANNING DRAFT. G0 is not approved, G1-G3 artifacts do not exist yet, and `product/` is locked until G3 and G4 are approved. REQ and SLICE IDs are provisional until the PRD (G2) and architecture overview (G3) are FINAL. Team size, ladder language and AI provider are unconfirmed (section 2).

## 1. Approach
1. **Walking skeleton first.** One thin path from a seeded task to a profile view, through CI, before any breadth.
2. **Risk before value.** The sandbox runner and the Level 4 session are the two riskiest slices, so they start early.
3. **Deterministic first.** Anything that can be checked by code is built before any AI-judged feature, so the demo never depends on the AI grader.
4. **Evidence while building.** Every slice produces its own test output for the build log and the Round 3 and 4 evidence pack.
5. **Cut line is fixed up front** (section 8). Never cut: seeded task, deterministic checks, probe, band, ledger, one failure case.

## 2. Assumptions and open decisions

| # | Item | Assumption used in this plan | Owner | Impact if wrong |
|---|---|---|---|---|
| D1 | Ladder language | SQL/analytics task (safest sandbox) | Founder | Python tasks need an isolated container; SLICE-003 grows to L |
| D2 | Team size and skills | 3 streams: A backend, B frontend, C assessment and quality | Founder | Fewer people means more cuts (section 8) |
| D3 | AI provider and budget | AI adapter with a stub fallback | Founder | If none, REQ-004 ships as stubbed feedback, labelled |
| D4 | Level 4 mode | Scripted adaptive text session | Founder | Voice or video is stretch only |
| D5 | Nyeras/NxtMove data | Simulated adapters, synthetic data | Founder | Real APIs are out of scope |
| D6 | Stack | FastAPI, PostgreSQL or SQLite, React (proposal for ADR-0001) | principal-architect | Stack ADR needed before SLICE-001 |

## 3. Provisional requirements

MoSCoW. PS-A references the issued problem statement (Part A) labels used in the breakdown.

| REQ | Requirement | Pri | Source |
|---|---|---|---|
| REQ-001 | Versioned competency and rubric definitions for one role, two competencies | Must | PS-A-01 |
| REQ-002 | Per-learner seeded analytics task with hidden deterministic checks | Must | PS-A-02, 06, 07 |
| REQ-003 | Criterion-level feedback with method label and confidence | Must | PS-A-02, 07 |
| REQ-004 | AI feedback for judgement criteria, labelled, injection-safe | Must | PS-A-07, 16 |
| REQ-005 | Predict-the-output probe on the learner's own solution | Must | Approach M3 |
| REQ-006 | Levels 1 to 3 progression with gates, saved progress, gated score update | Must | Founder ladder |
| REQ-007 | Level 4 scripted adaptive session with mutation-generated follow-up | Must | Founder ladder, M3 |
| REQ-008 | Hash-chained evidence ledger linking task, rubric, seed, submission, method, date | Must | PS-A-03, 10 |
| REQ-009 | Skill estimate with uncertainty band and recency | Must | PS-A-08 |
| REQ-010 | Profile view: no aggregate, method labels, understanding status, experimental label | Must | PS-A-08, 15 |
| REQ-011 | Assessor audit: invariance and directional tests with a health report | Must | PS-A-14, M7 |
| REQ-012 | Two scripted failure cases | Must | PS-A-13 |
| REQ-013 | Validation plan and evidence pack | Must | PS-A-14 |
| REQ-014 | Answer fingerprints and review flags | Should | PS-A-18 |
| REQ-015 | Appeals and uncertainty-ordered review queue | Should | PS-A-04, 16 |
| REQ-016 | Consent vault, recruiter coverage and gaps, why-surfaced | Should | PS-A-05, 09, 12, 17 |
| REQ-017 | Retry on a fresh seed with attempt history | Should | PS-A-04 |
| REQ-018 | Break-It Duel task type | Could | Approach |
| REQ-019 | Plain-English explanation probe | Could | Approach |
| REQ-020 | ESCO skill mapping for one role | Could | Approach |
| REQ-021 | Live voice or video Level 4 | Could | Founder ladder |
| NFR-001 | No secrets in files; dependencies declared | Must | Rule 8 |
| NFR-002 | Module boundaries respected (api surfaces only) | Must | Rule 7 |
| NFR-003 | Pseudonymous IDs; no data to recruiters without a grant | Must | PS-A-17 |
| NFR-004 | No time limit on probes; keyboard-operable UI; text alternative | Must | PS-A-19, access |

## 4. Slices

Size: S under 1.5h, M 1.5 to 3h, L 3 to 5h (effort for one engineer, indicative).

| SLICE | Title | REQ | Module(s) | Owner | Acceptance tests (summary) | Depends on | Size | Risk |
|---|---|---|---|---|---|---|---|---|
| 001 | Walking skeleton: repo scaffold, CI, health endpoint, UI shell, DB migration | NFR-001, NFR-002 | platform | backend | CI runs; health endpoint 200; UI loads; migration applies | ADR-0001 | S | L |
| 002 | Competency and rubric store with seed role data | REQ-001 | competency | backend | Versioned rubric retrievable; change creates new version | 001 | S | L |
| 003 | Seeded task engine and hidden checks runner (read-only SQL, timeouts) | REQ-002 | tasks | backend | Same seed gives same data; different seeds differ; mutating or slow queries rejected | 001 | M | **H** |
| 004 | Evaluation orchestrator: deterministic results, row-level diff feedback | REQ-002, 003 | assessment | backend | Known-good passes; known-bad fails with the right criterion; diff names differing rows | 002, 003 | M | M |
| 005 | Evidence ledger: append-only events, hash chain, verify | REQ-008 | evidence | backend | Tampering any event fails verification; event holds all required links | 001 | M | M |
| 006 | Skill estimate band and profile view v1 | REQ-009, 010 | evidence, ui | backend, frontend | Band narrows with evidence, widens with time; no aggregate field; experimental label shown | 004, 005 | M | M |
| 007 | Probe engine: predict-output on altered data, executed and checked | REQ-005 | assessment | assessment | Correct prediction passes; wrong fails; own query is executed, not the learner's text | 003, 004 | M | M |
| 008 | AI feedback adapter: labelled, delimited input, stub fallback | REQ-004 | assessment | assessment | Output carries AI label; embedded instruction does not change result; stub works offline | 004 | M | M |
| 009 | Level progression L1-L3: gates, saved progress, gated score update | REQ-006 | tasks, assessment | backend | Score unchanged until all levels pass; progress resumes; failed level blocks next | 004, 006 | M | M |
| 010 | Level 4 scripted session with mutation follow-up | REQ-007 | assessment | assessment, backend | Follow-up derived from learner's own code; adapted solution checked against hidden check | 007, 009 | **L** | **H** |
| 011 | Assessor audit v1: invariance, directional, health report | REQ-011 | assessor-audit | assessment | Paraphrase, typo, filler, style, injection cases run; report lists categories and failures | 004, 008 | M | M |
| 012 | Scripted failure cases and demo data | REQ-012 | cross | quality | Correct-but-probe-fail shows "understanding unconfirmed"; injection logged, score unchanged | 007, 008, 006 | S | L |
| 013 | Retry on fresh seed and attempt history | REQ-017 | tasks, evidence | backend | Retry gets a new seed; history shows both attempts | 003, 006 | S | L |
| 014 | Integrity: fingerprints and review flags | REQ-014 | integrity | backend | Cross-seed value flagged; clean control not flagged; flag never lowers score | 003, 004 | S | L |
| 015 | Consent vault and recruiter coverage view | REQ-016, NFR-003 | consent, recruiting, ui | backend, frontend | No grant returns nothing; revoke removes access; coverage and gaps correct | 006 | M | M |
| 016 | Appeals and review queue | REQ-015 | review, ui | backend, frontend | Appeal creates queue item ordered by uncertainty; decision appended to ledger | 005, 006 | M | L |
| 017 | Validation pack: benchmark set, runs, report, usability test | REQ-013 | quality | quality | Report covers agreement, invariance, probe, seed-copy, usability, recruiter relevance | 011, 012, 015 | M | M |
| 018 | Hardening: demo script, backup recording, defence notes, accessibility pass | NFR-004, all | cross | quality | Full path runs from a clean start; NFR-004 checklist passes | all Must | S | L |
| 019 | Break-It Duel task type | REQ-018 | tasks | assessment | Mutant catch rate computed; equivalent mutants curated | 003, 004 | M | M |
| 020 | ESCO mapping for one role | REQ-020 | recruiting | backend | Role skills mapped; human confirm step | 015 | M | M |
| 021 | Voice or video Level 4 | REQ-021 | assessment, ui | frontend | Text alternative always available; no retention by default | 010 | L | H |

## 5. Phases against the 24-hour clock

Hours follow the 24-Hour Hackathon timeline. Founder gate reviews at hours 2, 6, 16 and 22.

| Window | Event stage | Gate work | Slices | Exit evidence |
|---|---|---|---|---|
| H0-2 | Round 1 | G0, G1, G2 one-pagers | none | Round 1 page, brief, requirements list, MVP cut line |
| H2-6 | Round 2 | G3 design, ADR-0001, light threat model; G4 this plan | none | Blueprint, stack ADR, risk table, slice plan; G3 and G4 approved at H6 |
| H6-8 | Build start | G5 | 001, 002, 005 in parallel; UI shell | CI green, ledger verify test passing |
| H8-10 | Mentor checkpoint | G5 | 003 started | Honest status: built, working, broken, cut |
| H8-12 | Build | G5 | 003, 004, 006 | First end-to-end: seed, submit, check, event, profile |
| H12-16 | Round 3 | G5 | 007, 009, 013, 014 | Learner path running with probe and gated score; test output |
| H16-20 | Build and harden | G5, G6 | 008, 010, 011, 012 | Level 4 session, assessor report, failure cases |
| H20-22 | Should tier and validation | G6 | 015, 016, 017 | Recruiter view, appeals, evidence pack |
| H22-24 | Round 4 | G6, G7 | 018 | Demo, backup recording, defence notes |

Honest note: H12-16 is the Round 3 prototype review. Anything not running end to end by H16 is cut or shown as roadmap, not presented as working.

## 6. Critical path and parallelism

**Critical path:** ADR-0001 → 001 → 003 → 004 → 006 → 007 → 009 → 010 → 017 → 018.

| Stream | Work | Notes |
|---|---|---|
| A: backend core | 001, 003, 004, 005, 009, 013, 014 | Owns the sandbox and the ledger |
| B: frontend | UI shell, 006 view, 015, 016 | Starts at H6 against API stubs |
| C: assessment and quality | 007, 008, 010, 011, 012, 017 | Writes acceptance tests first for A and B |

**Parallel safely:** 002, 005, UI shell (H6-8); 008, 011, 014 (different modules, no contract in flux). **Serial:** 003 before 004 before 007; 009 before 010.

**Independent verification (rule 2):** each slice is verified by quality-engineer, reviewed by staff-code-reviewer, then audited. The author never verifies their own slice.

## 7. Test and evidence plan

| Level | What | Evidence |
|---|---|---|
| Unit | Seed generator, checks, hash chain, band, probe | Test output per slice in the build log |
| Integration | Submission to event to profile | Walking skeleton test, run in CI |
| Acceptance | One test per slice acceptance row above | Red then green, recorded |
| Invariance | Perturbation suite against the grader | SLICE-011 report |
| Validation | 10 to 20 hand-graded submissions, probe own-versus-copied, seed-copy detection, 3 to 5 person usability test | SLICE-017 report |
| Security | Sandbox escape attempts, injection, grant bypass | Light threat model checks (G3) |

## 8. Cut line

| Order | Cut | Effect |
|---|---|---|
| 1 | SLICE-021 video | Text is the committed version |
| 2 | SLICE-020 ESCO mapping | Role requirements stay hand-written |
| 3 | SLICE-019 Break-It Duel | Roadmap slide |
| 4 | SLICE-016 appeals UI | Appeal shown as a ledger event only |
| 5 | SLICE-015 consent UI | Grant via API in the demo |
| Never | 003, 004, 005, 006, 007, 012 | Without these there is no demonstrable proof |

## 9. Risk register

| ID | Risk | Likelihood | Impact | Mitigation | Fallback |
|---|---|---|---|---|---|
| R1 | Sandbox escape or unsafe query execution | M | H | Read-only SQL engine, allow-list, timeouts, no file access | Fixed query set, no free-form SQL |
| R2 | Level 4 session and mutation follow-up overruns | H | H | Three hand-written mutation types, scripted session | Static follow-ups, flagged as scripted |
| R3 | AI feedback unreliable or unavailable in demo | M | M | Deterministic-first, cached outputs, stub adapter | Show deterministic path only, say so |
| R4 | Too many slices for the team | H | H | Streams, cut line, daily rubric scoring | Cut per section 8 |
| R5 | Seeds change task difficulty | M | M | Vary values not structure, report spread | Fixed set of vetted seeds |
| R6 | Probe misread as proof of authorship | M | M | Label "understanding unconfirmed", never "misconduct" | Remove probe verdict from recruiter view |
| R7 | Overclaiming validity | M | H | Experimental labels; validation plan; claim guard in deck | Remove claim |
| R8 | Third-party documents or secrets pushed publicly | L | H | Exclusion list; secret scan hook | Remove and rotate |
| R9 | Gate approvals delay build start | M | M | Pre-reviewed one-pagers; 5-minute reviews | Parallel prep behind the lock |
| R10 | Canva or Notion tooling unavailable at demo time | M | L | Deck exported; repo copy of content | Local files |

## 10. Definition of Done confirmation
Each slice meets `governance/constitution/definition-of-done.md`: linked to a REQ and a task, tests first and passing, no module-boundary violations, no undeclared dependency, security checklist items met, accessibility acceptance criteria for UI slices, independent review without blocking findings, and a build-log entry with evidence.

## 11. Requirement coverage

| REQ | Slice(s) |
|---|---|
| REQ-001 | 002 |
| REQ-002 | 003, 004 |
| REQ-003 | 004 |
| REQ-004 | 008 |
| REQ-005 | 007 |
| REQ-006 | 009 |
| REQ-007 | 010 |
| REQ-008 | 005 |
| REQ-009 | 006 |
| REQ-010 | 006 |
| REQ-011 | 011 |
| REQ-012 | 012 |
| REQ-013 | 017 |
| NFR-001, NFR-002 | 001 |
| NFR-003 | 015 |
| NFR-004 | 018 |

Every Must requirement maps to at least one slice, and no slice lacks an acceptance test.

## 12. What this plan does not yet do
It does not replace the PRD or the architecture overview, and its estimates are indicative until team size is known. It does not authorise any file under `product/`.
