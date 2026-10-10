---
paths:
  - "delivery/**"
  - "governance/**"
  - "kaizen/**"
  - "profiles/**"
---
# Documentation Rules

- Every artifact starts with `<!-- STATUS: TEMPLATE | DRAFT | FINAL -->` on line 1. Create from `platform/templates/`.
- Only the owning role sets DRAFT; an independent reviewer sets FINAL. FINAL artifacts are changed only through a recorded change note.
- State facts with sources; mark assumptions explicitly; list open questions in a dedicated section.
- Use stable IDs: `REQ-###`, `SLICE-###`, `ADR-####`, `ESC-####`, `CP-####`, `RETRO-<date>`. Reference them instead of copying text.
- Keep documents short and scannable: purpose first, decisions before details, tables for comparisons.
- Never put secrets or personal data in documents.
- Update the gate log whenever a gate event occurs.
