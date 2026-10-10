"""GET /audit/ledger/verify is auditor/reviewer only."""
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import evidence.api as ev
import identity.api as ident

PW = "correct-horse-battery"


@pytest.fixture()
def client():
    ident.configure(database_url="sqlite://")
    ev.configure(database_url="sqlite://", clock=lambda: datetime(2026, 10, 10, tzinfo=timezone.utc))
    app = FastAPI()
    app.include_router(ident.router, prefix="/api")
    app.include_router(ev.router, prefix="/api")
    yield TestClient(app)
    ev.reset()
    ident.reset()


def login(client, role):
    ident.create_user(f"{role}@example.test", PW, role=role)
    r = client.post("/api/auth/login", json={"email": f"{role}@example.test", "password": PW})
    assert r.status_code == 200


def test_should_deny_anonymous_verify(client):
    assert client.get("/api/audit/ledger/verify").status_code == 401


def test_should_deny_learner_verify(client):
    login(client, "learner")
    assert client.get("/api/audit/ledger/verify").status_code == 403


def test_should_allow_auditor_verify(client):
    login(client, "auditor")
    r = client.get("/api/audit/ledger/verify")
    assert r.status_code == 200 and r.json()["ok"] is True
