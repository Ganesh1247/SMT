"""Public identity DTOs (immutable)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class User:
    id: str
    alias: str
    role: str
    track: Optional[str]
