<!-- STATUS: DRAFT -->
# ADR-0001: Technology stack for Crucible (Part A MVP)

Owner: principal-architect | Date: 2026-10-10 | Reviewer: staff-code-reviewer and security-engineer, then compliance-auditor

Inputs: delivery/G0-intake/final-solution-approach.md (DRAFT); delivery/G0-intake/curated-pitch-content.md (DRAFT); delivery/G4-delivery-plan/delivery-plan.md (D1, D3, D4, D6, R1, R3); delivery/G4-delivery-plan/implementation-plan.md; delivery/G3-solution-design/contracts/README.md and `*.schema.json`; delivery/G3-solution-design/contracts/hash-canonicalisation.md. Architecture context: delivery/G3-solution-design/architecture-overview.md.

## Status
Proposed. Blocks SLICE-001 (walking skeleton). Independent of ADR-0002: the stack below works for either deployment topology.

## Context and forces
| Force | Source | Implication for the stack |
|---|---|---|
| 24-hour build, 3 developers, one language preferred | Delivery plan D2, implementation plan section 1 | One backend language; minimal setup; no infrastructure to operate |
| Sandbox safety: learners submit free-form SQL | Delivery plan R1, SLICE-003 (risk H), assumption D1 (SQL/analytics ladder) | Engine must be in-process, read-only, time-bounded, with no file, network or extension access |
| Tamper-evident ledger with byte-exact hashing | hash-canonicalisation.md; `canonical_hash.py` uses the Python standard library only | Ledger language should run the reference implementation unchanged |
| JSON Schema 2020-12 contracts are the shared language | contracts/README.md | Backend must validate payloads against those schema files at every system boundary |
| Demo must not depend on an AI vendor | Delivery plan R3, D3 | AI provider behind a port with a deterministic stub that works offline |
| Accessible, keyboard-operable learner and recruiter UIs; no time limit on probes | NFR-004 | UI framework with good control of semantics and focus |
| Rule 8: no secrets in files; dependencies declared | CLAUDE.md, dependency policy | Keys from environment only; every library goes in the dependency register |
| Rule 7: modular monolith with `api/` surfaces | CLAUDE.md | Framework must support package-level module boundaries checkable by tooling |

## Options considered

### 1. Backend framework
| Option | Pros | Cons | Cost to reverse |
|---|---|---|---|
| **FastAPI (Python 3.12) + Pydantic v2 (chosen)** | Same language as `canonical_hash.py` and `validate_examples.py`; OpenAPI generated for frontend stubs; async not required but available; Pydantic models at the edge; team familiarity assumed | Pydantic models duplicate the JSON Schemas (mitigated: schemas stay authoritative and are validated with `jsonschema`); Python is slower than Go/Node (irrelevant at demo scale) | Medium: domain and application layers are framework-free, so only `api/` and wiring change |
| Django + DRF | Batteries included (admin, auth, ORM, migrations) | Heavier; its app model pulls toward shared ORM models across modules, which works against rule 7; slower to scaffold three thin services | High |
| Node (NestJS or Express) + TypeScript | One language across front and back end | Hash rule must be reimplemented and re-verified against the test vector; SQLite read-only authorizer support is weaker in common Node drivers | High |

### 2. Application database
| Option | Pros | Cons | Cost to reverse |
|---|---|---|---|
| **SQLite via SQLAlchemy 2 + Alembic, one database file per bounded context (chosen for MVP)** | Zero setup on demo laptops and CI; single-writer model suits the strictly sequential ledger; one file per context makes data ownership physical | No concurrent writers at scale; fewer database-level guarantees (no roles) | Low: SQLAlchemy and Alembic keep schemas portable to PostgreSQL |
| PostgreSQL 16 (one schema per context) | Real roles and grants per context; `statement_timeout`; triggers to forbid UPDATE/DELETE on the ledger; closer to production | Needs Docker or a hosted instance on every machine; setup risk inside a 24-hour window | Low |
| Document store (MongoDB etc.) | Stores contract JSON directly | No transactions across sequence allocation and append without care; new dependency class; no benefit at this scale | Medium |

Decision rule: SQLite is the MVP default. Move to PostgreSQL only if two or more processes must write the same context concurrently, or a hosted demo is required (open question Q5 in the architecture overview). Code must not use SQLite-only SQL in application repositories.

### 3. Task execution engine (learner SQL)
| Option | Pros | Cons | Cost to reverse |
|---|---|---|---|
| **Python standard-library `sqlite3`, fresh in-memory database per run, read-only (chosen)** | No new dependency; deterministic; window functions and CTEs supported; `set_authorizer` can deny every action except SELECT, READ and an allow-listed set of functions; `set_progress_handler` enforces a step budget (timeout); `PRAGMA query_only=ON`; extension loading off by default; nothing on disk to escape to | SQL dialect is SQLite, not PostgreSQL or ANSI; some analytics functions missing (for example `MEDIAN`); the engine runs in the API process, so a pathological query costs CPU until the step budget trips | Low: engine sits behind the `tasks` module `api/` as a `QueryRunner` port |
| DuckDB in-process | Richer analytics SQL; fast | New dependency; has file and network readers (`read_csv`, `httpfs`) that must be disabled (`enable_external_access=false`) and kept disabled across versions; larger escape surface to test | Low (same port) |
| PostgreSQL with a read-only role and `statement_timeout` | Realistic dialect; database-enforced permissions | Requires a server; per-learner seeded data must be loaded per run or isolated per schema; a shared server is a cross-learner leakage risk | Medium |
| Python or general code execution in a container | Supports a Python ladder | Needs a container sandbox and escape testing; SLICE-003 grows to L (delivery plan D1) | High |

