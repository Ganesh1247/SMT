"""Public contract of the identity module. Only these names may be used by other modules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from identity.api import runtime
from identity.api.dto import User
from identity.api.http import current_user, require_role, router
from identity.domain.model import IdentityError, ROLES, TRACKS

configure = runtime.configure
reset = runtime.reset


@dataclass(frozen=True)
class Principal:
    """Shape expected by other modules' IdentityPort (see their application/ports.py)."""
    user_id: str
    role: str
    org_id: Optional[str] = None


def authenticate(cookies: Mapping[str, str], headers: Mapping[str, str]) -> Optional[Principal]:
    """Non-HTTP equivalent of the `current_user` FastAPI dependency, for modules that call
    identity directly from a plain cookie/header mapping instead of a Request object."""
    user = runtime.service().user_for_token(cookies.get(runtime.COOKIE_NAME))
    if user is None:
        return None
    return Principal(user_id=user.id, role=user.role)


def alias_for(learner_id: str) -> Optional[str]:
    """Pseudonymous alias (cnd_...) for a learner id, or None if unknown."""
    return runtime.service().alias_for(learner_id)


def learner_for_alias(alias: str) -> Optional[str]:
    """Reverse lookup used by recruiter-facing flows; None if unknown or not a learner."""
    return runtime.service().learner_for_alias(alias)


def create_user(email: str, password: str, role: str = "learner",
                display_name: Optional[str] = None, track: Optional[str] = None) -> User:
    """Server-side account creation (seed/admin only; never exposed over HTTP)."""
    u = runtime.service().create_user(email, password, role, display_name, track)
    return User(id=u.id, alias=u.alias, role=u.role, track=u.track)


__all__ = [
    "router", "current_user", "require_role", "alias_for", "learner_for_alias", "create_user",
    "configure", "reset", "User", "IdentityError", "ROLES", "TRACKS", "Principal", "authenticate",
]
