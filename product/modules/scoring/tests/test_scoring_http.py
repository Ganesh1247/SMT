"""HTTP: /me/profile and /me/evidence are learner-only and own-data-only."""
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import evidence.api as ev
import identity.api as ident
import scoring.api as scoring

PW = "correct-horse-battery"


@pytest.fixture()
def client():
    ident.configure(database_url="sqlite://")
    ev.configure(database_url="sqlite://", clock=lambda: datetime(2026, 10, 10, tzinfo=timezone.utc))
    scoring.configure(database_url="sqlite://", clock=lambda: datetime(2026, 10, 10, 12, tzinfo=timezone.utc))
    app = FastAPI()
    for r in (ident.router, scoring.router):
        app.include_router(r, prefix="/api")
    yield TestClient(app)
    for m in (scoring, ev, ident):
        m.reset()


def learner(client, email="ada@example.test"):
    r = client.post("/api/auth/register", json={"email": email, "password": PW})
    return r.json()


def append_level(lid, level, seed, n):
    method = "live_screening" if level == 4 else "deterministic_test"
    extra = {"confidence": 0.9, "ai_disclosure": True} if level == 4 else {}
    base = dict(competency_id="cmp_python", level=level, method=method, outcome="pass", score=1,
                task_id="tsk_item_a", task_version="1.0.0", rubric_id="rbr_python_l1",
                rubric_version="1.0.0", seed_id=seed, **extra)
    ev.append("criterion_result", lid, dict(base, criterion_id="crt_item_a",
              submission_ref="sha256:" + "c" * 64), f"k-crit-{lid}-{level}-{n}")
    ev.append("level_outcome", lid, base, f"k-lvl-{lid}-{level}-{n}")


def test_should_require_login(client):
    assert client.get("/api/me/profile").status_code == 401
    assert client.get("/api/me/evidence").status_code == 401


def test_should_show_no_estimate_until_gate_then_band_with_label(client):
    me = learner(client)
    body = client.get("/api/me/profile").json()
    assert all(c["estimate"] is None for c in body["competencies"])
    for lvl in (1, 2, 3, 4):
        append_level(me["id"], lvl, f"sd_00000000000{lvl}", 1)
    scoring.apply_gated_update(me["id"], "python")
    py = client.get("/api/me/profile").json()["competencies"][0]
    assert set(py["estimate"]) >= {"estimate", "lower", "upper", "as_of", "label"}
    assert py["estimate"]["label"] == "Experimental"


def test_should_list_only_own_evidence_without_time_taken(client):
    me = learner(client)
    other = "lrn_ffffffffffffffff"
    append_level(me["id"], 1, "sd_000000000001", 1)
    append_level(other, 1, "sd_000000000009", 2)
    items = client.get("/api/me/evidence").json()["items"]
    assert items and all("duration" not in i and "time_taken" not in i for i in items)
    assert len(items) == 2
