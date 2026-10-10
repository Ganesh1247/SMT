<!-- STATUS: DRAFT -->
# Part A Detailed Breakdown: Nyeras / NxtMove Proof-of-Skill Sandbox

Owner: product-owner | Gate: G0 (feeds G1/G2) | Version: 0.1 | Date: 2026-10-10 | Reviewer: compliance-auditor
Inputs: delivery/G0-intake/problem-statement-SAMARTHA-02.txt (Part A, sections 1-10)

> Analysis aid, not a requirements baseline. `PS-A-nn` labels are provisional and map 1:1 to source statements; stable
> `REQ-###` IDs are assigned in the PRD at G2. Anything marked **[Inference]** is not in the source.

## 1. The problem in one sentence
Course completion and certificates do not show that a person can do the job; build a **transparent, auditable, human-overseen**
path from learning activity to evidence that a recruiter can inspect, with the learner in control.

## 2. What the source actually asks for (requirement extraction)

### 2.1 Objectives (section 5)
| ID | Source statement | Plain meaning | Verifiable by |
|---|---|---|---|
| PS-A-01 | Define a small set of role-specific competencies | Pick few, concrete competencies tied to a role (e.g. debugging, data analysis) | Competency definition doc; each has a rubric |
| PS-A-02 | Task-based assessments with clear rubrics, test cases, feedback | Each task has criteria, runnable checks, written feedback | Task spec; rubric visible to learner |
| PS-A-03 | Profile links every score to task, rubric, evidence, assessment date | No orphan scores; click-through provenance | Profile data model; UI drill-down |
| PS-A-04 | Challenge assessment, retry after feedback, show improvement over time | Appeal flow, attempt history, trend | Appeal record; attempt timeline |
| PS-A-05 | Recruiter filters on job-relevant evidence; human judgement; candidate consent | Search by role criteria, never auto-decide, share only with consent | Filter UI; consent gate; no auto-reject |

### 2.2 Capabilities (section 6)
| ID | Capability | Notes |
|---|---|---|
| PS-A-06 | Interactive code / analytics / workplace-scenario sandbox | Choose **one** type for the demo |
| PS-A-07 | Assessment engine: deterministic checks + rubric-guided AI feedback "where appropriate" | Deterministic first; AI only for what tests cannot judge |
| PS-A-08 | Dashboard: proficiency, evidence, confidence, recency, not one aggregate | Four dimensions per competency |
| PS-A-09 | Candidate-controlled sharing + recruiter search vs explicit role requirements | Role requirement is structured data |
| PS-A-10 | Audit log: assessment version, rubric, feedback provided | Versioned assessments and rubrics |

### 2.3 Demonstration (section 7)
| ID | Must show |
|---|---|
| PS-A-11 | Learner: task, criterion-level feedback, profile update |
| PS-A-12 | Recruiter: evidence for a sample role and why the candidate was surfaced |
| PS-A-13 | At least one failure case: ambiguous answer, AI-evaluation disagreement, or attempted shortcut |
| PS-A-14 | Short validation plan for quality and fairness before real hiring use |

### 2.4 Constraints (section 9)
| ID | Constraint | Design consequence |
|---|---|---|
| PS-A-15 | Do not equate experimental score with verified competence | Labelled "experimental"; confidence shown; no hire/no-hire output |
| PS-A-16 | Disclose AI use; human appeal route | AI disclosure on every AI feedback; appeal goes to a human queue |
| PS-A-17 | Minimise personal data; no private submissions to recruiters without consent | Pseudonymous candidate ID; per-share consent record |
| PS-A-18 | Prevent answer-key leakage; handle plagiarism / AI-assisted work without assuming misconduct | Keys server-side only; signals are flags for review, not verdicts |
| PS-A-19 | No ranking on proxies (e.g. typing speed) unless validated for role | Banned ranking features list; no time-based scoring by default |

