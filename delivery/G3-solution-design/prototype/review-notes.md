<!-- STATUS: DRAFT -->
# Independent review: learner dashboard mock-up

Reviewer: quality-engineer (independent of ux-architect). Date: 2026-10-10. Method: static reading of `learner-dashboard.html` (638 lines) and `README.md`, plus regex scans. No browser was run, so all behaviour is read from code, not observed. Rules: `ux-flows.md` G-1..G-10, 4.5-4.7, 9, 10; plan `start-with-web-dashbord-wiggly-puppy.md`.

**Verdict: CONDITIONAL.** Acceptable as a G3 design mock-up once F-01 is decided by the Founder and F-02 is resolved. No other blocker. Nothing here is evidence that any requirement is met (mock-up, rule 5).

## 1. Findings

| ID | Severity | Location | Finding | Recommendation |
|---|---|---|---|---|
| F-01 | High (decision) | html L386 | Probe-unconfirmed copy contains "score" (clashes with 4.7 "avoid score as bare noun") and "misconduct" (G-5 never-list; the word is in a negation but still puts the accusation concept in front of the learner). Implemented verbatim from 4.6. | Recommend removing both words: "...your result for it is unchanged. We could not confirm you can explain or predict how it works. This does not change your result. You can try another probe or ask a person to look." Update 4.6 in ux-flows; Founder to decide. |
| F-02 | Medium | html L373-376, README gap 2 | Estimate gating conflict (4.1 step 8 vs 4.6 Empty). Mock only has "no evidence" (Empty) and "all four passed" profiles. The partial case (1-3 levels passed) required by 4.1 step 8 ("Your estimate updates after all four levels are passed" plus progress) is not implemented. README line "shows the estimate only when all four are passed" is not enforced by code; estimate display depends only on `state`. | Recommend 4.1 gating: 4.6 Empty copy for zero evidence; 4.1 step 8 copy plus level progress for partial; estimate only once four levels passed. ux-architect to add a partial state and align both sections of ux-flows. |
| F-03 | Medium | css L36, L18 | Banner is `position:sticky` and wraps to several lines at 320 px or 400% zoom, with 140 px scroll padding. May occupy a large share of a 320x256 viewport and obscure focus (A11Y-2, A11Y-12). Not verifiable statically. | Make banner non-sticky below 768 px or shorten it; verify in browser at 320 px / 400% zoom. |
| F-04 | Low | html L304 | Loading `role="status"` region is injected together with its content, so many screen readers will not announce it. `#notice` (L165) is correctly present at load. | Keep an always-present live region and update its text. |
| F-05 | Low | html L361-363, L386-387 | Probe item in unconfirmed state keeps outcome "Passed" next to "Output verified, understanding unconfirmed"; the explanatory paragraph and actions appear only in Profile Understanding block, not on the evidence card (4.6 lists evidence too). | Define outcome mapping for probe items; show short explanation on the card. |
| F-06 | Low | html L265 | Third probe string "Understanding probe not attempted" is not in ux-flows. | Add to copy list or remove. |
| F-07 | Low | css L96, L50-59, 9.3 | Borders are 2-3 px on buttons, alerts, focus; 9.3 says 1 px border. Media breakpoints are 480/768, not 360/768/1200. | Align tokens or document intentional exception. |
| F-08 | Low | html L289-291, L324-327 | Empty state: Level 1 shows "In progress / Resume" with 0 attempts while Profile says "Complete Level 1". Appeal form in Empty state lists criteria with no evidence. | Show "Not started / Start" in Empty; disable appeal form until a result exists. |
| F-09 | Low | html L629-633 | State selector changes the whole view on `change` (A11Y-15 "no context change on input"). Review aid only. | Acceptable; note in test plan. Real UI must not do this. |
| F-10 | Low | html L553-566 | Error summary is `role="alert"` and also receives focus (possible double announcement). A11Y-3 asks for focus to error summary. | Keep focus; drop `role="alert"` or keep one. Verify with NVDA. |
| F-11 | Info | html L415, L428 | Org list allows sharing again with an already-granted org; no maximum expiry. Raw-submission toggle depends on open item 4. | Define rules in 4.3 / contract before build. |
| F-12 | Info | html L335 | Copy "There are no timers on any level." mentions timers. Reassurance, not a timer; 5 s load message (L522) is mandated by 4.6. | Acceptable. |
| F-13 | Info | html L334 | `ul` with `list-style:none` loses list semantics in Safari/VoiceOver. | Add `role="list"` if list semantics matter. |

## 2. Forbidden-concept scan (regex, case-insensitive)