Safety controls required on the chosen engine (verified in SLICE-003, see Fitness functions): new in-memory connection per execution, seeded data loaded by the server, authorizer deny-by-default, `ATTACH`, `PRAGMA` writes, `load_extension` and any write action refused, step-budget timeout, row-count and result-size caps, statement count of exactly one, and no learner text concatenated into any SQL the server builds. Fallback if unsafe or slow at H10: fixed query set, no free-form SQL (implementation plan section 10).

### 4. AI feedback provider
| Option | Pros | Cons | Cost to reverse |
|---|---|---|---|
| **Port `FeedbackProvider` in `assessment` with two adapters: `StubProvider` (deterministic, offline, always available) and one real provider adapter selected by configuration (chosen)** | Demo never depends on a vendor; provider choice (D3) can land late; invariance suite (SLICE-011) can run against the stub for repeatability and against the real provider for evidence; `model_ref` is recorded on every `ai_judged` event as the contract requires | Two code paths to test; stub output must be clearly labelled so it is never presented as real AI judgement | Low |
| Direct calls to one vendor SDK | Least code | Vendor lock-in; demo fails if network or quota fails; violates deterministic-first | Medium |
| Local open-weight model | No data leaves the machine | Hardware and setup cost; quality unknown; time risk | Medium |

Rules for every adapter: learner text is passed as delimited, untrusted data and never as instructions; output is parsed into a fixed structure (criterion, rationale, confidence) and rejected otherwise; API keys come from environment variables only; responses may be cached by input hash for demo repeatability; the label `ai_judged` plus `ai_disclosure: true` is applied by the application layer, not by the provider.

### 5. Frontend
| Option | Pros | Cons | Cost to reverse |
|---|---|---|---|
| **React 18 + TypeScript + Vite, two separate apps (`learner-ui`, `hr-ui`) (chosen)** | Separate builds make "HR portal never calls the Sandbox" a configuration fact; typed clients generated from OpenAPI; mature accessibility tooling (axe in tests) | Two build configs; JavaScript toolchain adds dependencies to declare | Medium |
| Server-rendered templates (Jinja2 + HTMX) | Fewer moving parts; good default accessibility; one language | Richer interactions (Level 4 session, band chart) are slower to build; less familiar to a frontend developer | Medium |
| Streamlit | Fastest prototype | Weak control of focus and semantics (NFR-004 risk); awkward multi-role auth; poor fit for two separate portals | High |

### 6. Supporting libraries (to be declared in the dependency register before use)
`uvicorn`, `pydantic`, `sqlalchemy`, `alembic`, `jsonschema` (contract validation; already required by `validate_examples.py`), `httpx` (service client and tests), `pytest`, `import-linter` (module boundary checks), and on the frontend `react`, `vite`, `typescript`, a test runner and `axe-core`. No library is added without a dependency-register entry (rule 8).

## Decision
Adopt FastAPI on Python 3.12, SQLAlchemy with SQLite per bounded context for the MVP (PostgreSQL-portable), the standard-library `sqlite3` engine in read-only, in-memory, time-bounded mode for learner SQL, an AI `FeedbackProvider` port with a stub adapter plus one configurable real adapter, and two React + TypeScript + Vite frontends. This is the simplest stack that satisfies the ranked quality attributes in the architecture overview: it reuses the existing standard-library hash reference implementation unchanged, adds no server to operate, keeps the sandbox engine inside a narrow, testable boundary, and keeps the demo independent of any AI vendor.

## Consequences
Positive
- One backend language; the contract validator and hash reference run unchanged in CI.
- Demo runs offline from a clean checkout.
- Every infrastructure choice sits behind a port, so swapping SQLite for PostgreSQL, or the stub for a vendor, touches `infrastructure/` only.

Negative
- Learner SQL is the SQLite dialect. Task authors must avoid functions SQLite lacks and the UI must say "SQLite SQL".
- SQLite gives no database-level roles; the ledger's append-only rule is enforced in code plus a `BEFORE UPDATE/DELETE` trigger, not by grants.
- Pydantic models and JSON Schemas can drift; the schema files win and drift is a test failure.

Follow-up work
- Dependency register entries for every library above (principal-architect, before SLICE-001).
- `platform/quality-commands.json` for this stack (pytest, import-linter, contract example validation, frontend lint and tests).
- Sandbox escape test list in the G3 threat model (security-engineer).
- D3: name the real AI provider, budget and data-handling terms (Founder).

## Fitness function / verification
| ID | Check | Where |
|---|---|---|
| FF-1 | Sandbox escape suite: write statements, `ATTACH`, `PRAGMA` writes, `load_extension`, multiple statements, recursive CTE that never ends, huge cross join; all are refused or time out within budget | SLICE-003 acceptance tests |
| FF-2 | Same seed gives identical dataset bytes; different seeds differ | SLICE-003 |
| FF-3 | `canonical_hash.py` test vector (`sha256:cd2f785f...c0d6`) is reproduced by the ledger implementation | SLICE-005 |
| FF-4 | All contract examples pass `validate_examples.py`; every inbound and outbound boundary payload is validated against the schema files | CI, every slice touching a boundary |
| FF-5 | Test suite passes with the stub provider and no network; no test calls a real AI vendor | CI |
| FF-6 | Secret scan finds no keys; configuration loads keys from environment only | CI and pre-commit hook |
| FF-7 | Accessibility checks (axe) on learner and HR pages have no serious violations | SLICE-018 |
