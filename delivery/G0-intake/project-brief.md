<!-- STATUS: DRAFT -->
# Project Brief

Owner: product-owner | Gate: G0 | Version: 0.1 | Date: 2026-10-10 | Reviewer: compliance-auditor
Inputs: delivery/G0-intake/problem-statement-SAMARTHA-02.pdf (txt copy alongside); reference/SAMARTHA_Handbook.pdf; reference/24_Hour_Hackathon_Handbook.pdf

## Problem / opportunity
Online learning proves completion, not capability, and employers cannot cheaply tell whether a CV or certificate reflects
current, job-relevant ability. Source problem statement (authoritative): SAMARTHA Hackathon, "Innovation in Education",
**Part A: Nyeras / NxtMove Proof-of-Skill Sandbox**. Build a proof-of-competency sandbox that presents realistic tasks, evaluates
submissions against transparent criteria, and produces an evidence-linked competency profile shareable with a recruiter, wired
into a simulated Nyeras-to-NxtMove workflow, without claiming scores are validated hiring predictors.

## Pathway decision
Part A selected by the Founder on 2026-10-10. Part B (School Gamified Learning) and a combined A+B are out of scope; the
brief permits one pathway unless organisers explicitly allow combining (not confirmed).

## Stakeholders and target users
- **Learner (Nyeras)**: wants usable feedback, a retry path, an appeal route, and a portable record of demonstrated skill.
- **Recruiter (NxtMove)**: wants job-relevant evidence filtered against explicit role requirements, not one opaque score.
- **Human reviewer / appeals handler**: owns consequential or disputed decisions.
- **Hackathon judges**: assess working functionality, evidence, responsible design (see rubric memory).

## Desired outcome
Per the source "Expected Outcomes and Demonstration":
1. A learner completes a task, gets criterion-level feedback, and sees the profile update.
2. A recruiter inspects evidence for a sample role and understands why a candidate was surfaced.
3. At least one failure case is demonstrated (ambiguous answer, AI evaluation disagreement, or attempted shortcut).
4. A short validation plan explains how assessment quality and fairness would be tested before real hiring use.

## Required capabilities (from source)
- Small set of role-specific competencies (e.g. debugging, data analysis, business reasoning, communication).
- Task-based assessments with rubrics, test cases and feedback; deterministic checks plus rubric-guided AI feedback.
- Competency profile: every score linked to task, rubric, evidence and assessment date; proficiency, evidence, confidence, recency.
- Learner challenge/appeal, retry after feedback, improvement over time.
- Candidate-controlled sharing; recruiter search against explicit role requirements; human judgement retained.
- Audit log: assessment version, rubric, feedback provided.

## Constraints
- **Time/profile**: hackathon format (see Active profile); exact deadline and demo length TBC.
- **Data**: synthetic learner and job data permitted; minimise personal data; no private submissions to recruiters without consent.
- **Responsible design (source section 9)**: no equating scores with verified competence or employability; disclose AI use and give
  a human appeal route; prevent answer-key leakage; handle plagiarism and AI-assisted work without assuming misconduct;
  no ranking on proxies such as typing speed.
- **Integration**: Nyeras and NxtMove are simulated unless real access is provided (open question).
- **Workspace**: constitution rules 1-10 apply; no product code before G3 and G4 approved.

## Success measures (from source section 8)
Agreement with human-reviewed benchmark submissions; feedback consistency across paraphrased submissions; completion and retry
rates in a small usability test; relevance of surfaced candidates to role criteria; error and disparity checks where feasible.

## Out of scope
- Part B (school gamified learning) and any combined A+B solution.
- Claims of validated hiring predictive power; automated hiring decisions without human review.
- Placement-fee business model (validate willingness to pay and reliability first, per source section 10).
- Real integration with production Nyeras/NxtMove systems (unless provided).

## Active profile
Proposed: `hackathon-24h` (rubric weights in memory `hackathon-rubric-weights`). Pending Founder confirmation.

## Assumptions and open questions
| # | Item | Owner |
|---|------|-------|
| 1 | Are real Nyeras/NxtMove APIs or data provided, or fully simulated? | Founder to ask organisers |
| 2 | Competency choice: which 1-3 competencies and which role for the demo? | product-owner (G1/G2) |
| 3 | Deadline, demo length, team size, stack constraints | Founder |
| 4 | Is hackathon-24h the correct profile for this event's rounds? | Founder |
| 5 | AI model/provider for rubric-guided feedback and any cost limits | principal-architect (G3) |
