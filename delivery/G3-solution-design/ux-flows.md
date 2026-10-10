<!-- STATUS: DRAFT -->
# UX Flows and Design System: Crucible (working name)

Owner: ux-architect | Gate: G3 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer (usability and accessibility checks), then compliance-auditor
Inputs: delivery/G0-intake/final-solution-approach.md; delivery/G0-intake/curated-pitch-content.md; delivery/G4-delivery-plan/implementation-plan.md; delivery/G3-solution-design/contracts/README.md, shared-evidence.schema.json, role-requirement.schema.json

> Scope: screens show only fields that exist in the contracts or in the approach document. Where a screen needs data no contract defines, it is listed in section 12 as a gap, not invented. No `REQ-###` IDs were available to this draft; traceability in section 11 uses the Must/Should tiers and flow IDs and must be re-keyed when the PRD is FINAL.

## 1. Personas and jobs-to-be-done

| Persona | Surface | Job to be done | Fear to design against |
|---|---|---|---|
| **Learner** (finished a Nyeras module) | Sandbox `learner-ui` | "Show what I can really do, and know why I got each result." | An unexplained score; being accused of cheating; losing control of who sees my work |
| **Recruiter / HR** | HR Portal `hr-ui` | "See which role requirements a candidate has evidence for, and how strong that evidence is." | Over-trusting one number; seeing something the learner never agreed to share |
| **Reviewer** (human assessor) | Trust review screens | "Decide the cases where the system is least sure, quickly and with full context." | Deciding without the original work; a queue that buries the hard cases |
| **Auditor** | Trust audit screens | "Check that the record was not altered and that the grader is tested." | Being asked to trust a claim without a check I can run |

## 2. Information architecture

```
Learner (Sandbox)                 Recruiter (HR Portal)            Reviewer (Trust)          Auditor (Trust)
 Home: my path (levels 1-4)        Roles                            Review queue              Ledger check
  Task (per level)                  Role setup (RoleRequirement)     Review case               Assessor health reports
   Criterion feedback               Role results (coverage, gaps)     original work
   Probe                            Candidate evidence page           AI rationale
   Level 4 text session              method labels                    rubric
  Profile                            receipt verification             decision
   Estimate band + evidence
  Sharing and consent
   Grants, access record*
  Appeals
```
\* Access record is conditional on contract open item 6.

Rules: each role sees only its own area; no cross-role links. Primary nav has 3 to 5 items per role. The "Experimental" label and the AI-use note sit in the global header or footer of every screen that shows an estimate, criterion result or evidence item.

## 3. Global rules (all roles)

| ID | Rule |
|---|---|
| G-1 | **Never** show an aggregate score, total, rank, percentile, "match %", "x of y met" or hire recommendation. Sort controls that order people by strength do not exist. |
| G-2 | Every estimate shows estimate **and** band **and** "as of" date, never a bare number. Scale 0 to 1 is shown as e.g. "0.58, likely range 0.45 to 0.70". |
| G-3 | "Experimental: not a validated hiring predictor" label visible on every estimate and evidence screen (`labels.experimental` is always true). |
| G-4 | If `ai_used` or `ai_disclosure` is true, show "AI-assisted feedback" on that item, with confidence and a link to appeal. |
| G-5 | Failed or missed probe wording is exactly **"Output verified, understanding unconfirmed"** (or "Understanding unconfirmed" in short form). Never "failed", "cheated", "misconduct", "suspicious" or "AI detected". |
| G-6 | Integrity flags (`flags`) appear only to Reviewers, as "Review flag: similar answer values to another seed". They never change a displayed outcome and never appear to Recruiters. |
| G-7 | Method label vocabulary (fixed, with plain names): `deterministic_test` = "Automated test", `probe` = "Understanding probe", `ai_judged` = "AI-assisted judgement", `live_screening` = "Level 4 text session", `human_review` = "Human review". Each label has an icon plus text, never colour alone. |
| G-8 | No timers, countdowns, "time taken" or speed indicators anywhere. Time appears only as dates ("as of", "evidence from"). |
| G-9 | No names, emails or phone numbers on any screen other than the learner's own session. Others see the pseudonymous alias (`cnd_...`). |
| G-10 | Evidence age is always visible next to the band; "older evidence widens the range" is explained once in a help link. |

