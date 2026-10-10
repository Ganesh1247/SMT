---
name: workspace-architecture
description: Why the workspace is a gate-stage modular monolith with a main-session orchestrator
type: decision
scope: project
status: active
updated: 2026-10-09
---
Layers: .claude control plane, governance, delivery, product, platform, kaizen, profiles, reference. Lifecycle G0-G8 with Founder approval and an independent auditor.
**Why:** subagents cannot spawn subagents, so the main session (Chief of Staff) orchestrates; separation of duties prevents self-review; gate lock enforces plan-before-code.
**How to apply:** route work via orchestrate-lifecycle; never approve own gates; extend via profiles instead of forking core.
