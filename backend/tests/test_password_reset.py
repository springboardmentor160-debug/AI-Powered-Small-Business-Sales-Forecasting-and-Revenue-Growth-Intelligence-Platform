"""Forgot / reset password + administrator sign-up code. Run from backend/:  python -m pytest tests -v"""
import re
from datetime import timedelta

import pytest

import config
import mailer
import models
import resettokens
from conftest import login
from database import SessionLocal


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(mailer, "send_email", lambda to, subject, text, html=None: sent.append({"to": to, "text": text}) or True)
    return sent


def _register(client, email, password="Password123"):
    r = client.post("/register", json={"name": "Reset User", "email": email, "password": password, "role": "store_manager"})
    assert r.status_code == 201, r.text


def _token(sent):
    m = re.search(r"reset_token=([A-Za-z0-9_\-]+)", sent[-1]["text"])
    assert m, sent[-1]["text"]
    return m.group(1)


def _age_tokens(email, minutes=0, expire=False):
    """Backdate a user's tokens (to get past the 1-minute cooldown) or force them to be expired."""
    with SessionLocal() as db:
        u = db.query(models.User).filter_by(email=email).one()
        for t in db.query(models.PasswordResetToken).filter_by(user_id=u.id):
            t.created_at = t.created_at - timedelta(minutes=minutes)
            if expire:
                t.expires_at = t.created_at - timedelta(seconds=1)
        db.commit()


def test_same_answer_for_known_and_unknown_email_and_only_known_gets_mail(client, outbox):
    _register(client, "forgot1@test.local")
    a = client.post("/auth/forgot-password", json={"email": "FORGOT1@test.local"})
    b = client.post("/auth/forgot-password", json={"email": "nobody@test.local"})
    assert a.status_code == b.status_code == 200 and a.json() == b.json()
    assert [m["to"] for m in outbox] == ["forgot1@test.local"]
    assert client.post("/auth/forgot-password", json={"email": "not-an-email"}).status_code == 422


def test_full_reset_flow_and_token_is_single_use(client, outbox):
    _register(client, "forgot2@test.local")
    client.post("/auth/forgot-password", json={"email": "forgot2@test.local"})
    tok = _token(outbox)
    r = client.post("/auth/reset-password", json={"token": tok, "new_password": "BrandNewPass9"})
    assert r.status_code == 200
    assert client.post("/login", json={"email": "forgot2@test.local", "password": "Password123"}).status_code == 401
    assert login(client, "forgot2@test.local", "BrandNewPass9")
    assert client.post("/auth/reset-password", json={"token": tok, "new_password": "AnotherPass99"}).status_code == 400    # already used


def test_bad_expired_and_weak_requests_are_rejected(client, outbox):
    assert client.post("/auth/reset-password", json={"token": "x" * 40, "new_password": "Password123"}).status_code == 400
    _register(client, "forgot3@test.local")
    client.post("/auth/forgot-password", json={"email": "forgot3@test.local"})
    tok = _token(outbox)
    assert client.post("/auth/reset-password", json={"token": tok, "new_password": "short"}).status_code == 422
    _age_tokens("forgot3@test.local", expire=True)
    assert client.post("/auth/reset-password", json={"token": tok, "new_password": "Password123"}).status_code == 400


def test_cooldown_and_new_request_kills_the_old_link(client, outbox):
    _register(client, "forgot4@test.local")
    client.post("/auth/forgot-password", json={"email": "forgot4@test.local"})
    client.post("/auth/forgot-password", json={"email": "forgot4@test.local"})          # within a minute -> no second mail
    assert len(outbox) == 1
    first = _token(outbox)
    _age_tokens("forgot4@test.local", minutes=2)
    client.post("/auth/forgot-password", json={"email": "forgot4@test.local"})
    assert len(outbox) == 2
    assert client.post("/auth/reset-password", json={"token": first, "new_password": "Password123"}).status_code == 400
    assert client.post("/auth/reset-password", json={"token": _token(outbox), "new_password": "Password456"}).status_code == 200


def test_database_only_stores_hashes(client, outbox):
    _register(client, "forgot5@test.local")
    client.post("/auth/forgot-password", json={"email": "forgot5@test.local"})
    tok = _token(outbox)
    with SessionLocal() as db:
        hashes = [t.token_hash for t in db.query(models.PasswordResetToken)]
    assert resettokens.hash_token(tok) in hashes and tok not in hashes


def test_administrator_signup_needs_the_access_code(client, monkeypatch):
    body = {"name": "Boss Admin", "email": "boss@test.local", "password": "Password123", "role": "admin"}
    monkeypatch.setattr(config, "ADMIN_REGISTRATION_CODE", "")
    assert client.post("/register", json=body).status_code == 403                                     # disabled by default
    monkeypatch.setattr(config, "ADMIN_REGISTRATION_CODE", "open-sesame")
    assert client.post("/register", json=body).status_code == 403                                     # no code
    assert client.post("/register", json={**body, "admin_code": "wrong"}).status_code == 403
    assert client.post("/register", json={**body, "admin_code": "ünï-cödé"}).status_code == 403       # non-ASCII must not crash
    r = client.post("/register", json={**body, "admin_code": "open-sesame"})
    assert r.status_code == 201 and r.json()["role"] == "admin"
    assert client.get("/admin/users", headers=login(client, "boss@test.local", "Password123")).status_code == 200