## 4. Learner view

**User goal:** "Do the task on my own data, understand every result, prove I understand it, control who sees it, and challenge anything that looks wrong."

### 4.1 Primary flow L-1: complete a level

1. Learner opens **My path** and sees four levels with status (Not started, In progress, Passed). A saved level offers "Resume".
2. Learner opens the **Task** for the current level. Their own dataset (per-learner seed) and instructions are shown; "Your data is different from other learners' data" is stated.
3. Learner writes a query and a short note, then selects "Submit".
4. **Criterion feedback** appears per criterion: result, method label, plain reason, row-level difference where it exists, and an "Appeal this result" action.
5. Learner is offered the **Probe** ("On this changed table, what does your query return?"). They answer at their own pace; "I need a different format" is always available.
6. Result shows both facts side by side: "Output: verified" and "Understanding: confirmed / unconfirmed".
7. If a level is not passed, learner selects "Try again", gets a fresh dataset and sees attempt history. Passed levels stay recorded.
8. After all four levels are passed, **Profile** shows the updated estimate band. Before that, Profile says "Your estimate updates after all four levels are passed" and shows progress.

### 4.2 Flow L-2: Level 4 text session

1. From My path, learner opens Level 4 (enabled when Levels 1 to 3 are passed).
2. Intro states: text only, no time limit, you can save and leave, AI feedback is labelled, a human can review.
3. Session shows one prompt at a time: "Explain how your solution works", then "Your table now also has [new constraint from your own query]. How would you change it?"
4. Learner types an answer, selects "Send". Each reply gets a short acknowledgement, not a score.
5. At the end, a summary lists each criterion with method label (Level 4 text session, AI-assisted judgement) and appeal action. Result is "Evaluated, reviewable", not pass/fail ranked.
6. Failure: if the follow-up service is unavailable, the session shows "Scripted follow-up" label and continues with a fixed prompt (matches contingency in the implementation plan).

### 4.3 Flow L-3: share with a recruiter

1. Learner opens **Sharing**. Empty state explains nobody can see anything.
2. Selects "Share with an organisation", picks the organisation, competency (scope), whether raw submission text is included (off by default, subject to open item 4), and an expiry date (required).
3. A plain-language preview says exactly what the organisation will see.
4. Learner confirms. Grant appears in the list with "Stop sharing" for each.
5. After "Stop sharing", the learner sees "Access removed. It takes effect on the organisation's next request."

### 4.4 Flow L-4: appeal

1. From any criterion, learner selects "Appeal this result".
2. A short form asks "What do you think is wrong?" (free text, plain, max length shown). The original result stays visible.
3. Confirmation: "Appeal sent. A person will review it. Your current result stays visible until then."
4. Appeals list shows status (Received, In review, Decided) and the human decision with reason once decided.

### 4.5 Learner screen inventory

| Screen | Purpose | Content (existing fields only) | Actions |
|---|---|---|---|
| My path | Progress across 4 levels | Level names, status, attempt count, resume | Open level, resume |
| Task | Do the work | Instructions, per-learner dataset, query editor, note field | Run check query (read-only), Submit |
| Criterion feedback | Explain each result | Criterion, outcome, method label, rationale, row diff, AI label and confidence when `ai_judged` | Appeal, Try again |
| Probe | Verify understanding | Altered table, question, answer field, alternative-format link | Submit answer, Request different format |
| Level 4 session | Explain and adapt | Prompt, text box, saved history, "Scripted" label if static | Send, Save and leave |
| Profile | Show estimate with evidence | Per competency: estimate, lower, upper, as-of date, levels passed, method counts, understanding status, evidence list (method, outcome, date, task and rubric version), experimental label, AI-use disclosure | Open evidence item, Share, Appeal |
| Sharing | Consent control | Grant list (organisation, scope, expiry), create form, revoke; access record if built | Share, Stop sharing |
| Appeals | Track challenges | Appeals with status and decision | New appeal (from criterion), view decision |

### 4.6 Learner states

