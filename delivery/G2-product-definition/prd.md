<!-- STATUS: DRAFT -->
# Product Requirements Document: Crucible (working name), Part A

Owner: product-owner | Gate: G2 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer (then compliance-auditor)
Inputs: delivery/G0-intake/problem-statement-SAMARTHA-02.txt (Part A s1-10); delivery/G0-intake/project-brief.md; delivery/G0-intake/final-solution-approach.md; delivery/G0-intake/part-a-detailed-breakdown.md (PS-A-nn labels); delivery/G4-delivery-plan/delivery-plan.md s3 (provisional IDs, kept)

> G1 research is not a separate FINAL artifact yet. Sources are the G0 approach document (research notes, sources in its s14) and the issued problem statement. Items without a source are marked ASSUMPTION. Upstream G0 is not yet Founder-approved.

## 1. Problem and goals

Course completion does not prove a learner can do the work, and recruiters cannot cheaply inspect current, job-relevant ability (PS s1, s2). Crucible is a proof-of-competency sandbox: realistic tasks, transparent criteria, an evidence-linked competency profile a learner can share with a recruiter, inside a simulated Nyeras-to-NxtMove flow (PS s4).

Goals (each measured in success-metrics.md):
1. A learner finishes a task, gets criterion-level feedback and sees the profile change (PS s7).
2. A recruiter sees role-relevant evidence and why a candidate was surfaced (PS s7).
3. The assessor shows how often it agrees with humans and how stable it is, including failures (PS s8).
4. No score is presented as validated, a hiring predictor, or one aggregate (PS s4, s9).

**Standing label.** Every score, band and level result is "experimental". Crucible makes no claim that any result predicts hiring outcomes or verifies professional competence.

## 2. Users and roles

| Role | Need | Sees | Never sees or does |
|---|---|---|---|
| Learner (Nyeras) | Usable feedback, retry, appeal, portable record | Own criterion feedback, probe results, bands, history, who can see what | Another learner's data; an unexplained score |
| Recruiter (NxtMove) | Evidence against explicit role requirements | Granted evidence, method labels, coverage and gaps | Ungranted submissions; a rank, hire or reject recommendation |
| Reviewer | Decide appeals and low-confidence results | Original work, AI rationale, rubric, probe results | Learner identity beyond what review needs |
| Auditor | Verify decisions are reproducible; read assessor health | Ledger, assessor health reports | Raw private submissions |

## 3. Competency ladder and score rule

Demo role: junior data analyst (ASSUMPTION, D1: SQL/analytics). Competencies in scope (REQ-001): **C1 Data analysis (SQL)**, **C2 Communication of findings**. Each competency has its own ladder.

| Level | Name | What it shows | Method |
|---|---|---|---|
| L1 | Conceptual | Knows the concepts and terms for the competency | Deterministic checks on structured questions |
| L2 | Debugging | Finds and fixes a seeded fault in provided work | Deterministic checks against hidden cases |
| L3 | Applied Logic and Adaptability | Solves a realistic task on the learner's seeded data and handles a changed requirement | Deterministic checks, plus labelled AI feedback on judgement criteria |
| L4 | Live AI Screening | Explains and adapts own solution in a short interactive session | MVP: scripted adaptive text session; follow-up derived from the learner's own L3 submission (D4) |

**Score rule, applied per competency (never one aggregate across competencies):**
1. A competency's score and band update only after all four of its levels are passed.
2. Progress is saved at each level; a learner can stop and resume.
3. Passed levels stay on the profile as labelled evidence (level, method, date, task and rubric version) even while the competency score has not yet updated.
4. A failed level blocks the next level of that competency only; other competencies are unaffected.
5. Passing C1 does not change C2. The profile shows one row per competency, with level status and, once all four levels pass, estimate, uncertainty band, recency and "experimental" label.

## 4. Scope and non-goals

In scope (MVP): one role, two competencies, SQL/analytics sandbox, four-level ladder (text L4), seeded per-learner data, evidence ledger, band, profile, assessor audit, two failure cases, validation plan. Should-tier: appeals, consent, recruiter coverage, retry, fingerprints.

Non-goals (out of scope):
- Part B or combined A+B.
- Any claim of validated hiring prediction; any automated hire/reject decision; any aggregate or ranked candidate list.
- Real Nyeras/NxtMove integration (simulated adapters, synthetic data; D5).
- Placement-fee business model; billing.
- Live voice or video L4 (Could only, REQ-021).
- Ranking on proxies (typing speed, time on task); detecting or accusing AI use.
- Fairness or validity claims beyond what the validation tests show.

Backlog (labelled, not scheduled): Break-It Duel, plain-English probe, ESCO mapping, signed credential export, jury grading.

**Change control.** After G2 approval, any scope change needs Founder approval and a dated entry in the change log below. Cut order follows delivery-plan s8; never cut: seeded task, deterministic checks, probe, band, ledger, one failure case.

## 5. Functional requirements

