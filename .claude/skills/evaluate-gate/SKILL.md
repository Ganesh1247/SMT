---
name: evaluate-gate
description: Run an independent gate audit. Checks required artifacts, exit criteria and cross-artifact consistency, then writes a PASS, CONDITIONAL or FAIL audit file. Use before asking the Founder to approve any gate.
---
# Evaluate Gate

Delegate to `compliance-auditor`. Inputs: gate ID.

## Steps
1. `python platform/scripts/gate_check.py <gate>` - capture output.
2. Auditor reads `governance/gates/<gate>.yaml` and each artifact; tests every exit criterion against evidence.
3. Cross-checks: requirement IDs trace upstream/downstream; ADRs consistent with architecture; no constitution violations; open risks recorded in `delivery/state/open-risks.md`.
4. Auditor writes `delivery/G6-assurance-audit/gate-audits/AUD-<gate>-<NN>.md` from `platform/templates/audit-report.md` (for G6 itself: `audit-report.md`).
5. Chief of Staff relays the verdict; PASS or CONDITIONAL goes to the Founder; FAIL goes back to owners (rework count +1).

## Verdict rules
- **PASS**: all exit criteria met with evidence.
- **CONDITIONAL**: minor gaps; each has owner, due date and cannot involve a Must requirement or a High/Critical security finding.
- **FAIL**: any exit criterion unmet, missing evidence, or a Must requirement unverified.
