---
name: conduct-retrospective
description: Run an evidence-based retrospective after G5, G7, G8 or an incident - metrics, lessons, and change proposals for the workspace. Use to feed continuous improvement.
---
# Conduct Retrospective

Owner: `process-improvement-engineer`. Template: `platform/templates/retrospective.md`. Output: `kaizen/retrospectives/RETRO-<date>-<scope>.md`.

## Steps
1. Gather data: gate-log (cycle time per gate), rework counts, audit reports (what failed and why), build-log (review findings), escalations, defects and incidents.
2. Compute metrics into `kaizen/metrics.md`: gate cycle time, first-pass audit rate, rework per gate, defects by stage found vs escaped, escalation count.
3. Identify the top 3 problems by impact; for each give evidence and root cause (5 whys).
4. Record lessons in `kaizen/lessons-register.md` (ID, context, lesson, action, status).
5. For each fixable process problem, write `kaizen/change-proposals/CP-NNNN-<slug>.md` with exact proposed edits, expected effect, risk, rollback.
6. Chief of Staff presents proposals to the Founder; apply only the approved ones, then log the change in `kaizen/lessons-register.md`.
