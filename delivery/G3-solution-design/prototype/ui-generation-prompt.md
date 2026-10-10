<!-- STATUS: DRAFT — DESIGN REFERENCE, NOT APPROVED PRODUCT SCOPE -->
# Crucible UI Generation Prompt

Owner: product-owner | Gate: G3 design reference | Version: 0.1 | Date: 2026-10-10

> Purpose: copy this prompt into a UI-generation tool to produce a cohesive, clickable product concept for the current Part A direction. This document translates existing workspace context into a design brief; it does not approve scope, resolve open contract gaps, or claim that the prototype is working software.

## Workspace context and source of truth

The active workspace is **SMT**, a stage-gated engineering workspace. Its lifecycle state currently identifies G0 as in progress, with later gates pending. The product context relevant to this prompt is **Crucible (working name)**: a proof-of-competency sandbox for the SAMARTHA Hackathon's **Part A: Nyeras / NxtMove Proof-of-Skill**. Part B, school gamified learning, is explicitly out of scope. Do not turn this into a generic LMS or add unrelated school gamification.

The hackathon brief asks for realistic role-specific tasks, transparent assessment criteria, criterion-level feedback, an evidence-linked learner profile, learner-controlled sharing, and a simulated Nyeras-to-NxtMove workflow. The product must not claim its results predict hiring outcomes or verify professional competence. Use synthetic data and clearly label simulated integrations.

Workspace references to follow, in precedence order:

1. `delivery/G0-intake/project-brief.md` — selected pathway, users, constraints, outcomes, and open questions.
2. `delivery/G0-intake/problem-statement-SAMARTHA-02.txt` — source challenge and expected capabilities.
3. `delivery/G0-intake/final-solution-approach.md` — product thesis and proposed mechanisms.
4. `delivery/G2-product-definition/prd.md` — draft role definitions, score rules, requirements, and scope boundaries.
5. `delivery/G3-solution-design/ux-flows.md` — draft UX flows, screen inventory, copy rules, and design safeguards.
6. `delivery/G3-solution-design/contracts/` — schemas are authoritative for contract-backed data fields; do not invent contract fields and present them as settled.
7. `delivery/G3-solution-design/prototype/README.md` and `review-notes.md` — existing learner mockup context and known gaps. The existing `learner-dashboard.html` is a design reference only, not working software.
8. `governance/constitution/principles.md`, `governance/policies/quality-bar.md`, and `delivery/state/lifecycle-state.yaml` — engineering constraints and current gate status.

When these draft references disagree or leave a field undefined, keep the UI conservative, mark the detail as proposed/sample, and list it as an assumption. Do not silently resolve contract or scope decisions.

## Role for the design generator

Act as a senior product designer, UX architect, and prototyping specialist. Create a coherent, responsive, accessible, high-fidelity interface and a clickable prototype for Crucible. Focus on the product's core proof-of-skill journey and the trust boundaries between learner, recruiter, human reviewer, and auditor. Build realistic screens and meaningful states, not just a collection of attractive dashboard cards.

If the tool can generate a multi-page app, use real linked routes or screens. If it can only create a visual prototype, make every primary navigation item and call-to-action clickable and provide a clear interaction map. Do not implement a backend or imply data persistence, real assessment, real authentication, or production integrations unless the tool was explicitly asked to build those capabilities.

## Product definition

**Working name:** Crucible. Treat it as provisional and make the name easy to replace.

**One-line description:** A proof-of-skill sandbox where learners complete realistic tasks, see how each result was produced, confirm understanding, and choose whether to share evidence with a recruiter.

**Problem:** Course completion and certificates alone do not show whether a learner can apply a skill. Recruiters need relevant evidence without being encouraged to rely on one opaque score. Learners need actionable feedback, retry and appeal routes, and control over who sees their work.

**Core design promise:** Every result is understandable, traceable to its task and rubric, labelled by assessment method, and shown with appropriate uncertainty. The interface helps a person inspect evidence; it does not make hiring decisions.

**MVP demonstration assumption:** Use one sample role, **Junior Data Analyst**, with two separate competencies: **Data analysis (SQL)** and **Communication of findings**. This is a draft demo assumption from the workspace, not a confirmed final scope decision. Keep competencies separate; never create a combined candidate score.

## Users and strict role boundaries

### Learner — Nyeras sandbox

Needs to complete a task on their own seeded data, understand each result, retry, appeal, see evidence over time, and control sharing. The learner sees their own submissions and feedback. They never see another learner's data.

