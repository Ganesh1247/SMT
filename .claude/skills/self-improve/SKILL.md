---
name: self-improve
description: Run the continuous-improvement loop - analyze telemetry, audits and lessons into ranked signals, draft and review change proposals, apply Founder-approved changes to rules, agents, skills, routing and gates, and measure the effect. Use after each gate close, round, release or incident, when the brief reports new signals, or when the Founder asks to improve, refine or evolve the system.
---
# Self-Improve

Owner: `process-improvement-engineer`; applied by the Chief of Staff; decided by the Founder.

## Loop (MEASURE -> LEARN -> PROPOSE -> DECIDE -> APPLY -> VERIFY)
1. **Measure:** `python platform/scripts/improve.py analyze` (reads telemetry: routes, unmatched prompts, hook blocks, rework). Also read the last retrospective, `kaizen/lessons-register.md` and recent gate audits for qualitative signals.
2. **Learn (auto, low-risk):** for unmatched or misrouted prompts, teach the router: `improve.py learn "<phrase>" <intent>`. These go to `kaizen/learned-routing.txt` and are reversible with `unlearn`.
3. **Propose:** auto-drafted proposals appear in `kaizen/change-proposals/` (`Status: PROPOSED`). Add proposals for qualitative findings (a new skill, a sharper agent prompt, a new intent, a template field, a gate criterion). Each is one problem, exact files and diff, expected measurable effect, risk, rollback. Prefer the smallest change; merge repeated lessons into one.
4. **Decide:** present the ranked list to the Founder (impact / effort, 1-2 lines each). The Founder approves, rejects or defers: `improve.py resolve CP-NNNN approved|rejected|deferred`.
5. **Apply:** the Chief of Staff makes only the approved edits (agents, skills, rules, routing, gates, templates), then `improve.py resolve CP-NNNN applied`. Record the rationale with `capture-memory` (type decision or lesson) and note it in the gate log.
6. **Verify:** next cycle compare the metric the proposal targeted (fewer unmatched prompts, fewer blocks, lower rework, higher first-pass audit rate). If it did not help, revert via version history and record the lesson.
7. **Compact:** run `compact-memory`; re-run `analyze` to reset the signal baseline.

## Creating new capabilities
When a recurring need has no role or skill, propose it: a new skill (`.claude/skills/<verb-noun>/SKILL.md`), a new agent in the right tier, a new intent in the routing table, or a new profile. Include the trigger phrases, owner role, inputs/outputs per `governance/contracts/handoff-contracts.md`, and tool scope (least privilege).

## Guardrails
- Never edit `.claude/`, `governance/` or `profiles/` without an approved proposal. Never weaken constitution rules 1-10 or the gate lock.
- Auto-applied changes are limited to learned routing phrases and memory housekeeping.
- Keep every change small, reversible and measured.
