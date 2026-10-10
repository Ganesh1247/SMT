---
name: review-change
description: Independent code review of a slice's diff against acceptance criteria, module boundaries, security and maintainability, ending in a verdict recorded in the build log. Use after quality verification of a slice.
---
# Review Change

Reviewer: `staff-code-reviewer` (never the author).

## Checklist
1. **Correctness** - behaviour matches acceptance criteria; edge cases and error paths handled.
2. **Architecture** - stays within the module; only other modules' `api/` used; layering respected; fitness tests pass.
3. **Contracts** - public API changes are intentional, versioned and covered by contract tests.
4. **Security** - input validated at boundaries, authZ enforced, no injection, no secrets, safe logging.
5. **Tests** - assert behaviour, cover negatives, are deterministic; not coverage padding.
6. **Simplicity** - no speculative generality; names are clear; comments explain why.
7. **Dependencies** - any addition has a register entry and approval.
8. **Accessibility** (UI) - semantic markup, keyboard, labels, contrast.

## Output
In the slice's build-log entry, fill "Review": findings (BLOCKER/MAJOR/MINOR/NIT with file:line and fix), verdict APPROVE | APPROVE_WITH_CONDITIONS | REQUEST_CHANGES, date.