| State | Screen(s) | Behaviour and copy |
|---|---|---|
| Empty | Profile | "No evidence yet. Complete Level 1 to start your profile." Link to My path. |
| Empty | Sharing | "Nobody can see your evidence. Sharing is off until you choose to share." |
| Empty | Appeals | "You have no appeals." |
| Loading | Any | Skeleton or spinner with text "Loading your results" announced via `role="status"`. After 5 s, "Still loading. Your work is saved." No time shown against the learner. |
| Evaluating | Criterion feedback | "Checking your answer. This can take up to a minute." Progress is indeterminate; the page can be left and re-opened. |
| Error | Any | "We could not load this. Your work is saved. Try again." with a Retry button and error reference. No technical stack text. |
| Error | Submit | "Your answer was not sent. It is still in the box. Try again." Draft retained. |
| No-grant | Sharing, Profile | Profile shows "Only you can see this." with "Share" action. |
| Low-confidence | Criterion feedback | "We are not sure about this result. A person will check it." Result shown as "Pending review"; confidence shown in words (Low, Medium, High) with the number on request. Auto-routed to the review queue. |
| Probe-failed | Probe result, Profile, evidence | "Output verified, understanding unconfirmed." Explanation: "Your answer to the main task is correct and your score for it is unchanged. We could not confirm you can explain or predict how it works. This is not a finding of misconduct. You can try another probe or ask for a person to look." Actions: "Try another probe", "Appeal". |
| Probe format request | Probe | "We will offer a different format, such as a written explanation. Your answer is not timed." |
| Success | Profile | Band shown with date; "Updated just now". |
| Experimental | Profile | Persistent: "Experimental. This is not a validated predictor of job performance." |
| Injected instruction | Criterion feedback | Not surfaced to the learner as an accusation. The note is graded on content only; ledger records the event. Neutral line if shown: "Text in your note that looks like an instruction to the grader was ignored." |

### 4.7 Learner content rules

- Plain language, reading level about grade 8; short sentences; one idea per sentence.
- Say what happened, why, and what can be done next. Example: "Criterion 2: the query returns 41 rows, expected 38. 3 rows have a date outside the range."
- Use "result", "evidence", "estimate range". Avoid "score" as a bare noun; avoid "fail"; avoid "confidence interval", "posterior", "Glicko".
- Neutral, non-accusatory tone for anything about integrity. No exclamation marks, no gamified praise.
- Every AI-involved result says "AI-assisted" and shows a human appeal path.
- Dates use an unambiguous format, e.g. "10 Oct 2026".

## 5. Recruiter / HR view

**User goal:** "Define what this role needs, then see which of those requirements each consenting candidate has evidence for, which are gaps, and how that evidence was produced and can be verified."

### 5.1 Primary flow R-1: set up a role

1. Recruiter opens **Roles**, selects "New role" (or opens an existing role; a version number shows).
2. Enters title (3 to 80 characters) and optional summary (up to 500).
3. Adds 1 to 8 competencies from the registry; for each sets priority (Required or Preferred).
4. Optionally sets per competency: minimum level passed (1 to 4), minimum estimate lower edge (0 to 1, shown as "lowest likely value"), maximum evidence age (days, 1 to 1825), "understanding must be confirmed", allowed methods.
5. A plain-language summary reads back the role: "Required: Data analysis, level 3 or higher, evidence from the last 180 days, understanding confirmed."
6. Saves. Version increments; a notice says earlier results stay reproducible at their version.

### 5.2 Flow R-2: view results (coverage and gaps)

1. From a saved role, recruiter selects "See shared evidence".
2. Results lists consenting candidates by alias. For each candidate, a row per role competency shows a coverage state: Met, Partly met, Not met, No shared evidence.
3. A Required competency that is Not met or has No shared evidence is highlighted as a **Gap**, with the reason in words (e.g. "Level passed, but newest evidence is 240 days old; window is 180").
4. Recruiter selects a competency cell to open the evidence page.
5. No total, no ordering by strength, no "best match". Default order is alias ascending; a note reads "Order is not a ranking."

### 5.3 Flow R-3: inspect evidence and verify

