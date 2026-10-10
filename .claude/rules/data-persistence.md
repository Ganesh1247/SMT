---
paths:
  - "product/modules/*/infrastructure/**"
  - "product/**/migrations/**"
---
# Data and Persistence Rules

- Each module owns its schema/tables; no cross-module joins or foreign keys. Share data via `api/` or events.
- Schema changes are versioned migrations: forward and rollback tested; backward-compatible deploys (expand -> migrate -> contract).
- Repositories implement application-layer ports; domain code never touches the database.
- Transactions are scoped to a single use case within one module; cross-module consistency via events/sagas (eventual consistency documented).
- Index for the queries actually used; justify with a query plan for anything performance-critical.
- Personal/sensitive data is classified, minimised, encrypted where required, with a retention and deletion path.
- Seed/fixture data contains no real personal data or secrets.
- Back up and restore procedures are documented in the runbook and tested.
