# memory/ - Project Knowledge Store

Durable, **non-derivable** knowledge: decision rationale, constraints, preferences, lessons, external references.
Not for code structure, file contents, or anything already in `delivery/` (link to it instead).

```
memory/
├─ INDEX.md          generated; one line per memory; hard cap 60 lines
├─ handoff.md        rolling "where we left off" (<=25 lines), overwritten each session
├─ decision/  fact/  lesson/  preference/  reference/    one file per memory (<=30 lines)
└─ archive/<type>/   superseded or stale memories (kept out of the index)
```

## Token model (progressive disclosure)
| Layer | Loaded when | Cost |
|---|---|---|
| Session brief (state + handoff + counts) | every session start, by hook | ~500 tokens |
| `INDEX.md` | only if you open it | ~1k tokens max |
| `search` results | on demand | one line per hit |
| A memory file | on demand via `show` | <=30 lines |

## Entry format
```
---
name: kebab-slug            (= filename)
description: one line <=140 chars - what it is for
type: decision | fact | lesson | preference | reference
scope: project | gate:G3 | module:billing
status: active | archived
updated: YYYY-MM-DD
---
body <=30 lines. For decision/lesson/preference: fact, then **Why:** and **How to apply:**
```

## Commands
`python platform/scripts/memory.py add|search|show|index|lint|archive|handoff|brief|stats` (see `--help`).
Skills: `capture-memory`, `recall-context`, `compact-memory`. Owner: `knowledge-curator`.
Safety: entries are secret-scanned on write; `lint` re-checks all. Memory is committed with the repo, so it is shared, reviewable and versioned.

## Relation to Claude Code's built-in memory
Claude Code also keeps a personal, per-user auto-memory outside the repo. This store is the project's
shared memory: it travels with the repo and is the source of truth for the team and for every agent.
