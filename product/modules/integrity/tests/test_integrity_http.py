"""HTTP contract tests for the integrity router with a fake injected identity."""
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from integrity import api

A1 = "attempt-0001"
GOOD_REPORT = {"down_mbps": 10, "up_mbps": 5, "latency_ms": 50, "camera": True, "mic": True,
               "screen_surface": "monitor", "fullscreen": True, "single_display": True, "browser": "Chrome"}


class FakeUser:
    def __init__(self, user_id, role="learner"):
        self.user_id, self.role = user_id, role


def make_client(user_ref):
    app = FastAPI()
    app.include_router(api.router, prefix="/api")
    app.dependency_overrides[api.current_user_dependency] = lambda: user_ref["user"]
    return TestClient(app)


@pytest.fixture
def who():
    return {"user": FakeUser("learner-1")}


@pytest.fixture
def client(who):
    return make_client(who)


def test_should_reject_every_route_without_injected_identity():
    app = FastAPI()
    app.include_router(api.router, prefix="/api")
    c = TestClient(app)
    for method, url in (("get", "/api/precheck/payload?size=10"), ("post", "/api/precheck/echo"),
                        ("post", "/api/precheck/report"), ("post", f"/api/attempts/{A1}/consent"),
                        ("post", f"/api/attempts/{A1}/events"), ("post", f"/api/attempts/{A1}/chunks/camera/0"),
                        ("post", f"/api/attempts/{A1}/recording/finalize")):
        assert getattr(c, method)(url).status_code == 401, url


def test_should_serve_precheck_payload_of_requested_size_with_cap(client):
    r = client.get("/api/precheck/payload?size=1000")
    assert r.status_code == 200 and len(r.content) == 1000 and r.headers["cache-control"] == "no-store"
    assert client.get("/api/precheck/payload?size=0").status_code == 422
    assert client.get("/api/precheck/payload?size=999999999").status_code == 422


def test_should_echo_upload_size_and_cap_it(client):
    assert client.post("/api/precheck/echo", content=b"x" * 5000).json() == {"received": 5000}
    assert client.post("/api/precheck/echo", content=b"x" * (3 * 1024 * 1024)).status_code == 413


def test_should_evaluate_precheck_report(client):
    ok = client.post("/api/precheck/report", json=GOOD_REPORT)
    assert ok.status_code == 200 and ok.json()["passed"] is True
    bad = client.post("/api/precheck/report", json={**GOOD_REPORT, "screen_surface": "window"}).json()
    assert bad["passed"] is False and [c["name"] for c in bad["checks"] if not c["passed"]] == ["screen"]
    assert client.post("/api/precheck/report", json={**GOOD_REPORT, "x": 1}).status_code == 422
    assert client.post("/api/precheck/report", content=b"not json").status_code == 422
    assert api.latest_precheck_passed("learner-1") is False  # latest report failed


def test_should_record_consent_then_accept_events_chunks_and_finalize(client):
    assert client.post(f"/api/attempts/{A1}/consent", json={"version": "v1", "scopes": ["camera", "events"]}).json() \
        == {"recorded": True, "version": "v1", "scopes": ["camera", "events"]}
    r = client.post(f"/api/attempts/{A1}/events", json=[{"type": "paste", "t_ms": 5}, {"type": "copy", "t_ms": 6}])
    assert r.status_code == 202 and r.json() == {"accepted": 2}
    c = client.post(f"/api/attempts/{A1}/chunks/camera/0", content=b"video-bytes")
    assert c.status_code == 200 and c.json()["size"] == 11 and "path" not in json.dumps(c.json())
    fin = client.post(f"/api/attempts/{A1}/recording/finalize").json()
    assert fin["chunks"] == 1 and len(fin["manifest_hash"]) == 64


def test_should_return_identical_404_for_foreign_and_unknown_attempts(client, who):
    client.post(f"/api/attempts/{A1}/consent", json={"version": "v1", "scopes": ["camera"]})
    who["user"] = FakeUser("learner-2")
    foreign = client.post(f"/api/attempts/{A1}/events", json=[{"type": "copy", "t_ms": 1}])
    unknown = client.post("/api/attempts/attempt-9999/events", json=[{"type": "copy", "t_ms": 1}])
    assert foreign.status_code == unknown.status_code == 404 and foreign.json() == unknown.json()
    for url in (f"/api/attempts/{A1}/chunks/camera/0", f"/api/attempts/{A1}/recording/finalize"):
        assert client.post(url, content=b"x").status_code == 404
    consent_hijack = client.post(f"/api/attempts/{A1}/consent", json={"version": "v1", "scopes": ["camera"]})
    assert consent_hijack.status_code == 404


def test_should_forbid_non_learner_roles_from_learner_endpoints(client, who):
    who["user"] = FakeUser("reviewer-1", role="reviewer")
    assert client.post(f"/api/attempts/{A1}/consent", json={"version": "v1", "scopes": ["camera"]}).status_code == 403


def test_should_validate_inputs_at_the_boundary(client):
    client.post(f"/api/attempts/{A1}/consent", json={"version": "v1", "scopes": ["camera", "events"]})
    assert client.post(f"/api/attempts/{A1}/consent", json={"version": "v1", "scopes": ["root"]}).status_code == 422
    assert client.post(f"/api/attempts/{A1}/consent", json={"version": "v1", "scopes": ["camera"], "x": 1}).status_code == 422
    assert client.post(f"/api/attempts/{A1}/events", json=[{"type": "nope", "t_ms": 1}]).status_code == 422
    assert client.post(f"/api/attempts/{A1}/events", content=b"{").status_code == 422
    assert client.post(f"/api/attempts/{A1}/chunks/audio/0", content=b"x").status_code == 422
    assert client.post(f"/api/attempts/{A1}/chunks/camera/0", content=b"").status_code == 422


def test_should_reject_oversized_bodies(client, monkeypatch):
    client.post(f"/api/attempts/{A1}/consent", json={"version": "v1", "scopes": ["camera", "events"]})
    big_events = json.dumps([{"type": "copy", "t_ms": 1, "detail": {"k": "x" * 60}}] * 100).encode() * 8
    assert client.post(f"/api/attempts/{A1}/events", content=big_events).status_code == 413
    assert client.post(f"/api/attempts/{A1}/chunks/camera/0", content=b"x" * (6 * 1024 * 1024)).status_code == 413


def test_should_not_leak_internals_in_error_bodies(client):
    r = client.post("/api/attempts/..%2F..%2Fetc/events", json=[])
    assert r.status_code in (404, 422)
    assert "Traceback" not in r.text and "sqlite" not in r.text.lower()