### Recruiter — simulated NxtMove HR portal

Needs to define explicit role requirements and inspect only learner-authorized evidence against them. The recruiter sees pseudonymous candidate aliases, coverage and gaps per competency, evidence provenance, method labels, recency, and verification status. The recruiter does not see ungranted evidence, personal contact details, reviewer-only flags, a total score, a ranked list, or a hire/reject recommendation.

### Human reviewer

Reviews appeals and uncertain cases using the original work, rubric, automated checks, AI rationale when applicable, and history. The reviewer records a reasoned decision. This role is not an automated system and should not be represented as one.

### Auditor

Checks the tamper-evident evidence ledger and assessor health reports. The auditor sees reproducibility and test information, not raw private submissions unless the design explicitly marks an access rule as unresolved.

### Access and role selection

For the prototype, use a role selector or demo entry screen to switch among sample workspaces. Label it **Demo workspace selector** so it cannot be mistaken for a production permission mechanism. In a real product, role access must derive from authenticated authorization, not a learner-controlled selector. Never mix learner, recruiter, reviewer, and auditor data in one view.

## Design principles and non-negotiable safeguards

1. **Evidence before score.** Lead with task evidence, method, date, rubric version, and explanation. A bare number is never the main story.
2. **No aggregate or ranking.** Show one row/card per competency. Recruiter results are ordered by pseudonymous alias (or another neutral, explicitly named rule) and state “Order is not a ranking.” Never show “best match,” candidate rank, hire likelihood, or a cross-competency total.
3. **Persistent experimental disclosure.** Place “Experimental — not a validated predictor of job performance” adjacent to every estimate or band and on any screen likely to detach evidence from its context.
4. **Separate output from understanding.** A task can have a verified output while the understanding probe is unconfirmed. Display these as separate facts; do not let a probe failure silently reduce the task output result.
5. **Method labels everywhere.** Use text and an icon (never color alone): “Automated test,” “Understanding probe,” “AI-assisted judgement,” “Level 4 text session,” and “Human review.”
6. **AI transparency and appeal.** Every AI-involved result says “AI-assisted,” explains which criterion it affected, exposes rationale in plain language, and links to a human appeal route. If AI is unavailable, show a labelled scripted/stub result rather than pretending it is real model output.
7. **Neutral integrity language.** Do not accuse learners of cheating, misconduct, suspicious behavior, or AI use. Similarity flags are reviewer-only and never change a displayed result automatically. Do not add AI-detection features.
8. **Learner consent by default.** Sharing starts off. Preview exactly what an organization can see; require scope and expiry; allow revocation. No grant means the recruiter query returns nothing and does not disclose whether an unshared learner exists.
9. **No speed proxies.** No countdowns, timers, time-taken comparisons, typing speed, or speed-based scoring. Dates may be shown for evidence recency.
10. **Human judgment stays in consequential workflows.** No automatic hire/reject or employment suitability decision.
11. **Privacy minimization.** Use synthetic data and pseudonymous aliases such as `cnd_...` for other people. Never expose names, email addresses, or phone numbers in recruiter/reviewer/auditor lists.
12. **Accessible, plain language.** Aim for short, grade-eight-level copy. Provide keyboard access, visible focus, semantic headings, accessible labels, sufficient contrast, reduced-motion support, and non-color status cues.

## Visual direction

Create a credible, modern education/workforce-skills product. Use a restrained neutral canvas, strong readable typography, one primary accent, and small semantic status colors with text labels. Make the visual tone supportive, calm, and evidence-oriented—not gamified, childish, or like a trading terminal.

- Use a desktop app shell with role-specific left navigation, a compact top bar, page title/breadcrumb, help, notifications where relevant, and profile menu.
- On mobile, replace the sidebar with a usable menu or compact bottom navigation; keep tables scroll-safe or transform them into labeled cards.
- Use cards for competencies and tasks, a clear four-level progress path, evidence timelines, compact charts, and comparison tables only where comparisons do not create ranking.
- Keep status chips consistent: Not started, In progress, Passed, Pending review, Not passed, Shared, Revoked, and Experimental. Always pair color with text/icon.
- Use clear spacing and hierarchy. Do not overfill the learner home page with vanity metrics.
- For the SQL sandbox, show a realistic query editor area, data preview, task instructions, and result feedback. Treat it as a prototype unless actual editor execution is implemented.
- Include empty, partial, loading, error, success, pending review, and mobile states.
- Use realistic synthetic examples; label any fabricated metric or candidate as sample data.

