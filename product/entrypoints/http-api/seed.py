"""Create demo accounts. Passwords are GENERATED at random, printed once to the console and never stored
in any file.  Usage:  python product/entrypoints/http-api/seed.py

Existing accounts are left untouched (their password cannot be shown again); delete the identity database
under DATA_DIR to start over.
"""
from __future__ import annotations

import secrets
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[1]
for p in (PRODUCT / "modules", PRODUCT / "shared-kernel", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

DEMO_ACCOUNTS = (
    ("reviewer", "demo-reviewer@crucible.example", "Demo Reviewer", None),
    ("auditor", "demo-auditor@crucible.example", "Demo Auditor", None),
    ("recruiter", "demo-recruiter@crucible.example", "Demo Recruiter", None),
    ("learner", "demo-learner@crucible.example", "Demo Learner", "python"),
)


def seed(identity_api, password_factory=lambda: secrets.token_urlsafe(14)) -> list[tuple[str, str, str]]:
    """Create the demo accounts that do not exist yet. Returns [(role, email, password)] for new ones."""
    created = []
    for role, email, name, track in DEMO_ACCOUNTS:
        password = password_factory()
        try:
            identity_api.create_user(email, password, role=role, display_name=name, track=track)
        except identity_api.IdentityError as exc:
            if getattr(exc, "code", "") == "email_unavailable":
                continue
            raise
        created.append((role, email, password))
    return created


def main() -> int:
    from config import Settings
    import identity.api as identity_api

    settings = Settings.from_env()
    identity_api.configure(data_dir=settings.data_dir)
    created = seed(identity_api)
    if not created:
        print("All demo accounts already exist; passwords are not shown again.")
        return 0
    print("Demo accounts created. Passwords are shown ONCE and are not stored anywhere:\n")
    for role, email, password in created:
        print(f"  {role:<10} {email:<34} {password}")
    print("\nCopy them now. Re-run after deleting the identity database to generate new ones.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
