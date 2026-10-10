<!-- STATUS: DRAFT -->
# Real-browser spot-check: SLICE-C1 (learner flow)

Owner: Chief of Staff (manual Playwright-style check via built-in browser) | Date: 2026-10-10
Scope: first real-browser verification of the frontend; build-log SLICE-C1 explicitly stated this had never been done (jsdom/fake-fetch only).

## What was run
Started `crucible-api` (port 8000) and `crucible-web` (port 5173) against freshly seeded demo accounts. In a real browser:
1. Signed in as `demo-learner@crucible.example` against the live API — succeeded, redirected to `/path`.
2. Opened `/lobby/1` — Level 1 lobby rendered with the 7-step wizard (Confirm, Consent, Network, Camera and mic, Screen, Full screen, Rules and start), track selector defaulted to "Python developer", alias shown as `cnd_2c8ccc85dc5b`.
3. Advanced to step 2 — consent screen rendered as specified: explicit list of what's captured (camera/mic, entire screen, named events), explicit "nothing will be recorded" on decline, checkbox gate before "Agree and continue" is meaningful.
4. Two stray 401s on `/api/...` appeared in console before sign-in completed (pre-auth requests); not reproduced after login, not investigated further — low priority, flag for the next full verification pass.

## Verdict
CONDITIONAL PASS for the part exercised (auth, routing, consent-gate UI match the spec). Camera/mic/screen-share/recording steps were not exercised (require real device permissions this environment can't grant) — that gap remains open, same as the build-log already disclosed. No contradiction found between claimed and actual behavior for the steps reached.

## Not covered
Camera/mic/screen capture, exam question flow, code editor/test runner, Level 4 interview screen, reviewer/recruiter/auditor UIs, integrity detectors firing on real events.