1. **Evidence page** opens for one candidate and one competency.
2. Top: estimate, band, as-of date, levels passed, understanding status, last evidence date, "Experimental" label, "AI-assisted items: yes/no".
3. Method summary: counts of Automated test, Understanding probe, AI-assisted judgement, Level 4 text session, Human review.
4. Evidence list: each item shows method label, criterion, outcome, understanding status, date, task and rubric version, AI disclosure.
5. Recruiter selects "Verify receipt" on an item. Result: "Matches the ledger (entry 214)" or "Does not match the ledger. Do not rely on this item." or "Could not check right now."
6. "Assessor health report for this rubric version" links to the report summary (read-only) when `assessor_report_ref` exists.
7. If the grant includes raw submission, an excerpt is shown labelled "Shared by the learner".

### 5.4 Recruiter screen inventory

| Screen | Purpose | Content (existing fields only) | Actions |
|---|---|---|---|
| Roles | List roles | Title, version, created date | New role, open, edit |
| Role setup | Create or edit RoleRequirement | title, summary, competencies[], priority, min_levels_passed, min_estimate_lower, max_evidence_age_days, require_understanding_confirmed, allowed_methods, version | Add or remove competency, Save |
| Role results | Coverage and gaps | Candidate alias, per-competency coverage state, gap highlight, reason text, last evidence date | Open evidence, filter by competency or state |
| Evidence page | Inspect evidence | proficiency (estimate, lower, upper, as_of), levels_passed, method_counts, understanding_status, evidence_items, last_evidence_at, labels, assessor_report_ref, ledger_proof (head sequence, head hash) | Verify receipt, open health report |

### 5.5 Recruiter states

| State | Screen | Behaviour and copy |
|---|---|---|
| Empty | Roles | "No roles yet. Create a role to see shared evidence against it." |
| Empty | Role results | "No shared evidence yet for this role." No reason given. (A learner with no grant is indistinguishable from one who does not exist; no totals, no "n hidden".) |
| Loading | Role results | "Loading shared evidence" (`role="status"`); rows appear as they arrive without reordering. |
| Error | Any | "We could not load shared evidence. Try again." with Retry; no partial totals. |
| Validation error | Role setup | Inline, field-specific, e.g. "Add at least one competency." "Title must be 3 to 80 characters." Summary of errors at top, focus moved to it. |
| No-grant | Evidence page, Role results | Cell reads "No shared evidence for this competency". Same wording whether not shared, expired or revoked. |
| Grant expired or revoked mid-session | Evidence page | "This evidence is no longer shared." Content removed. |
| Low-confidence | Evidence page | Wide band shown with words: "Wide range: little or older evidence." Items with `inconclusive` outcome carry "Inconclusive". Recruiter sees no reviewer-queue detail. |
| Understanding unconfirmed | Results, Evidence page | Cell shows "Output verified, understanding unconfirmed" in neutral colour. If the role requires understanding confirmed, the state is Partly met and the reason names it. Never "failed". |
| Understanding not attempted | Evidence page | "Understanding probe not attempted." |
| Verify failed | Evidence page | "Does not match the ledger. Do not rely on this item." plus reference to report to Trust. |
| Success | Role setup | "Role saved as version 3." |

### 5.6 Recruiter content rules

- Say "coverage" and "gap", not "match", "fit", "score" or "candidate strength".
- Every threshold is shown in plain words next to its result. "min_estimate_lower" reads "Lowest likely value of at least 0.60".
- Show evidence method before outcome so a recruiter knows how strong the item is.
- No highlighting of any single candidate as "top" or "recommended"; no colour scale that implies better or worse across people.
- Label every screen "Experimental. Not a validated hiring predictor. These results should support, not replace, your own assessment."
- No personal-attribute or speed filters exist, and the role form has no field for them.

## 6. Reviewer view

**User goal:** "Open the cases where the system is least sure, see the original work and the reasoning, and make a clear, recorded decision."

### 6.1 Primary flow V-1: review a case

