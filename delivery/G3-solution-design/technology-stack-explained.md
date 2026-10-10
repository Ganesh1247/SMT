<!-- STATUS: DRAFT -->
# Crucible Technology Stack — Explained by Layer

> **Audience:** Product owners, designers, hackathon judges and engineers who need to understand what each technical term means, which technology Crucible uses, why it is there, and how the parts connect.
>
> **Status note:** This document describes the repository and its recorded build notes. Proposed technologies are identified as proposed. Crucible is a working name; Nyeras/NxtMove are simulated and demo data are synthetic.

## 1. The short version

Crucible is a web application. A learner, recruiter, reviewer or auditor opens it in a browser. The **frontend** displays pages and collects actions. It sends requests through an **API** to the **backend**, which checks identity and permissions, applies the business rules, calls the code runner or AI adapter when needed, and reads or writes the correct **database**. The runner returns bounded task results. The backend stores assessment evidence and can later return only the evidence a learner has agreed to share.

```text
Person
  ↓ uses
Frontend (React + TypeScript, built by Vite)
  ↓ sends HTTPS/JSON requests to
API (routes and validates requests)
  ↓ handled by
Backend (Python + FastAPI, identity, assessment, review, HR modules)
  ├── Database (SQLite files owned by modules)
  ├── Isolated runner (Docker container or explicitly labelled fallback)
  └── Optional AI / LLM provider (stub works offline; Anthropic adapter is optional)
```

## 2. What each term means

| Term | Plain-language meaning | Crucible example |
|---|---|---|
| Frontend | The part people see and use in a web browser | Learner task page, role setup page and reviewer case page |
| Backend | The server-side application that owns rules, permissions and operations | Python modules that create attempts, evaluate answers, record evidence and enforce sharing grants |
| API | The defined doorway through which the frontend or one module asks another to do something | `POST /api/attempts`, `GET /api/me/progress`, recruiter evidence query |
| Database | Durable structured storage used after a request ends | SQLite files for identity, attempts, ledger, review, HR and integrity data |
| Algorithm | A precise set of steps/rules that turns input into an output | Hidden tests, level pass rules, score gate, hash-chain verification, competency coverage calculation |
| AI | A broad term for software that performs tasks associated with reasoning or generation | Crucible's optional rubric-guided feedback and Level 4 interview evaluation |
| LLM | Large language model: a type of AI trained to process and generate language | Optional Anthropic model adapter for feedback; deterministic stub is used when offline |
| SDK/library | Reusable code maintained by others that the application imports | React, FastAPI, Pydantic, HTTPX, CodeMirror |
| Framework | A library that provides the structure and calls application code at known points | FastAPI routes and React component lifecycle |
| Runtime | The environment/language engine that executes the application | Python runs the backend; a browser's JavaScript engine runs the frontend |
| Hosting/deployment | Where the application processes run and how users reach them | Current design is local/demo scale; production hosting is not established |

## 3. Frontend: the user-facing application

### Technologies and their jobs

| Technology | What it is | What Crucible uses it for |
|---|---|---|
| React 18 | JavaScript UI library | Build reusable screens: sign-in, My Path, task workspace, results, profile, sharing, appeals, reviewer queue and recruiter portal |
| TypeScript 5 | JavaScript with compile-time types | Catch mistakes in page data, API results, component props and state before the browser runs the app |
| Vite 8 | Frontend development server and build tool | Fast local development, `/api` proxy during development, and creation of optimized static browser assets for a demo build |
| React Router 7 | Client-side navigation library | Move between role-specific pages without a full page reload; route guards provide a user-friendly access boundary |
| CodeMirror 6 | Browser code-editor component | Let learners write Python or SQL with syntax-aware editing; a plain text fallback supports simpler environments |
| React Testing Library | UI test helpers | Tests pages through user-visible actions rather than implementation internals |
| Vitest + jsdom | Test runner and simulated DOM | Run component and frontend logic tests in the development environment |
| axe-core | Automated accessibility checker | Detect selected accessibility issues in tested screens |

### What the frontend does

