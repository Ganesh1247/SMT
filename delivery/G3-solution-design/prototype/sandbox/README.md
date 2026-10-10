<!-- STATUS: DRAFT -->
# Sandbox shell prototype (clickable, simulated)

Owner: ux-architect | Gate: G3 | Version: 0.1 | Date: 2026-10-10 | Reviewer: not yet reviewed (author does not review own work)
Inputs: `sandbox-environment.md`, `ADR-0003-os-level-sandbox.md`, `sandbox-security-review.md`, `ux-flows.md` (G-rules, s9, s10), `learner-dashboard.html`, Founder correction (roles Python developer and Data analyst, learner-chosen).

## What it is
One self-contained file, `sandbox-shell.html`: a role-scoped, allow-listed-tab workspace shell in front of a **simulated** per-run runner. It shows how a learner picks a learning track, sees only that track's tabs, runs work, and reads neutral feedback. Inline CSS and JS, no CDN, no external request, no server.

## What it is NOT
- Not isolation. No container exists. The banner says so on every screen: "PROTOTYPE · simulated runner · synthetic data · no real isolation".
- Not execution. Nothing typed is run, parsed or analysed. Every result, diff, output and probe outcome is **scripted** per scenario.
- Not a measurement. Limits are the **Proposed** values from `sandbox-environment.md` s2, shown as labels only.
- Not a security control. Tab denial here is client-side presentation; the real control is server-side route policy (TAB-FF-1..5).
- Not a statement that any threat is mitigated. No Medium/High finding is closed by this prototype.

## How to open
Open `sandbox-shell.html` in a browser (double-click). No build step. Use hash routes such as `#/brief` or `#/sql` in the address bar to try the denial page.

## Roles x tabs (as implemented)
| Tab | Python developer | Data analyst |
|---|---|---|
| Brief | Allow | Allow |
| Editor (Python) | Allow | Deny |
| Tests (visible tests) | Allow | Deny |
| Output (captured stdout/stderr, no shell) | Allow | Deny |
| Data (tables + preview) | Deny | Allow |
| SQL editor | Deny | Allow |
| Results (table + text summary) | Deny | Allow |
| Feedback | Allow | Allow |
| Probe | Allow | Allow |
| Profile | Allow | Allow |

Any other route (other-role tab, unknown id, staff-style id) shows the same "Not available in your workspace" page and adds one entry to the Shell event log. Track data is built only after the role is confirmed; the denial path loads nothing.

## Screens and states
Choose your role (card per role, confirm, validation error), Change role (confirm dialog, focus trapped and returned, resets workspace), seven tabs per role, Not available page. States: loading (role confirm, plus a prototype control), error (control), empty (no run yet, no output, no feedback), evaluating (during a simulated run), non-results (blocked, limit, runner unavailable).

## Scripted scenarios
| Track | Scenario | Learner sees | Runner (operator view) |
|---|---|---|---|
| Python | Passes visible tests | Passed, Output shows stdout | all five steps done |
| Python | One test not passing | Not passed with Expected/Got line difference | all steps done |
| Python | Blocked import (os, subprocess, socket) | "Not run", not available in workspace | create refused at validation, no container |
| Python | Network attempt | "Not run", network not available | run done, connection refused (network none, proposed) |
| Python | Infinite loop | "Took too long", no duration shown | run stopped at proposed hard deadline, container removed |
| Python | Runner unavailable | alert, Try again; no fallback | create refused, stays closed |
| Analyst | Correct query | Passed, result table, text summary | all steps done |
| Analyst | Wrong rows | Not passed with row-level difference (extra, missing, matches) | all steps done |
| Analyst | ATTACH, DROP, multiple statements | "Not run", statement not available | create refused at validation |
| Analyst | Runaway query | "Took too long", no duration shown | run stopped at proposed budget |
| Analyst | Runner unavailable | alert, Try again; no fallback | create refused, stays closed |

Blocked, limit and unavailable outcomes are non-results: they are never shown as a criterion outcome (per `sandbox-environment.md` s6, assessment_core row). The in-process manual mode appears only as a disabled radio with an explanation.

## Rule conformance (self-check, not a review)
G-1 no aggregate or "x of y"; G-2/G-10 estimate with band and as-of date; G-3 Experimental label on Profile; G-4 AI-assisted label with confidence and appeal; G-5 probe chip text exactly "Output verified, understanding unconfirmed"; G-7 five fixed method labels with icons; G-8 no timers or time-taken in learner views (the 5 s wall-clock limit appears only in the operator limits table, marked operator-only); G-9 no names, synthetic ids only. Words fail, cheat, misconduct, suspicious, "AI detected" are absent from the file. Tokens 9.1-9.3 reused from `learner-dashboard.html`. Reflow targeted at 320 px, 44 px targets, visible focus, one h1 per view, `role=status`/`alert`, dialog focus trap and return.

