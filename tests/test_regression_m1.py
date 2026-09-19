import pytest
import os
import sys
from fastapi.testclient import TestClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(project_root, "backend")
for p in [project_root, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_m1_health_check(client):
    """Verify M1 health check is unchanged."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_m1_root_endpoint(client):
    """Verify root documentation info."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "online"

def test_m1_auth_endpoints(client):
    """Verify login, token issuance, and /me endpoint."""
    resp = client.post("/api/v1/auth/login", data={"username": "owner", "password": "password123"})
    assert resp.status_code == 200
    token_data = resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Test /me
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == "owner"
    assert me_data["role_name"] == "business_owner"

def test_m1_sales_endpoints(client):
    """Verify sales listing endpoint returns records."""
    resp = client.get("/api/v1/sales/?limit=10")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 10
    assert "transaction_id" in items[0]
    assert "total_amount" in items[0]

def test_m1_inventory_endpoints(client):
    """Verify inventory catalog and low-stock alerts."""
    resp = client.get("/api/v1/inventory/")
    assert resp.status_code == 200
    assert len(resp.json()) > 0

    alerts_resp = client.get("/api/v1/inventory/?low_stock_only=true")
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    for item in alerts:
        assert item["stock_level"] <= item["reorder_threshold"]

def test_m1_analytics_summary(client):
    """Verify analytics summary produces valid aggregate metrics."""
    login_resp = client.post("/api/v1/auth/login", data={"username": "owner", "password": "password123"})
    token = login_resp.json()["access_token"]

    resp = client.get("/api/v1/analytics/summary", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_revenue"] > 0
    assert data["total_transactions"] > 0
    assert len(data["category_breakdown"]) > 0
    assert len(data["top_products"]) > 0

def test_m1_users_admin_rbac(client):
    """Verify user administration is strictly admin only."""
    # Sales Exec fails -> 403
    login_exec = client.post("/api/v1/auth/login", data={"username": "exec", "password": "password123"})
    token_exec = login_exec.json()["access_token"]
    resp_exec = client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token_exec}"})
    assert resp_exec.status_code == 403

    # Admin succeeds -> 200
    login_admin = client.post("/api/v1/auth/login", data={"username": "admin", "password": "password123"})
    token_admin = login_admin.json()["access_token"]
    resp_admin = client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token_admin}"})
    assert resp_admin.status_code == 200
    assert len(resp_admin.json()) >= 4
