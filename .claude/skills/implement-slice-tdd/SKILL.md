---
name: implement-slice-tdd
description: Implement one approved slice test-first within module boundaries, with evidence and an independent verification chain. Use only for G5 after G3 and G4 are approved.
---
# Implement Slice (TDD)

Engineers: `backend-engineer`, `frontend-engineer`. Preconditions: G3 and G4 `approved`; slice in the delivery plan.

## Cycle
1. Read the slice, its REQ-IDs, relevant ADRs, ux-flows screens and the module's `MODULE.md`. Confirm scope; list files you expect to touch.
2. **Red**: write failing tests from the acceptance criteria (unit, plus contract test if `api/` changes).
3. **Green**: smallest code that passes. Respect layering: domain has no I/O; application orchestrates; infrastructure adapts; api exposes.
4. **Refactor**: remove duplication; keep tests green. Run the full module suite and `product/architecture-tests/`.
5. Update `MODULE.md` if the public surface changed. Add dependencies only via the dependency register.
6. Append a build-log entry (template `build-slice.md`): slice ID, files, test commands and results, deviations.
7. Hand off: `quality-engineer` verifies -> `staff-code-reviewer` reviews. Fix BLOCKER/MAJOR findings and repeat 2-6 for the fix.

## Done when
Definition of Done (governance/constitution/definition-of-done.md) for a slice is satisfied and the reviewer verdict is APPROVE.
