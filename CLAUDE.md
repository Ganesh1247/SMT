# SMT Engineering Workspace — Constitution

A stage-gated, role-separated product-engineering system. Nothing is built until it is
researched, defined, designed and planned, and every gate is audited and approved by the Founder.

## Operating model
- **Founder** (the user) is the final approver of every gate and every scope/architecture change.
- **Chief of Staff** = the main session. It runs the `orchestrate-lifecycle` skill, dispatches
  specialist agents, and never approves its own gates. Subagents cannot spawn subagents, so all
  delegation flows through the Chief of Staff.
- **Specialist agents** live in `.claude/agents/<tier>/`. Each owns specific artifacts and has
  scoped tools. Roster and decision rights: `governance/org/`.
- **State** is machine-readable: `delivery/state/lifecycle-state.yaml`. Read it first, every session.

## Lifecycle
`G0 Intake → G1 Discovery → G2 Product Definition → G3 Solution Design → G4 Delivery Plan →
G5 Build → G6 Assurance Audit → G7 Release → G8 Operate → Retrospective`
Gate definitions: `governance/gates/`. Artifacts: `delivery/<gate>/`. Templates: `platform/templates/`.

## Hard rules (enforced by hooks where possible)
1. No file under `product/` is written before G3 and G4 are `approved` in the state file.
2. The author of an artifact never reviews it. Developers → quality-engineer → staff-code-reviewer → compliance-auditor.
3. Only the Chief of Staff edits `lifecycle-state.yaml`, and only after the Founder explicitly approves a gate in chat.
4. `reference/` is read-only source material. Never edit it.
5. Evidence over claims: every requirement maps to a test or measurable check; never present a mock-up as working.
6. Every significant decision gets an ADR in `delivery/decisions/adr/`. Conflicts go to `delivery/decisions/escalations/`.
7. Product code is a modular monolith: modules interact only through each module's `api/` surface.
8. No secrets in files. Third-party dependencies are declared per `governance/policies/dependency-policy.md`.
9. Agents return short summaries; detail goes into artifacts on disk.
10. Rework loops are capped (see state file); then escalate to the Founder.

## Automatic routing (the main brain)
A UserPromptSubmit hook classifies every prompt (`governance/routing/routing-table.txt` + learned phrases) and injects a
`[route]` line: intent, gate, roles, skills, relationship chain. For every prompt the Chief of Staff:
1. Confirms or corrects the route in one line (`triage-request` when unmatched/ambiguous).
2. Checks the gate and lock; routes to the earliest missing gate if the request is premature.
3. Maps relationships with `platform/scripts/trace.py` (`impact`, `matrix`, `req`) before changing any approved artifact.
4. Dispatches roles in handoff order; independent verifiers check the work; the Founder approves gates.
5. Captures memory and the handoff. If the route was wrong: `improve.py learn "<phrase>" <intent>`.

## Continuous improvement
Telemetry (routes, unmatched prompts, hook blocks, rework) feeds `improve.py analyze` -> `kaizen/signals.md` and auto-drafted
change proposals. The `self-improve` skill runs the loop: measure -> learn -> propose -> Founder decides -> apply -> verify.
Learned routing phrases apply automatically; changes to `.claude/`, `governance/`, `profiles/` need an approved proposal.
Run `self-improve` after each gate close, hackathon round, release or incident, and whenever the brief shows an IMPROVE line.

## Memory and token discipline
Project memory lives in `memory/` (typed files + a capped `INDEX.md`). A SessionStart hook injects a
~500-token brief (state, handoff, memory counts), so do not re-read state files to "get oriented".
- **Recall cheaply:** `python platform/scripts/memory.py search <terms>` (one line per hit), then `show <name>` for 1-3 entries. Never read all of `memory/` or whole artifacts to find one fact (`recall-context`).
- **Capture durable, non-derivable facts** (rationale, constraints, preferences, lessons) with `capture-memory`; link to artifacts instead of copying them. Search first to avoid duplicates.
- **Handoff:** at the end of every session or gate step run `memory.py handoff write "<done / in progress / next / blockers>"`.
- **Save tokens:** grep/glob before reading; read file ranges, not whole files; subagents return <=150 words and write detail to disk; delegate bulk reading/search to a subagent; keep chat updates to gate, step, next action, blockers.
- Keep memory lean with `compact-memory` after each gate close.

## Profiles
Context overlays in `profiles/` (e.g. `hackathon-24h`) compress or reweight the lifecycle. Active
profile is set in the state file. A profile may add agents, skills and a rubric but may not weaken rules 1–10.

## Where things are
| Need | Path |
|---|---|
| Principles, Definition of Done | @governance/constitution/principles.md, @governance/constitution/definition-of-done.md |
| Who decides what | governance/org/raci-matrix.md, decision-rights.md |
| Gate criteria | governance/gates/Gn-*.yaml |
| Artifact templates | platform/templates/ |
| Validation scripts | platform/scripts/ (`validate_state.py`, `gate_check.py`, `scaffold_module.py`) |
| Lessons and metrics | kaizen/ |

## Start of every session
1. Read `delivery/state/lifecycle-state.yaml`.
2. Run `python platform/scripts/gate_check.py` for the current gate to see what is missing.
3. Continue via `orchestrate-lifecycle`.
