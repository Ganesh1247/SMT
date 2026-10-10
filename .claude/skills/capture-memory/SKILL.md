---
name: capture-memory
description: Store a durable, non-derivable fact (decision rationale, constraint, preference, lesson, external reference) or write the session handoff. Use when a decision is made, the user states a preference or constraint, a lesson is learned, or a session/gate step ends.
---
# Capture Memory

Store only what cannot be re-derived from the repo: rationale, constraints, preferences, lessons, external pointers. Never store code structure, file contents, secrets or things already in `delivery/` artifacts (link to them instead).

## Steps
1. Search first to avoid duplicates: `python platform/scripts/memory.py search <terms>`. If a match exists, add `--update` to refine it instead of creating a new one.
2. Choose the type: `decision` (why we chose X, link the ADR), `fact` (constraint or domain truth), `lesson` (what went wrong/right and the rule it implies), `preference` (how the Founder wants things done), `reference` (where to find something external).
3. Write it:
   `python platform/scripts/memory.py add --type lesson --name <kebab-slug> --desc "<one line, <=140 chars>" --scope <project|gate:G3|module:x> --body "<=30 lines"`
   Body for decisions/lessons/preferences: the fact, then `**Why:**` and `**How to apply:**`.
4. The script rebuilds `memory/INDEX.md` and rejects likely secrets.

## Handoff (end of every work session and at each gate step)
`python platform/scripts/memory.py handoff write "<what is done / in progress / next action / blockers, <=25 lines>"`
It overwrites the previous handoff; it is the first thing the next session sees.
