---
paths:
  - "product/**/*.tsx"
  - "product/**/*.jsx"
  - "product/**/*.vue"
  - "product/**/*.svelte"
  - "product/**/*.html"
  - "product/**/*.css"
---
# Frontend and Accessibility Rules (WCAG 2.1 AA)

- Semantic HTML first; ARIA only to fill gaps. One `h1` per view; logical heading order; landmarks for regions.
- Every interactive control is keyboard operable with a visible focus indicator; no keyboard traps; logical tab order.
- Every input has a programmatically associated label; errors are announced and tied to fields; do not rely on colour alone.
- Contrast: text >= 4.5:1, large text and UI components >= 3:1. Respect `prefers-reduced-motion` and `prefers-color-scheme`.
- Provide alt text for informative images; hide decorative ones. Captions/transcripts for media.
- Implement all states from `ux-flows.md`: empty, loading, error, success. Use design-system tokens only.
- Target size >= 24x24 CSS px (44 preferred on touch). Responsive down to 320px; no horizontal scroll at 320px.
- Escape all dynamic content; never inject unsanitised HTML.
- Write accessibility tests (axe-style checks plus keyboard interaction tests) for each screen.
