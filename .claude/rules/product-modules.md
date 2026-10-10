---
paths:
  - "product/**"
---
# Modular Monolith Rules

- One deployable unit; modules under `product/modules/<capability>/` with layers `domain/`, `application/`, `infrastructure/`, `api/`, `tests/`.
- **Dependency direction:** `api -> application -> domain`; `infrastructure -> application/domain`. `domain` imports nothing from other layers, frameworks or I/O.
- **Cross-module access only through the other module's `api/`.** Never import another module's domain, application or infrastructure. A hook blocks this; `product/architecture-tests/` verifies it in CI.
- No shared database tables across modules: each module owns its data; others read it via `api/` or events.
- Prefer in-process events (published from `api/`) for decoupling; keep payloads versioned.
- `shared-kernel/` holds only primitives (ids, money, time, result types, error base classes). Never business logic.
- Module names are business capabilities. No `utils`, `common`, `helpers`, `misc`.
- Every module keeps `MODULE.md` current: responsibility, public surface, dependencies, data owned, events.
- Entrypoints (`entrypoints/`) are composition roots only: wiring, config, transport. No business logic.
- Distribution (extracting a module to a service) requires an ADR with evidence.
