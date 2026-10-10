---
paths:
  - "product/**"
  - "platform/**"
---
# Security Rules (see governance/policies/security-policy.md)

- Validate and normalise all external input at the boundary (type, length, range, format); reject by default.
- Parameterised queries only; never build SQL/commands/paths from raw input. Encode output for its context (HTML, URL, JSON, shell).
- Authentication and authorisation are explicit on every entrypoint; deny by default; check object-level ownership, not just roles.
- Secrets only from environment or a secret manager; never in code, tests, fixtures, logs or committed config.
- Passwords hashed with a modern adaptive algorithm; use vetted crypto libraries; never invent cryptography.
- Log security-relevant events; never log secrets, tokens or personal data. Errors returned to clients are generic.
- Set secure defaults: HTTPS, secure/HttpOnly/SameSite cookies, CSRF protection for cookie auth, CORS allow-list, security headers.
- Dependencies follow `governance/policies/dependency-policy.md`; no unreviewed additions.
- Apply least privilege to services, tokens and database roles.