Priority is MoSCoW. Source = PS-A label from part-a-detailed-breakdown.md. Criteria are Given/When/Then.

| REQ | Title | Pri | Source | Acceptance criteria |
|---|---|---|---|---|
| REQ-001 | Versioned competency and rubric definitions (1 role, 2 competencies) | Must | PS-A-01 | Given C1 and C2 exist, when a rubric is edited, then a new version is created and the prior version stays retrievable. Given any competency, then its four levels and criteria are listed. |
| REQ-002 | Per-learner seeded task with hidden deterministic checks | Must | PS-A-02, 06, 07 | Given two learners, when each opens the L3 task, then data differs but structure is the same. Given the same seed, then data is identical. Given any client payload, then no answer key or hidden check is present. |
| REQ-003 | Criterion-level feedback with method label and confidence | Must | PS-A-02, 07, 11 | Given a submission, when evaluated, then each criterion shows pass/fail, rationale, method label (deterministic, AI, human) and a confidence value. |
| REQ-004 | AI feedback for judgement criteria: labelled, injection-safe | Must | PS-A-07, 16, 18 | Given AI feedback, then it carries an AI-use label. Given a submission containing an embedded instruction, when evaluated, then the criterion result is unchanged and the event is logged. Given no AI provider, then labelled stub feedback is shown (D3). |
| REQ-005 | Predict-the-output probe on the learner's own solution | Must | Approach M3 | Given a submitted query, when the probe runs on altered data, then the system executes the learner's query to get the expected output and compares it with the learner's prediction. Given a wrong prediction, then status reads "understanding unconfirmed", the output score is unchanged, and no misconduct wording appears. |
| REQ-006 | Four-level ladder (L1-L3 gated; L4 per REQ-007), saved progress, score updates only after all four pass, per competency | Must | Founder ladder; PS-A-03, 08 | Given a learner has passed L1-L3 of C1, then the C1 score is unchanged. Given L4 of C1 passes, then C1 score and band update and C2 is unchanged. Given a learner leaves mid-ladder, when they return, then they resume at the same level. Given a passed level, then it is visible as labelled evidence. |
| REQ-007 | L4 scripted adaptive text session with mutation-generated follow-up | Must | Founder ladder; Approach M3 | Given an L3 submission, when L4 starts, then the follow-up is derived from that learner's own code (one of a fixed set of mutation types) and the adapted answer is checked by a hidden deterministic check. Given a text-only device, then L4 is completable. |
| REQ-008 | Hash-chained evidence ledger | Must | PS-A-03, 10 | Given any event, then it records task, rubric version, seed, submission pointer, method and date. Given any stored event is altered, when the chain is verified, then verification fails and names the first bad event. |
| REQ-009 | Skill estimate with uncertainty band and recency, per competency | Must | PS-A-08 | Given more evidence, then the band narrows. Given elapsed time without evidence, then the band widens. Given the profile, then each competency shows estimate, band, evidence count and last-evidence date. |
| REQ-010 | Profile view: no aggregate, method labels, understanding status, experimental label | Must | PS-A-08, 15, 03 | Given a profile, then there is no cross-competency total field or display. Given any score, then an "experimental" label is adjacent. Given any score, when the learner drills down, then task, rubric, evidence and date are shown. |
| REQ-011 | Assessor audit: invariance and directional tests with health report | Must | PS-A-14; Approach M7 | Given a rubric version, when the suite runs, then a report lists categories tested (paraphrase, typo, filler, style, injection, requirement removal), counts, and each failure. Categories not tested are stated as untested. |
| REQ-012 | Two scripted failure cases | Must | PS-A-13 | Given the correct-but-probe-fail case, then the profile shows "output verified, understanding unconfirmed". Given the injection case, then the score is unchanged and the log shows the attempt. |
| REQ-013 | Validation plan and evidence pack | Must | PS-A-14 | Given the pack, then it includes plan, benchmark agreement, invariance, probe, seed-copy and usability results as obtained, including failures, with N stated. |
| REQ-014 | Answer fingerprints and review flags | Should | PS-A-18 | Given a value from another learner's seed appears in a submission, then a review flag is raised. Given a clean control, then no flag. Given a flag, then the score is not lowered automatically. |
| REQ-015 | Appeals and uncertainty-ordered review queue | Should | PS-A-04, 16 | Given a criterion result, when the learner appeals, then a queue item is created and ordered by uncertainty. Given a reviewer decision, then it is appended to the ledger and shown to the learner. |
| REQ-016 | Consent vault, recruiter coverage and gaps, why-surfaced | Should | PS-A-05, 09, 12, 17 | Given no grant, when a recruiter queries a candidate, then nothing is returned. Given a revoked grant, then access ends. Given a role requirement, then coverage and gaps by competency are shown with a why-surfaced reason and no rank. |
| REQ-017 | Retry on a fresh seed with attempt history | Should | PS-A-04 | Given a failed level, when retried, then new seed data is issued and history shows both attempts with dates. |
| REQ-018 | Break-It Duel task type | Could | Approach | Mutant catch rate is computed; equivalent mutants are curated. |
| REQ-019 | Plain-English explanation probe | Could | Approach | Given a free-text explanation, then it is rubric-assessed, labelled, and never lowers the output score. |
| REQ-020 | ESCO skill mapping for one role | Could | Approach | Given the role, then skills are mapped and a human confirm step is recorded. |
| REQ-021 | Live voice or video L4 | Could | Founder ladder | Text alternative always available; no retention by default. |
| REQ-022 | No hire output and no proxy ranking | Must | PS-A-05, 15, 19 | Given any recruiter or learner view or API response, then there is no hire/reject recommendation, no ranked list, and no time-on-task or typing-speed field. |
| REQ-023 | Auditor view of ledger and assessor health | Should | PS-A-10 | Given the auditor role, then ledger verification result and per-version health reports are viewable and raw private submissions are not. |

