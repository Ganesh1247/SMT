<!-- STATUS: DRAFT -->
# Curated Pitch Content: Crucible (Part A)

Owner: product-owner | Gate: G0 | Version: 0.2 | Date: 2026-10-10 | Reviewer: compliance-auditor
Inputs: delivery/G0-intake/final-solution-approach.md; Founder's four-level ladder (chat); problem-statement-SAMARTHA-02.txt
Note: "Crucible" is a working name. No claim that scores predict hiring. Thresholds are proposals. Flaw count corrected to 28 flaws across 9 areas.

## 1. Problem statement
**One line:** Finishing a course does not show a person can do the job, and today nobody can show how they know.

**Context**
- Certificates prove attendance. CVs are self-claimed. Quizzes test recall.
- AI graders add speed but also inconsistency, manipulation and language bias.
- Recruiters get one opaque score or a keyword match, with no way to inspect the evidence.

**The challenge (Part A)**
Build a proof-of-competency sandbox: realistic tasks, transparent criteria, and an evidence-linked competency profile a recruiter can inspect, on a simulated Nyeras-to-NxtMove workflow, without claiming the scores are validated hiring predictors.

**Why current approaches fail**
1. Completion is treated as competence.
2. One familiar task is thin evidence.
3. A correct answer is not the same as understanding it.
4. The grader is trusted, not tested.
5. Scores carry no uncertainty and no audit trail.

We mapped **28 flaws across 9 areas**: evidence validity, grading, integrity, learner agency, recruiter side, privacy and trust, fairness and access, validation and claims, operations and adoption.

## 2. Solution: Crucible
**One line:** A four-level proof-of-skill ladder where every claim carries its proof, its method and its uncertainty.

| Level | Name | What is proven | Gate |
|---|---|---|---|
| 1 | Conceptual Knowledge | Fundamentals: trace outputs, variable changes, definitions | Minimum correct answers |
| 2 | Code Debugging | Find the error, explain why it fails, fix it, explain the fix | Qualifying score |
| 3 | Applied Logic and Adaptability | Scenario problems, new constraints, adapt an earlier solution, edge cases | Qualifying score |
| 4 | Live AI Screening | Explain and defend the solution, justify the approach, complexity, adapt to a new constraint | Evaluated and reviewable |

**Outcome:** a Proof-of-Skill Profile that separates skills shown by automated tests from skills judged in the live screening.
**Score rule:** the score for a competency rises only after all four levels are passed. Progress is saved so learners resume without repeating levels, and passed levels stay as labelled evidence.

**Who gets what**
- Learner: criterion feedback, retry, appeal, control of who sees what.
- Recruiter: granted evidence, method labels, coverage and gaps against a role.
- Reviewer: original work, AI rationale, rubric, queue ordered by uncertainty.

## 3. Innovation approach
**The idea:** a correct answer and a confirmed understanding are recorded as two separate facts, and the grader is tested in public.

| # | Signature | What it does |
|---|---|---|
| 1 | **Defend-Your-Answer** | Short probes on the learner's own solution (predict the output on altered data; explain a step). Verifies understanding without detecting or accusing AI use. |
| 2 | **Self-auditing assessor** | Continuous invariance tests (paraphrase, typos, filler, language style, injected instructions) and directional tests (removed requirement lowers the score), published per rubric version. |
| 3 | **Honest skill estimate** | Per competency, an estimate with an uncertainty band that narrows with evidence and widens with time. |
| 4 | **Mutation-driven follow-ups** | Level 4's new constraint is generated from the learner's own code, personal and not memorisable. |

**What is established and what is ours:** each component has published research behind it (evidence-centred design, tracing and explaining skills, invariance testing, rating bands). The combination, labelled for recruiters, and our measurements are what is new. Probes as a hiring signal are an unvalidated hypothesis we test.

## 4. Key features
| Layer | Features |
|---|---|
| **Assess** | Per-learner seeded datasets; deterministic checks first; AI feedback only where tests cannot judge, clearly labelled; Break-It Duel task type (write tests that catch hidden buggy versions) |
| **Verify** | Defend-Your-Answer probes; mutation-driven follow-ups; answer fingerprints that flag cross-seed copying for review; human review queue for low confidence and conflicts |
| **Represent** | Profile with estimate band, evidence method labels, date and understanding status; no aggregate rank |
| **Trust** | Hash-chained audit ledger; consent vault with scoped, revocable grants; appeals; assessor health report; experimental label on every score |

## 5. MVP (24 hours)
**Scope:** one role (junior data analyst), one competency path through all four levels, on a per-learner seeded analytics task.

| Tier | Content |
|---|---|
| **Must** | Levels 1 to 3 with deterministic checks and labelled AI feedback; Level 4 as a scripted adaptive text session (explain and adapt); predict-the-output probe; skill band; mini invariance suite; hash-chained log; two scripted failure cases; validation plan |
| **Should** | Appeals and review queue; consent and recruiter coverage view |
| **Could** | Break-It Duel task; plain-English probe; ESCO mapping for one role; live video (text or audio alternative always available) |
| **Won't** | Real Nyeras/NxtMove integration, validity claims, placement fees |

**Demo:** submit, criterion feedback, probe, profile update, failure case (correct output but understanding unconfirmed), embedded instruction ignored, appeal, share, recruiter coverage and gaps, assessor health report.

**Proof we will show (reported as obtained, including failures):** agreement with 10 to 20 hand-graded submissions, invariance results by category, probe results on own versus copied work, seed-copy detection and false-flag rate, a 3 to 5 person usability test, recruiter relevance on a synthetic pool.

**Cut order if time runs short:** video, appeals UI, ESCO mapping, Break-It Duel. Never cut: seeded task, deterministic checks, probe, band, ledger, one failure case.

## 6. Closing line
"Other platforms record that you passed. We record how we know you understand it, and we test our own grader in public."

**We do not claim** scores predict hiring. Every score is labelled experimental. AI use is disclosed, appeal is human, consent comes before sharing, and there is no speed or appearance scoring.