## Information architecture and page inventory

Create these app areas as separate role workspaces with a shared visual system.

### A. Public / entry pages

#### 1. Product landing page

- Header: Crucible logo/name, “How it works,” “For learners,” “For recruiters,” “Trust & assessment,” Sign in, and a primary “Explore the demo” CTA.
- Hero headline: communicate that learners can show how they apply a skill, not just that they completed a course. Supporting copy must avoid employability promises.
- Primary CTA: “Explore a sample skill path.” Secondary CTA: “See how evidence works.”
- Product visual: learner task → criterion feedback → evidence profile → learner-controlled share → recruiter role coverage. Make the simulated connection between Nyeras and NxtMove explicit.
- Explain the four-step mechanism: Do a realistic task; get criterion-level feedback; confirm understanding; choose whether to share evidence.
- Trust section: transparent rubrics, separate evidence methods, experimental estimates, learner-controlled sharing, human appeal.
- Recruiter section: define role requirements, inspect coverage/gaps, verify evidence provenance—no ranking or automated decisions.
- Sample task/competency cards for SQL data analysis and communication of findings.
- FAQ: What does a result mean? Is this a hiring predictor? Who can see my work? Is AI used? Can I appeal? What happens when I retry?
- Footer: About, Help, Privacy, Terms, Assessment transparency. Use placeholder destinations only when labelled as prototype links.

#### 2. Sign in

- Email and password fields, show/hide password, forgot-password link, sign-in CTA, and sign-up/demo route if applicable.
- Optional Google/Microsoft buttons only as nonfunctional prototype controls unless supported.
- Inline required-field and invalid-credential states, loading state, and success transition.
- Never display a signed-in workspace before the sign-in action succeeds in the prototype flow.

#### 3. Account creation / access setup

- Name and email fields only if needed for a learner's own account; password and terms agreement.
- Explain the purpose of account details and minimize collection.
- Include validation, success, and error states. If using demo access, offer a clearly labelled “Enter demo workspace” path with synthetic data.

#### 4. Forgot/reset password

- Email request form and neutral confirmation (“If an account matches, reset instructions will be sent”).
- New password form, password requirements, and completion confirmation.

#### 5. Demo workspace selection

- Explain that all entries use synthetic sample data.
- Choices: Learner sandbox, Recruiter portal, Reviewer workspace, Auditor workspace.
- Show a short description and “Open sample workspace” action for each.
- Keep this visibly separate from real authentication/authorization.

### B. Learner workspace — Nyeras sandbox

Navigation: **My path**, **My profile**, **Sharing**, **Appeals**. Notifications/profile may sit in the top bar. Do not add generic course catalog, certificates, instructor authoring, or team management as core pages: those belong to a general LMS and are outside this selected product direction unless later approved.

#### 1. My path / learner home

- Greeting and concise explanation of current demo role and competencies.
- Prominent resume card for the current level with task title, status, and “Resume task.” Do not show elapsed time.
- Four-level ladder per competency, with separate progress for SQL and communication. Level names: L1 Conceptual; L2 Debugging; L3 Applied Logic and Adaptability; L4 Text session. Show prerequisites and locked states clearly.
- Show “Your estimate updates after all four levels are passed” before the ladder is complete.
- Recent evidence and next useful action. Avoid generic streaks, leaderboards, points, or badges.
- Empty state: “No evidence yet. Complete Level 1 to start your profile.”

#### 2. Competency detail / level overview

- Competency name, what it covers, current level, passed levels, level prerequisites, and the type of assessment used at each level.
- Task list and attempt history with dates and neutral statuses.
- Explain that each learner receives their own seeded dataset with the same task structure.
- Actions: Start, Resume, Review feedback, Retry with fresh data (when enabled).

#### 3. Task / SQL workspace

- Task brief with workplace context, goal, input tables, expected deliverables, and rubric criteria visible before submission.
- Synthetic dataset schema and preview; disclose that each learner's data is seeded uniquely and answer keys/hidden checks are not exposed.
- SQL editor mock area with accessible labels, sample query affordance, and “Run preview” only if the prototype simulates it. Distinguish preview from hidden assessment checks.
- Optional short explanation field. Show no timer and allow save/leave/resume.
- Submit confirmation and retained draft on recoverable error.
- States: not started, in progress, submitting, evaluating, submission error, completed.

#### 4. Criterion feedback

