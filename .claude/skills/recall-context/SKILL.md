---
name: recall-context
description: Retrieve relevant prior decisions, constraints, preferences and lessons cheaply before planning or deciding. Use at the start of a gate step, before an ADR, or when the user refers to something decided earlier.
---
# Recall Context

Progressive disclosure - spend tokens only on what matters.

1. The session brief and handoff are already in context. Do not re-read them.
2. Search with specific terms (module, gate, technology, topic): `python platform/scripts/memory.py search <terms> [--type decision] [-n 8]`. Output is one line per hit.
3. Open only the 1-3 relevant memories: `python platform/scripts/memory.py show <name>`.
4. For rationale behind architecture, open the linked ADR in `delivery/decisions/adr/`; for requirements, grep `REQ-` in the PRD. Do not read whole artifacts to find one fact.
5. If recalled memory conflicts with the current repo or the Founder's latest instruction, trust the latest evidence and update/archive the stale memory via `capture-memory`.

Never dump `memory/` or whole artifacts into context.
