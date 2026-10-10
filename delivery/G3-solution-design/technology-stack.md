<!-- STATUS: DRAFT -->
# Crucible — Detailed Technology Stack

> **Document status:** Engineering reference for the current repository. It distinguishes implemented technology from proposed architecture. **ADR-0001, ADR-0002 and ADR-0003 are Proposed** in the current decision records; a dependency being installed or code being present does not, by itself, mean the ADR or production use is approved.

## 1. Executive overview

Crucible is currently a browser-based, role-aware proof-of-skill application. The web client is built with React, TypeScript and Vite. A Python/FastAPI application exposes the `/api` boundary and composes capability modules for identity, assessment, code execution, integrity, evidence, scoring, review and recruiter workflows. The modules own their persistence and interact through public facades or ports. Learner-provided code is sent through a narrow runner boundary and executed in an isolated child process/container when Docker is available.

### Stack at a glance

| Concern | Current implementation | Architectural intent |
|---|---|---|
| Web app | React 18 + TypeScript 5 + Vite 8 + React Router 7 | Accessible role-specific UI without a separate app deployment for each role |
| API | FastAPI + Uvicorn + Pydantic 2 | One Python HTTP composition root, `/api` routes, strict request validation |
| Backend runtime | Project metadata requires Python `>=3.11`; ADR recommends Python 3.12 | Standardize production/dev on Python 3.12 after CI/runtime pin is aligned |
| Module structure | Capability modules with `domain/`, `application/`, `infrastructure/`, `api/` | Modular monolith; cross-module use only through public APIs/ports |
| Data | Python `sqlite3`, separate files by module/context | Keep local demo simple; PostgreSQL can be considered for multi-writer/hosted operation |
| Learner execution | Runner module, Docker CLI adapter and restricted process fallback | One constrained execution boundary; no learner-controlled Docker arguments |
| Contracts | JSON Schema 2020-12; Pydantic at HTTP edge | Schemas define cross-module evidence, grant, role and shared-evidence payloads |
| Ledger | Canonical JSON + SHA-256 hash chain in Python | Append-only evidence, idempotent event ingestion, explicit verification |
| AI | `FeedbackProvider` port; offline stub and optional Anthropic adapter | AI assists rubric criteria only; output is validated, disclosed and reviewable |
| Tests | pytest, Vitest, Testing Library, axe-core | Unit, contract, journey, architecture-boundary and accessibility checks |

## 2. Technology inventory and versions

Versions below come from the repository manifests, dependency register, or build notes. They are not a claim that every version is locked for production.

### 2.1 Frontend

| Package / platform | Version recorded | Role |
|---|---:|---|
| React / React DOM | 18.3.1 | Component rendering and client UI |
| TypeScript | 5.9.3 | Static typing for UI, route data and client logic |
| Vite | 8.3.4 | Local development server and optimized static build |
| `@vitejs/plugin-react` | 6.1.2 | React integration for Vite |
| React Router DOM | 7.18.4 | Role-aware route composition and navigation |
| CodeMirror 6 (`state`, `view`, `commands`, `language`) | 6.7.6 / 6.43.14 / 6.11.1 / 6.13.1 | Accessible editing surface for programming tasks |
| CodeMirror Python / SQL languages | 6.2.1 / 6.10.0 | Syntax support in the learner editor |
| Vitest | 5.0.3 | Unit/component test runner |
| jsdom | 30.1.2 | DOM environment for UI tests |
| Testing Library React / user-event / jest-dom | 16.3.3 / 14.6.7 / 7.0.1 | User-oriented component and interaction tests |
| axe-core | 4.14.0 | Automated accessibility checks in selected UI tests |

**Frontend build:** `npm run build` runs TypeScript (`tsc --noEmit`) followed by Vite. `npm test` runs Vitest. The current build log reports a successful Vite build and 132 passing frontend tests. These tests use fakes for browser media APIs; they are not equivalent to an end-to-end run in a real browser with camera, microphone and screen devices.

**UI behavior:** roles are obtained from the authenticated `/api/me` response. `canAccess(role, path)` blocks routes by default, but API-side authorization remains authoritative. Learner, recruiter, reviewer and auditor views are in the web client; HR screens are not granted direct access to the assessment service.

### 2.2 Backend and API

