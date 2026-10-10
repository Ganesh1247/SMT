<!-- STATUS: DRAFT -->
# Learner dashboard mock-up (Crucible `learner-ui`)

Owner: ux-architect | Gate: G3 | Source of truth: `delivery/G3-solution-design/ux-flows.md` (sections 3, 4, 9, 10) and `contracts/shared-evidence.schema.json`.

## What it is
A single-file, clickable picture of the learner competency dashboard so the Founder can react to the real screens before G3 sign-off. Inline CSS and vanilla JS only. No CDN, no libraries, no network requests.

## What it is NOT
- Not working software. There is no backend, no auth, no grading, no persistence. Reload resets everything.
- Not evidence of any requirement being met. Every number and name is synthetic (one placeholder competency, "Data analysis (SQL)").
- Not the Task, Probe or Level 4 screens. Their buttons show "Mock-up only" notices.
- The state switcher (dashed box under the banner) is a review aid and is not part of the product.

## How to open
Double-click `learner-dashboard.html`, or open it in any current browser. It works offline. Screens are hash routes: `#/my-path`, `#/profile`, `#/sharing`, `#/appeals`.

## Screen to ux-flows mapping
| Screen | ux-flows | Notes |
|---|---|---|
| My path | 4.1 step 1, 4.2 step 1, 4.5 "My path" | 4 level cards, attempts, Resume, Level 4 locked until 1 to 3 passed |
| Profile (hero) | 4.5 "Profile", 4.6, G-2 to G-5, G-7, G-10 | Estimate text + bar + table, levels, 5 method labels, understanding chip, evidence list, Share and Appeal |
| Sharing | 4.3 (L-3), 4.6 Empty/No-grant | Required expiry, preview, confirm dialog (focus trap, Escape, focus return) |
| Appeals | 4.4 (L-4), 4.6 Empty | Received / In review / Decided, new-appeal form |
| State switcher | 4.6 | Normal, Empty, Loading (message changes after 5 s), Error, Low-confidence, Probe-unconfirmed |

A11Y covered: 1, 2, 3, 6, 7, 8, 11, 12, 13, 15 (skip link, landmarks, one h1, focus ring, status/alert roles, no colour-only meaning, reflow at 320 px).

## Data
`MOCK.profile` mirrors SharedEvidence field names exactly (`proficiency.estimate/lower/upper/as_of`, `levels_passed`, `method_counts`, `understanding_status`, `evidence_items[]`, `labels`). Everything else lives in `MOCK.ui_extras` because no contract defines it.

## Gaps found (ux-flows.md not edited)
1. Probe copy in 4.6 contains "score" and "misconduct" (in a negation), which clash with 4.7 ("avoid score") and the never-use word list. Implemented 4.6 verbatim; needs a copy decision.
2. 4.1 step 8 (estimate only after all four levels passed) conflicts with 4.6 Empty. Mock-up follows 4.6 and shows the estimate only when all four are passed.
3. Outcome enum has `fail`; learner wording not defined. Mock-up uses "Not passed" (neutral).
4. `live_screening` outcome shown as "Evaluated, reviewable" (4.2) but contract outcome is pass/partial/inconclusive; mapping rule undefined.
5. No contract for confidence (Low/Medium/High plus number on request) on AI-assisted items, for ShareGrant display fields (organisation, expiry, raw-submission flag), organisation list, or appeals (status, decision, reason). Held in `ui_extras`.
6. No contract field for attempt count, level status or in-progress level on My path.
7. Competency and criterion display names are placeholders (registry open item 5).
8. Access record on Sharing omitted (contract open item 6). Raw-submission toggle depends on open item 4.
9. 4.6 "Evaluating" and "Submit error" states belong to Task screens and are not shown.
10. 4.6 "After 5 s, Still loading" implies a client timer; A11Y-4 says no timers on probes. Assumed it applies to page loading only.
11. Success toast "does not auto-dismiss under 8 s" is satisfied here by never auto-dismissing; the pattern for clearing is undefined.
12. After "Stop sharing" the trigger is removed, so focus goes to the status message (not the trigger). Needs a rule.