- Renders role-specific pages and navigation.
- Shows task instructions, rubrics, code editor, feedback and progression.
- Requests consent before Level 4 camera, microphone, screen recording or integrity-event capture.
- Displays captions/transcripts and typed alternatives where supported.
- Lets the learner preview and control sharing grants.
- Shows recruiter role criteria, coverage, gaps and evidence details.
- Shows reviewers the queue and case context; shows auditors ledger verification.
- Sends user actions to the API and displays success, validation and recoverable error states.

### What the frontend must not be trusted to do

Frontend controls are not security controls. A user can modify browser code or call endpoints without using the UI. Therefore:

- The browser may hide routes for usability, but the backend checks the role again.
- The browser never decides that a learner is authorized to see another learner's data.
- The browser never receives hidden answers, API secrets, signing secrets or unrestricted database access.
- The browser may ask to start a recording, but the backend verifies recorded consent and attempt ownership.

### Build/runtime distinction

Vite runs the frontend during development and bundles the app for use. The built frontend is static files (HTML, CSS and JavaScript). A browser downloads those files and runs the interface. In the current demo design, FastAPI can serve the built `web/dist` directory; a separate static host is also possible later.

## 4. Backend: rules, workflows and protected operations

### Technologies

| Technology | What it is | Crucible use |
|---|---|---|
| Python | Backend programming language | Business workflows, assessment rules, persistence adapters, evidence hashing and runner orchestration |
| FastAPI | Python web/API framework | Registers HTTP routes, dependencies and request handling; composes module routers under `/api` |
| Uvicorn | ASGI web server | Runs the FastAPI application and accepts browser/API traffic |
| Pydantic 2 | Python data-validation library | Validates typed request data at HTTP boundaries and produces predictable error handling |
| Starlette | ASGI toolkit used by FastAPI | Middleware, static-file serving and lower-level request/response handling |
| HTTPX | Python HTTP client and test transport | Tests API calls and is used by the optional Anthropic provider adapter |

### Backend responsibilities

1. Authenticate the user using the server-side session.
2. Determine role from trusted server state, never from a role string supplied by the browser.
3. Authorize access to an attempt, appeal, role, share grant or evidence item.
4. Apply the relevant product rules (level order, retry policy, score gate, consent, grant expiry, reviewer decision rules).
5. Call other modules through public interfaces, the runner through its narrow API, and the AI provider only when configured.
6. Store state in the module that owns it.
7. Return a response with the minimum information needed by the caller.
8. Log operational events without logging passwords, session tokens, private answers or unnecessary personal data.

### Backend modules in this project

| Module | Business responsibility |
|---|---|
| `identity` | Accounts, password hashes, sessions, roles, learner IDs and recruiter aliases |
| `assessment` | Attempts, task progression, answers, level checks, retry variants and result workflow |
| `runner` | Executes registered learner task code under limits and returns bounded output |
| `intelligence` | Defines AI feedback provider boundary, offline stub and optional real provider |
| `interview` | Level 4 interview prompts, turns, follow-up and evaluation handoff |
| `integrity` | Consent records, prechecks, session events, recording chunks and review-only flags |
| `evidence` | Append-only, hash-chained evidence and verification |
| `scoring` | Gated competency estimates and uncertainty ranges |
| `review` | Appeals, human review cases/decisions, learner grants and shared-evidence query |
| `hr` | Versioned role requirements, competency coverage/gaps and evidence inspection |

### Module design: why `api/` matters

Each module has a public `api/` boundary. Other modules should call that interface instead of reaching into its database tables or private business logic. This gives the project a modular-monolith shape: one main application can run locally, while internal responsibilities remain separated. It also keeps a future move to separate processes possible, but that split is not a current deployment claim.

## 5. API: the connection contract

An API is the agreed set of operations and data shapes that one software part can use to request work from another. In a web application, an HTTP API commonly uses URLs, methods, JSON bodies and status codes.

### Crucible HTTP API examples

