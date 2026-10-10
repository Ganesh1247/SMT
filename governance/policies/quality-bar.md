# Quality Bar

| Dimension | Minimum |
|---|---|
| Requirements traceability | Every PRD requirement ID maps to ≥1 test or measurable check |
| Test pyramid | Unit tests per module; contract tests at every module `api/`; few end-to-end tests on critical journeys |
| Coverage | Targets set in test-strategy (default: domain/application ≥ 80% line coverage; critical paths 100% branch) |
| Architecture | Fitness functions in `product/architecture-tests/` pass; zero cross-module internal imports |
| Accessibility | WCAG 2.1 AA criteria in ux-flows verified for UI slices |
| Performance | Budgets defined in success-metrics; measured at G6 |
| Reliability | Health checks, structured logs and alerts defined before G7 |
| Documentation | README per module (`MODULE.md`), runbook before G8 |
| Static analysis | Lint, format and type checks clean (commands in `platform/quality-commands.json`) |
