---
name: triage-request
description: Classify any incoming Founder request, map it to roles, skills, gate impact and artifact relationships, and produce a short execution plan. The orchestrator's first move on every prompt, especially when the router reports unmatched, multi-intent or ambiguous requests.
---
# Triage Request

Every prompt arrives with a `[route]` line from the router hook. Confirm or correct it in one line, then plan.

## Steps
1. **Classify** - intent from `governance/routing/routing-table.txt` (use the hook's suggestion; if `unmatched` or two intents tie, decide from the request itself).
2. **Check preconditions** - current gate and gate lock (from the brief). If the request needs work beyond the current gate (for example implementation before G3/G4), route to the earliest missing gate and say so.
3. **Relationships** - for any change to an existing artifact run `python platform/scripts/trace.py impact <artifact>`; for requirement questions `trace.py req REQ-###` or `matrix`. List downstream artifacts and gates that must be revisited.
4. **Plan** - roles in handoff order, skills per role, artifacts to write, verification roles (never the author), approvals needed from the Founder. Parallelise independent work.
5. **Execute via `orchestrate-lifecycle`.** Keep the chat update to: intent, gate, roles, next action, blockers.
6. **Learn** - if the route was wrong or the request type recurs, run `python platform/scripts/improve.py learn "<phrase>" <intent>`. If no intent fits and it will recur, propose a new intent via `self-improve`.
7. **Remember** - `capture-memory` for decisions, constraints or preferences revealed; write the handoff.

## Ambiguity rule
Ask the Founder only when the answer changes scope, architecture or cost. Otherwise choose the sensible default, state it in one line, and proceed.