| Term | Hits (line) | Violation? |
|---|---|---|
| aggregate / total / rank / percentile / match % / "x of y" | none in user-facing copy. L404 "The order is by date only" is a negation of ranking. "of" hits (L138, 169, 299, 339, 371, 386) are plain prose, not "x of y". Per-method "Results: n" (L383) and "Attempts: n" are contract fields (method_counts), not totals. | No |
| timers / time taken / speed | L335 "no timers" (statement); L522 5 s message timer (4.6); no countdowns, durations or times; dates only. | No (F-12) |
| fail / cheat / suspicious / AI detected | none. Outcome shown as "Not passed". | No |
| misconduct | L386 (in negation) | Yes, vs G-5 list (F-01) |
| score | L386 | Yes, vs 4.7 (F-01) |
| name / email | Only the phrases "not your name" (L417) and "not your name or email" (L440). Alias `cnd_3f9a1c07b2d84e65` shown; org names marked synthetic. | No |

## 3. Probe wording and chip
"Output verified, understanding unconfirmed" appears exactly at L264, rendered by `understandingChip("unconfirmed")` using `chip("neutral","dash",...)`: neutral class (bg #E6EAF0, text #1A1A1A, 1 px #767676 border), dash icon, not red. PASS. Used in Profile (L384) and on probe evidence cards (L361).

## 4. Banner and external requests
- Banner (L133-136) sits in `header.top` outside `#view`, so it is present on all four routes and in loading and error states. Text: "MOCK-UP · synthetic data · Experimental: not a validated hiring predictor". Footer repeats mock-up status. PASS.
- Scan for `http`, `fetch(`, `import`, `XMLHttpRequest`, `src=`: zero matches. All `href` are `#...` fragments or `#i-*` sprite references. No CDN or fonts. PASS.

## 5. Accessibility structure (static)
| Check | Result |
|---|---|
| Skip link | L131, targets `#main`, visible on focus, 44 px. PASS |
| Landmarks | header, nav (aria-label "Main"), main, footer. Mock control is an `aside` labelled. PASS |
| One h1 per view | Every view and the loading/error views emit one `h1#h1`. PASS |
| Heading order | h1, h2, h3, h4 with no skips on all routes; dialog uses h2. PASS |
| Focus styles | `:focus-visible` 3 px #0B4F9E plus 2 px white offset; scroll-padding 140 px. PASS (see F-03) |
| Status / alert | `#notice` role=status always present; error views and form error summaries role=alert. PASS with F-04, F-10 |
| Dialog | aria-modal, labelled and described, `#app` inert, Tab trap, Escape closes, focus returns to trigger on cancel/Escape, Cancel focused first. Confirm path moves focus to notice because trigger is removed (README gap 12). PASS |
| Form labels | All fields have visible `label for`, hint via aria-describedby, "(required)" in text, aria-invalid and error linked. PASS |
| Estimate text alternative | Text sentence "0.58, likely range 0.45 to 0.70, as of 10 Oct 2026", bar `aria-hidden`, plus data table in details with caption and `th scope`. PASS |
| Not colour alone | Every chip and alert has icon plus text. PASS |

## 6. Tokens, targets, reflow
- Colour tokens L10-12 match 9.1 exactly (all 11 values). Type scale 14/16/20/24/32 and 1.5/1.25 line heights match. Spacing scale matches. Radius 4 px. See F-07 for border and breakpoint deviations.
- 44 px: `.btn`, nav links, summary, inputs, selects, skip link, checkbox row all `min-height:44px`. Inline link in error summary (L564) is text-sized; acceptable as inline link.
- 320 px (CSS review only): `overflow-wrap:anywhere`, auto-fit grid with `min(100%,15rem)`, `flex-wrap` on header/nav/actions, `dl.kv` single column at 480 px, table `width:100%`, dialog `width:100%` with scroll. No fixed widths over 320 found. Not verified in a browser.

## 7. States (4.6)
| State | Implemented | Note |
|---|---|---|
| Normal | Yes, all routes | |
| Empty | Profile, Sharing, Appeals copy exact; My path zeroed | F-08 |
| Loading | role=status "Loading your results"; 5 s "Still loading. Your work is saved." | F-04 |
| Error | Exact copy, Retry, error reference, no stack text | |
| Low-confidence | Pending review chip, "We are not sure about this result. A person will check it.", Low plus number on request, wide band | Banner is profile-level, not per criterion |
| Probe-unconfirmed | Exact chip, 4.6 explanation, Try another probe / Appeal | F-01, F-05 |

Required expiry: `required`, label "(required)", empty and past/today dates rejected with linked error and summary (L557-558). PASS. Raw-submission checkbox unchecked by default, hint "Off by default", preview and grant list show "Not included". PASS.

## 8. Author-reported conflicts
| Conflict | Recommended reading |
|---|---|
| 4.6 probe copy vs never-list / 4.7 | Never-list and 4.7 win; drop "misconduct" and "score" (F-01). Founder decides; ux-flows 4.6 must change. |
| Estimate gating 4.1 step 8 vs 4.6 Empty | Keep 4.1 gating (estimate after four levels); 4.6 Empty applies only to zero evidence; add partial-progress state (F-02). |

Other README gaps (3-12) are reasonable open items; none is contradicted by the code.

## 9. Not verified
Rendered contrast, actual 320 px and 400% zoom layout, screen-reader output, inert support in target browsers, keyboard tab order at runtime. Needs a browser pass (NVDA, VoiceOver) before G3 sign-off.

## 10. Re-verification (2026-10-10, after ux-architect rework)

Reviewer: quality-engineer. Method: re-read of `learner-dashboard.html` (663 lines now), `README.md`, `ux-flows.md` 4.1, 4.6, 5.5, 6.3 and change note (L424); fresh regex scans. Static only, no browser run. Line references are to the current files.

**Verdict: CONDITIONAL.** All High/Medium findings are fixed in code. Conditional on (a) Founder decision on the reviewer-facing "misconduct" negation in ux-flows 6.3, and (b) the browser and screen-reader pass in 10.4. Still a mock-up, not evidence of any requirement (rule 5).

### 10.1 Findings

| Finding | Status | Evidence |
|---|---|---|
| F-01 "score"/"misconduct" in probe copy | Fixed | html L401 now "This is not a finding about your conduct."; scan for score/misconduct in html: 0 hits. ux-flows L118 (4.6) carries the identical sentence; change note L424. |
| F-02 Partial progress state | Fixed | html L149 option, L290-295 `currentProfile`, L298-302 `pathStatus`, L392 `showEst` requires all four levels, L415-417 copy "Your estimate updates after all four levels are passed." ux-flows 4.6 L108 (Empty = zero evidence only) and L109 (Partial) agree with 4.1 step 8 (L65). README L25 lists the state. |
| F-03 Sticky banner | Fixed (code); browser unverified | html L77 `@media (max-width:400px),(max-height:500px){.banner{position:static}html{scroll-padding-block-start:0}}`, placed after L36 so it wins. Still sticky at 401-767 px wide; verify wrapped height. |
| F-04 Loading live region | Fixed | `#live` role=status exists at load (L169), text set at L545-546; no role on injected content (L314). |
| F-05 Probe card explanation | Fixed | html L374 short explanation plus L377 "Output verified" chip replaces "Passed". Note: card text says "try another probe" but the action button lives only in the Profile Understanding block (L402); see N-02. |
| F-06 "Understanding probe not attempted" | Accepted | html L269. String is in ux-flows 5.5 L186 ("Understanding probe not attempted."), needed for the `not_attempted` enum value. Not reachable in any mock state. |
| F-07 Borders and breakpoints | Fixed | Controls use 1 px (L50, L55, L57, L96). Breakpoints 360 (L76), 768 (L110), 1200 (L78), plus a 400/500 banner rule. Undocumented minor: 6 px preview rule (L105), 2 px band edges (L82). README L39 lists only the focus ring and nav indicator. |
| F-08 Empty state | Fixed | `pathStatus` empty gives `inProg:0` (L299), so Level 1 renders "Not started / Start" (L337); appeal form `hidden` with explanatory panel (L486-488). |
| F-09 State switcher changes view on change | Accepted | html L654-658; labelled "Mock-up control. Not part of the product." (L140); README L13 records it. Real UI must not do this (A11Y-15). |
| F-10 Double announcement | Fixed | Error summaries have `tabindex="-1"`, no role=alert (L589, L632); focus moved (L591, L634). `role="alert"` remains only on the load-error view (L319), which 4.6 requires. |
| F-11 Re-share / max expiry undefined | Accepted | Rules undefined in 4.3 and contracts; carried as README L38. Must be decided before build, not before G3. |
| F-12 "no timers" sentence | Fixed | Scan for "timer": hits only JS identifiers (L276, L537, L546). |
| F-13 List semantics | Fixed | html L554 sets `role="list"` on all `ul` after each render. Gap: lists created later (live preview L574, dialog body) are not covered; they use `list-style:disc` so semantics survive. Low. |

### 10.2 Scans (case-insensitive, current files)

| Scan | Result |
|---|---|
| html: score, misconduct, fail, cheat, suspicious, rank, percentile, aggregate, total, match % | 0 hits in user-facing copy |
| html: "conduct" | L401 only, in a negation; not on the G-5 never-list |
| html: http, fetch(, XMLHttpRequest, import, src= | 0 hits; all href are `#` fragments or `#i-*` sprites. No external requests. |
| ux-flows "misconduct" | L45 (G-5 never-list itself) and L229 (6.3). README says 5.5 also contains it: **incorrect**, 5.5 (L173-188) has no hit. |
| ux-flows "score" | L13 (persona fear), L72 ("not a score"), L128 (4.7 rule), L192 (5.6 rule), L386/L388 (U-2/U-4 test text). All prohibitions or test descriptions, none learner-visible copy. |

### 10.3 Other checks

- Probe wording: "Output verified, understanding unconfirmed" at html L268 via `chip("neutral","dash",...)`, neutral class (L67), dash icon, not red. Matches 4.6 L118 and G-5. PASS.
- Banner: in `header.top` outside `#view` (L135-138), present on all routes and states; text unchanged. PASS.
- Structure unchanged and still sound: skip link L133, header/nav/main/footer, one `h1#h1` per view including loading and error views, labelled form fields, dialog with inert plus Tab trap. PASS (static).
- Mock copy vs ux-flows 4.6: probe explanation (html L401 vs L118), Empty (html L389 vs L108), Partial (html L415 vs L109), Error and Loading copy: agree word for word. Evidence-card short form (L374) is not in 4.6 (N-02).

### 10.4 New observations from this pass

| ID | Severity | Location | Observation |
|---|---|---|---|
| N-01 | Low | html L331-336, L610 | In Partial state, Level 4 shows "In progress / Resume" with 0 attempts (same pattern as old F-08). Appeals "Current result" reads `MOCK.profile` unfiltered, so crt_follow_up still shows a Level 4 result although Partial removes it (L292). Mock data inconsistency only. |
| N-02 | Info | html L374 | Probe-card short explanation is not in ux-flows 4.6; add to 4.6 or reuse the full sentence. |
| N-03 | Info | README L41, L11 | Heading "ux-flows.md not otherwise edited" is stale (4.6 was edited); gap 11 wrongly cites 5.5. Documentation fix. |

### 10.5 Leftover items: acceptable?

| Item | Judgement |
|---|---|
| F-06, F-09, F-11 | Acceptable for a G3 mock-up; each has a documented reason. |
| ux-flows 6.3 L229 "This is not evidence of misconduct." | Not strictly acceptable: it puts a word from the G-5 never-list in front of a reviewer. Reviewer-facing, in a negation, so low harm. Recommend rewording to mirror 4.6 ("This says nothing about the learner's conduct. Decide only on the rubric.") or Founder records an exception. Owner: ux-architect. |
| ux-flows 5.5 | No "misconduct" present; the claim is wrong. No action. |
| G-5 L45 | Contains the word as the rule itself; acceptable. |

### 10.6 Still needs a real browser / screen-reader pass

1. 320 px and 400% zoom: banner height at 401-767 px wide while sticky, focus not obscured (A11Y-2, A11Y-12).
2. NVDA (Firefox/Chrome) and VoiceOver (Safari): loading announcement via `#live`, notice focus after share/stop/appeal, error summary focus, dialog announcement, `role="list"` on nav, estimate sentence versus hidden bar.
3. `inert` support and focus return on Escape in target browsers.
4. Rendered contrast of all chips, warning banner and focus ring against 9.1 values.
5. Keyboard-only walk through all four routes and both forms; tab order and 44 px targets.
6. Founder reaction session (usability check U-2) is not covered by any of the above.

## 11. Re-verification 2 (2026-10-10)

Static re-read of the current files, no browser.

| Item | Status | Evidence |
|---|---|---|
| ux-flows 6.3 "misconduct" | Fixed | L229 now "This is not a finding about the learner's conduct. Decide only on the rubric." Remaining "misconduct" hits: L45 (G-5 never-list, naming the forbidden term as a rule) and L424 (change note, history). Both are the term being prohibited or recorded, not UI copy. Acceptable under G-5. |
| Partial: Level 4 status (N-01a) | Fixed | html L300 `inProg:0`; L327-337: with 1-3 passed Level 4 is unlocked and renders "Not started / Start" with 0 attempts. Start is offered only when `l123` is true; otherwise L330 gives "Locked" with "Pass Levels 1 to 3 to open this level." (Empty state confirms). Matches 4.1/L-2. |
| Partial: Appeals lists only criteria with results (N-01b) | Fixed | html L481-483 filters the criterion dropdown by `currentProfile().evidence_items`; Partial removes live_screening (L292), so crt_follow_up is absent. Empty state yields no options and the form is hidden (L486+). |

Residual (info): seeded appeals still reference criteria from the Normal data; none concerns Level 4, so no conflict in Partial.

**Final verdict: PASS for the G3 mock-up on static review.** No open static findings. Browser-only checks remain (section 10.6): 320 px / 400% zoom banner behaviour at 401-767 px, NVDA and VoiceOver announcements and focus moves, inert and Escape focus return, rendered contrast, keyboard-only walkthrough. These gate G3 sign-off evidence for A11Y but not the design content.
