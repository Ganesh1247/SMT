<!-- STATUS: DRAFT -->
# Learner dashboard mock-up (Crucible `learner-ui`)

Owner: ux-architect | Gate: G3 | Source of truth: `delivery/G3-solution-design/ux-flows.md` (sections 3, 4, 9, 10) and `contracts/shared-evidence.schema.json`. Review findings: `review-notes.md` (owned by the verifier).

## What it is
A single-file, clickable picture of the learner competency dashboard so the Founder can react to the real screens before G3 sign-off. Inline CSS and vanilla JS only. No CDN, no libraries, no network requests.

## What it is NOT
- Not working software. There is no backend, no auth, no grading, no persistence. Reload resets everything.
- Not evidence of any requirement being met. Every number and name is synthetic (one placeholder competency, "Data analysis (SQL)").
- Not the Task, Probe or Level 4 screens. Their buttons show "Mock-up only" notices.
- The state switcher (dashed box under the banner) is a review aid and is not part of the product. It changes the view on selection, which the real UI must not do (A11Y-15).

## How to open
Double-click `learner-dashboard.html`, or open it in any current browser. It works offline. Screens are hash routes: `#/my-path`, `#/profile`, `#/sharing`, `#/appeals`.

## Screen to ux-flows mapping
| Screen | ux-flows | Notes |
|---|---|---|
| My path | 4.1 step 1, 4.2 step 1, 4.5 "My path" | 4 level cards, attempts, Resume, Level 4 locked until 1 to 3 passed |
| Profile (hero) | 4.5 "Profile", 4.6, G-2 to G-5, G-7, G-10 | Estimate text + bar + table (only after all four levels passed), levels, 5 method labels, understanding chip, evidence list, Share and Appeal |
| Sharing | 4.3 (L-3), 4.6 Empty/No-grant | Required expiry, preview, confirm dialog (focus trap, Escape, focus return) |
| Appeals | 4.4 (L-4), 4.6 Empty | Received / In review / Decided, new-appeal form (hidden until a result exists) |
| State switcher | 4.6 | Normal, Partial progress, Empty, Loading (message changes after 5 s), Error, Low-confidence, Probe-unconfirmed |

A11Y covered: 1, 2, 3, 6, 7, 8, 11, 12, 13, 15. Banner is sticky except below 400 px width or 500 px height, so it cannot obscure content at 320 px or 400% zoom.

## Data
`MOCK.profile` mirrors SharedEvidence field names exactly. Everything else lives in `MOCK.ui_extras` because no contract defines it.

## Changes after review (2026-10-10)
F-01 probe copy reworded (also in ux-flows 4.6). F-02 partial-progress state added, estimate gated on four levels passed. F-03 banner non-sticky on small screens. F-04 always-present live region for loading. F-05 probe card shows "Output verified" plus a short explanation. F-07 borders 1 px, breakpoints 360/768/1200. F-08 Empty shows Level 1 Not started; appeal form hidden. F-10 error summary no longer role=alert (focus moves to it). F-12 timer sentence removed. F-13 `role="list"` on lists.

## Left as is (deliberate)
- F-06 "Understanding probe not attempted" kept; it comes from ux-flows 5.5 and is needed for the `not_attempted` enum value.
- F-09 state switcher changes view on selection; it is a review aid only.
- F-11 sharing again with an already-granted organisation and no maximum expiry: rules undefined, need 4.3 or contract decision.
- Intentional exceptions to 1 px borders: 3 px focus ring (A11Y-2) and the 4 px current-page nav indicator.

## Open gaps (ux-flows.md not otherwise edited)
1. Outcome enum has `fail`; learner wording not defined. Mock-up uses "Not passed" (neutral).
2. `live_screening` outcome shown as "Evaluated, reviewable" (4.2) but contract outcome is pass/partial/inconclusive; mapping undefined. Probe item with unconfirmed understanding is shown as "Output verified" (proposed mapping).
3. No contract for confidence (Low/Medium/High plus number), ShareGrant display fields, organisation list, or appeals. Held in `ui_extras`.
4. No contract field for attempt count, level status or in-progress level on My path.
5. Competency and criterion display names are placeholders (registry open item 5).
6. Access record on Sharing omitted (contract open item 6). Raw-submission toggle depends on open item 4.
7. 4.6 "Evaluating" and "Submit error" states belong to Task screens and are not shown.
8. 4.6 "After 5 s, Still loading" implies a client timer; A11Y-4 forbids timers on probes. Assumed it applies to page loading only.
9. Success messages never auto-dismiss; clearing rule undefined.
10. After "Stop sharing" the trigger is removed, so focus goes to the status message. Needs a rule.
11. Reviewer probe line (ux-flows 6.3) reworded to drop "misconduct"; the reviewer screens are not in this mock-up. Only the G-5 never-list still names the word. Section 5.5 never contained it.
12. Partial progress: Level 4 shows Not started and Appeals lists only criteria that have results.