| Example | Meaning |
|---|---|
| `GET /api/me` | Return the authenticated user's role and safe profile details |
| `GET /api/me/progress` | Return the learner's path and level progress |
| `POST /api/attempts` | Create or resume an assessment attempt |
| `POST /api/attempts/{id}/submit-item` | Submit a learner response for the owned attempt |
| `POST /api/me/grants` | Create a learner-controlled evidence-sharing grant |
| `DELETE /api/me/grants/{id}` | Revoke a grant |
| `GET /api/hr/roles` | List roles belonging to the authenticated recruiter organisation |
| `POST /api/shared-evidence/query` (through the review/consent service interface) | Return only evidence allowed by the active share grant |
| `GET /api/audit/ledger/verify` | Verify the evidence ledger's chain integrity for an authorized reviewer/auditor |

Exact endpoint lists are defined in module `MODULE.md` files and may evolve. Do not rely on an endpoint example here as a complete API specification.

### Request lifecycle

```text
Browser request
  -> HTTP middleware (origin, size, security headers)
  -> authentication/session lookup
  -> role + ownership authorization
  -> request validation (Pydantic; JSON Schema where contractual)
  -> route calls owning module facade
  -> business rules + ports + storage/runner/provider as needed
  -> normalized JSON success or error response
```

### API-related terms

- **HTTP:** the request/response protocol used between browser and server.
- **JSON:** a text format for structured API data.
- **Route/endpoint:** a specific API address and method, such as `GET /api/me`.
- **Request body:** data sent to the server, such as an answer or role definition.
- **Response:** result returned by the server.
- **Status code:** general HTTP result (for example, success, not found, validation problem).
- **Middleware:** shared request handling that runs before/after route logic, e.g. origin checks or size limits.
- **Authentication:** who the user is.
- **Authorization:** what that authenticated user may do.
- **Contract/schema:** rules that specify which fields and values are allowed in shared API data.

### API technologies in Crucible

- FastAPI defines routers and route dependencies.
- Pydantic validates API inputs and typed application data.
- JSON Schema validates versioned payloads shared between contexts.
- HTTPX supports outbound provider calls and test clients/transports.
- The browser uses JSON requests through the configured same-origin `/api` path or Vite's development proxy.

## 6. Data and database: what persists

### What a database does

A database stores information so it remains available after a request or application restart. It supports safe lookup and updates according to defined rules. The database does not decide product policy by itself; application code decides whether a user is allowed to request a change, and storage code persists that change.

### Crucible storage technology

The current implementation uses SQLite, accessed with Python's standard-library `sqlite3` in several modules. SQLite is an embedded database: the data are stored in local files and no separate database server is required. The files are separated by ownership/context in the current demo.

| Information | Current owner | Example storage |
|---|---|---|
| User account and session | Identity | `identity.db` |
| Attempt, progress and answer state | Assessment | `assessment.db` |
| Evidence chain | Evidence | `evidence.db` |
| Estimate projection | Scoring | scoring module store |
| Review case, appeal, grant/access information | Review | `review.sqlite3` |
| Role requirements | HR | `hr.sqlite3` |
| Consent, events, media metadata and fingerprints | Integrity | `integrity.db` and recording folder |
| Recording bytes | Integrity | `DATA_DIR/recordings/` |

Names may be configured or updated in code. The important architectural rule is that the owning module writes its data. The learner answer store and evidence ledger have different jobs: the assessment store supports the learner workflow; the ledger stores tamper-evident facts about results and their provenance.

### SQLite, SQLAlchemy and PostgreSQL: do not confuse them

- **SQLite** is the database engine actually used by the current module stores.
- **`sqlite3`** is Python's built-in library for connecting to SQLite; current modules such as review, HR and integrity explicitly use it.
- **SQLAlchemy** is an object-relational mapper/database toolkit. It is declared in project metadata and appears in the proposed stack/dependency register, but not every built module uses it. Verify a particular adapter before saying that it does.
- **Alembic** is a database migration tool often used with SQLAlchemy. It appears in the proposed architecture; a finalized migration workflow is not established by the provided implementation notes.
- **PostgreSQL** is a separate database server that could be adopted if hosted operations or concurrent writing outgrow SQLite. It is not the current project database.

## 7. Algorithms: the explicit decision-making rules

