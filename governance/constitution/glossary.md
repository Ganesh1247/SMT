# Glossary

| Term | Meaning |
|---|---|
| Founder | The human user; final approver of gates, scope, architecture and process changes |
| Chief of Staff | The main Claude session acting as orchestrator; routes work, never approves gates |
| Gate | A checkpoint (G0–G8) with entry criteria, required artifacts, exit criteria and an approver |
| Artifact | A document or evidence file produced at a gate, kept under `delivery/` |
| Slice | The smallest vertical unit of deliverable, testable behaviour |
| Module | A bounded context under `product/modules/` exposing only its `api/` surface |
| Shared kernel | Minimal cross-cutting primitives in `product/shared-kernel/` |
| ADR | Architecture Decision Record in `delivery/decisions/adr/` |
| Escalation | A cross-role conflict recorded for the Founder to resolve |
| Profile | An overlay in `profiles/` that reweights or compresses the lifecycle for a context |
| Fitness function | An automated architecture test that fails the build on a boundary violation |
| Rework loop | A gate fail → fix → re-audit cycle; capped by `rework_limit` |
