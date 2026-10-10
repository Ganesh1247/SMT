# Architecture Fitness Functions (specification)

Implemented in `product/architecture-tests/` once the stack is chosen at G3 (tooling recorded in an ADR, wired into `platform/ci/` and `platform/quality-commands.json`). They must pass before any slice is accepted.

The tests fail the build when:

1. A module imports another module's `domain/`, `application/` or `infrastructure/` (only `api/` is allowed).
2. `domain/` imports from `application/`, `infrastructure/`, `api/`, a framework or an I/O library.
3. A module is named `utils`, `common`, `helpers`, `misc` or `shared`.
4. `shared-kernel/` imports from any module.
5. A cycle exists in the module dependency graph.
6. `entrypoints/` imports a module's `domain/` directly instead of its `api/`.
7. A module accesses another module's database tables.

Pre-commit protection: `.claude/hooks/enforce_module_boundaries.py` blocks the most direct violations (1) at edit time for agent writes.
