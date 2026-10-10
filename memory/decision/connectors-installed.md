---
name: connectors-installed
description: Which connectors are installed and which agents may use them (least privilege)
type: decision
scope: project
status: active
updated: 2026-10-10
---
Context7 (library docs): engineers + principal-architect. Vercel: platform-engineer read-only (list/get projects and deployments, runtime logs/errors, docs); deploy/rollback tools intentionally NOT granted - Founder approval required. GitHub, Figma, Notion, Linear, Atlassian, Slack, Datadog still need OAuth authorization by the Founder.
**Why:** least privilege; production-changing tools need explicit approval.
**How to apply:** when adding a connector, grant read tools to the owning role only; record here.