| Package / platform | Version recorded | Role |
|---|---:|---|
| Python project requirement | `>=3.11` in `product/pyproject.toml` | Minimum interpreter declaration currently in the package manifest |
| Python target in ADR | 3.12 | Proposed standard backend runtime; align manifest, CI and deployments before claiming a 3.12-only baseline |
| FastAPI | `>=0.110` manifest; 0.141.1 in dependency register | Router framework and OpenAPI-capable API composition |
| Uvicorn | `>=0.27` manifest; 0.47.0 in dependency register | ASGI server for local/demo HTTP API |
| Pydantic | `>=2.5` manifest; 2.13.4 in dependency register | Request/response shape validation at API boundaries |
| Starlette | FastAPI transitive dependency | Middleware, static-file response and ASGI primitives |
| HTTPX | `>=0.27` test extra; 0.28.1 in register | Test transport and Anthropic Messages API HTTP adapter |
| JSON Schema | 4.26.0 in dependency register | Validate shared boundary contracts and evidence events |
| `referencing` | Included alongside `jsonschema` in register | JSON Schema reference resolution |

The composition root lives in `product/entrypoints/http-api/`. It wires module APIs, mounts routers under `/api`, normalizes errors, applies request/body and origin controls, and can serve `product/entrypoints/web/dist` when that directory exists. API documentation endpoints are disabled in the current composition root. `/api/health` reports loaded modules and runner isolation status.

The current server configuration is environment-driven: `DATA_DIR`, `CRUCIBLE_HOST`, `CRUCIBLE_PORT`, `CRUCIBLE_COOKIE_SECURE`, `CRUCIBLE_ALLOWED_ORIGINS`, body/chunk size limits, web-serving options, and explicit runner fallback settings. Optional AI configuration uses `ANTHROPIC_API_KEY` and `CRUCIBLE_MODEL`; secrets are not intended to be placed in source files.

### 2.3 Persistence and schemas

| Technology | Current use | Important detail |
|---|---|---|
| Python standard-library `sqlite3` | Persistence adapters across built modules | Current modules generally open their own SQLite file under `DATA_DIR`; review, HR, interview and integrity use `sqlite3` directly |
| SQLAlchemy 2 | Declared in `product/pyproject.toml` and ADR-0001; dependency register has it installed | Architecture proposal lists it for parameterized persistence; inspect module-specific implementation before assuming a module uses it |
| Alembic | Proposed in ADR-0001 | Not established as a current migration workflow in the supplied implementation evidence |
| JSON Schema 2020-12 | Cross-module/event contract definitions | Contract files in `delivery/G3-solution-design/contracts/` are the canonical shared payload definitions |
| Pydantic models | HTTP validation and typed request handling | Keep edge models aligned to the schemas; schema files win if definitions drift |
| SHA-256 / canonical JSON | Evidence and recording integrity | Evidence event canonicalization is versioned; recording manifests hash ordered chunk metadata |

**Current module data files called out by module documentation** include `identity.db`, `assessment.db`, `evidence.db`, `scoring.db`, `integrity/integrity.db`, `review.sqlite3` and `hr.sqlite3`, plus `DATA_DIR/recordings/` for media chunks and manifests. Exact file names are module configuration details and may evolve. The primary rule is ownership: one module is responsible for writes to its data.

The dependency register notes a mixed implementation: some early modules were planned around SQLAlchemy, while review, HR, interview and integrity explicitly use the standard-library store. Therefore this document describes SQLite as the actual storage engine, but SQLAlchemy/Alembic as proposed/partially declared tooling unless a specific adapter confirms its use.

### 2.4 Learner-code execution

| Technology | Current implementation / status |
|---|---|
| Runner module | `product/modules/runner/`; narrow `run_python`, `run_sql`, task registration API |
| Docker Engine / Docker Desktop | Used by the container executor where available; dependency register records Docker 29.6.1 on the build machine |
| Container image | Python 3.11 slim base, image pin supported by `RUNNER_IMAGE_ID`; image digest appears in the dependency register and should be refreshed/verified per build |
| Container launch | Docker CLI with fixed argv from the runner adapter; no shell string and no learner-supplied mounts, paths or runtime options |
| SQL engine | Standard-library SQLite in the child harness, fresh in-memory DB, authorizer restrictions, statement and result caps |
| Fallback | Restricted child-process executor; enabled only via explicit `RUNNER_ALLOW_FALLBACK=true`, reported as `process-fallback` |

