---
name: audit-release
description: Run the G6 end-to-end assurance audit - requirements traceability, independent test re-run, security review, performance and accessibility results - and issue the release verdict. Use after all G5 slices are done.
---
# Audit Release

## Orchestration
1. `quality-engineer` -> `delivery/G6-assurance-audit/test-report.md` (traceability matrix REQ -> test -> result; defects; coverage vs targets).
2. `security-engineer` -> `security-review.md` (OWASP Top 10, dependency audit, secret scan, config review, findings by severity).
3. `compliance-auditor` -> `audit-report.md`:
   - Re-run the test suite and architecture tests independently; compare with reported results.
   - Verify every Must requirement has passing evidence; check NFR results against success-metrics.
   - Verify no open Critical/High findings (or Founder-accepted risk in writing).
   - Verify documentation and runbook readiness for G7/G8.
   - Verdict PASS | CONDITIONAL | FAIL.
4. Chief of Staff presents to the Founder; release (G7) cannot start without G6 `approved`.
