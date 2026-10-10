<!-- STATUS: DRAFT -->
# Feasibility Assessment: Crucible (working name), SAMARTHA Part A

Owner: research-analyst | Gate: G1 | Version: 0.1 | Date: 2026-10-10 | Reviewer: compliance-auditor (independent; not yet reviewed)
Inputs: delivery/G0-intake/final-solution-approach.md; delivery/G0-intake/curated-pitch-content.md (their source lists are reused, not re-researched)

Evidence tags: **FACT** = sourced and checked this session; **FACT-G0** = taken from G0 documents, source not re-opened here; **INFERENCE** = reasoned; **ASSUMPTION** = unvalidated. Constraint assumed from the task: 24 hours, 3 developers. This document supplies evidence and options; it does not choose scope or stack.

## 0. Decision-relevant summary

1. Eight of ten mechanisms are technically straightforward. The weak points are evidence and judgement, not engineering: nothing found shows probes, seeded-defect checks or the band predict job performance (PS §4/§9 already forbids that claim).
2. **Level 4 mutation-generated follow-ups** and **live video screening** are the two Low-feasibility items for 24 hours. Video also carries the heaviest privacy and fairness exposure.
3. The "uncertainty band" is mathematically sound as a Glicko-style rating deviation (verified), but with 1 to 4 evidence items per learner it is illustrative, not calibrated. The label must say so.
4. The hash chain proves internal consistency only. Without an external anchor, whoever holds the database can rewrite the whole chain. "Tamper-evident" must be scoped accordingly.
5. The tracing/explaining-to-writing link is real in intro-programming exam studies but is correlational, population- and question-sensitive, and is about novices on exams, not about hiring or SQL analytics (verified, section 3).

## 1. Summary matrix

Feasibility = likelihood of a credible working version inside 24 h by 3 developers (and, separately, the evidence-validity rating of what it shows).

| # | Mechanism | Feasibility (24 h) | Evidence validity | Biggest risk | Recommendation (options, not a decision) |
|---|---|---|---|---|---|
| 1 | Seeded per-learner tasks with hidden checks (M5) | High | Medium | Seeds change difficulty; hidden checks leak via error messages or client bundle | Build |
| 2 | Predict-the-output probes (M3) | High (executable) / Medium (plain-English) | Low-Medium | Probe fails for reasons unrelated to understanding; no validated link to job skill | Build executable probe; stub plain-English |
| 3 | AI rubric feedback (M2) | Medium | Low-Medium | Inconsistency, prompt injection, bias; cost and provider unknown | Build with labels, deterministic-first, low-confidence to human; stub the model if no provider is approved |
| 4 | Level 4 scripted adaptive session with mutation-generated follow-ups | Low | Low | Mutation of arbitrary learner code yields invalid, trivial or unfair follow-ups; scoring free-text defence is unreliable | Stub (scripted follow-ups per seed, mutation as roadmap), or cut mutation |
| 5 | Skill estimate with uncertainty band (M6) | High (maths) / Low (calibration) | Low | False precision; arbitrary parameters on tiny data | Build as illustrative, label parameters |
| 6 | Hash-chained ledger (M8) | High | Medium (integrity), n/a (validity) | Overclaiming tamper-proof; canonicalisation bugs break verification | Build, scoped claim; roadmap external anchor/signing |
| 7 | Consent vault | Medium | n/a | Authorisation gaps (object-level), revocation semantics, scope creep into real identity | Build minimal (grant, revoke, deny-by-default); stub UI |
| 8 | Assessor invariance suite (M7) | Medium | Medium (for categories tested only) | False comfort; transferred from NLP testing, not validated for this grader | Build small (4 categories, few cases); report categories tested |
| 9 | Break-It Duel | Low-Medium | Low (no source) | Needs a bank of buggy variants and a sound mutation-score check; no supporting evidence found in G0 | Roadmap (or single scripted task if slack) |
| 10 | Live video screening | Low | Low | Biometric/personal data, consent, accessibility and appearance bias; no demonstrated scoring method | Cut from build; roadmap, text/audio alternative is the baseline |