Recorded container controls include a non-root UID, read-only root filesystem, no network, no mounts, dropped capabilities, no-new-privileges, process, memory and CPU limits, bounded output and cleanup after a run. The runner tests exercised actual containers on the build machine. The fallback has weaker/different isolation and must never be described as an equivalent container. Do not claim a separate HTTP runner service: build notes say Docker access currently occurs through the runner module's CLI adapter in the application process.

ADR-0003 is a proposed security design. It recommends a narrower privilege-separated runner service and a per-run container. The current implementation has a runner module and Docker-per-run behavior but documents deviations from the separate-service topology. Treat ADR design requirements and measured implementation as distinct.

### 2.5 AI and interview

| Component | Technology / rule |
|---|---|
| Provider boundary | Python `FeedbackProvider` protocol/port keeps business logic separate from vendors |
| Offline mode | Deterministic `StubProvider` for no-network, repeatable demo and tests |
| Optional real provider | Anthropic Messages API adapter using HTTPX; enabled only when configured |
| Prompt input | Learner content is untrusted data, delimited and excluded from instruction authority |
| Output | Parse into a fixed result structure; reject invalid or malformed output; attach method, model reference, confidence and disclosure |
| Interview | Backend state machine with prompts, turns, follow-up, rubric evaluation and human-review handoff |
| Frontend media | MediaRecorder/camera/screen/microphone, captions/transcript and speech/typed alternatives; browser APIs are feature-dependent |

The dependency register says no real Anthropic request was made in the recorded test run. The adapter's tests use an HTTPX mock transport; provider availability, cost and data-processing terms remain deployment/configuration decisions.

## 3. Application architecture and module stack

The codebase follows a layered module pattern:

```text
product/
  entrypoints/http-api/       HTTP composition, configuration, middleware, API wiring
  entrypoints/web/            React + TypeScript + Vite frontend
  modules/<capability>/
    domain/                   business rules and value objects; framework-free
    application/              use cases, orchestration, ports
    infrastructure/           persistence, runner and provider adapters
    api/                      the module's public facade/router/DTOs
    tests/                    module unit, contract and boundary tests
  architecture-tests/         rules for imports and module ownership
```

| Module / capability | Owns | Main technology touchpoints |
|---|---|---|
| `identity` | Accounts, password hashes, server sessions, roles and pseudonyms | FastAPI dependency, standard-library `scrypt`, SQLite |
| `assessment` | Task bank, attempts, progression, answer state, retry variants and score gate | FastAPI router, SQLite, runner/intelligence/integrity/evidence/scoring facades |
| `runner` | Task registration, constrained execution and bounded results | Python child harness, SQLite, Docker CLI adapter, OS limits |
| `intelligence` | Feedback-provider interface and evaluation output | HTTPX, deterministic stub, optional Anthropic adapter, schema checks |
| `interview` | Level 4 session prompts, turns, adaptation and evaluation handoff | Python state machine, assessment/review ports, SQLite adapter |
| `integrity` | Consent, prechecks, event ingestion, recordings, fingerprints and flags | FastAPI router, `sqlite3`, filesystem chunks, SHA-256 manifests |
| `evidence` | Append-only event history and verification | `sqlite3`, canonical JSON, `hashlib.sha256`, idempotency keys |
| `scoring` | Gated estimate updates and competency estimates | Python domain logic, evidence inputs, SQLite adapter |
| `review` | Appeals, reviewer queue, human decisions, grants and shared-evidence query | FastAPI, SQLite document store, JSON Schema validation, evidence/integrity/assessment ports |
| `hr` | Versioned role requirements, coverage/gaps, evidence view and receipt verification | FastAPI, SQLite, shared-evidence contracts, review/evidence ports |

**Dependency constraints:** `domain/` should not import FastAPI, SQLAlchemy, HTTP clients or another module's internals. `application/` may use its own domain and other modules' public `api/` surfaces/ports. Infrastructure adapts external technologies to ports. Cross-module shortcuts into another module's persistence or domain layer are architecture violations.

## 4. Request and data flow in detail

### 4.1 Browser request

