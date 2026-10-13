"""API tests for the Milestone 3 endpoints.

They read the committed artifacts in artifacts/milestone-3/. Regenerate them
with `python -m backend.ml.run_milestone3` if these tests report 404.
"""

import time

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.auth import ALGORITHM, SECRET_KEY
from backend.database import Base, get_db
from backend.main import app


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def auth_headers(role="admin"):
    token = jwt.encode(
        {"sub": "m3-test@example.com", "role": role, "exp": int(time.time()) + 300},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    "endpoint",
    ["/recommendations/overview", "/recommendations/customer/12347", "/churn", "/anomalies"],
)
def test_m3_endpoints_reject_missing_token(client, endpoint):
    assert client.get(endpoint).status_code == 422


@pytest.mark.parametrize("endpoint", ["/churn", "/anomalies"])
def test_sales_executive_cannot_see_churn_or_alerts(client, endpoint):
    response = client.get(endpoint, headers=auth_headers("sales_executive"))
    assert response.status_code == 403


def test_sales_executive_can_use_recommendations(client):
    response = client.get(
        "/recommendations/customer/12347?stock_code=85123A",
        headers=auth_headers("sales_executive"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["recommended_for_you"]["source"] == "collaborative_filtering"
    assert len(body["recommended_for_you"]["recommendations"]) > 0


def test_unknown_customer_gets_best_sellers(client):
    response = client.get("/recommendations/customer/999999999", headers=auth_headers("admin"))
    assert response.status_code == 200
    assert response.json()["recommended_for_you"]["source"] == "popular_products"


def test_unknown_product_returns_404(client):
    response = client.get("/recommendations/product/NOT-A-PRODUCT", headers=auth_headers("admin"))
    assert response.status_code == 404


def test_churn_overview_structure_and_filter(client):
    response = client.get("/churn?risk=High Risk&active_only=true&limit=5", headers=auth_headers("store_manager"))
    assert response.status_code == 200
    body = response.json()
    assert set(body["risk_counts"]) == {"High Risk", "Medium Risk", "Low Risk"}
    assert 0 < len(body["customers"]) <= 5
    for customer in body["customers"]:
        assert customer["retention_risk"] == "High Risk"
        assert customer["already_inactive_90d"] is False
        assert 0.7 <= customer["churn_probability"] <= 1.0


def test_churn_rejects_invalid_risk_level(client):
    response = client.get("/churn?risk=Extreme", headers=auth_headers("admin"))
    assert response.status_code == 422


def test_anomaly_alerts_filtering(client):
    response = client.get(
        "/anomalies?alert_type=stock_write_off&severity=high",
        headers=auth_headers("business_owner"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["alerts"]
    assert all(a["alert_type"] == "stock_write_off" and a["severity"] == "high" for a in body["alerts"])


def test_anomaly_rejects_unknown_alert_type(client):
    response = client.get("/anomalies?alert_type=bogus", headers=auth_headers("admin"))
    assert response.status_code == 422
