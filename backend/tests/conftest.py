"""Test fixtures: a throw-away SQLite file, a few real rows inserted via SQLAlchemy, and a TestClient with real auth.
Run from the backend folder:  python -m pytest tests -v
"""
import os
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

TMP = tempfile.mkdtemp(prefix="marketmind_test_")
os.environ["DATABASE_URL"] = "sqlite:///" + (Path(TMP) / "test.db").as_posix()
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["ADMIN_EMAIL"] = "admin@test.local"
os.environ["ADMIN_PASSWORD"] = "AdminPass123!"
os.environ["REBASE_DATES_TO_TODAY"] = "0"      # existing tests assert the real dates; the shift has its own tests
os.environ["SMTP_HOST"] = ""                    # never send real mail from tests (reset tests also stub mailer.send_email)
os.environ["ADMIN_REGISTRATION_CODE"] = ""
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

import models
from database import SessionLocal
from main import app


def _seed_sales():
    """Two stores x two products x 10 days; the last day has one item below its reorder point."""
    with SessionLocal() as db:
        if db.query(models.SalesTransaction).count():
            return
        d0 = date(2024, 1, 1)
        for day in range(10):
            for store in ("S001", "S002"):
                for pid, cat, price in (("P0001", "Groceries", 10.0), ("P0002", "Toys", 20.0)):
                    last = day == 9
                    db.add(models.SalesTransaction(
                        date=d0 + timedelta(days=day), store_id=store, product_id=pid, category=cat, region="North",
                        inventory_level=5 if (last and store == "S001" and pid == "P0001") else 200,
                        units_sold=10, units_ordered=10, demand_forecast=10.0, price=price, discount=0,
                        weather_condition="Sunny", holiday_promotion=0, competitor_pricing=price, seasonality="Winter",
                        net_price=price, revenue=10 * price, reorder_point=20))
        db.commit()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:          # context manager runs the lifespan -> tables, roles, admin
        _seed_sales()
        yield c


def login(client, email, password):
    r = client.post("/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="session")
def admin(client):
    return login(client, "admin@test.local", "AdminPass123!")


@pytest.fixture(scope="session")
def make_user(client):
    def _make(role, n=[0]):
        n[0] += 1
        email = f"{role}{n[0]}@test.local"
        r = client.post("/register", json={"name": f"{role} user", "email": email, "password": "Password123", "role": role})
        assert r.status_code == 201, r.text
        return login(client, email, "Password123")
    return _make