1. React route renders the current role's experience and obtains identity from `/api/me`.
2. Browser submits JSON to `/api`; credentials use the server session cookie.
3. FastAPI middleware applies security headers, allowed-origin checks and request-size caps.
4. Identity dependency resolves the session and server-side role. The API rejects unknown roles and unauthorized ownership; frontend visibility is not authorization.
5. Pydantic validates the HTTP shape. Where the payload crosses a module/system contract, JSON Schema validates the canonical versioned contract as well.
6. Router calls the owning module's public facade; application service runs domain rules; ports route persistence, runner, AI or other capability calls.
7. API returns a normalized response/error. Logs use a field allow-list; request bodies, credentials and personal data are not logged.

### 4.2 Assessment submission

```text
Learner UI
  -> assessment API (session + attempt ownership check)
  -> task rules / validate closed submission request
  -> runner API facade
  -> child harness in fresh container (or explicit labelled fallback)
  -> bounded execution result
  -> trusted assessment compares hidden checks
  -> optional AI criterion feedback (disclosed)
  -> assessment result / integrity and understanding context
  -> append EvidenceEvent (idempotency key; canonical hash)
  -> progress/profile projection updates only under configured gate
```

Expected results and hidden checks stay outside the untrusted child. Run metadata records the isolation mode. Learner-visible execution limits should present as save/retry behavior, not as a competitive timer or speed measure.

### 4.3 Recruiter query

```text
Recruiter UI -> HR API -> role and organisation authorization
           -> shared-evidence query through review/consent facade
           -> active grant + recipient + role + expiry + scope checks
           -> contract-validated, alias-based evidence response
           -> competency coverage/gaps (no total, rank or recommendation)
           -> evidence receipt verification through ledger facade
```

The HR side must never call the Sandbox/assessment module. No active grant yields an empty response with no disclosure of whether a learner exists or chose not to share.

### 4.4 Video/recording path

1. Level 4 precheck screen explains the activity and capture scopes.
2. Consent is recorded against the learner and attempt before capture starts.
3. Frontend sends bounded recording chunks and integrity events to authenticated endpoints.
4. Integrity module verifies attempt ownership and consent scope, caps chunk/event sizes, stores chunk hashes, then finalizes a manifest hash.
5. Manifest hash and relevant event are sent to the evidence ledger. Reviewer playback is role-gated and served using HTTP Range support.
6. Reviewer-only risk summary is advisory. It does not alter assessment results or create an automatic misconduct decision.

## 5. Interfaces, contracts and identifiers

| Contract/interface | Purpose | Validation / invariant |
|---|---|---|
| `EvidenceEvent` | Assessment, integrity, appeal and review facts recorded to ledger | Versioned JSON Schema; method and AI/live disclosure rules; idempotent append |
| `ShareGrant` | Learner authorization for evidence sharing | Expiry required; receiver, scope and role reference checked on every recruiter query |
| `SharedEvidence` | Contracted evidence returned from consent-controlled query | Schema-validated; aliases; no hidden thresholds, ranking or ungranted content |
| `RoleRequirement` | Recruiter-owned structured role criteria | Versioned; bounded competency list; rejects rank/speed/personal attributes |
| Runner request | Request to execute one registered task | Closed schema; opaque known IDs; bounded submission; no path or arbitrary container option |
| Evidence receipt | Proof that a result is tied to a ledger event | Hash/sequence validation; mismatch and unavailable are distinct outcomes |
| User/session | Authenticated identity and server-assigned role | Role is not accepted from the browser as an authorization claim |

The JSON Schema files are the source of truth for shared contracts. Breaking changes require a schema version change and coordinated updates to producers/consumers. Identifiers are opaque and pseudonymous at cross-role boundaries; recruiter-facing candidate references are recipient-specific aliases.

## 6. Security and privacy stack

