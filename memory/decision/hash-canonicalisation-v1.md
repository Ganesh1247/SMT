---
name: hash-canonicalisation-v1
description: Ledger hashing uses explicit versioned field list, not RFC 8785; Trust stores normalised values
type: decision
scope: project
status: active
updated: 2026-10-10
---
Spec: delivery/G3-solution-design/contracts/hash-canonicalisation.md; reference impl canonical_hash.py (stdlib only, 16/16 self-tests). Test vector sha256:cd2f785f...c81dc0d6 for the sample event. **Why:** RFC 8785 needs ECMAScript number formatting and UTF-16 key order, not in Python stdlib; explicit list is portable and auditable. Six-place rounding would let sub-precision edits go undetected unless Trust stores normalised values, so rule 9 requires that. **How to apply:** any field or rule change bumps the version string; HR portal must reproduce the test vector.