1. Reviewer opens the **Review queue**; items are ordered by uncertainty (highest first). Each row shows an alias, criterion, reason for queue entry (Low confidence, Appeal, Conflict between methods), and age of the item.
2. Selects a case. **Review case** shows side by side: the original work (query and note, unmodified), the AI rationale with confidence, the rubric criterion with its version, probe result and understanding status, and any review flag.
3. Reviewer chooses a decision per criterion: "Uphold result", "Change result" (select outcome) or "Needs more information".
4. A reason (free text, required) is entered.
5. Reviewer selects "Record decision". Confirmation: "Decision recorded in the ledger as entry N." Next case opens on request.
6. Failure: if recording fails, the decision stays in the form and "Not recorded yet. Try again." is shown. No duplicate is created on retry.

### 6.2 Reviewer screen inventory

| Screen | Purpose | Content | Actions |
|---|---|---|---|
| Review queue | Prioritise by uncertainty | Case ID, alias, criterion, entry reason, confidence (words), item age | Open case, filter by reason |
| Review case | Decide | Original work, AI rationale and confidence, rubric text and version, probe result and understanding status, review flags, learner appeal text if any, prior decisions | Decide per criterion, enter reason, Record |
| Decision recorded | Confirm | Ledger entry number, outcome, reason | Next case, back to queue |

### 6.3 Reviewer states

| State | Behaviour and copy |
|---|---|
| Empty queue | "No cases need review." |
| Loading | "Loading case" (`role="status"`). Original work loads before AI rationale; the decision form is disabled until both are loaded. |
| Error | "We could not load this case. Try again." No partial decision form. |
| Low-confidence | The queue's normal case; confidence labelled "Low" with the reason. |
| Conflict | "Automated test and AI-assisted judgement disagree" shown as the entry reason with both results side by side. |
| Probe unconfirmed | Shown as "Output verified, understanding unconfirmed" with an explicit line: "This is not evidence of misconduct. Decide only on the rubric." |
| Review flag | "Review flag: answer values match another learner's seed. A flag does not change the result." |
| Already decided | "This case was decided by another reviewer." Read-only. |
| Missing original work | "Original work is unavailable. You cannot decide this case." Decision actions disabled; case reported. |

### 6.4 Reviewer content rules

- Neutral, factual: "AI-assisted judgement: Partial (confidence 0.42)". Show the rubric wording verbatim.
- Identity: alias only; no names or contact details.
- Reasons must be specific to a rubric criterion; the form prompts "Which part of the rubric does this rest on?"
- Never display speed, typing pattern or time spent.

## 7. Auditor view

**User goal:** "Run a check that the record is intact, and read how well the grader was tested for the rubric version in use."

### 7.1 Primary flow A-1: verify the ledger

1. Auditor opens **Ledger check** and sees the latest head sequence and head hash.
2. Selects "Verify ledger". Progress indeterminate; status announced.
3. Result: "Verified: entries 1 to 842 form an unbroken chain. Head hash sha256:ab12... ." or "Not verified: entry 317 does not match its expected hash. Entries 317 onward cannot be relied on."
4. Auditor can copy the head hash and the sequence for an external record.

### 7.2 Flow A-2: read the assessor health report

1. Auditor opens **Assessor health reports**, picks a rubric version.
2. Report shows each tested category (paraphrase, filler, typos, language style, injected instructions, requirement removed), number of cases, number within tolerance, and failures listed.
3. A standing note states the limit: "This report covers only the categories listed. It is not a fairness or validity guarantee."
4. Auditor can compare two rubric versions side by side.

### 7.3 Auditor screen inventory

| Screen | Purpose | Content | Actions |
|---|---|---|---|
| Ledger check | Show integrity | Head sequence, head hash, last verified time, result | Verify ledger, copy hash |
| Assessor health reports | List reports | Rubric version, date, report ID | Open, compare |
| Report detail | Show test results | Category, cases, within tolerance, failures with example, rubric and model references | Compare, export view (print-friendly) |

### 7.4 Auditor states