| Layer | Mechanism | Notes / limitation |
|---|---|---|
| Login | Password hashing with Python `scrypt`; server-side session record; HttpOnly and SameSite=Strict cookie | Secure cookie is configured for HTTPS deployments; login lockout is currently process-local |
| Role authorization | FastAPI dependencies and role/ownership checks | Role state is server-side; frontend route guard is defense-in-depth for UX only |
| Browser/API boundary | Origin allow-list, CORS credentials configuration, security headers, body-size middleware | Production origin/TLS configuration is an operator responsibility |
| Request validation | Pydantic and explicit closed schemas; JSON Schema for contracts | Unknown fields rejected on selected contract boundaries |
| Sandbox | Docker per run when available, no network/mounts, read-only root, non-root, capability drop, no-new-privileges, CPU/memory/PID/output/time limits | Docker engine access is sensitive; current API process invokes CLI through runner adapter; fallback is weaker and explicit |
| Data privacy | Separate stores, aliases, no raw answer in ledger, consent scopes and expiring share grants | Local SQLite/files are not yet a full production data-protection deployment; at-rest encryption is not implemented |
| Integrity | SHA-256 event chain, recording chunk and manifest hashes, verification route | Removal of a newest ledger suffix is not detectable without a trusted signed/external chain head |
| AI input/output | Delimited untrusted learner input; strict structured output; provider key from environment | Vendor data handling and retention terms need review for deployment; AI judgment requires disclosure/appeal |
| Recording | Consent before capture, ownership checks, bounded uploads, reviewer-only playback, purge operation | Purge exists but must be scheduled; retention and encryption need production configuration |
| Logs | Structured JSON with an explicit safe field whitelist | Do not add request/response body logging or secrets |

## 7. Development, testing and release tooling

### Backend

- `product/pyproject.toml` declares FastAPI, Uvicorn, Pydantic and SQLAlchemy; pytest and HTTPX are test extras.
- `product/entrypoints/http-api/requirements.txt` repeats runtime/test requirements.
- `pytest` runs module tests, HTTP API tests and architecture tests.
- Runner tests include abuse inputs and real-container cases when Docker is available; tests requiring Docker are marked.
- Architecture tests enforce API-only imports and selected module-boundary rules.

### Frontend

- `product/entrypoints/web/package.json` pins the current UI dependencies.
- `npm test` runs Vitest; frontend build runs TypeScript checking and Vite bundling.
- React Testing Library validates interactions; axe-core checks selected screens.
- Test fakes simulate camera, microphone, screen capture, MediaRecorder, speech input and fullscreen. These do not establish real-browser compatibility.

### Build/release expectations

1. Use lockfiles for Python and Node package resolution; the dependency register notes pins still need a finalized lockfile before the relevant gate.
2. Run backend unit, contract, architecture and HTTP journey suites.
3. Run frontend tests, type-check and production build.
4. Run Docker-marked runner tests only on a host with an available Docker engine and verify reported isolation mode.
5. Run a real-browser smoke journey for login, learner path, consent, camera/screen, reviewer playback and recruiter grant query before any hosted demo.
6. Keep build/approval status truthful: source files and passing tests do not imply an independent quality/security review is complete.

## 8. Configuration and runtime shape

| Variable / setting | Purpose | Handling note |
|---|---|---|
| `DATA_DIR` | Persistent SQLite and recording data root | Restrict filesystem permissions; include in backup/retention plan if hosted |
| `CRUCIBLE_HOST`, `CRUCIBLE_PORT` | Local API bind address and port | Do not expose publicly without TLS/reverse proxy and security configuration |
| `CRUCIBLE_COOKIE_SECURE` | Mark session cookie Secure | Must be `true` behind HTTPS |
| `CRUCIBLE_ALLOWED_ORIGINS` | CORS/origin-check allow-list | Set exact deployed origins; avoid wildcard with credentials |
| `CRUCIBLE_MAX_BODY_BYTES`, `CRUCIBLE_MAX_CHUNK_BYTES` | Request and recording chunk caps | Tune consistently with reverse proxy and app limits |
| `CRUCIBLE_SERVE_WEB` | Serve built Vite `dist` from FastAPI | Frontend can be hosted separately if API origin/CORS is configured |
| `RUNNER_ALLOW_FALLBACK` | Explicitly permit restricted process fallback | Fallback is not Docker-equivalent; expose/report the mode |
| `RUNNER_IMAGE_ID` | Pin expected runner image identity | Refuse unexpected/mismatched images when configured |
| `ANTHROPIC_API_KEY`, `CRUCIBLE_MODEL` | Optional AI provider selection | Secret comes from environment/secret manager, not committed config |
| `INTEGRITY_*` | Precheck thresholds, risk weights, event caps and retention | Validate operator settings; retention purge must be scheduled |

**Local topology:** Vite dev server at port 5173 proxies `/api` to the FastAPI app at `127.0.0.1:8000`. For a built demo, FastAPI can serve the generated frontend files. Data remains local under `DATA_DIR`. No managed production infrastructure is implied.

