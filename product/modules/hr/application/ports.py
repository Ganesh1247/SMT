"""Ports of the hr module."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Protocol


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: str
    org_id: str | None = None  # recruiter organisation `org_...`; derived from user_id when absent


class IdentityPort(Protocol):
    def authenticate(self, cookies: Mapping[str, str], headers: Mapping[str, str]) -> Principal | None: ...


class ReviewPort(Protocol):
    def query_shared_evidence(self, request: dict, caller_recipient_id: str) -> dict:
        """SharedEvidenceQueryRequest -> SharedEvidenceQueryResponse (contract v0.1)."""


class EvidencePort(Protocol):
    def verify_receipt(self, receipt_hash: str) -> dict:
        """{status: match|mismatch|unavailable, sequence?: int}"""


class Clock(Protocol):
    def now(self) -> datetime: ...


class Ids(Protocol):
    def new_id(self) -> str: ...


class DocStore(Protocol):
    def put(self, collection: str, key: str, doc: dict) -> None: ...
    def put_if_absent(self, collection: str, key: str, doc: dict) -> bool: ...
    def get(self, collection: str, key: str) -> dict | None: ...
    def all(self, collection: str) -> list[dict]: ...


class Contracts(Protocol):
    def is_valid(self, name: str, doc: dict) -> bool: ...
    def errors(self, name: str, doc: dict) -> list[dict]: ...