## 2. Per-mechanism assessment

### 2.1 Seeded per-learner tasks with hidden checks
- **Technical (High).** INFERENCE: generate a dataset from a seed (deterministic RNG), compute the expected answer server-side, compare. Standard practice; no novel research needed.
- **Delivery (High).** One task family, one role, one seed generator, 3 to 6 hidden checks fits a single developer in a few hours (ASSUMPTION on effort; not measured).
- **Data (High).** Fully synthetic data; no licensing or personal-data problem.
- **Legal/ethical (High).** No personal data beyond pseudonymous ID. Fairness: the same structure for all, so equal access.
- **Evidence validity (Medium).** FACT-G0: randomised problem pools reduce copying ([Chen, Zilles et al. 2018](https://lagrange.mechse.illinois.edu/pubs/ChWeZi2018a/)); wrong-answer matching detects copying ([NBER w21628](https://www.nber.org/papers/21628)). GAP: no source shows per-learner seeding yields an equal-difficulty task; difficulty spread must be measured by us (G0 V-plan lists it as a risk).
- **Biggest risk.** Seeds shift difficulty; answer fingerprints give false copy flags when many learners legitimately produce identical correct answers (fingerprint must hash wrong-answer values, not correct ones; see V5 false-flag rate).
- **Recommendation: build.** Never-cut item in G0.

### 2.2 Predict-the-output probes
- **Technical (High for executable).** Run the learner's own query on an altered table and compare to the stated prediction; deterministic. Plain-English explanation needs rubric/AI scoring (Medium).
- **Delivery (High / Medium).** Executable probe is a few hours; sandboxed execution of learner SQL/code is the real cost (INFERENCE: use an embedded, resource-limited engine; sandbox escape is a security item for G3).
- **Data (High).** Synthetic.
- **Legal/ethical (Medium).** Probe outcome must not be read as misconduct. G0 already scopes it as "understanding unconfirmed", no penalty to output score. Accessibility: no time limit, alternative format (G0).
- **Evidence validity (Low-Medium).**
  - VERIFIED: tracing and explaining performance correlates with code-writing performance in intro-programming exams. Lopez et al. (2008) reported tracing-to-writing and explain-to-writing correlations; Venables, Tan and Lister (ICER 2009) reported that tracing and explaining questions together accounted for 46% of variance in the writing portion; the strength of explain-to-writing was sensitive to the questions used; a later CS1 replication (600+ students, Python, computer-based) found the original hierarchy was not the best-fitting model although similar models were. Sources via search: [Lopez et al. 2008 (UTS repository)](https://opus.lib.uts.edu.au/bitstream/10453/11384/1/2009002706OK.pdf), [Lister replication (QUT)](https://eprints.qut.edu.au/27653). Confidence: Medium (summaries read, original PDFs not read in full).
  - NOT VERIFIED: any link from probes to hiring outcomes, to SQL/data-analysis tasks, or to adult job-seekers. All studies found are university novices on exams, and are correlational. The G0 doc's own caveat (no study validates probes as hiring signals) stands.
  - NOT VERIFIED: that a probe can separate own work from copied/AI-assisted work. That is Crucible's validation V4 with small N.
  - Note: G0 cites the Auckland ITiCSE 2004 working-group report for this; that report was not re-opened here.
- **Biggest risk.** A learner who solved honestly but mis-predicts (misreading, anxiety, no time limit notwithstanding) is labelled "understanding unconfirmed"; over-reading that label is the harm.
- **Recommendation: build executable probe; stub plain-English probe.**

### 2.3 AI rubric feedback
- **Technical (Medium).** Rubric-conditioned prompting with structured output per criterion is routine; reliability is the issue. FACT-G0: [LLM-judge biases](https://arxiv.org/pdf/2306.05685); [rubric-conditioned grading and confidence deferral](https://arxiv.org/abs/2601.08843) (a 2026 arXiv preprint; not independently re-read here).
- **Delivery (Medium).** Prompt, schema, retries, labelling, injection handling, and a cached/stub fallback for demo reliability. Provider, key management and cost cap are open decisions (G0 section 15 item 5). Without an approved provider this is blocked.
- **Data (Medium).** Learner text sent to a third-party model is a data transfer; needs disclosure and consent copy (see legal).
- **Legal/ethical (Medium).** PS §9: disclose AI use; human appeal. Sending submissions to an external provider needs a lawful basis and processor terms (INFERENCE; not verified against a specific provider).
- **Evidence validity (Low-Medium).** Agreement with human grading is unknown until V1 (10 to 20 synthetic items is too few for any statistical claim; report raw agreement and treat as a smoke test).
- **Biggest risk.** Prompt injection from the submission text and style/verbosity bias; mitigation is deterministic-first plus the invariance suite, which itself is limited (2.8).
- **Recommendation: build** with strict "AI-judged" label, injection test as a standing case, and a stub-mode so the demo does not depend on a live API.

### 2.4 Level 4 scripted adaptive session with mutation-generated follow-ups
- **Technical (Low).** Two distinct parts.
  - Scripted adaptive session: a branching text dialogue with fixed question templates is easy (High).
  - Mutation-generated follow-ups: automatically deriving a "new constraint" from arbitrary learner code and a matching reference answer is open-ended. INFERENCE: it is feasible only if mutations are chosen from a closed catalogue per task family (e.g. change grouping key, add filter, change null handling) with a precomputed expected result; generic code mutation is research-grade.
- **Delivery (Low).** Generation, expected-answer computation, validity filtering (mutants that are equivalent or break the task), scoring of free-text defence, and a reviewable transcript. Likely exceeds one developer's share of 24 h on top of Levels 1 to 3 (INFERENCE).
- **Data (Medium).** Transcripts are personal data and may contain identifying text; needs retention limits.
- **Legal/ethical (Medium).** "Live AI screening" is an automated evaluation; PS §9 requires human appeal. The pitch says "Evaluated and reviewable", which implies human review of the transcript is retained.
- **Evidence validity (Low).** GAP: no source found (and none in G0) that tests mutation-derived follow-ups. FACT-G0: conversational/oral exam preprint ([arXiv 2601.10691](https://arxiv.org/abs/2601.10691v1)) is the only support, a 2026 preprint not re-read here. Treat as hypothesis.
- **Biggest risk.** Unfair or malformed follow-up for a given learner; a scripted demo passes while real inputs fail. Showing a scripted path as "adaptive" would be a claim-integrity problem (constitution rule 5: never present a mock-up as working). Label it "scripted".
- **Recommendation: stub** (scripted, labelled, per-seed catalogue follow-ups); mutation generation as roadmap. Alternative: build a 2 to 3 entry mutation catalogue for one task family only.

### 2.5 Skill estimate with uncertainty band
- **Technical (High).** VERIFIED against [Wikipedia: Glicko rating system](https://en.wikipedia.org/wiki/Glicko_rating_system) (the original Glickman PDF at glicko.net could not be text-extracted; Wikipedia reproduces its formulas):
  - Time widening: RD = min(sqrt(RD0^2 + c^2 t), 350), t = rating periods since last evidence; c chosen so RD grows from a typical value to 350 over a stated number of periods (article's example: 50 to 350 over 100 periods, c about 34.6).
  - Evidence narrowing: RD' = sqrt( (1/RD^2 + 1/d^2)^-1 ), where d^2 = 1 / (q^2 * sum of g(RD_i)^2 * E * (1-E)), g(RD) = 1 / sqrt(1 + 3 q^2 RD^2 / pi^2), q = ln(10)/400.
  - Inference: this models win/loss against opponents of known rating. Crucible's "opponent" would be task difficulty, which requires calibrated task difficulty ratings. That is a design adaptation, not what Glicko provides.
- **Delivery (High).** 40 to 80 lines; simulated evidence streams (V6) are easy.
- **Data (Low).** No real learner data. Difficulty parameters and c are ASSUMPTIONS. FACT-G0: [Math Garden](https://dare.uva.nl/id/67ab8977-5e36-4f9f-962d-be294f2b8c09) is a precedent for rating-based adaptive learning, in school arithmetic, with large data; not transferable by default.
- **Legal/ethical (Medium).** A score is a profiling output; keep the "Experimental" label, no ranking, no time-based inputs (PS §9). If shared with recruiters, consent applies.
- **Evidence validity (Low).** With 1 to 4 items the band is mostly the prior. A narrow band implies precision the data cannot support; a wide band may be unusable. No validation against any external criterion is possible in 24 h.
- **Biggest risk.** False precision; "honest uncertainty" claims become dishonest if parameters are arbitrary and not disclosed.
- **Recommendation: build as illustrative**, show parameters, state "not calibrated". Option: show the band as a categorical evidence-strength label instead of a numeric interval.

### 2.6 Hash-chained ledger
- **Technical (High).**
  - Hash chain: each record stores hash(prev_hash || canonical(record)). Simple.
  - Canonicalisation, VERIFIED from [RFC 8785 (JCS)](https://www.rfc-editor.org/rfc/rfc8785): input must be I-JSON (no duplicate keys, valid Unicode, numbers within IEEE 754 double); numbers serialised per ECMAScript JSON.stringify rules; NaN/Infinity error; keys sorted recursively by UTF-16 code units; array order kept; no whitespace; no Unicode normalisation; lone surrogates error; UTF-8 output. Implication (INFERENCE): store big integers and timestamps as strings; use a vetted JCS library or one tested against RFC vectors rather than `json.dumps(sort_keys=True)`, which differs on number formatting and non-ASCII escaping.
  - RFC 6962 (cited in G0) specifies a Merkle tree for Certificate Transparency, not a linear hash chain. The G0 label "RFC 6962 principle" is a loose analogy; do not claim RFC compliance.
- **Delivery (High).** Append, verify-all, and a tamper demo (flip a byte, verification fails) in a few hours.
- **Data (High).** Internal events only.
- **Legal/ethical (Medium).** Conflict between immutability and erasure rights (see section 3). Mitigation (INFERENCE): ledger holds hashes and pointers, not personal content, so deletion of the underlying record leaves the chain intact.
- **Evidence validity.** Proves integrity of sequence, not truth of content. Anyone with write access can recompute the whole chain; tamper-evidence needs an external anchor (published head hash, signature, or third-party witness). Not verified against a source this session; standard cryptographic reasoning.
- **Biggest risk.** Overclaim ("tamper-proof"); concurrency forks in a single-writer assumption.
- **Recommendation: build** with a scoped claim ("detects edits to past records given a trusted head hash"); signing/anchoring as roadmap.

### 2.7 Consent vault
- **Technical (Medium).** Grants (learner, recipient, scope, expiry, revoked flag) plus a deny-by-default check on every recruiter query. The hard part is object-level authorisation on every path and making revocation take effect immediately (INFERENCE).
- **Delivery (Medium).** Backend rule is small; the UI and audit of grant events are the cut-able parts (G0 cut order lists consent UI).
- **Data (High).** Synthetic users.
- **Legal/ethical (Medium).** FACT-G0: PS §9 requires consent before sharing. A real deployment needs a lawful-basis analysis; see section 3. Consent is not a legal basis the platform can assume to be freely given where a recruiter relationship creates a power imbalance (INFERENCE; jurisdiction-dependent, not verified).
- **Evidence validity.** Not applicable; testable by a negative test: query without grant returns nothing.
- **Biggest risk.** A single bypass route (e.g. a profile endpoint that ignores scope) breaks the central claim.
- **Recommendation: build minimal** (grant/revoke/deny-by-default with tests); stub the UI.

### 2.8 Assessor invariance suite
- **Technical (Medium).** Perturbation generators (typos, filler, paraphrase, language-style, injected instruction) are easy; paraphrase and language-style variants need an LLM or hand-written variants. Directional tests (remove a requirement, score should drop) need hand-built pairs.
- **Delivery (Medium).** A small hand-written set (about 4 categories x 3 to 5 cases) is realistic; an automatic generator at scale is not.
- **Data (Medium).** Seed submissions are synthetic and written by the team; they may not resemble real learner text.
- **Legal/ethical (High).** Synthetic data. The fairness-relevant categories (language style, accessibility-related variants) must not be written as stereotypes of groups; use neutral perturbations (INFERENCE).
- **Evidence validity (Medium for tested categories).** FACT-G0: [CheckList](https://arxiv.org/pdf/2005.04118) (behavioural testing of NLP models, with minimum-functionality, invariance, directional tests) and [LLM-judge biases](https://arxiv.org/pdf/2306.05685). GAP: invariance to our perturbations does not establish fairness, and no source shows these perturbation sets cover real-world language variation. Pass rates on tens of cases carry wide uncertainty.
- **Biggest risk.** A green health report is read as "bias-free". Report counts, categories, failures, and the explicit sentence on what was not tested.
- **Recommendation: build small**; publish by rubric version with category list and denominators.

### 2.9 Break-It Duel
- **Technical (Low-Medium).** The learner writes tests that must fail on hidden buggy versions and pass on a correct one (mutation-testing idea). Needs a curated set of bugs and a safe runner. For SQL/analytics, "buggy query variants" must be authored by hand.
- **Delivery (Low-Medium).** One bug set for one task is possible; it adds a second task type and a second scoring path to a plan that already carries seven must-have items.
- **Data (Medium).** Hand-authored bugs.
- **Legal/ethical (High).** No new concern.
- **Evidence validity (Low).** GAP: no source for the duel format is listed in G0. The related literature on mutation testing and test-writing skill was not searched in this task and is unverified.
- **Biggest risk.** Equivalent mutants or bugs a learner can find only by chance produce unreliable scores.
- **Recommendation: roadmap** (already "Could" in G0); one scripted task only if slack.

### 2.10 Live video screening
- **Technical (Low for scoring; Medium for capture).** Browser capture is routine; transcription and any "evaluation" of content is separable from video. Scoring appearance, voice or behaviour is excluded by PS §9 (no appearance scoring). INFERENCE: nothing in video adds to the evidence that a text/audio defence does not.
- **Delivery (Low).** Real-time media, storage, playback for reviewers, and consent flows are a large surface for 3 developers in 24 h, with a text alternative required anyway.
- **Data (Low).** Video and voice are personal data and potentially biometric; storage, retention and third-party processing add obligations.
- **Legal/ethical (Low).** Highest exposure in the set: consent, retention, access for people with disabilities, regional and accent bias, and discrimination risk. Several jurisdictions regulate automated video interviews and biometric processing (e.g. Illinois AI Video Interview Act); NOT VERIFIED in this session and applicability to the target market (India, per Nyeras/NxtMove naming, ASSUMPTION) is unconfirmed.
- **Evidence validity (Low).** GAP: nothing found or cited that video adds validity for this purpose.
- **Biggest risk.** Introduces proxy bias (F17/F23) that the product's own principles prohibit.
- **Recommendation: cut from build / roadmap**; keep a text (optionally audio) session as the primary Level 4 channel.

## 3. Cross-cutting feasibility

### Technical and delivery (24 h, 3 developers)
- INFERENCE: the Must tier in G0 (M1, M2, M3, M5, M6, M7, M8, two failure cases, validation plan) plus Level 4 is at the upper bound for three people. Items with highest hidden cost: sandboxed execution of learner code, AI provider integration and its stub, validation run and report (V1 to V8).
- Level 4 requirement "score rises only after all four levels are passed" couples every level to the final score; a Level 4 failure blocks the whole demo path unless a scripted fallback exists (INFERENCE).
- Spikes worth doing early (each under 1 h): sandboxed SQL/code execution; JCS canonicalisation test vectors; one-shot LLM structured output with injection test.

### Data
- No real learner, Nyeras or NxtMove data is assumed available (G0 open decision 4). All evidence in the demo is synthetic or team-generated, so results are demonstration of mechanism behaviour, not of real-world performance. FACT-G0.
- Hand-graded comparison set of 10 to 20 items: too small for inferential claims; label as smoke test.

### Legal and ethical (all UNVERIFIED in this session; for compliance-auditor)
- Data-protection regime depends on market. If India: Digital Personal Data Protection Act 2023 (consent, purpose limitation, erasure). If EU users: GDPR Art. 22 on solely automated decisions and the EU AI Act, which lists education/vocational assessment and recruitment systems among high-risk categories. NOT VERIFIED here; no source opened. Needs verification before any compliance statement is made.
- Immutable ledger vs erasure: keep personal content out of the chain (hash and pointer only).
- Issued-problem constraints (PS §9, FACT-G0) are the binding requirements: no equating experimental score with verified competence, AI disclosure, human appeal, data minimisation, consent, no proxy ranking, no assumed misconduct.
- Third-party AI provider: processor terms and data-location are open and cost-limit undecided.

### Evidence validity (overall)
- What the evidence supports: tracing/explaining correlates with code-writing in novice exam studies (verified, correlational, sensitive to questions and population). Rating-band mathematics is correct (verified).
- What it does not support: that Crucible's probes, bands or invariance results predict job performance, are fair across groups, or that mutation-generated follow-ups measure anything. These must stay hypotheses with the "Experimental" label (consistent with PS §4/§9).

## 4. Verification log (what was and was not verified)

| Claim | Status | Source | Confidence |
|---|---|---|---|
| RFC 8785 JCS rules (I-JSON, ES number format, UTF-16 key sort, no whitespace, no normalisation) | VERIFIED | https://www.rfc-editor.org/rfc/rfc8785 (fetched 2026-10-10; summarised by fetch tool, not read line by line) | Medium-High |
| Glicko RD time-decay, c, q, g, d^2, RD' | VERIFIED via secondary source | https://en.wikipedia.org/wiki/Glicko_rating_system (fetched 2026-10-10) | Medium-High |
| Glicko formulas in Glickman's original paper | NOT VERIFIED (PDF returned as binary, unreadable) | http://www.glicko.net/glicko/glicko.pdf | n/a |
| Tracing/explaining skills relate to code-writing skill in novice programmers | VERIFIED (via search summaries of papers) | https://opus.lib.uts.edu.au/bitstream/10453/11384/1/2009002706OK.pdf ; https://eprints.qut.edu.au/27653 | Medium |
| That the relationship holds for SQL/analytics, adults, or predicts hiring | NOT VERIFIED; no source found | | n/a |
| That probes distinguish own from copied or AI-assisted work | NOT VERIFIED | | n/a |
| Mutation-generated follow-ups or Break-It Duel effectiveness | NOT VERIFIED; no source found | | n/a |
| Video screening validity, and biometric/AI-interview regulation | NOT VERIFIED | | n/a |
| DPDP Act, GDPR Art. 22, EU AI Act applicability | NOT VERIFIED | | n/a |
| G0 sources (ECD, 2601.08843, 2306.05685, CheckList, NBER, etc.) | FACT-G0, not re-opened; two are 2026 preprints | see G0 | Low-Medium |

## 5. Key assumptions and validation method

| ID | Assumption | Validation method | When |
|---|---|---|---|
| A1 | Per-learner seeds keep task difficulty within tolerance | Generate 50 seeds, solve with reference solution, compare check pass-rates and edge-case coverage | G5 early |
| A2 | Executable probe can run safely and deterministically on learner code | Sandbox spike with resource limits and adversarial inputs | G3/G5 spike |
| A3 | AI feedback agrees with human grades on most criteria | V1 on 10 to 20 items; report per-criterion raw agreement, no inference | G5 |
| A4 | An approved AI provider and cost cap exist | Founder decision (G0 item 5) | G2 |
| A5 | Fingerprints flag cross-seed copies with acceptable false flags | V5 injected copies and clean controls | G5 |
| A6 | Band parameters give sensible behaviour | V6 simulated streams | G5 |
| A7 | Learners understand the "understanding unconfirmed" label | V7, 3 to 5 supervised testers | G5/G6 |
| A8 | Recruiters can use coverage/gap view without reading it as a rank | V8 plus short think-aloud | G5/G6 |
| A9 | Jurisdictional requirements are as assumed (India/EU) | Compliance-auditor review of DPDP, GDPR, AI Act | G1 review |

## 6. Risk register

L = likelihood, I = impact (1 low to 3 high); rating = L x I.

| ID | Risk | L | I | Rating | Mitigation | Fallback |
|---|---|---|---|---|---|---|
| R1 | Too many mechanisms for 24 h | 3 | 3 | 9 | Fixed Must tier; cut order in G0 | Deliver seeded task, checks, probe, band, ledger and one failure case only |
| R2 | Level 4 mutation follow-ups malformed or unfair | 3 | 2 | 6 | Closed mutation catalogue per task family | Scripted follow-ups, labelled scripted |
| R3 | Live video adds privacy/fairness harm and time | 2 | 3 | 6 | Do not build; text/audio default | Roadmap slide only |
| R4 | AI provider unavailable, expensive or unreliable at demo | 2 | 3 | 6 | Stub mode with cached outputs, labelled | Deterministic checks only for demo |
| R5 | Prompt injection or bias moves AI scores | 2 | 3 | 6 | Untrusted-input handling, standing invariance tests | Route to human; AI feedback non-scoring |
| R6 | False precision in the band | 3 | 2 | 6 | Show parameters; "illustrative"; categorical label | Replace numeric band with evidence-strength tier |
| R7 | Ledger overclaimed as tamper-proof | 2 | 2 | 4 | Scoped wording; head hash exported | Remove "tamper" wording |
| R8 | Probe label read as accusation | 2 | 3 | 6 | Wording, no penalty to output score, appeal | Show probe as separate informational evidence |
| R9 | Invariance report read as fairness proof | 3 | 2 | 6 | List categories and denominators; stated limits | Rename "regression checks" |
| R10 | Consent bypass via an unprotected route | 2 | 3 | 6 | Deny-by-default at one choke point; negative tests | Disable recruiter view |
| R11 | Legal framework wrong or missed | 2 | 2 | 4 | Compliance review (A9) | Synthetic-data-only, no real-person claims |
| R12 | Hand-graded and synthetic data too small and unrepresentative | 3 | 1 | 3 | Report as smoke tests | State no generalisation |

## 7. Recommendation

Proceed with conditions (decision belongs to the Founder):
1. Treat as 24-hour feasible: seeded tasks, executable probe, band (illustrative), hash-chained ledger, consent minimal, small invariance suite, AI feedback with stub.
2. Treat as not feasible at credible quality in the window: mutation-generated Level 4 follow-ups (offer scripted alternative), live video (cut), Break-It Duel (roadmap).
3. Resolve before G2: AI provider and cost cap; demo configuration; target jurisdiction for the legal review.
4. Do not present any mechanism as validated beyond the verification log in section 4.

## 8. Open questions
1. Which jurisdiction(s) are in scope for the legal review?
2. Is a Level 4 scripted session acceptable as "Live AI Screening" under the issued problem statement, or must it be generative?
3. Is "Level 4 passes required for score" in the pitch a hard requirement, given the Level 4 risk?
4. Is a numeric band required, or is a categorical evidence-strength label acceptable?
