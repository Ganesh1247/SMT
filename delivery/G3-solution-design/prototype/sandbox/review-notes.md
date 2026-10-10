<!-- STATUS: DRAFT -->
# Review notes: sandbox shell prototype

Reviewer: quality-engineer (independent of author ux-architect) | Date: 2026-10-10 | Gate: G3
Subject: `sandbox-shell.html` (827 lines), `README.md`. Method: static reading of the full HTML/JS plus grep checks. No browser, no screen reader, no axe/Lighthouse was available; nothing below was executed. Runtime behaviour, 320 px reflow and focus order are therefore "read, not observed".

## Verdict
**CONDITIONAL PASS** as a prototype. Role choice, per-role allow-lists, denial, all 11 scripted scenarios and fail-closed behaviour are present and match the README. No forbidden words, no external requests, no secrets. Two Medium findings (F-01, F-02) and several Low findings should be fixed or recorded before the prototype is used as design evidence. No High findings.

## Checks that passed (evidence: file lines)
| Check | Result |
|---|---|
| Role flow: two learner-selectable roles only (`ROLES`, l.189-204); confirm with validation error (l.710-714); change-role dialog with safe default focus "Keep my role" (l.774-780) | Pass |
| Tab matrix (l.192, 199) equals README matrix for all 10 tabs x 2 roles | Pass |
| Direct/hash navigation to other-role, unknown or staff-style id: one uniform page "Not available in your workspace" (l.650-653, 695-707); one log entry per refusal; no data function invoked | Pass |
| Track data built only after confirm (`TRACK[id]()` l.719); other track not instantiated; cleared on reset (l.727-738) | Pass |
| Python scenarios: pass, failing test with line diff, blocked import, network attempt, infinite loop (stopped at deadline, no duration shown), runner unavailable (l.256-267) | Pass |
| Analyst scenarios: correct, wrong rows with extra/missing/match diff, ATTACH, DROP, multiple statements, runaway query, runner unavailable (l.297-309) | Pass |
| Runner unavailable fails closed: step 1 error, rest skipped, copy "no other way of running was used", in-process radio disabled (l.233, 456, 370) | Pass |
| Banner on every view (l.139, outside the swapped `#view`); "Proposed" chip on every limit row (l.362) and in step notes | Pass |
| Grep for fail, cheat, misconduct, suspicious, "AI detected", aggregate, rank, score, percentile, hire, "x of y": no hits in learner copy | Pass |
| Grep for http, fetch, XHR, WebSocket, @import, url(, secret, key, localStorage: no hits; only sessionStorage with role id | Pass |
| Probe chip text exactly "Output verified, understanding unconfirmed" (G-5), neutral class with icon, method labels and icons match G-7 (l.205-211) | Pass |
| Estimate shows value, likely range and as-of date (G-2, G-10) with table alternative; AI-assisted chip with confidence and appeal control (G-4) | Pass |
| A11y read: skip link, `header`/`nav`/`main`/`footer` landmarks, one h1 per view with focus on route change, labels on all inputs, `role=alert` errors, dialog `aria-modal`, background `inert`, Tab trap and Escape, focus return, 44 px targets, `min(100%,15rem)` grid, scroll wrappers for tables and 1fr `dl` under 400 px | Pass (unverified in a browser) |

## Findings
| ID | Severity | Location | Finding | Recommendation |
|---|---|---|---|---|
| F-01 | Medium | l.601-603, 619 (`bandBlock(..., unc)`) | When the probe outcome is "unconfirmed" the Profile estimate changes from 0.58 / 0.62 to 0.50 with range 0.25 to 0.78. The same screens say "its result is unchanged" (l.583, 628, ux-flows 4.6). Displayed outcome changes because of the probe, which contradicts that copy and the "does not change the result" promise. | Keep the estimate identical for both probe outcomes, or change the copy and get a product decision. Record as an open question for product-owner. |
| F-02 | Medium | l.590 | Probe copy says "Your own work is then run on slightly changed data" and result copy says "matched what the changed data produces" (l.584). This claims real execution of the learner's work; the prototype runs nothing and the probe outcome is a prototype control. The Tests, Probe and Profile views carry no "scripted" label (only the banner). | Add a scripted-result line on Tests, Probe and Profile as already done on Output, Results and Feedback, and prefix the probe sentence with "(simulated)". |
| F-03 | Medium | l.149-173, 225 | Operator view (limits table including "hard deadline 5 s ... never shown to learners") and event log sit on the same page directly below every learner view. A learner-facing screen therefore shows the 5 s wall-clock value and operator internals, contradicting its own label and the G-8 intent (no time values in learner views). | Move the operator view behind a separate "Operator preview" route or toggle outside the learner shell, or render it in a clearly separate frame and remove the 5 s value from the same document as learner tabs. |
| F-04 | Low | l.261-267, 456 and Editor hint l.484 | Copy "Your work is saved" appears on every non-result, but the editor states the draft is kept in this page only and it is lost on reload (`ws` is memory only; only the role id is stored). A11Y-4 "drafts autosaved" is not met. | Mark the "saved" copy as prototype-only, or persist the draft in sessionStorage with an explicit note. |
| F-05 | Low | l.583 | Probe explanation reads "predict how it works"; ux-flows 4.6 text is "explain or predict how it works". | Align wording with ux-flows or change the spec with a note. |
| F-06 | Low | l.615 | Experimental label reads "Experimental. This is not a validated predictor of job performance." G-3 wording is "Experimental: not a validated hiring predictor". Estimate is a fixed constant unrelated to the work, labelled only by the banner. | Use the G-3 wording; add "illustrative value" near the estimate. |
| F-07 | Low | l.702, 351; README gap 5 | Event log prints the requested route text (sanitised, 40 chars) in the learner page. SR-15 intent is tab id and role, not free text; reflected user text is also a logging-hygiene smell. | Log "refused tab id (known/unknown)" and role only. |
| F-08 | Low | l.817-819 | `ROLES[saved]` accepts inherited keys from sessionStorage ("constructor", "toString"). `TRACK[saved]()` then yields a non-track and `freshWs()` throws on init, leaving a broken page. Role is also trusted from client storage (README D-4). | Use `Object.prototype.hasOwnProperty.call(ROLES, saved)`; keep note that server derives role (SR-02). |
| F-09 | Low | l.639-647 | Role validation error `#role-err` is not referenced by the radios' `aria-describedby`; `data-err` is unused. Probe error is linked correctly. | Add `role-err` to `aria-describedby` when `chooseError`. |
| F-10 | Low | l.502, 501 | Tests view: card `h2` followed by `h4` "Line difference" skips h3. `ul.grid` with `list-style:none` may lose list semantics in some screen readers. | Use h3 for the card sub-heading, or h3 for card titles under an h2. |
| F-11 | Low | l.263 | Network attempt scenario shows the "Not run" chip while operator view shows run steps done and stderr is displayed in Output. Wording is inconsistent between learner and operator views. | Use "Blocked" or "Stopped" chip text for this case. |
| F-12 | Low | l.158, 137 | Event log (`aria-live=polite`) and `#announce` both fire on refused navigation (double announcement). Static banner has `role=status` though it never changes. | Drop `aria-live` on the log or the announce call; drop `role=status` from the banner. |
| F-13 | Info | l.399-401, 385-387 | On run start the focused Run button is replaced by re-render (focus falls to body) and is restored only at completion. Not verifiable without a browser. | Keep focus on the control, or move focus to the status region; verify in browser. |

## Consistency with the security review
| Item | UI visibility | Result |
|---|---|---|
| SR-01 (`dataset_ref`, runner confused deputy) | Not visible in UI; README makes no claim of mitigation | Not testable here; no inconsistency |
| SR-02 (role assignment) | Only two learner tracks selectable; staff roles absent; README states the track is not an authorization claim. Client-side storage of the role (F-08) must not be carried into the build | Consistent as a prototype |
| SR-15 (log content) | Event log shows route text (F-07) | Minor inconsistency |
| B-1 CSP vs inline script | README D-5 discloses | Accepted for prototype |

## Not verified (cannot be established statically)
Actual rendering and 320 px reflow, keyboard order, focus visibility, screen-reader output, colour contrast computed values (token values look compliant: #767676 on white 4.5:1), timing of the simulated run, behaviour with reduced motion.

## Next step
Author to address F-01 to F-03 (and ideally F-04 to F-09), then re-verify by an independent reviewer with a browser and axe.

## Re-verification (2026-10-10, quality-engineer, static read of the revised 845-line file)
Method: full re-read of `sandbox-shell.html` l.120-845, README grep, scans. Not run in a browser.

| ID | Status | Evidence (sandbox-shell.html) |
|---|---|---|
| F-01 estimate varies with probe | Fixed | `bandBlock(e)` takes no widened argument (l.614-615); called with `data.est` only (l.632); copy states "same whatever the probe outcome" (l.632). `unc` at l.631 is now unused. |
| F-02 claims of execution / missing scripted labels | Partially fixed | `scripted()` (l.355-357) on Tests l.504, Probe form l.603, Profile l.643; "Scripted result." in Feedback l.571, l.584; probe intro now "(Simulated here: nothing is run.)" l.603. Residual: Probe result view (l.594-598) has no scripted label and l.597 still says "matched what the changed data produces". |
| F-03 operator view co-located | Fixed | `#operator` is `hidden` by default (l.177), toggled by `toggle-op` (l.782-787). Limits table, run id, isolation_mode and 5 s are only built into that hidden section (l.368-387, l.234). Learner copy mentions categories only (l.160). Event log text has no route, run id or limits (l.716, 734, 745). README D-7. |
| F-04 "work is saved" vs memory-only draft | Accepted | Editor states drafts are memory-only and "saved" lines describe the product (l.497). Other tabs repeat "Your work is saved" (l.270-276, 465, 672) without that caveat. |
| F-05 probe wording | Fixed | l.596 and l.641 now "explain or predict", matching ux-flows 4.6. |
| F-06 Experimental wording, fixed estimate | Fixed | l.628 "Experimental: not a validated hiring predictor"; l.632 "Illustrative value ... fixed example". |
| F-07 route text in event log | Fixed | l.716 logs role label and action only. |
| F-08 inherited-key crash | Fixed | l.836 uses `hasOwnProperty.call(ROLES, saved)`; only "python" or "analyst" can restore. |
| F-09 role error not described | Fixed | l.652 adds `role-err` to `aria-describedby` when `chooseError`; `#role-err` rendered in the same pass (l.660). |
| F-10 heading skip, list semantics | Fixed | l.514 uses h3 under card h2; l.696 sets `role="list"` on every `ul` in the view. |
| F-11 network chip "Not run" | Fixed | l.272 `chip: "Blocked"`; used at l.471. |
| F-12 double announce | Fixed | `announce` removed from `navigate` (l.709-720); banner no longer `role=status` (l.140). Log keeps implicit role=log polling only. |
| F-13 focus on run start | Fixed (static) | l.400 refocuses `#run-btn` after re-render. "Try again" in Tests/Output/Results has no `#run-btn`, so focus falls to body there (new Low, R-01). |

Regression checks: tab arrays unchanged and equal to README matrix (l.201, 208); uniform denial and `render(true)` focus (l.663-666, 709-720); 6 Python and 7 Analyst scenario entries (5 Analyst categories incl. ATTACH, DROP, multiple) present (l.265-276, 306-318); `R_DOWN` unchanged and fails closed with "no other way of running was used" (l.242, 469); dialog trap, inert background and focus return unchanged (l.753-773, 820-830). Track data still built only after confirm (l.732). Forbidden-term scan (fail, cheat, misconduct, suspicious, "AI detected", aggregate, rank, percentile, score, match %, hire): 0 hits. External-request scan (http, fetch, XHR, WebSocket, @import, url(, secret, key, localStorage, import(): 0 hits.

New Low findings: R-01 above; R-02 operator toggle changes both its text and `aria-pressed` (l.785-786), which a screen reader reads as "off, pressed"; use a fixed label with `aria-pressed` only. R-03 the Probe result view lacks the scripted label (F-02 residual).

### Verdict: PASS (prototype, static). No open Medium findings except the F-02 residual, which is Low severity in effect. Fix R-02/R-03 at the next revision.

### Browser-only checks still needed
1. 320 px reflow with no horizontal scroll, 200% zoom, tables scroll inside `.tw`.
2. Keyboard-only pass: skip link, tabs, role form, dialog trap, Escape, focus return, operator toggle.
3. Screen reader (NVDA or VoiceOver): announcements for run, denial, role reset; role=log behaviour; toggle state.
4. axe or Lighthouse run for contrast, landmarks, names, duplicate IDs.
5. Direct hash entry (`#/sql` as Python role, `#/reviewer`, `#/%00`) shows the denial and logs once.
6. Run each scenario and confirm step chips in the operator view; reduced-motion behaviour; sessionStorage restore and tampered value.
