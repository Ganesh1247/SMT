# Security Policy

1. **No secrets in the repository.** Use environment variables or a secret manager; commit only `.env.example` with placeholders. A hook blocks likely secrets.
2. **Threat model before design lock.** Required at G3 (STRIDE per trust boundary; data classification; abuse cases).
3. **Validate at trust boundaries.** All external input is validated and encoded; output contexts are escaped.
4. **AuthN/AuthZ explicit.** Every endpoint declares its authentication and authorisation rule; deny by default.
5. **Least privilege** for services, tokens, database roles and agents.
6. **Data protection.** Classify data; encrypt in transit; encrypt sensitive data at rest; log without personal or secret data.
7. **Dependencies** follow `dependency-policy.md`; known critical vulnerabilities block release.
8. **Security review at G6** covers OWASP Top 10, dependency audit, secret scan, and configuration review.
9. **Findings** are rated Critical / High / Medium / Low. Critical and High block release unless the Founder accepts the risk in writing.
