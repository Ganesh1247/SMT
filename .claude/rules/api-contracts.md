---
paths:
  - "product/modules/*/api/**"
  - "product/entrypoints/**"
---
# API and Module Contract Rules

- A module's `api/` is its only public contract: facade functions/services, DTOs, events. Internal types never leak.
- DTOs are immutable, versioned where external, and independent of domain entities.
- Backward compatibility: additive changes only within a version; breaking changes need a new version and an ADR.
- Every `api/` member has a contract test and documented preconditions, postconditions and error cases.
- Errors are typed and stable (code, message, details); no stack traces or internals in responses.
- HTTP/external APIs: resource-oriented naming, correct status codes, idempotency for retriable writes, pagination for lists, request size limits, rate limits.
- Events: past-tense names, include id, timestamp, version; consumers must tolerate unknown fields.
- Document each contract in `MODULE.md` and, for external APIs, in an OpenAPI/equivalent spec checked in under the module.
