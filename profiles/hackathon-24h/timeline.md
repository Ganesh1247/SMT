# Hackathon 24h - Gate-to-Event Timeline

| Event stage | Hours | Score weight | Lifecycle gates covered | Compressed artifacts (one-pagers) | Lead agents |
|---|---|---|---|---|---|
| Round 1 - Problem Interpretation and Solution Concept | 0-2 | 15 | G0, G1, G2 | project-brief, requirements list (REQ-IDs, MoSCoW), feasibility note, MVP cut line | product-owner, research-analyst |
| Round 2 - Architecture and Technical Strategy | 4-6 | 20 | G3, G4 | one-page blueprint, ADRs for stack, risk and fallback table, slice plan | principal-architect, security-engineer (light threat model) |
| Mentor checkpoint (not scored) | 8-10 | 0 | G5 (in progress) | honest status: built / working / broken / cut | Chief of Staff |
| Round 3 - Prototype and Execution Review | 12-16 | 25 | G5 | working slices, requirement-to-feature map, test evidence | engineers, quality-engineer |
| Hardening | 16-22 | - | G5, G6 | audit against rubric, fixes, demo recording as backup | compliance-auditor, hackathon-judge-simulator |
| Round 4 - Grand Demonstration and Final Defence | 22-24 | 40 | G6, G7 | demo script (2-2-2-1-3 min), evidence pack, Q&A prep | demo-defence-coach |

## Iteration loop (repeat after every round and every 3-4 hours)
1. `score-against-rubric` for the next round -> ranked fixes by score gain per hour.
2. Execute the top fixes through the normal slice chain (engineer -> quality-engineer -> staff-code-reviewer).
3. `trace.py matrix` + `slices` -> close requirement gaps; update the requirement-to-feature-to-evidence matrix.
4. `self-improve` (10 min): read signals, apply approved process tweaks, capture lessons to memory.
5. Write the handoff; repeat. Each pass should raise a measurable rubric criterion or remove a risk.

## Compression rules
- Gate approvals by the Founder happen at hours 2, 6, 16 and 22 (fast, 5-minute reviews).
- Rework limit is 1 per gate; escalate at once.
- Auditor checks are rubric-driven (see `rubric.md`) rather than full-length.
- Gate G8 (operate) is skipped for a hackathon; record that in the gate log with reason "profile: hackathon-24h".
- Never skip the gate lock: product code starts only after G3+G4 approval (hour ~6).