## 6. Non-functional requirements

| ID | Requirement | Pri | Source | Threshold and acceptance |
|---|---|---|---|---|
| NFR-001 | No secrets in files; dependencies declared | Must | Rule 8 | Secret scan reports 0 findings; every dependency has a policy entry. |
| NFR-002 | Module boundaries respected (api surfaces only) | Must | Rule 7 | Architecture fitness tests pass with 0 violations. |
| NFR-003 | Pseudonymous IDs; no data to recruiters without a grant | Must | PS-A-17 | Recruiter-facing payloads contain 0 direct identifiers; 100% of no-grant queries return empty. |
| NFR-004 | No time limit on probes; keyboard-operable UI; text alternative | Must | PS-A-19, accessibility | 0 probe timers; all learner flows completable by keyboard; every non-text step has a text alternative. |
| NFR-005 | Reproducibility | Must | PS-A-10 (ASSUMPTION on threshold) | Re-running a stored submission against the pinned task and rubric version reproduces the deterministic result in 100% of sampled cases. |
| NFR-006 | Interactive latency for deterministic checks | Should | ASSUMPTION | p95 under 5 s on the demo dataset size. Proposed. |
| NFR-007 | Demo resilience | Must | Delivery plan R3 | Full path runs offline with the stub AI adapter; backup recording exists. |

## 7. Assumptions and dependencies

| # | Assumption | Source/owner |
|---|---|---|
| A1 | D1: ladder language is SQL/analytics | Founder to confirm |
| A2 | D4: L4 is a scripted adaptive text session; voice/video is stretch | Founder to confirm |
| A3 | D5: Nyeras/NxtMove simulated; data synthetic | Brief, open Q1 |
| A4 | D3: AI provider may be absent; stub fallback acceptable | Founder |
| A5 | C2 (communication) can be given four meaningful levels with mostly rubric-based L3/L4; its L1/L2 may be thinner than C1 | ASSUMPTION, see Q2 |
| A6 | Benchmark set is 10-20 hand-graded synthetic submissions made by the team | Approach V1 |
| A7 | Profile `hackathon-24h` is active | Brief open Q4 |

## 8. Release criteria

1. All Must requirements pass their acceptance criteria with test evidence (build log).
2. Score rule demonstrated for both competencies independently, including a case where one competency has updated and the other has not.
3. "Experimental" label present wherever a score appears; no aggregate anywhere.
4. Two failure cases run live; backup recording exists.
5. Validation pack published with failures included.
6. Anything not working end to end is shown as roadmap, not as working.

## 9. Open questions

| # | Question | Owner | Due |
|---|---|---|---|
| Q1 | D1: Confirm SQL/analytics as ladder language (affects sandbox risk) | Founder | Before G3 (H2-6) |
| Q2 | Is C2 (communication) the right second competency, given thinner L1/L2 and AI-judged L3? Alternative: two SQL-adjacent competencies | Founder / product-owner | Before G3 |
| Q3 | D4: Is text L4 acceptable to judges, or is voice/video expected? | Founder to ask organisers | Before G3 |
| Q4 | Pass thresholds per level (for example share of criteria passed), and whether a failed L4 allows re-entry without redoing L1-L3 | product-owner | G2 review |
| Q5 | Team size and skills; deadline and demo length (drives cut line) | Founder | H2 |
| Q6 | AI provider and cost limit (D3) | Founder / principal-architect | G3 |
| Q7 | Are real Nyeras/NxtMove data or APIs provided? | Founder to ask organisers | H2 |
| Q8 | Recency decay parameters for the band (illustrative only) | principal-architect | G3 |

## 10. Change log

| Date | Change | Reason | Impact | Founder approval |
|---|---|---|---|---|
| 2026-10-10 | v0.1 draft; delivery-plan IDs kept; REQ-022, REQ-023, NFR-005 to NFR-007 added | G2 definition | Adds one Must (REQ-022) and NFR-005, NFR-007 beyond the provisional plan; delivery-plan s11 coverage needs update | Pending |