An algorithm is a defined procedure. It does not have to involve machine learning or an LLM. Most important Crucible decisions should be deterministic: for the same input and same version of rules, the output should be reproducible.

| Algorithm / rule | Input | How it works | Output / purpose |
|---|---|---|---|
| Level progression state machine | Learner's level status and attempt result | Enforces the ordered path, resume/retry behavior and prerequisites | Determines which level can be started next |
| Deterministic assessment checks | Learner answer, task version, hidden tests | Runs tests/checks against a task-specific dataset; expected values stay in the trusted side | Criterion outcomes and explainable result details |
| Retry variant selection | Previous task attempts and seed history | Selects a fresh task/data variant and records attempt history | Allows practice without silently replacing past results |
| Understanding probe comparison | Probe answer and altered-data output | Compares the learner's prediction/explanation with the computed expected result | Separates “output verified” from “understanding confirmed” |
| Level 4 rubric rule | Five criterion results, each with method/confidence | Applies the currently configured rule and routes low-confidence cases for human review | Level outcome and evidence event |
| Score gate | Level outcomes and ledger verification | Updates the estimate only when configured prerequisites are satisfied and evidence is valid | Prevents an incomplete/unverified path from updating the profile |
| Estimate and uncertainty calculation | Eligible evidence by competency, age and result | Produces an experimental estimate and range under the scoring module's rule | A dated estimate with uncertainty, not a validated hiring prediction |
| Competency coverage | Role requirement plus shared evidence | Evaluates each competency against that role's threshold and evidence conditions | Met, partly met, not met or no shared evidence, with reason |
| Consent/grant filtering | Authenticated organisation, role, grant scope, expiry and requested evidence | Returns only items allowed by the active grant; applies revoke on the next query | Privacy-preserving recruiter result |
| SHA-256 hash-chain verification | Stored ledger events, hashes and previous-entry links | Recomputes canonical event hash and verifies order/link continuity | Indicates whether checked records are internally consistent |
| Integrity event summary | Events and configured weights | Produces reviewer-only neutral indicators; never changes the learner result | Helps a human decide whether context warrants review |
| Runner resource enforcement | Closed task request and configured limits | Uses OS/container controls plus engine controls to constrain runtime, memory, processes, files, network and result size | Stops task code from exceeding its execution boundary |

### Rule versus AI distinction

The level pass rules, grant checks, hash verification, hidden test comparison and recruiter coverage calculation are ordinary program logic. They produce a result from explicit conditions. They do not require an LLM.

AI is an optional component used for text-heavy criteria where a fixed test may not be enough. It must not be used to replace deterministic checks that can directly test the answer.

## 8. AI, LLM and generative AI in Crucible

### What is an LLM?

An LLM (large language model) is a machine-learning model trained on large amounts of language data to interpret and generate text. A provider hosts a model behind an API; an application sends a prompt and receives a response. An LLM can produce useful explanations, but its output can vary, be mistaken, or be influenced by poorly handled input. It is not a reliable database, rules engine or source of truth.

### Where Crucible uses AI

The backend can ask an AI provider for rubric-guided feedback on criteria that are difficult to check with exact tests, and for Level 4 interview evaluation. The provider is behind a `FeedbackProvider` interface. The module validates a structured response and labels the result as AI-assisted with a model reference and confidence information.

### AI stack components

| Component | Current choice | Purpose |
|---|---|---|
| `FeedbackProvider` port | Python interface/protocol | Keeps assessment and interview logic independent from a specific vendor |
| `StubProvider` | Deterministic local implementation | Lets demo/tests work offline and produce repeatable results; must be labelled as a stub where shown |
| Anthropic adapter | Optional HTTPX client for the Anthropic Messages API | Sends a constrained request to a configured model if credentials/model are set |
| Output parser/validator | Fixed typed/contract shape | Rejects unexpected response structures rather than silently accepting them |
| Disclosure metadata | `ai_disclosure`, method label, `model_ref`, confidence | Tells learners and reviewers which result involved AI and enables review/appeal |

### How an AI judgement should work

