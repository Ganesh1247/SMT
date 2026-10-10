<!-- STATUS: DRAFT -->
# Success Metrics: Crucible (working name), Part A

Owner: product-owner | Gate: G2 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer (then compliance-auditor)
Inputs: delivery/G2-product-definition/prd.md; delivery/G0-intake/problem-statement-SAMARTHA-02.txt (Part A s8); delivery/G0-intake/final-solution-approach.md s11

> All pass lines are **Proposed** by the team, not taken from the source. Samples are tiny, so results are descriptive, not statistical proof of quality or fairness. Every result is reported as obtained, including failures. Nothing here validates any score as a hiring predictor; all scores are experimental. "Baseline" below is what exists without the system (mostly none); no baseline data exists yet.

## Metrics

Review date for all rows: end of build window (H20-22) and again before the Round 4 demo (H22).

| ID | PS s8 measure | Metric | Type | Baseline | Target (Proposed) | How measured within 24 h | Owner | Related REQ |
|---|---|---|---|---|---|---|---|---|
| M1 | Agreement with human-reviewed benchmarks | Per-criterion agreement between automated result and hand-graded label on 10-20 synthetic submissions, split by method (deterministic vs AI) | quality | None (no benchmark) | Deterministic criteria >= 90%; AI-judged criteria >= 80%; criteria below line flagged, not hidden | Two team members grade independently with the rubric; disagreements resolved and counted; run assessor; compute agreement and report N | quality-engineer | REQ-003, 004, 013 |
| M2 | Consistency across paraphrased submissions | Share of invariance cases whose criterion result is unchanged within tolerance, by category (paraphrase, typo, filler, language style, injection) | quality | None | >= 90% overall; each category reported with its own rate; any category under 80% flagged | Assessor audit suite runs generated variants of benchmark items; report per rubric version | quality-engineer | REQ-011 |
| M3 | Consistency (directional) | Share of requirement-removed or wrong-figure variants where the relevant criterion drops | quality | None | >= 90% | Same suite, directional cases | quality-engineer | REQ-011 |
| M4 | Feedback usefulness | Share of testers who can state what to change next after reading feedback | quality | None | Report only; target >= 60% (n=3-5, indicative) | Supervised usability test; one question after feedback; observer note | product-owner | REQ-003 |
| M5 | Completion and retry | Completion rate per level; retry rate after a fail; share of retries that improve | adoption | None | Report only; indicative: >= 60% of testers finish L1-L3 of C1 | 3-5 testers; event log counts; no time-based scoring | quality-engineer | REQ-006, 017 |
| M6 | Score-rule integrity | Cases where a competency score changed before all four levels passed, or one competency's change moved another | quality | n/a | 0 cases in all test runs | Automated acceptance test on seeded learner states; audit of ledger | quality-engineer | REQ-006, 009 |
| M7 | Candidate relevance | Precision at top-k of surfaced candidates against known fit on a synthetic pool (k and pool size stated) | quality | Keyword match on CV text (comparison arm, if time) | Report; target >= 0.8 at k=3 on a pool of ~20 with planted ground truth (circular by construction, so labelled as a functional check only) | Build synthetic candidates with known role fit; run role blueprint; compute | quality-engineer | REQ-016 |
| M8 | Disparity checks | Difference in criterion pass rate between matched submissions varied only by language style, verbosity or accessibility-related format (for example plain vs verbose, screen-reader-friendly formatting) | quality | None | Absolute difference <= 5 percentage points per category; larger gaps reported and not explained away | Matched-pair variants in the invariance suite; no real demographic data used (lawful, feasible) | quality-engineer | REQ-011 |
| M9 | Probe usefulness | Probe pass rate when the author solves vs when a different person receives the solution | quality | None | Report; N small, no generalisation | Team members, both conditions | quality-engineer | REQ-005 |
| M10 | Integrity | Fingerprint detection rate and false-flag rate on injected cross-seed copies and clean controls | quality | None | Report both; false flags on clean controls target 0 of N | Injected set | quality-engineer | REQ-014 |
| M11 | Ledger | Tamper tests detected | quality | n/a | 100% of injected alterations detected | Automated test, alter each event field | quality-engineer | REQ-008 |
| M12 | Responsible design | Checklist items passed (experimental label, AI label, no aggregate, no hire output, no ungranted data) | quality | n/a | 100% of items | Scripted review of every view and API response | compliance-auditor | REQ-010, 022, NFR-003 |
| M13 | Profile comprehension | Share of testers who correctly say what the band means and that the score is experimental | quality | None | Report only (n=3-5) | Two comprehension questions in usability test | product-owner | REQ-009, 010 |

## Guardrail metrics

What must not get worse (checked on every rubric or task change):
- Invariance rate (M2) must not fall below the last published version for any category; a drop blocks release of that rubric version.
- Seed difficulty spread: solve outcomes across seeds for the same task should not differ by more than the Proposed tolerance (report spread; target <= 10 percentage points).
- A failed probe must never change the output score (0 cases).
- No integrity flag may lower a score automatically (0 cases).
- No time-on-task or typing-speed feature present in any score or view (0).

## What will be reported even if it fails

The evidence pack (REQ-013) will include every metric above with N, method and date, whether or not it meets the Proposed line. Specifically: M1 criteria below 80%; M2 categories with failures and example cases; M8 gaps above tolerance; M10 false flags; M5 and M13 low completion or comprehension; any untested category (language coverage, real accessibility users, real recruiters). Limits stated plainly: tiny N, synthetic data, team-graded benchmark, no real hiring outcomes, so no validity or fairness claim is made.

## Instrumentation needs

Events recorded in the ledger or log (no personal data, pseudonymous IDs only):
- level started, submitted, passed, failed, resumed; attempt number; seed ID
- criterion result with method, confidence, rubric and task version
- probe shown, prediction, executed result
- AI feedback issued (provider label or stub), injection attempt detected
- score and band update, with levels that triggered it
- fingerprint flag; appeal opened and decided
- consent granted and revoked; recruiter query and returned fields
- assessor audit run: version, categories, counts, failures

No keystroke timing or time-on-task collection for scoring. Session timing, if kept for the usability test, is observational only and excluded from scores.