| State | Behaviour and copy |
|---|---|
| Empty | Reports: "No health report exists for this rubric version yet. Results made with it are not covered." |
| Loading | "Verifying the ledger. This can take a while for long ledgers." Status role; cancellable. |
| Error | "Verification could not run. This is not a result; try again." (distinct from Not verified) |
| Not verified | Red-text state with first failing sequence; no remediation claims. |
| Low coverage | "Fewer than N cases in this category; treat as indicative." (N set by assessor-audit) |
| Failures present | Failures listed, not hidden or averaged. |

### 7.5 Auditor content rules

- Report what was tested and no more. Use counts, not a single "health score".
- Distinguish three outcomes: Verified, Not verified, Could not run.
- Auditors never see raw private submissions (hash references only).

## 8. Cross-cutting state patterns

| Pattern | Component | Rule |
|---|---|---|
| Loading | Skeleton + `role="status"` text | Never an unlabeled spinner; no fake percentage |
| Error | Inline alert (`role="alert"`) | Says what failed, whether data is safe, what to do |
| Empty | Empty panel | One sentence, one action |
| No-grant | Neutral panel | Identical wording across not-shared, expired, revoked, non-existent |
| Low-confidence | Band + word label + review route | Never presented as a precise number |
| Probe unconfirmed | Neutral (non-red) status chip | Wording fixed by G-5 |
| Success | `role="status"` toast, persistent inline copy | Does not auto-dismiss under 8 s, and is repeated on-screen |

## 9. Design system tokens and components

Contrast ratios are computed against white `#FFFFFF` and should be re-verified with a tool at build.

### 9.1 Colour

| Token | Value | Use | Contrast on white |
|---|---|---|---|
| `color.text` | `#1A1A1A` | Body text | about 17:1 |
| `color.text-muted` | `#4A4A4A` | Secondary text | about 8.9:1 |
| `color.surface` | `#FFFFFF` | Page | n/a |
| `color.surface-alt` | `#F3F5F8` | Panels | text on it at least 15:1 |
| `color.border` | `#767676` | Input and component borders | 4.5:1 (meets 3:1 for non-text) |
| `color.primary` | `#0B4F9E` | Links, primary buttons (white text on it about 8:1) | about 8:1 |
| `color.focus` | `#0B4F9E` ring, plus `#FFFFFF` inner offset | Focus ring | at least 3:1 against both sides |
| `color.success` | `#1B6E3A` | Verified, matches ledger | about 6.3:1 |
| `color.warning-text` / `color.warning-bg` | `#7A4B00` / `#FFF4D6` | Low confidence, partly met, unconfirmed | about 7.4:1 |
| `color.error` | `#B3261E` | Errors, not verified | about 6.5:1 |
| `color.neutral-chip-bg` | `#E6EAF0` with `color.text` | "Understanding unconfirmed", "No shared evidence" | at least 12:1 |

Colour is never the only carrier of meaning; every state also has an icon and text. "Understanding unconfirmed" deliberately uses the neutral chip, not the error colour.

### 9.2 Type

| Token | Value |
|---|---|
| `font.family` | System UI stack; monospace for code and hashes |
| `font.size.base` | 16 px (1 rem); never below 14 px |
| Scale | 14 / 16 / 20 / 24 / 32 px; heading levels in order |
| `font.lineheight` | 1.5 body, 1.25 headings |
| Line length | at most 75 characters |

### 9.3 Spacing and layout

| Token | Value |
|---|---|
| Spacing scale | 4, 8, 12, 16, 24, 32, 48 px |
| Touch and click target | at least 44 x 44 px |
| Breakpoints | 360, 768, 1200 px; content reflows at 320 CSS px with no horizontal scrolling |
| Radius / border | 4 px / 1 px |

### 9.4 Components (minimal reusable set)

| Component | Variants | Notes |
|---|---|---|
| Button | Primary, secondary, danger-confirm | Text label always present |
| Field and textarea | Default, error, disabled | Visible label, hint text, error text linked by `aria-describedby` |
| Status chip | Success, info, warning, neutral, error | Icon + text |
| Method label | five methods per G-7 | Icon + text; tooltip is not the only route to meaning |
| Estimate band | Compact, detailed | Visual bar plus text "0.58, likely range 0.45 to 0.70, as of 10 Oct 2026"; includes a data table alternative |
| Criterion card | Passed, Partial, Not passed, Inconclusive, Pending review | Contains method label, reason, appeal action |
| Evidence item | Collapsed, expanded | Receipt verify action |
| Coverage cell | Met, Partly met, Not met, No shared evidence, Gap | Reason text always shown |
| Alert / toast | Info, success, error | `role="status"` / `role="alert"` |
| Experimental banner | Fixed | Always present with estimates |
| Dialog | Confirm (stop sharing, record decision) | Focus trapped, Escape closes, focus returns |
| Table | Sortable only where order is not a ranking | Caption, header scope |

