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

@pytest.fixture(scope="module")
def tokens(client):
    """Retrieve JWT access tokens for all 4 test roles."""
    roles = ["owner", "manager", "exec", "admin"]
    token_dict = {}
    for r in roles:
        resp = client.post("/api/v1/auth/login", data={"username": r, "password": "password123"})
        assert resp.status_code == 200, f"Login failed for role {r}: {resp.text}"
        token_dict[r] = resp.json()["access_token"]
    return token_dict

def test_unauthenticated_requests_return_401(client):
    """Verify missing authorization header returns 401 Unauthorized."""
    endpoints = ["/segments", "/segments/customers", "/forecast/revenue", "/forecast/series", "/reports/business"]
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 401, f"Expected 401 for unauthenticated {ep}, got {resp.status_code}"

def test_invalid_token_returns_401(client):
    """Verify invalid / malformed token returns 401 Unauthorized."""
    bad_headers = {"Authorization": "Bearer invalid_malformed_token_xyz"}
    endpoints = ["/segments", "/forecast/revenue", "/reports/business"]
    for ep in bad_headers:
        for ep in endpoints:
            resp = client.get(ep, headers=bad_headers)
            assert resp.status_code == 401, f"Expected 401 for bad token on {ep}, got {resp.status_code}"

def test_segments_accessible_to_all_authenticated_roles(client, tokens):
    """Verify all 4 authenticated roles can access customer segmentation."""
    for role_name, token in tokens.items():
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/segments", headers=headers)
        assert resp.status_code == 200, f"Role {role_name} failed to access /segments: {resp.status_code}"
        data = resp.json()
        assert len(data) == 4, "Must return 4 segments"

def test_segments_customers_pagination(client, tokens):
    """Verify paginated customer directory."""
    headers = {"Authorization": f"Bearer {tokens['owner']}"}
    resp = client.get("/segments/customers?page=1&limit=5", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["page"] == 1
    assert body["limit"] == 5
    assert len(body["items"]) == 5
    assert body["total"] == 25

def test_forecast_revenue_rbac_access_matrix(client, tokens):
    """
    Verify exact Access Matrix for /forecast/revenue:
    Business Owner: 200 YES
    Store Manager: 200 VIEW
    Administrator: 200 YES
    Sales Executive: 403 FORBIDDEN
    """
    # Allowed roles
    for role_name in ["owner", "manager", "admin"]:
        headers = {"Authorization": f"Bearer {tokens[role_name]}"}
        resp = client.get("/forecast/revenue", headers=headers)
        assert resp.status_code == 200, f"Role {role_name} should have access to /forecast/revenue, got {resp.status_code}"
        data = resp.json()
        assert "predicted_revenue" in data
        assert "model_used" in data

    # Forbidden role: Sales Executive -> 403
    exec_headers = {"Authorization": f"Bearer {tokens['exec']}"}
    resp_exec = client.get("/forecast/revenue", headers=exec_headers)
    assert resp_exec.status_code == 403, f"Sales Executive must receive 403 on /forecast/revenue, got {resp_exec.status_code}"

def test_forecast_series_rbac_access_matrix(client, tokens):
    """Verify Sales Executive receives 403 on /forecast/series while others receive 200."""
    for role_name in ["owner", "manager", "admin"]:
        headers = {"Authorization": f"Bearer {tokens[role_name]}"}
        resp = client.get("/forecast/series", headers=headers)
        assert resp.status_code == 200, f"Role {role_name} should have access to /forecast/series"

    exec_headers = {"Authorization": f"Bearer {tokens['exec']}"}
    resp_exec = client.get("/forecast/series", headers=exec_headers)
    assert resp_exec.status_code == 403, "Sales Executive must receive 403 on /forecast/series"

def test_reports_business_rbac_and_download(client, tokens):
    """Verify Sales Executive receives 403 on /reports/business while Owner downloads 200 Excel."""
    exec_headers = {"Authorization": f"Bearer {tokens['exec']}"}
    resp_exec = client.get("/reports/business", headers=exec_headers)
    assert resp_exec.status_code == 403, "Sales Executive must receive 403 on /reports/business"

    owner_headers = {"Authorization": f"Bearer {tokens['owner']}"}
    resp_owner = client.get("/reports/business", headers=owner_headers)
    assert resp_owner.status_code == 200
    assert "spreadsheetml" in resp_owner.headers.get("content-type", "")
    assert len(resp_owner.content) > 1000
