"""Identity domain: roles, tracks, users and input rules. No I/O, no frameworks."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

ROLES = ("learner", "reviewer", "auditor", "recruiter")
TRACKS = ("python", "data_analyst")

_EMAIL = re.compile(r"^[A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)+$")
PASSWORD_MIN = 10
PASSWORD_MAX = 128


class IdentityError(Exception):
    """Base for typed identity errors; `code` is stable and safe to return."""

    code = "identity_error"


class InvalidInput(IdentityError):
    code = "invalid_input"


class EmailUnavailable(IdentityError):
    code = "email_unavailable"


class InvalidCredentials(IdentityError):
    code = "invalid_credentials"


class TooManyAttempts(IdentityError):
    code = "too_many_attempts"


@dataclass(frozen=True)
class User:
    id: str
    alias: str
    role: str
    track: Optional[str]
    email: str = ""
    display_name: str = ""


def normalise_email(email: str) -> str:
    value = (email or "").strip().lower()
    if len(value) > 254 or not _EMAIL.match(value):
        raise InvalidInput("email")
    return value


def check_password(password: str) -> None:
    if not isinstance(password, str) or not (PASSWORD_MIN <= len(password) <= PASSWORD_MAX):
        raise InvalidInput("password")


def check_role(role: str) -> str:
    if role not in ROLES:
        raise InvalidInput("role")
    return role


def check_track(track: Optional[str]) -> Optional[str]:
    if track is not None and track not in TRACKS:
        raise InvalidInput("track")
    return track


def clean_display_name(name: Optional[str]) -> str:
    value = (name or "").strip()
    if len(value) > 80 or any(ord(c) < 32 for c in value):
        raise InvalidInput("display_name")
    return value
