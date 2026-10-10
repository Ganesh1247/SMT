---
name: compact-memory
description: Keep the memory store lean - merge duplicates, archive stale or superseded entries, tighten descriptions, rebuild the index, and report token cost. Use after each gate close, after a retrospective, or when the index nears its line cap.
---
# Compact Memory

Delegate to `knowledge-curator`.

1. `python platform/scripts/memory.py lint` and `stats` - note index tokens and entry count.
2. Find overlap: list entries by type (`INDEX.md`), search shared terms. Merge duplicates into one entry (`add --update`) and archive the rest (`archive <name>`).
3. Archive entries that are superseded (by a newer ADR or decision), tied to a finished gate, or no longer true. Do not delete; archive keeps history out of the index.
4. Rewrite vague descriptions so one line says what the memory is for ("Why X was chosen over Y for Z").
5. Promote repeated lessons into a proposal: `kaizen/change-proposals/` (the Improver) instead of keeping many near-identical lessons.
6. `memory.py index`, then `lint` and `stats`. Targets: INDEX under 60 lines (~1.2k tokens), session brief under ~600 tokens.