- Summary with overall level status, but not a single competency aggregate.
- One card per criterion showing criterion name, outcome, plain-language rationale, method label, rubric version, and relevant row/result difference.
- For AI-assisted criteria, show “AI-assisted judgement,” concise rationale, confidence in words (Low/Medium/High), and “Appeal this result.”
- Separate “Task output” and “Understanding probe” states.
- Use neutral wording such as “Not passed” rather than “Failed.”
- Provide actions: Review task, Try again (fresh seed when supported), Appeal this result.

#### 5. Understanding probe

- A follow-up uses the learner's own work and altered data; e.g. “On this changed table, what does your query return?”
- Allow a text response and an alternate format request. No clock, countdown, or time pressure.
- Explain that this checks understanding, not conduct. A wrong prediction must not alter the task output result.
- Required unconfirmed copy: **“Output verified, understanding unconfirmed.”** Follow with a short explanation and options to try another probe or request human review.
- Include saving, submitting, unavailable-service/scripted fallback, and error states.

#### 6. Level 4 text session

- Text-only, one prompt at a time: explain the learner's own solution, then adapt it to a changed requirement derived from that work.
- State “No time limit. You can save and leave.”
- Label any AI-assisted evaluation. If the adaptive service is unavailable, say “Scripted follow-up” and continue with a fixed prompt.
- End with criterion-level summary, method labels, appeal action, and a reviewable status. Do not depict it as an automated interview or hiring screen.

#### 7. My profile / evidence profile

- One separate section/card per competency; never a total score.
- Before all four levels pass: show completed level evidence and the message that estimate updates only after the full ladder.
- After all four levels pass: show estimate, lower/upper band, as-of date, evidence count, last evidence date, and method counts. Keep the **Experimental** label adjacent to each estimate.
- Explain simply: “More evidence can narrow this range. Older evidence can widen it.”
- Evidence list: task, rubric version, date, outcome, method, probe status, and AI disclosure where applicable.
- Prominent “Only you can see this” / “Manage sharing” message.
- Do not expose raw submission text to a recruiter unless an explicit approved grant includes it; default off.

#### 8. Sharing and consent

- Empty state: **“Nobody can see your evidence. Sharing is off until you choose to share.”**
- Create grant flow: choose organization, select competency scope, required expiry, optional raw-submission inclusion only if configured, then preview.
- Preview in plain language exactly what will be shared: selected competencies, estimates/evidence fields, included raw submission if any, and expiry.
- Confirmation screen and grants list with organization, scope, date, expiry, and “Stop sharing.”
- Revoke confirmation and result: “Access removed. It takes effect on the organisation's next request.”
- Do not show recruiter search results for non-consenting learners or counts that reveal their presence.
- Mark access-log/history UI as “Proposed — contract field not finalized” if shown; otherwise omit it.

#### 9. Appeals

- List appeals with Received, In review, and Decided statuses.
- New appeal starts from a criterion result and includes a short free-text reason, length guidance, and the original result for context.
- Confirmation: “Appeal sent. A person will review it. Your current result stays visible until then.”
- Decision detail shows human reviewer outcome and reason, with date and evidence provenance.
- Empty state: “You have no appeals.”

#### 10. Learner settings and notifications (supporting pages)

- Profile preferences, accessible display preferences, password/account settings, and notification choices only where needed.
- Keep data collection minimal and do not invent sensitive demographic profiling.
- Notifications: assessment ready, reviewer update, grant created/revoked; show read/unread states.

### C. Recruiter workspace — simulated NxtMove portal

Navigation: **Roles**, **Shared evidence**, **Help & transparency**. Keep the simulated integration label visible. Use aliases only.

#### 1. Recruiter overview

- Explain: “Review evidence against role requirements. This workspace does not rank candidates or make hiring decisions.”
- Cards for saved role blueprints, recently viewed evidence, and workflow guidance; do not show candidate totals that disclose unshared learners.
- Clear empty state leading to “Create a role blueprint.”

#### 2. Roles list and role blueprint setup

- Role list shows title, version, created/updated date, and competency requirements—not fit scores.
- Create/edit role: title, optional summary, 1–8 competencies, Required/Preferred, minimum level passed, minimum estimate lower edge if supported, maximum evidence age, understanding requirement, allowed methods.
- Use human-readable controls and explain each requirement. Show a live plain-language summary of the requirements.
- Save increments blueprint version; disclose that earlier results remain tied to their prior version.
- Clearly mark optional controls that are draft or not yet contract-backed.

#### 3. Shared evidence results / coverage and gaps