## 10. Accessibility criteria (WCAG 2.1 AA)

Applies to every screen above. Each is a testable acceptance criterion for the frontend-engineer (IDs `A11Y-n`).

| ID | Criterion | WCAG | Test |
|---|---|---|---|
| A11Y-1 | **Keyboard operable:** every function (submit, probe, send message, share, appeal, decide, verify) is reachable and usable by keyboard alone, with no keyboard trap. | 2.1.1, 2.1.2 | Manual tab-through of each flow |
| A11Y-2 | **Focus visible:** a focus ring of at least 2 px with 3:1 contrast is shown on every interactive element; focus is never hidden by sticky headers. | 2.4.7, 2.4.11 draft | Visual |
| A11Y-3 | **Logical focus order:** DOM order matches reading order; after route change, submit, error and dialog open or close, focus moves to the page heading, error summary or triggering control. | 2.4.3 | Manual |
| A11Y-4 | **No time limit on probes and Level 4:** no timers, no session expiry mid-answer; drafts are autosaved; if a session must expire, a warning offers extension at least 20 hours before. | 2.2.1 | Wait test; code review for timers |
| A11Y-5 | **Text alternative to any audio or video**, including future live screening: transcript and captions; Level 4 is text-first and a text option is always available. | 1.2.1, 1.2.2, 1.2.3 | Content review |
| A11Y-6 | **Contrast:** text at least 4.5:1 (3:1 for 18.66 px bold or 24 px), UI components and focus at least 3:1, using the tokens above. | 1.4.3, 1.4.11 | Automated plus manual |
| A11Y-7 | **Screen-reader labels:** every control has an accessible name; icons paired with text; estimate bands have a text equivalent; method labels and states are read as words, not colour. | 1.1.1, 4.1.2 | NVDA and VoiceOver pass |
| A11Y-8 | **Status announcements:** loading, saved, error and recorded-decision messages use `role="status"` or `role="alert"` without moving focus unexpectedly. | 4.1.3 | Screen-reader pass |
| A11Y-9 | **Forms:** visible labels, instructions before input, errors identified in text and linked to the field, with suggestion where known; required fields marked in text. | 3.3.1, 3.3.2, 3.3.3 | Manual |
| A11Y-10 | **Plain language:** copy meets the content rules; abbreviations expanded on first use; error text states cause and next step. | 3.1.5 (AAA, adopted as target), 3.3.3 | Copy review against content rules |
| A11Y-11 | **Not colour alone:** coverage, status and gaps use icon and text as well as colour. | 1.4.1 | Greyscale check |
| A11Y-12 | **Reflow and zoom:** usable at 200 % text zoom and 320 CSS px width with no loss of content or horizontal scroll. | 1.4.4, 1.4.10 | Browser zoom |
| A11Y-13 | **Structure:** one `h1` per page, ordered headings, landmarks (header, nav, main), tables with captions and header scope, a skip link. | 1.3.1, 2.4.1, 2.4.6 | Automated plus manual |
| A11Y-14 | **Consistent navigation and identification:** same nav order, same names for same actions across roles. | 3.2.3, 3.2.4 | Review |
| A11Y-15 | **No surprise:** no auto-submit, no focus or context change on input. Destructive or consent actions use a confirm dialog. | 3.2.1, 3.2.2 | Manual |
| A11Y-16 | **Code editor accessible:** query editor offers a way to leave with Tab (documented Escape-then-Tab), screen-reader-compatible mode, and a plain textarea fallback. | 2.1.2, 4.1.2 | Manual |