## 9. Stack choices: why these technologies fit

| Choice | Reason in this project | Trade-off / when to revisit |
|---|---|---|
| React + TypeScript + Vite | Rich role-gated task and evidence screens, typed clients, fast local feedback | Two toolchains/language ecosystems; keep generated/handwritten contracts tested |
| FastAPI + Pydantic | Python is already used for canonical hashing, schema tools, runner and assessment; fast API composition and typed boundaries | Avoid coupling domain rules to Pydantic/FastAPI; framework remains at the edge |
| SQLite per module/context | Minimal setup, local demo-friendly, data ownership visible in separate files | Single-writer/concurrency limits, local file security and backup responsibility; consider PostgreSQL when hosted or concurrent writes are needed |
| Docker-per-run execution | OS boundary and reproducible environment for untrusted task code; validated by container inspection and escape tests | Cold start and Docker prerequisite; isolate Docker control; keep process fallback explicitly weaker |
| JSON Schema contracts | Language-neutral shared boundary for evidence, sharing and role data | Schema/model duplication can drift; contract tests must catch it |
| SHA-256 hash chain | Simple local tamper-evidence for ordered append-only facts | Does not establish truth of original assessment and cannot detect a truncated tail without signed external anchoring |
| AI provider behind a port | Keeps demo available offline and avoids locking the domain layer to one vendor | AI output can vary, cost money and require privacy review; deterministic tests use stub |

## 10. Proposed future evolution (only when requirements justify it)

1. **Hosted, multiple operators or concurrent writes:** evaluate PostgreSQL with migrations, role separation, backup/restore and ledger hardening. Keep repository ports and module ownership stable.
2. **Runner privilege separation:** move Docker access to a narrow runner service/process so the API process does not hold the Docker control socket/pipe. Keep the runner request schema closed.
3. **Multiple API instances:** use shared session storage, concurrency-safe database/queue semantics and distributed rate limiting before horizontal scaling.
4. **Reliable recording retention:** schedule purge as a managed job and add retention/deletion evidence, encrypted storage and access audit.
5. **External integrity anchoring:** periodically sign/publish chain heads to independent storage if detection of ledger-tail deletion is required.
6. **Production authentication:** connect an identity provider only after roles, invitation/admin assignment, account recovery, session lifecycle and privacy requirements are defined.
7. **Observability:** add metrics/traces with privacy-safe dimensions, operational alerts and error budgets; never use learner speed or integrity heuristics as employee-ranking signals.
8. **Contract/client generation:** generate TypeScript client types from canonical schemas or OpenAPI after resolving schema-to-Pydantic mapping and API versioning policy.

These are recommendations, not claims that the features exist or approval to introduce them.

## 11. Current limitations and non-claims

- Crucible is not a full LMS; it demonstrates a proof-of-skill workflow.
- Real Nyeras/NxtMove systems are not integrated; data are simulated/synthetic.
- Experimental profile estimates do not predict hiring outcomes or prove professional competence.
- A ledger receipt confirms internal record consistency, not fairness, authorship or job performance.
- Integrity flags are advisory signals for human review and never automatic misconduct findings.
- The current implementation is local/demo scale, not high availability or a production employment decision system.
- Database encryption at rest, production rate limiting, managed secrets, external chain-head signing, and scheduled recording purge are not fully delivered.
- Browser APIs have not all been validated in real supported browsers/devices.
- Independent security/quality review status is shown in build logs and may remain pending.

## 12. Related project documents

- [High-level system design](high-level-system-design.md)
- [System architecture diagram](crucible-high-level-system-design.svg)
- `delivery/decisions/adr/ADR-0001-stack.md` — proposed stack selection and alternatives
- `delivery/decisions/adr/ADR-0002-three-systems.md` — proposed modular-monolith/deployment decision
- `delivery/decisions/adr/ADR-0003-os-level-sandbox.md` — proposed isolation architecture
- `delivery/G3-solution-design/architecture-overview.md` — module map, data ownership and contracts
- `delivery/G3-solution-design/ux-flows.md` — role journeys and UX rules
- `delivery/G3-solution-design/dependency-register.md` — dependencies and approval state
- `delivery/G5-build-log/build-log.md` — implementation evidence, deviations and known gaps
