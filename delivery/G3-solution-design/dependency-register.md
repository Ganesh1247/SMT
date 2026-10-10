<!-- STATUS: DRAFT -->
# Dependency Register

Owner: principal-architect | Gate: G5 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer
Inputs: governance/policies/dependency-policy.md, delivery/G4-delivery-plan/build-brief.md (section 9)

## Dependencies
| Name | Version | Licence | Purpose | Owner | Alternatives considered | Fallback | Approved by | ADR |
|---|---|---|---|---|---|---|---|---|
| fastapi | 0.141.1 (installed) | MIT | HTTP routers in module api/ | stream A | Flask, Starlette only | none (stack fixed in build brief) | PENDING principal-architect | build-brief s9 |
| pydantic | 2.13.4 (installed) | MIT | request-body validation at HTTP boundary | stream A | dataclasses + manual checks | manual validation | PENDING principal-architect | build-brief s9 |
| jsonschema (+ referencing) | 4.26.0 (installed) | MIT | validate boundary payloads and ledger events against G3 contract schemas | streams A2 (review, hr, interview) | fastjsonschema (installed, no $ref registry) | hand-written validators | PENDING principal-architect | contracts README |
| httpx | 0.28.1 (installed) | BSD-3-Clause | Anthropic Messages API client (intelligence); test client transport | stream A2 | anthropic SDK (0.104.0 installed, not used), urllib | StubProvider (offline) | PENDING principal-architect | build-brief s5 |
| pytest | 9.1.1 (installed) | MIT | tests | all streams | unittest | none | PENDING principal-architect | build-brief s9 |
| SQLAlchemy | 2.0.28 (installed) | MIT | SQLite persistence in identity, evidence, scoring, assessment (parameterised `text()` queries via engine) | stream A1 | stdlib sqlite3 | stdlib sqlite3 | PENDING principal-architect | build-brief s9 |
| uvicorn | 0.47.0 (installed) | BSD-3-Clause | ASGI server for the HTTP composition root | stream A1 | hypercorn, granian | none | PENDING principal-architect | build-brief s9 |
| starlette (transitive via fastapi) | as installed with fastapi | BSD-3-Clause | middleware, static files, test client | stream A1 | none | none | PENDING principal-architect | build-brief s9 |
| Anthropic Messages API (service) | api version 2023-06-01 | commercial terms | optional AI feedback and L4 evaluation; enabled only when ANTHROPIC_API_KEY and CRUCIBLE_MODEL are set in the environment | stream A2 | StubProvider | StubProvider (deterministic, offline, labelled) | PENDING principal-architect | build-brief s5 |
| Docker Engine / Docker Desktop (tool, WSL2 backend) | 29.6.1 (installed) | Docker Desktop subscription terms (free for personal/small business; Founder to confirm eligibility) | per-run container isolation for learner code (runner only; CLI via fixed argv, no Python Docker library) | stream B (runner) | restricted subprocess (kept as explicit fallback), micro-VM | `RUNNER_ALLOW_FALLBACK=true` labelled `process-fallback`; otherwise fail closed | PENDING principal-architect | ADR-0003 |
| python:3.11-slim (container image) | image ID pinned via `RUNNER_IMAGE_ID` (digest sha256:e88e9763f943...f65ce at pull time) | PSF + Debian licences | base image for the runner container; stdlib only, no extra packages | stream B (runner) | distroless, custom image | none (fail closed) | PENDING principal-architect | ADR-0003 |
| (none new) stdlib only: sqlite3, ctypes (Windows Job Object in fallback), threading | Python 3.11 | PSF | runner and integrity persistence; fallback memory/process limit | stream B | SQLAlchemy, pywin32 | n/a | n/a | build-brief s9 (deviation noted in build log) |
| react / react-dom | 18.3.1 (pinned) | MIT | UI rendering | stream C | Vue, Svelte | none (stack fixed in build brief) | PENDING principal-architect | build-brief s9 |
| react-router-dom | 7.18.4 | MIT | client routing and route guards | stream C | hand-written history router | small in-house router | PENDING principal-architect | build-brief s9 |
| @codemirror/state, view, commands, language | 6.7.6 / 6.43.14 / 6.11.1 / 6.13.1 | MIT | code editor for Python/SQL items | stream C | Monaco (heavy, weaker a11y), plain textarea | plain textarea (built-in toggle) | PENDING principal-architect | build-brief s9 |
| @codemirror/lang-python, lang-sql | 6.2.1 / 6.10.0 | MIT | syntax support | stream C | none | plain textarea | PENDING principal-architect | build-brief s9 |
| vite, @vitejs/plugin-react | 8.3.4 / 6.1.2 | MIT | dev server (proxy /api) and build | stream C | webpack, esbuild only | none | PENDING principal-architect | build-brief s9 |
| typescript | 5.9.3 | Apache-2.0 | type checking | stream C | JS only | none | PENDING principal-architect | build-brief s9 |
| vitest, jsdom | 5.0.3 / 30.1.2 | MIT | unit and component tests | stream C | jest | none | PENDING principal-architect | build-brief s9 |
| @testing-library/react, user-event, jest-dom | 16.3.3 / 14.6.7 / 7.0.1 | MIT | component and interaction tests | stream C | enzyme | none | PENDING principal-architect | build-brief s9 |
| axe-core | 4.14.0 | MPL-2.0 (dev/test only, not shipped) | automated accessibility checks in tests | stream C | pa11y, jest-axe | manual audit | PENDING principal-architect | build-brief s9 |
| @types/react, @types/react-dom, @types/node | 18.3.31 / 18.3.7 / 22.20.5 | MIT | type definitions (dev only) | stream C | none | none | PENDING principal-architect | build-brief s9 |

Note: persistence in review, hr and interview uses the Python standard library sqlite3 (document store), not SQLAlchemy, so no extra dependency is added. Pins to be fixed in a lockfile before G6.

## Disclosure notes
Learner text sent to the Anthropic API (only when enabled) is delimited as untrusted data and contains no names or contact details; AI results carry ai_disclosure=true and model_ref.
