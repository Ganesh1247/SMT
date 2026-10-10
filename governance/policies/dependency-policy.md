# Dependency Policy

- Prefer the platform/standard library; add a dependency only when it removes meaningful complexity.
- Every third-party dependency (library, API, model, dataset, service) is recorded in `delivery/G3-solution-design/dependency-register.md` with: name, version, licence, purpose, owner, alternatives considered, fallback.
- Licences must be compatible with the product's distribution model (check at addition).
- Pin versions; use a lockfile; update on a schedule, not ad hoc.
- A new dependency in a slice requires `principal-architect` approval (ADR if it affects architecture).
- Dependencies with known Critical/High vulnerabilities block release (G6/G7).
- For time-boxed profiles (e.g. hackathon), the register doubles as the required third-party disclosure.
