# Module: identity

**Responsibility:** Accounts, password hashing (stdlib scrypt), server-side sessions (HttpOnly, SameSite=Strict cookie `crucible_session`), roles (learner, reviewer, auditor, recruiter) assigned server-side only, track preference, pseudonymous aliases.
**Owner:** stream A1 | **Status:** built (tests pass; not yet independently reviewed)

## Public surface (`identity.api`)
| Member | Contract |
|---|---|
| `router` | `POST /auth/register` (learner only; body `{email,password>=10,display_name?}`, extra fields rejected), `POST /auth/login` (identical 401 for unknown user / wrong password, 429 after 5 failures in 5 min), `POST /auth/logout`, `GET /me`, `PUT /me/track {track}` |
| `current_user(request) -> User` | FastAPI dependency. `User{id, alias, role, track}` (frozen). 401 `unauthenticated` without a valid session |
| `require_role(*roles)` | dependency factory. 403 `forbidden` when the role is not listed |
| `alias_for(learner_id) -> str \| None` | `cnd_<12 hex>` pseudonym |
| `learner_for_alias(alias) -> str \| None` | reverse lookup (recruiter flows) |
| `create_user(email, password, role, display_name, track) -> User` | server-side only (seed/admin); never exposed over HTTP |
| `configure(database_url \| data_dir, clock, session_ttl_seconds, cookie_secure)`, `reset()` | composition and tests |

Errors: `IdentityError` subclasses with stable `code` (`invalid_input`, `email_unavailable`, `invalid_credentials`, `too_many_attempts`). HTTP bodies: `{"detail": {"code","message"}}` (the entrypoint reshapes to `{"error": ...}`).

## Depends on
Nothing (no other module).

## Data owned
`users(id, alias, email, display_name, role, track, password_hash, created_at)`, `sessions(token_hash, user_id, expires_at, created_at)` in `DATA_DIR/identity.db`. Only the SHA-256 of a session token is stored. Email and display name are personal data: shown only to the owner via `/me`.

## Events
None published. Learner ids are `lrn_<16 hex>`, other roles `usr_<16 hex>`.

## Notes
`CRUCIBLE_COOKIE_SECURE=true` must be set behind HTTPS (default false for local http). Login lockout is per process (in memory).
