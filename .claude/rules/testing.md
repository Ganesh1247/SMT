---
paths:
  - "product/**"
  - "platform/**"
---
# Testing Rules

- Test first. A failing test must exist before production code for a behaviour.
- Pyramid: many fast unit tests (domain/application), contract tests at each module `api/`, few end-to-end tests on critical journeys.
- Tests assert behaviour and outcomes, not implementation details. One reason to fail per test; descriptive names (`should_<result>_when_<condition>`).
- Deterministic: no wall-clock, randomness or network without injection/fakes. No test order dependence.
- Cover negatives: invalid input, boundary values, permission denial, failures of dependencies, concurrency where relevant.
- Each PRD acceptance criterion has at least one test referencing its `REQ-###` in the name or comment.
- Never delete or weaken a failing test to pass a build; fix the cause or escalate.
- Record evidence: command, summary of results and date in the build-log entry.
- Architecture fitness tests in `product/architecture-tests/` must pass before any slice is accepted.