### 2.5 Success measures (section 8) and how a prototype can evidence them
| Measure | Cheapest credible evidence in a hackathon |
|---|---|
| Auto-score vs human benchmark agreement | 10-20 hand-graded synthetic submissions; report agreement per criterion |
| Consistency over repeated/paraphrased submissions | Run same answer 3x and 3 paraphrases; report score variance |
| Completion and retry rates | 3-5 person usability test; log attempts |
| Relevance of surfaced candidates | Synthetic pool with known ground-truth fit; precision at top-k vs role criteria |
| Disparity checks (language, accessibility, background) | Paraphrase/non-native-English variants of same answer; compare scores |

## 3. Actors and their jobs
| Actor | Jobs | Must never |
|---|---|---|
| Learner | Do task, read criterion feedback, retry, appeal, decide who sees what | Be scored opaquely or shared without consent |
| Recruiter | Define role requirements, search evidence, inspect provenance | See unshared submissions; get a single aggregate rank |
| Human reviewer | Resolve appeals and AI/deterministic disagreements, record outcome | Be bypassed on consequential decisions |
| Content author (task/rubric owner) **[Inference]** | Create and version tasks and rubrics | Change a rubric silently after scores exist |
| System / auditor | Keep immutable log of version, rubric, feedback | n/a |

## 4. Core flows
1. **Learn-to-assess (Nyeras side):** learner finishes a module, is offered a proof-of-skill task, then submits.
2. **Evaluate:** deterministic checks run, then rubric-guided AI feedback for qualitative criteria, then results merged per criterion with a confidence value.
3. **Profile update:** scores written as evidence records (task, rubric version, evidence pointer, date), then competency view recomputed with recency.
4. **Retry / improve:** learner reads feedback, retries a variant, and the profile shows trend, not just latest.
5. **Appeal:** learner challenges a criterion, which creates a human-review item with the original evidence and AI output, and the outcome is logged.
6. **Consent and share (NxtMove side):** learner picks competencies and evidence to share with a named role/recruiter, with expiry and revocation **[Inference]**.
7. **Recruiter search:** role requirement (competency, minimum proficiency, recency, evidence count), then ranked/filtered candidates with "why surfaced" explanation.
8. **Failure case handling:** ambiguous answer, then low confidence, then routed to human review rather than guessed.

## 5. Logical system decomposition (modular monolith, rule 7)
Candidate modules, to be confirmed by the principal-architect at G3:
| Module | Responsibility |
|---|---|
| `competency` | Competency definitions, role requirement templates |
| `tasks` | Task specs, test cases, sandbox runner, variants |
| `assessment` | Deterministic checks, AI rubric evaluator, merge and confidence |
| `evidence` | Evidence records, profile computation (proficiency, recency, confidence) |
| `review` | Appeals, disagreement queue, human decisions |
| `consent` | Sharing grants, scopes, revocation |
| `recruiting` | Role requirements, search, why-surfaced explanation |
| `audit` | Append-only log of versions, rubrics, feedback, access |
| `identity` | Pseudonymous IDs, roles (learner / recruiter / reviewer) |
Each exposes only an `api/` surface to the others.

## 6. Core data entities (conceptual)
`Competency` | `Rubric` (versioned, criteria with weights and descriptors) | `Task` (versioned, variants) | `Attempt` |
`Submission` | `CriterionResult` (score, method: deterministic/AI/human, confidence, rationale) | `Evidence` (links result
to submission pointer and date) | `Appeal` | `ShareGrant` | `RoleRequirement` | `AuditEvent`.
Key invariant: **every `CriterionResult` references exactly one task version, one rubric version, one submission, one date.**

## 7. Assessment engine considerations
**Deterministic-first.** Unit tests, output checks, schema/number checks, SQL result equivalence for data tasks. These give
reproducible, explainable scores.
**AI-assisted only where tests cannot judge** (communication clarity, business reasoning). Constraints from source section 3:
| Risk named in source | Mitigation to design in |
|---|---|
| Inconsistency | Fixed rubric, low temperature, multiple samples, report variance, flag high variance for review |
| Prompt manipulation | Treat submission as untrusted data, delimit it, ignore embedded instructions, add an injection test case to the demo |
| Language/presentation-style bias | Criterion descriptors focus on substance; run paraphrase and non-native-English variants; log disparity |
| Opaque judgement | Per-criterion rationale citing quoted evidence; rubric shown to learner |
**Agreement design [Inference]:** if deterministic and AI results conflict beyond a threshold, mark `needs_review` and do not
publish the AI score to the profile as final.