- Query only candidates with active grants for the relevant scope.
- Candidate rows use pseudonymous alias and per-competency coverage states: Met, Partly met, Not met, No shared evidence.
- Explain each gap in words (e.g. “Evidence is older than this role’s 180-day requirement”).
- Neutral alias order by default with the persistent line **“Order is not a ranking.”**
- Filters may narrow by competency or coverage state; they may not sort candidates by a hidden aggregate or overall fit score.
- No results state: “No shared evidence yet for this role.” Do not state how many hidden/non-consenting people exist.

#### 4. Evidence detail

- Header: alias, selected role competency, estimate band if available, as-of date, passed levels, understanding status, evidence recency, and Experimental label.
- Method counts/labels and AI-assisted disclosure.
- Evidence items show task, criterion, outcome, date, task/rubric version, and method; raw submission excerpts appear only when the learner's active grant explicitly includes them.
- “Verify receipt” action checks ledger proof. Show Matches, Does not match (do not rely on this item), or Could not check now states.
- Link to the assessor health report for the applicable rubric version, if available.
- Never add a hire recommendation or candidate comparison score.

#### 5. Recruiter transparency/help

- Explain what experimental estimates mean, what they do not mean, how consent works, how recency affects uncertainty, and how to interpret each method label.
- Explain that role coverage is a checklist against recruiter-authored requirements, not a ranking or employment decision.

### D. Human reviewer workspace

Navigation: **Review queue**, **Cases**, **Rubric reference**.

#### 1. Review queue

- Queue ordered by uncertainty/need for review, with explicit ordering rationale and no learner ranking.
- Case row shows pseudonymous learner alias, competency, criterion, reason for review, age/date, and status.
- Similar-answer fingerprint flags are visible only here, neutral wording: “Review flag: similar answer values to another seed.”
- Do not let flags automatically lower a result or appear to recruiters.

#### 2. Review case detail

- Original learner work, task seed context, visible rubric criteria, deterministic test results, AI rationale and disclosure, probe results, prior attempts, and appeal text.
- Keep facts separated by method; make missing evidence obvious.
- Reviewer decision form: uphold, adjust, or request more evidence only if these are supported by the draft workflow; otherwise use a generic reasoned decision action and mark outcome mapping unresolved.
- Record decision rationale, reviewer identity within reviewer-only space, and timestamp; append event rather than overwrite history.
- Confirmation before submitting a decision; show the resulting learner-facing message preview.

### E. Auditor workspace

Navigation: **Ledger verification**, **Assessor health**, **Validation plan**.

#### 1. Ledger verification

- Search/inspect a synthetic event by reference; show sequence, event type, task, rubric version, assessment method, date, and chain verification result.
- Tamper check displays verified or the first invalid event. Do not expose raw private submissions by default.

#### 2. Assessor health report

- Report is scoped to a rubric/version. Show categories tested: paraphrase, typo, filler, style, instruction injection, requirement removal; counts and failures; explicitly mark untested categories.
- Show benchmark agreement and stability only when sample data is explicitly labeled and sample size N is shown.
- Do not use green “fair/valid” badges or imply proof of fairness from a small demo.

#### 3. Validation plan

- Show planned checks for agreement with human-reviewed benchmarks, invariance, probe behavior, seed-copy robustness, usability, and disparity review where feasible.
- Separate plan, measured result, and not-yet-tested status. Use no fabricated success claims.

## Core prototype journeys to connect

### Journey 1: first-time learner completes a task

Landing page → Demo workspace selector or sign up/sign in → Learner My path → Open SQL competency → Start L1/L2/L3 task → Read criteria → Work in SQL task view → Submit → Inspect criterion-level feedback → Complete understanding probe → See output and understanding separately → Retry with a fresh sample seed if not passed → Open My profile and see evidence update.

### Journey 2: learner shares evidence

Learner My profile → Sharing → Select simulated organization and competency scope → Choose expiry → Review exact preview → Confirm grant → View grant → Revoke → See access removed confirmation.

### Journey 3: learner appeals

Criterion feedback → Appeal this result → Enter reason → Submit → Appeals list shows Received → Reviewer resolves case → Learner sees human decision and reason.

### Journey 4: recruiter checks role evidence

Recruiter demo entry → Roles → Create role blueprint for Junior Data Analyst → Add explicit competencies/requirements → Save version → Shared evidence results (only grants) → Open a competency → Inspect evidence and method → Verify ledger receipt → Open assessor health report.

