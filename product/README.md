# product/ - The System (Modular Monolith)

**Locked** until G3 (Solution Design) and G4 (Delivery Plan) are `approved` in `delivery/state/lifecycle-state.yaml`.
A hook blocks writes here otherwise (this README is exempt).

```
product/
├─ shared-kernel/        cross-cutting primitives only (ids, time, result/error types) - no business logic
├─ modules/
│  └─ <capability>/      one bounded context per business capability
│     ├─ domain/         entities, value objects, domain services - no I/O, no frameworks
│     ├─ application/    use cases, ports (interfaces), orchestration
│     ├─ infrastructure/ adapters: persistence, HTTP clients, queues
│     ├─ api/            the ONLY surface other modules may use (facade, DTOs, events)
│     ├─ tests/          unit + contract tests
│     └─ MODULE.md       responsibility, public surface, dependencies, data owned
├─ entrypoints/          composition roots: http-api/, worker/, cli/ - wiring and transport only
├─ architecture-tests/   fitness functions that fail the build on boundary violations
└─ tests/                e2e/, contract/, performance/ cross-module suites
```

Create modules with `python platform/scripts/scaffold_module.py <name> "<responsibility>"`.
Rules: `.claude/rules/product-modules.md`, `api-contracts.md`, `testing.md`, `security.md`, `data-persistence.md`.
Architecture tests are specified in `governance/policies/architecture-fitness-functions.md` and implemented here once the stack is chosen.
The technology stack is chosen at G3 through ADRs; nothing here assumes one.
