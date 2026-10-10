# Crucible web (stream C)

React 18 + TypeScript + Vite + CodeMirror 6. Talks only to `/api` (see delivery/G4-delivery-plan/build-brief.md section 8).

- `npm install`, then `npm run dev` (proxy `/api` -> http://127.0.0.1:8000)
- `npm test` (Vitest + Testing Library + axe-core), `npm run build`
- No mock data ships in the app; fakes exist only under `src/test/`.
