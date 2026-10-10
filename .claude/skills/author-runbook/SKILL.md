---
name: author-runbook
description: Write an operational runbook - start/stop, deploy, rollback, backup/restore, health checks, alerts, incident response and escalation. Use at G8.
---
# Author Runbook

Owner: `platform-engineer`; polish by `technical-writer`. Template: `platform/templates/runbook.md`. Output: `delivery/G8-operations/runbook.md`.

## Sections
1. System overview and dependency map (modules, data stores, external services).
2. Environments and configuration (variables only, no secret values).
3. Routine operations: start/stop, deploy, rollback, scaling, backup and restore with verification steps.
4. Monitoring: SLIs/SLOs, dashboards, alerts with thresholds and first response for each.
5. Incident response: severity levels, roles, communication, triage steps, common failure modes with diagnosis and fix commands.
6. Escalation contacts and decision rights (Founder for destructive actions).
7. Post-incident: timeline, blameless review, lessons into `kaizen/`.

Every procedure must be copy-pasteable and tested at least once; record the date tested.