```text
Criterion + rubric version + relevant learner response
  -> redact/minimize unnecessary identity data
  -> mark learner response as untrusted quoted data
  -> send through configured FeedbackProvider
  -> parse/validate fixed response fields
  -> attach AI method, disclosure, model reference and confidence
  -> route low confidence / disagreement to human review
  -> record provenance in evidence
```

### AI safety boundaries

- Do not send passwords, session cookies, personal contact details or unnecessary identifiers to the provider.
- Treat submitted learner text as untrusted content, not instructions to the model or grader.
- Ask the model only for defined rubric criteria; do not ask it for a hiring decision.
- Validate the model output; malformed or incomplete responses should fail safely or use a labelled fallback.
- Disclose AI use to the learner and provide an appeal route.
- Keep provider credentials in environment/secret configuration, not in source or frontend bundles.
- Use deterministic tests with the stub; test real-provider adapter behavior with mocked HTTP responses unless an authorized, controlled provider evaluation is being run.
- A model confidence value is not proof that the output is correct, fair or calibrated.

## 9. Isolated runner: how learner code is executed

The runner is a protected execution capability, not the same thing as the LLM. Crucible sends a validated task and learner answer to the runner. The runner returns a limited result to the assessment module.

### Current runner stack

1. Assessment validates that the user owns the attempt and that the submission fits the task.
2. The runner accepts a closed request shape and registered task/dataset identifiers.
3. Runner infrastructure starts a fresh child/container. Docker is used when available.
4. Learner code receives only its task input; expected outputs and hidden checks remain with the trusted parent.
5. SQLite execution uses an in-memory database, a deny-by-default authorizer, single-statement checks, step/time limits and row/output caps. Python execution uses a restricted harness and resource controls.
6. The runner returns a bounded, structured result and an isolation-mode label.
7. Assessment compares results with hidden checks and constructs criterion-level feedback.

### Why Docker is used

Docker runs the task in a constrained Linux container with controls such as no network, read-only root filesystem, no mounted host directories, non-root user, reduced capabilities and resource caps. This provides an operating-system boundary stronger than running learner code in the same Python process. Docker is not a guarantee against every possible vulnerability; the runner and image still need maintenance and security testing.

### Fallback meaning

An explicitly configured process fallback is a different, weaker isolation mode. The build records it as `process-fallback`. If it is used, the UI/health/reporting must not claim container-level isolation. The proposed ADR prefers fail-closed container mode and a clear retry message if Docker is unavailable.

## 10. Important system terms

| Term | Explanation in project context |
|---|---|
| Modular monolith | One application/process can contain separately organized modules with strict boundaries. Current FastAPI composition is one app; modules call public facades/ports. |
| Microservice | An independently deployed process/service with network communication and its own operational lifecycle. Crucible does not currently claim Sandbox, Trust and HR are deployed as independent services. |
| Bounded context | A domain area with its own rules and data ownership, such as assessment, evidence or HR. It can live in a modular monolith. |
| Adapter | Code that connects a module to an external technology, e.g. Docker CLI or Anthropic HTTP API. |
| Port | An interface the business module needs, such as `QueryRunner` or `FeedbackProvider`; an adapter implements it. |
| Contract | Agreed structure and rules for a message exchanged at a boundary, often defined by JSON Schema. |
| Idempotency | Repeating the same request after a network error does not create a duplicate result/event. Evidence append uses idempotency keys. |
| Hash chain | Each ledger record's hash depends on the previous record, so changing an entry breaks verification from that point forward. |
| Pseudonym/alias | Identifier shown to other roles instead of a learner's name or email. Recruiter alias is recipient-specific. |
| Uncertainty range | A lower and upper bound displayed with an estimate. It represents uncertainty in the current method; it is not automatically statistically calibrated. |
| LLM provider | The service/API that hosts and runs a language model. It is optional for the offline demo path. |
| Static frontend | Built HTML/CSS/JavaScript files served to the browser; it does not directly connect to the database. |
| Middleware | Shared API processing for every request, such as origin validation, request-size limit or security headers. |
| CI | Continuous integration: automated builds/tests run on code changes. It is tooling/process, not a user-facing product module. |