## 8. Failure cases worth demonstrating (pick 2-3)
| Case | Expected system behaviour |
|---|---|
| Ambiguous / partially correct answer | Low confidence, criterion marked uncertain, human-review option, learner told why |
| AI vs deterministic disagreement | Flagged, held back from profile as final, goes to reviewer |
| Attempted shortcut (hardcoded test outputs, pasted answer key, prompt injection in free text) | Detected by hidden tests / injection guard; score not inflated; event logged, no accusation |
| AI-assisted submission | Disclosed use is accepted; undisclosed heuristics produce a *review flag*, never an automatic penalty |
| Appeal | Reviewer sees original, AI rationale, rubric; decision and reason appended to audit |

## 9. Responsible-design checklist (section 9 turned into tests)
- [ ] "Experimental score" label shown wherever a score appears (PS-A-15)
- [ ] AI-use disclosure on every AI-generated feedback block (PS-A-16)
- [ ] Appeal reachable from every criterion result; produces a human work item (PS-A-16)
- [ ] Recruiter API cannot return a submission lacking an active `ShareGrant` (PS-A-17)
- [ ] No answer key or hidden test in any client-delivered payload (PS-A-18)
- [ ] Ranking features list reviewed; typing speed / time-on-task absent (PS-A-19)
- [ ] No auto-reject or hire recommendation anywhere (PS-A-05, PS-A-15)
- [ ] Personal data limited to pseudonymous ID plus what the task needs (PS-A-17)

## 10. Demo storyboard (maps to PS-A-11 to PS-A-14)
1. Learner finishes a short module, offered the proof-of-skill task.
2. Submits; sees criterion-level feedback (deterministic results plus AI feedback labelled as AI).
3. Profile updates: proficiency, evidence list, confidence, recency; trend after a retry.
4. Failure case: shortcut or ambiguous answer, shown being flagged and routed to review.
5. Learner appeals a criterion; reviewer outcome appears in the audit log.
6. Learner shares selected evidence with a recruiter (consent screen).
7. Recruiter searches by role criteria; sees candidate with "why surfaced"; cannot see unshared data.
8. Slide/section: validation plan (benchmark agreement, paraphrase consistency, disparity checks) and honest limits.

## 11. Scope tiers for a time-boxed build **[Inference]**
| Tier | Content |
|---|---|
| Must | 1 role, 2 competencies, 1 sandbox type, deterministic checks plus AI feedback, profile with 4 dimensions, audit log, 1 failure case, validation plan |
| Should | Appeal flow with reviewer view, consent-based sharing, recruiter search with why-surfaced, retry/trend |
| Could | Second sandbox type, disparity report, variant generation, expiry/revocation of shares |
| Won't | Real Nyeras/NxtMove integration, predictive-validity claims, placement-fee model, auth beyond demo roles |

## 12. Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Scope sprawl across all of sections 5-7 | High | High | Hold to Must tier; cut Could first |
| AI grader inconsistency visible in live demo | Medium | High | Deterministic-first; cached/seeded runs; variance shown honestly |
| Looks like a quiz app | Medium | High | Lead demo with evidence graph and recruiter view |
| Overclaiming validity | Medium | High | Fixed "experimental" labelling; validation plan |
| Sandbox security (running untrusted code) | Medium | High | Restricted runner or non-code task type; threat model at G3 |
| Synthetic data too clean to show disparity | Medium | Medium | Include deliberately varied-language submissions |

## 13. Open questions (carried from the brief)
1. Real Nyeras/NxtMove APIs or data, or simulate? (Founder to ask organisers)
2. Which role and 1-3 competencies for the demo? (G1/G2, product-owner)
3. Which sandbox type: code, analytics, or workplace scenario? (G1 feasibility; recommend by team skill)
4. Deadline, demo length, team size, stack constraints. (Founder)
5. AI provider, cost limit, and offline fallback for the demo. (G3, principal-architect)
6. Hackathon rubric alignment: is `hackathon-24h` the right profile? (Founder)
