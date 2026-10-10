"""Composition root: wiring, security headers, error envelope, limits, startup errors, seed script."""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import seed as seed_script
import wiring
from config import Settings
from main import create_app

PW = "correct-horse-battery"


class FakeRunner:
    def __init__(self):
        self.registered = []

    def register_task(self, task_id, kind, spec_json):
        self.registered.append(task_id)

    def run_python(self, *a):
        raise AssertionError("not used in smoke tests")

    run_sql = run_python

    def isolation_status(self):
        return "container"


def _reset_all(apis):
    for name in ("assessment", "scoring", "evidence", "identity"):
        apis[name].reset()


@pytest.fixture()
def app_parts(tmp_path):
    settings = Settings(data_dir=str(tmp_path), allowed_origins=("http://localhost:5173",), serve_web=False)
    runner = FakeRunner()
    app = create_app(settings, apis={"runner": runner})
    yield app, runner, settings
    _reset_all(app.state.apis)


@pytest.fixture()
def client(app_parts):
    return TestClient(app_parts[0])


def test_should_report_health_with_loaded_modules(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and {"identity", "assessment", "scoring", "evidence"} <= set(body["modules"])
    assert body["runner_isolation"] == "container"


def test_should_register_every_hidden_task_with_the_runner_on_startup(app_parts):
    _, runner, _ = app_parts
    assert len(runner.registered) == 2 * (7 + 4 * 2)


def test_should_set_security_headers_and_no_store_on_api_responses(client):
    r = client.get("/api/health")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["cache-control"] == "no-store"
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]


def test_should_return_typed_error_envelope_without_internals(client):
    r = client.get("/api/me")
    assert r.status_code == 401 and r.json() == {"error": {"code": "unauthenticated", "message": "Authentication required"}}
    bad = client.post("/api/auth/login", json={"email": 5})
    assert bad.status_code == 422 and bad.json()["error"]["code"] == "invalid_input"
    assert "traceback" not in bad.text.lower()


def test_should_reject_state_changing_requests_from_foreign_origins(client):
    r = client.post("/api/auth/login", json={"email": "a@example.test", "password": PW}, headers={"Origin": "https://evil.example"})
    assert r.status_code == 403
    ok = client.post("/api/auth/login", json={"email": "a@example.test", "password": PW}, headers={"Origin": "http://localhost:5173"})
    assert ok.status_code == 401


def test_should_reject_oversized_json_bodies(client):
    r = client.post("/api/auth/register", content=b"x" * (300 * 1024), headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_should_allow_cors_only_for_listed_origins(client):
    ok = client.options("/api/health", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    bad = client.options("/api/health", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in bad.headers


def test_should_start_a_learner_attempt_through_the_composed_app(client):
    r = client.post("/api/auth/register", json={"email": "ada@example.test", "password": PW})
    assert r.status_code == 201
    assert client.put("/api/me/track", json={"track": "data_analyst"}).status_code == 200
    created = client.post("/api/attempts", json={"level": 1})
    assert created.status_code == 201 and created.json()["consent_required"] is True
    assert client.get("/api/me/progress").json()["levels"][0]["status"] == "in_progress"


def test_should_fail_startup_with_a_clear_message_when_runner_is_missing(tmp_path, monkeypatch):
    real = wiring.load_api
    monkeypatch.setattr(wiring, "load_api", lambda name: None if name == "runner" else real(name))
    with pytest.raises(wiring.StartupError) as exc:
        create_app(Settings(data_dir=str(tmp_path), serve_web=False))
    assert "runner" in str(exc.value) and "CRUCIBLE_ALLOW_MISSING_MODULES" in str(exc.value)
    for name in ("assessment", "scoring", "evidence", "identity"):
        try:
            real(name).reset()
        except Exception:
            pass


def test_should_allow_degraded_start_only_when_explicitly_enabled(tmp_path, monkeypatch):
    real = wiring.load_api
    monkeypatch.setattr(wiring, "load_api", lambda name: None if name == "runner" else real(name))
    app = create_app(Settings(data_dir=str(tmp_path), serve_web=False, allow_missing_modules=True))
    assert "runner" not in app.state.apis
    _reset_all(app.state.apis)


# ----------------------------------------------------------------- seed script
def test_should_seed_demo_accounts_with_random_passwords_and_store_none(tmp_path):
    import identity.api as identity
    identity.configure(data_dir=str(tmp_path))
    try:
        first = seed_script.seed(identity)
        assert {r for r, _, _ in first} == {"reviewer", "auditor", "recruiter", "learner"}
        passwords = [p for _, _, p in first]
        assert len(set(passwords)) == 4 and all(len(p) >= 16 for p in passwords)
        assert seed_script.seed(identity) == []  # idempotent, nothing re-shown
        identity.reset()
        for path in Path(tmp_path).rglob("*"):
            if path.is_file():
                blob = path.read_bytes()
                assert not any(p.encode() in blob for p in passwords), path
    finally:
        identity.reset()


def test_should_log_in_with_a_seeded_password(tmp_path):
    import identity.api as identity
    identity.configure(data_dir=str(tmp_path))
    try:
        created = {r: (e, p) for r, e, p in seed_script.seed(identity)}
        email, password = created["reviewer"]
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(identity.router, prefix="/api")
        c = TestClient(app)
        r = c.post("/api/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200 and r.json()["role"] == "reviewer"
    finally:
        identity.reset()