## Deltas from sandbox-environment.md
| # | Delta | Why |
|---|---|---|
| D-1 | Roles are Python developer and Data analyst, **chosen by the learner**; design doc has learner/reviewer/auditor from the session | Founder correction |
| D-2 | Python runs inside the container | Founder correction; widens ADR-0001 D1 (SQL-only) |
| D-3 | Tab set per role differs from s4 `L-*` rows (Editor, Tests, Output, Data, Results are new) | Track-specific tools |
| D-4 | Role is held in sessionStorage for the demo | B-6 forbids learner data in browser storage; role only, no learner content |
| D-5 | Inline script and style | Single-file prototype; B-1 CSP (`script-src 'self'`) is unchanged. The product build will use external script and style files served under that CSP |
| D-7 | Operator view (limits, run id, isolation_mode, 5 s budget) is behind a demo-only "Operator view (demo)" toggle, off by default | Learner screens show no limits or durations (G-8, review F-03) |
| D-6 | Denial is rendered client-side from the hash | Prototype has no server; real denial is uniform 404 from route policy |

## Open gaps and assumptions
1. **Python in the container (needs Founder decision and ADR amendment).** ADR-0001 D1 and sandbox-environment Q1 say SQL only. Python needs a separate image, a stricter profile (no imports of system modules, no network, no file writes outside tmpfs), its own escape test suite, and a different output schema (stdout/stderr plus test results; SR-10 validation must be extended). The import blocklist (os/subprocess/socket) is a UX illustration, not a sufficient control: a denylist is bypassable and the container is the real boundary.
2. **Role-change semantics.** Prototype resets the workspace on change. Open: does the server keep one track per account (changing deletes the other track's evidence?), or can a learner hold both tracks with separate evidence? The matrix and Profile assume one track at a time. Learner role is a learning-track preference, **not** an authorization claim; tab authorization must still be derived from the session on the server (SR-02, TAB-FF-4). Changing track must not alter any other privilege.
3. **Staff views excluded.** Reviewer and auditor tabs are not in this prototype and staff role is never selectable in the UI (SR-02: assigned server-side from an allow-list). Existing `V-*` and `A-*` screens remain in `ux-flows.md`.
4. **Cross-track data.** Single static file contains both tracks' scripted data in source; only the chosen track is instantiated. In production each track's tab routes and data must be separate and checked server-side (SR-03).
5. **Denial wording.** Uniform page implemented. The event log records the role and the action only, not the requested route text (SR-15).
5a. **Inline script.** The prototype is single-file with inline JS and CSS. The product build will use external script files with a CSP (B-1 unchanged).
5b. **Estimate and probe.** The estimate is an illustrative fixed value, labelled as such, and is identical whatever the probe outcome (an unconfirmed probe does not change the displayed estimate, G-5 and ux-flows 4.6). Open for product-owner: whether an unconfirmed probe should ever affect the band.
5c. **Drafts.** Drafts are in memory only and lost on reload; the "Your work is saved" lines describe the product autosave (A11Y-4), which the prototype does not implement.
5d. **Stored role.** The stored role id is validated against the known role list; it is a demo convenience, never an authorization input.
6. Python-specific wording for "run limit" and memory outcomes (OOM, output too large, busy) is not designed here; only unavailable, blocked and limit are.
7. Probe on Python needs re-running learner code on altered input in the container; latency and limits per run are unmeasured (A7).
8. Hidden checks and appeals are referenced but not built (info dialog).
9. The reduced-isolation (in-process) banner is not shown because the mode is not selectable; its Python behaviour on Windows is undefined (SR-11).
10. Review notes (`review-notes.md`) F-01 to F-12 were addressed in this revision; F-13 (focus on run start) is handled by refocusing the Run control, still unverified in a browser. Accessibility checks were authored, not tested with a screen reader or automated tool. No Lighthouse/axe evidence exists yet.

## Open questions
- Founder: approve Python in the container as a scope change (ADR-0001 amendment, new threat model rows)?
- Founder/product-owner: one track per learner or both, and what happens to existing evidence on change?
- security-engineer: review Python image profile before any build slice.
