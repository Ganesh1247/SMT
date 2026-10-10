---
name: design-ux-flow
description: Produce user flows, information architecture, screen/state inventory, design tokens and accessibility criteria from the PRD. Use at G3 for any product with a user interface.
---
# Design UX Flow

Owner: `ux-architect`. Template: `platform/templates/ux-flows.md`. Output: `delivery/G3-solution-design/ux-flows.md`.

## Steps
1. Personas and primary jobs-to-be-done from G1 research.
2. One task flow per Must requirement: entry point, steps, decisions, success and failure paths.
3. Information architecture: navigation model, page/screen hierarchy, naming.
4. Screen inventory: purpose, content, actions, and all states (empty, loading, partial, error, success, offline where relevant).
5. Design system: tokens (colour with contrast ratios, type scale, spacing, radius, elevation), component list with variants.
6. Accessibility criteria per screen: keyboard path, focus order, labels, contrast, motion, screen reader announcements (WCAG 2.1 AA).
7. Usability checks: task-success and time-on-task targets linked to success-metrics.
8. Traceability table: REQ-ID -> flow -> screens.