### Journey 5: auditor checks system evidence

Auditor demo entry → Ledger verification → Inspect synthetic event → See chain status → Assessor health report → Review validation plan and distinguish tested from untested.

## Global interaction and state requirements

For every relevant form or page, include:

- Initial, hover, focus, pressed, disabled, selected, loading, success, and error states.
- Validation messages next to fields and a concise summary for multi-field forms.
- Recoverable errors that preserve a learner's draft submission.
- Confirmations for submitting an appeal, granting access, revoking access, and final reviewer decisions.
- Keyboard-operable dialogs with focus management and Escape behavior where appropriate.
- Empty, partial-progress, no-results, pending-review, probe-unconfirmed, expired-grant, revoked-grant, and unavailable-service states.
- Status copy in plain language, with actions that tell the user what to do next.
- Never rely on color alone; use text and icons and maintain screen-reader announcements for async status.

Use these approved draft copy patterns where applicable:

- “Experimental — not a validated predictor of job performance.”
- “Output verified, understanding unconfirmed.”
- “Your estimate updates after all four levels are passed.”
- “Nobody can see your evidence. Sharing is off until you choose to share.”
- “Order is not a ranking.”
- “AI-assisted judgement.”
- “A person will review it.”
- “This result is not a finding about your conduct.”

Avoid: “failed,” “cheated,” “misconduct,” “AI detected,” “suspicious candidate,” “best match,” “hire,” “reject,” “job-ready,” “verified professional,” or any unsupported promise of employability.

## Data and realism rules

- Use synthetic learners, organizations, tasks, and evidence only.
- Use a role and competency set from the current draft demo assumption; clearly mark it sample content.
- Do not invent a final estimate algorithm, confidence formula, AI provider, retention period, access-log contract, raw-submission policy, or integration API.
- Where a visual requires undefined fields, label them “Sample display” or “Proposed — confirm in product design” and list them under Open assumptions below.
- Do not claim the UI is connected to Nyeras, NxtMove, a real LMS, a real code runner, an AI service, or a real ledger. Use “Simulated” or “Prototype” badges.

## Responsive and accessibility requirements

- Start with desktop layout but fully adapt at narrow widths; support 320 px viewport without horizontal page overflow.
- Preserve heading hierarchy and logical reading order.
- Use semantic buttons/links, labeled inputs, table headers, and accessible names for icon buttons.
- Show keyboard focus clearly and ensure dialogs return focus to the invoking action.
- Provide reduced-motion behavior and avoid animation as the only feedback.
- Provide accessible chart summaries and data tables or text equivalents.
- Use readable text sizing and WCAG-conscious contrast; statuses must remain understandable in grayscale.
- Do not use drag-only interactions, timed tasks, or hover-only explanations.

## Expected deliverables from the UI generator

1. A coherent design system: colors, typography, spacing, buttons, fields, alerts, status chips, cards, tables, dialogs, navigation, chart style, and responsive breakpoints.
2. High-fidelity screens for all applicable pages in the page inventory.
3. A clickable prototype linking the five core journeys above.
4. Key screen states for empty, partial, success, error, pending review, unconfirmed understanding, consent, and mobile.
5. A short screen/route map and interaction notes.
6. An assumptions/gaps list that calls out unresolved fields and choices rather than inventing them as settled facts.
7. A clear disclaimer on prototype/sample data and simulated integrations.

## Open assumptions to preserve for product review

Do not decide these inside the visual design. Flag them in the generated notes if a screen depends on them:

- Final demo competency/role selection and exact task content.
- Whether real Nyeras/NxtMove APIs or only simulated adapters will be available.
- AI provider, model, cost limits, and fallback behavior.
- Final estimate/band calculation and confidence presentation.
- Whether recruiters may receive raw submission text and under what explicit grant.
- Sharing expiry limits, re-sharing behavior, and access-record fields.
- Appeals schema, reviewer outcome mapping, and service-level expectations.
- Which role blueprint fields are contract-backed versus proposed.
- Final visual brand, product name, and whether the marketing page is part of the judged demo.

## Final instruction

Generate a focused, polished, trustworthy Crucible proof-of-skill product experience based on the references above. Treat the project as an evidence and learner-agency product with simulated Nyeras/NxtMove workspaces. Keep the UI internally consistent, accessible, role-separated, explicit about uncertainty and AI use, and honest about what is experimental or simulated. Do not turn it into a generic LMS, do not invent product facts, and do not make or imply employment decisions.