Per-screen minimum: Task, Probe and Level 4 session must satisfy A11Y-1, 2, 3, 4, 7, 8, 9, 16; Profile and Evidence page must satisfy A11Y-6, 7, 11, 13 (band text alternative); Review case must satisfy A11Y-1, 3, 7 (side-by-side panes announced and reachable); Ledger check and Report must satisfy A11Y-8 (verification result announced).

## 11. Usability checks and traceability

### 11.1 Usability checks (supervised, 3 to 5 testers; reported as obtained, including failures)

| ID | Task | Target (Proposed) | Maps to |
|---|---|---|---|
| U-1 | Learner finds and explains why one criterion was marked down | 4 of 5 correct, unaided | V7 comprehension |
| U-2 | Learner states what "understanding unconfirmed" means and that the output score is unchanged | 4 of 5 correct; 0 of 5 describe it as an accusation | V7, risk "probe read as accusation" |
| U-3 | Learner reads the estimate band and says whether evidence is thin | 4 of 5 | V7 |
| U-4 | Learner shares evidence then stops sharing | 5 of 5 complete; time on task recorded for design, not scored | consent Should tier |
| U-5 | Learner files an appeal | 4 of 5 complete | appeals Should tier |
| U-6 | Recruiter identifies the gaps for a role and cannot name a "best" candidate | 4 of 5 name gaps; 0 of 5 rank | V8, no-rank rule |
| U-7 | Recruiter explains how one evidence item was produced and verifies it | 4 of 5 | V8 |
| U-8 | Reviewer reaches a decision on a case and states the reason | 4 of 5; decision recorded | M10 |
| U-9 | Keyboard-only and screen-reader run through L-1 | 100 % of steps completable | A11Y-1, A11Y-7 |

Time on task is recorded to find friction, never shown to or scored for the learner.

### 11.2 Traceability (to be re-keyed to REQ-### when the PRD is FINAL)

| Tier item | Flow | Screens | Checks |
|---|---|---|---|
| Must: levels 1 to 3, labelled feedback | L-1 | Task, Criterion feedback | U-1, A11Y-1..9 |
| Must: predict-output probe, failure case | L-1 | Probe, Criterion feedback, Profile | U-2, A11Y-4 |
| Must: Level 4 scripted text session | L-2 | Level 4 session | A11Y-4, A11Y-5 |
| Must: skill band, experimental label | L-1 | Profile, Evidence page | U-3, A11Y-6, A11Y-7 |
| Must: hash-chained log | A-1 | Ledger check | A11Y-8 |
| Must: mini invariance suite | A-2 | Reports | A11Y-13 |
| Should: consent | L-3 | Sharing | U-4 |
| Should: appeals and queue | L-4, V-1 | Appeals, Review queue, Review case | U-5, U-8 |
| Should: recruiter coverage | R-1, R-2, R-3 | Role setup, Role results, Evidence page | U-6, U-7 |

## 12. Gaps and questions (not requirement changes)

| # | Item | For |
|---|---|---|
| 1 | No contract for "verify receipt". SharedEvidence has `receipt_hash` and `ledger_proof` but no defined verification call; the UI needs a Trust endpoint or a client-side proof rule. | principal-architect |
| 2 | Contract open item 6 (access record shown to learner) is not yet defined; the Sharing screen shows it only if built. | principal-architect, product-owner |
| 3 | Contract open item 4 (`submission_excerpt` in MVP). Screens assume off by default. | Founder |
| 4 | No contract fields for review queue, appeals or ledger verify results; reviewer and auditor screens above are based on the approach document and the module catalogue only. | principal-architect |
| 5 | Competency, task and rubric ID registries (item 5) are required so the UI can show names, not IDs. | Dev 1, Dev 2 |
| 6 | Learner-facing display of the 0 to 1 scale: proposed plain wording "0.58, likely range 0.45 to 0.70" rather than percent, to avoid implying a grade. | Founder |
| 7 | Recruiter filtering by coverage state is permitted; any sort by "number met" is not. Confirm filtering is acceptable. | Founder |
| 8 | Probe alternative format: what is the alternative at MVP (written explanation)? Plain-English probe is a Could tier. | product-owner |