## 11. Proposed versus implemented: precise statements

| Topic | Safe, accurate statement |
|---|---|
| Python version | The project metadata says Python `>=3.11`; ADR-0001 proposes Python 3.12; container test notes used Python 3.11 slim. Align before claiming a single pinned production runtime. |
| ORM/migrations | SQLAlchemy is declared and proposed; module persistence is mixed and several built modules explicitly use standard-library `sqlite3`; Alembic is proposed, not established as the migration system. |
| Deployment shape | One FastAPI composition root is built. ADR-0002's modular-monolith recommendation is proposed. Three separately deployed systems are not claimed. |
| Runner service | A runner module and Docker-per-run executor exist; current build notes say it invokes Docker CLI through the module adapter in the app process. The separate HTTP runner service in ADR-0003 is a proposed design and not the current topology. |
| AI | A deterministic stub exists; the Anthropic adapter is optional. A real provider call is not required for the demo and was not part of the recorded adapter tests. |
| Data scale | SQLite/local data is for local/demo scale. No high-availability, multi-region or production scale claim is made. |
| Scores | Results/estimates are experimental; they do not predict job performance or recommend hiring outcomes. |

## 12. End-to-end example: learner submits a SQL answer

1. **Frontend:** learner enters SQL in the React/CodeMirror editor and selects Submit.
2. **API:** browser sends an authenticated JSON request to FastAPI. Middleware checks origin and request size.
3. **Backend identity:** the session cookie resolves to a learner; the assessment module confirms the attempt belongs to that learner.
4. **Validation:** Pydantic and task rules validate request shape, task ID, current attempt state and submission size.
5. **Runner:** assessment calls the runner facade; Docker launches a fresh restricted container with a registered task dataset and the learner query.
6. **Database/engine:** the child runs SQLite against an in-memory task database under read-only and resource constraints.
7. **Algorithm:** the trusted parent runs hidden checks/comparisons and produces criterion outcomes. It does not trust a success value supplied by learner code.
8. **Optional AI:** where a criterion is qualitative, the assessment may call the configured feedback adapter. The stub works offline; a real model is optional and disclosed.
9. **Evidence:** assessment writes a versioned evidence event. The evidence module canonicalizes it, attaches an idempotency key, appends it to the SHA-256 chain and stores the result.
10. **Response:** FastAPI returns criterion feedback and next-step actions. React renders the result, AI/method labels and appeal action.
11. **Review if needed:** low confidence, conflict, appeal or integrity flag may create a reviewer case. Only the human reviewer can record a review decision; integrity flags never auto-fail.

## 13. Quick answer for a presentation

> “Crucible uses a React and TypeScript web interface, a Python/FastAPI backend, and SQLite stores owned by the application modules. The API is the secured doorway between browser and backend. A dedicated runner boundary executes learner code in a limited Docker container, and an optional LLM adapter can assist with rubric-based language feedback. Deterministic tests and business rules remain the main source of assessment decisions. Evidence is stored in a SHA-256-linked ledger, and recruiters only receive evidence a learner has explicitly shared. The current implementation is a local/demo-scale modular application, and the stack/deployment ADRs are still proposed.”

## 14. Source references

- `product/pyproject.toml` and `product/entrypoints/web/package.json` — declared frontend/backend packages.
- `product/entrypoints/http-api/README.md`, `config.py`, `main.py` — API startup, configuration and middleware.
- `product/modules/*/MODULE.md` — module responsibilities, public surfaces, data and limitations.
- `delivery/decisions/adr/ADR-0001-stack.md` — proposed stack and alternatives.
- `delivery/decisions/adr/ADR-0002-three-systems.md` — deployment alternatives and proposed modular monolith baseline.
- `delivery/decisions/adr/ADR-0003-os-level-sandbox.md` — proposed OS-level runner architecture.
- `delivery/G3-solution-design/contracts/` — JSON Schema contracts and hash canonicalization.
- `delivery/G3-solution-design/dependency-register.md` — library versions, purposes and approval states.
- `delivery/G5-build-log/build-log.md` — build evidence, test outcomes, deviations and open verification work.
