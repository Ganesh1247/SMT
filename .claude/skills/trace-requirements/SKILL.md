---
name: trace-requirements
description: Identify relationships and change impact across artifacts - requirement coverage matrix, where a REQ appears, planned vs built slices, orphan IDs, and which approved gates must re-open when an artifact changes. Use for traceability questions, scope changes and before any gate audit.
---
# Trace Requirements

Backed by `python platform/scripts/trace.py` (stdlib; scans `REQ-###`, `SLICE-###`). Map: `governance/routing/relationship-map.md`.

| Question | Command |
|---|---|
| Is every requirement covered end to end? | `trace.py matrix` |
| Where is REQ-007 mentioned? | `trace.py req REQ-007` |
| What is planned but not built? | `trace.py slices` |
| What breaks if the PRD / architecture changes? | `trace.py impact prd` (or `arch`, `ux`, `plan`, ...) |
| Any dangling references? | `trace.py orphans` |

## Use
- **Before each gate audit:** run `matrix`, `slices`, `orphans`; include results in the audit report. Gaps on Must requirements are FAIL conditions.
- **On any change request:** run `impact <artifact>`; present the affected artifacts and the approved gates to re-open; get Founder approval; record the change in the PRD change log and the gate log; re-open gates in the state file; re-audit.
- **Report format:** counts first (covered / total, gaps), then the specific gaps with owners from the relationship map.
