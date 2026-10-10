"""Identity: accounts, sessions, roles (server-side only), alias, track preference."""
import re
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

import identity.api as ident

PW = "correct-horse-battery"


class Clock:
    def __init__(self):
        self.now = datetime(2026, 10, 10, 9, 0, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


@pytest.fixture()
def clock():
    return Clock()


@pytest.fixture()
def client(clock):
    ident.configure(database_url="sqlite://", clock=clock, session_ttl_seconds=3600)
    app = FastAPI()
    app.include_router(ident.router, prefix="/api")

    @app.get("/api/_rev")
    def rev(user=Depends(ident.require_role("reviewer"))):
        return {"alias": user.alias}

    @app.get("/api/_any")
    def anyuser(user=Depends(ident.current_user)):
        return {"role": user.role}

    yield TestClient(app)
    ident.reset()


def register(client, email="ada@example.test", **extra):
    return client.post("/api/auth/register", json={"email": email, "password": PW, "display_name": "Ada", **extra})


def test_should_register_learner_and_open_session_cookie(client):
    r = register(client)
    assert r.status_code == 201
    body = r.json()
    assert body["role"] == "learner" and re.fullmatch(r"cnd_[a-f0-9]{12}", body["alias"])
    assert re.fullmatch(r"lrn_[a-f0-9]{16}", body["id"])
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie
    assert client.get("/api/me").json()["email"] == "ada@example.test"


def test_should_ignore_role_escalation_attempts_on_register(client):
    r = register(client, role="reviewer")
    assert r.status_code == 422
    assert client.get("/api/_rev").status_code in (401, 403)


def test_should_reject_weak_password_and_bad_email(client):
    assert client.post("/api/auth/register", json={"email": "a@example.test", "password": "short"}).status_code == 422
    assert client.post("/api/auth/register", json={"email": "not-an-email", "password": PW}).status_code == 422


def test_should_reject_duplicate_email(client):
    assert register(client).status_code == 201
    assert register(client).status_code == 409


def test_should_login_logout_and_invalidate_session(client):
    register(client)
    client.post("/api/auth/logout")
    assert client.get("/api/me").status_code == 401
    assert client.post("/api/auth/login", json={"email": "ada@example.test", "password": PW}).status_code == 200
    assert client.get("/api/me").status_code == 200
    token = client.cookies.get("crucible_session")
    client.post("/api/auth/logout")
    client.cookies.set("crucible_session", token)
    assert client.get("/api/me").status_code == 401


def test_should_give_same_error_for_wrong_password_and_unknown_user(client):
    register(client)
    client.post("/api/auth/logout")
    a = client.post("/api/auth/login", json={"email": "ada@example.test", "password": "wrong-password-1"})
    b = client.post("/api/auth/login", json={"email": "nobody@example.test", "password": "wrong-password-1"})
    assert a.status_code == b.status_code == 401 and a.json() == b.json()


def test_should_lock_out_after_repeated_failures(client):
    register(client)
    client.post("/api/auth/logout")
    for _ in range(5):
        client.post("/api/auth/login", json={"email": "ada@example.test", "password": "wrong-password-1"})
    r = client.post("/api/auth/login", json={"email": "ada@example.test", "password": PW})
    assert r.status_code == 429


def test_should_expire_session_after_ttl(client, clock):
    register(client)
    clock.now += timedelta(seconds=3601)
    assert client.get("/api/me").status_code == 401


def test_should_enforce_roles_server_side(client):
    ident.create_user("rev@example.test", PW, role="reviewer")
    register(client)
    assert client.get("/api/_rev").status_code == 403
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"email": "rev@example.test", "password": PW})
    assert client.get("/api/_rev").status_code == 200


def test_should_set_track_preference_only_to_known_values(client):
    register(client)
    assert client.put("/api/me/track", json={"track": "data_analyst"}).status_code == 200
    assert client.get("/api/me").json()["track"] == "data_analyst"
    assert client.put("/api/me/track", json={"track": "admin"}).status_code == 422


def test_should_resolve_alias_both_ways_without_exposing_email(client):
    me = register(client).json()
    assert ident.alias_for(me["id"]) == me["alias"]
    assert ident.learner_for_alias(me["alias"]) == me["id"]
    assert ident.alias_for("lrn_0000000000000000") is None
    assert ident.learner_for_alias("cnd_000000000000") is None


def test_should_store_scrypt_hash_not_password(client):
    from identity.api import runtime
    from sqlalchemy import text
    register(client)
    with runtime.get_engine().connect() as c:
        stored = c.execute(text("SELECT password_hash FROM users")).scalar_one()
    assert PW not in stored and stored.startswith("scrypt$")


def test_should_require_authentication_by_default(client):
    assert client.get("/api/_any").status_code == 401
    assert client.get("/api/me").status_code == 401
