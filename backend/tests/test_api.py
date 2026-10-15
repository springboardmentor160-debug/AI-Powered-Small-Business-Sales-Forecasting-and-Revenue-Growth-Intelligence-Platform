import pytest
from conftest import login


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok", "database": "ok"}


def test_register_and_login(client):
    r = client.post("/register", json={"name": "Alice Owner", "email": "Alice@Test.local", "password": "Password123", "role": "business_owner"})
    assert r.status_code == 201 and r.json()["email"] == "alice@test.local" and r.json()["role"] == "business_owner"
    assert client.post("/register", json={"name": "Alice Again", "email": "alice@test.local", "password": "Password123"}).status_code == 400
    assert client.post("/login", json={"email": "alice@test.local", "password": "wrong-password"}).status_code == 401
    assert login(client, "alice@test.local", "Password123")


def test_register_cannot_create_admin_and_validates_input(client):
    base = {"name": "Mallory", "email": "mal@test.local", "password": "Password123"}
    assert client.post("/register", json={**base, "role": "admin"}).status_code == 403
    assert client.post("/register", json={**base, "password": "short"}).status_code == 422
    assert client.post("/register", json={**base, "email": "not-an-email"}).status_code == 422


def test_protected_endpoints_need_a_valid_token(client):
    assert client.get("/sales/summary").status_code == 401
    assert client.get("/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_me_lists_role_features(client, make_user):
    h = make_user("sales_executive")
    me = client.get("/me", headers=h).json()
    assert me["role"] == "sales_executive" and "forecast" not in me["features"] and "invoice_create" in me["features"]


def test_sales_summary_and_trend_use_the_database(client, make_user):
    h = make_user("store_manager")
    s = client.get("/sales/summary", headers=h).json()
    assert s["total_orders"] == 40 and s["total_units"] == 400
    assert s["total_revenue"] == pytest.approx(10 * 10 * 2 * 10 + 10 * 20 * 2 * 10)     # 10 days x 2 stores x (10*10 + 10*20)
    assert s["latest_date"] == "2024-01-10" and s["low_stock_count"] == 1 and s["top_product"] == "P0002"
    trend = client.get("/sales/trend?days=7", headers=h).json()
    assert len(trend) == 7 and trend[0]["date"] < trend[-1]["date"]
    assert client.get("/sales/trend?days=3", headers=h).status_code == 422          # below the allowed minimum


def test_sales_breakdowns(client, make_user):
    h = make_user("business_owner")
    cats = {c["category"]: c for c in client.get("/sales/by-category", headers=h).json()}
    assert cats["Toys"]["revenue"] == pytest.approx(4000.0) and cats["Groceries"]["share_pct"] == pytest.approx(33.3, abs=0.1)
    assert len(client.get("/sales/by-store", headers=h).json()) == 2
    assert client.get("/sales/top-products?limit=1", headers=h).json()[0]["product_id"] == "P0002"


def test_inventory_alerts_and_summary(client, make_user):
    h = make_user("store_manager")
    a = client.get("/inventory/alerts", headers=h).json()
    assert a["date"] == "2024-01-10" and len(a["alerts"]) == 1 and a["alerts"][0]["shortfall"] == 15
    s = client.get("/inventory/summary", headers=h).json()
    assert s["total_items"] == 4 and s["status_counts"]["critical"] == 1 and s["most_urgent"][0]["suggested_reorder_qty"] == 25
    assert client.get("/inventory/alerts", headers=make_user("sales_executive")).status_code == 403


def test_forecast_access_matrix(client, make_user):
    assert client.get("/forecast/revenue", headers=make_user("sales_executive")).status_code == 403
    assert client.get("/forecast/revenue", headers=make_user("business_owner")).status_code in (200, 503)   # 503 only if ML outputs are absent


def test_ml_backed_endpoints_serve_real_output_files(client, make_user):
    h = make_user("business_owner")
    for path in ("/segments", "/segments/metrics", "/churn/risk", "/anomalies", "/models/performance", "/recommendations"):
        r = client.get(path, headers=h)
        assert r.status_code in (200, 503), (path, r.text)       # 503 = ml/outputs not generated yet (see README)
    assert client.get("/models/performance", headers=make_user("sales_executive")).status_code == 403


def test_invoices_lifecycle(client, make_user):
    sales, owner = make_user("sales_executive"), make_user("business_owner")
    r = client.post("/invoices", headers=sales, json={"customer_id": "12345", "description": "Order", "amount": 99.5})
    assert r.status_code == 201 and r.json()["payment_status"] == "pending"
    inv_id = r.json()["id"]
    assert client.post("/invoices", headers=owner, json={"customer_id": "1", "amount": 5}).status_code == 403
    assert client.post("/invoices", headers=sales, json={"customer_id": "1", "amount": -5}).status_code == 422
    assert client.patch(f"/invoices/{inv_id}", headers=sales, json={"payment_status": "paid"}).json()["payment_status"] == "paid"
    assert client.patch(f"/invoices/{inv_id}", headers=sales, json={"payment_status": "bogus"}).status_code == 422
    assert client.get(f"/invoices/{inv_id}", headers=owner).json()["amount"] == 99.5
    assert client.get("/invoices/999999", headers=owner).status_code == 404
    assert any(i["id"] == inv_id for i in client.get("/invoices", headers=owner).json())


def test_admin_user_management(client, admin, make_user):
    assert client.get("/admin/users", headers=make_user("store_manager")).status_code == 403
    r = client.post("/admin/users", headers=admin, json={"name": "New Admin", "email": "newadmin@test.local", "password": "Password123", "role": "admin"})
    assert r.status_code == 201 and r.json()["role"] == "admin"
    users = client.get("/admin/users", headers=admin).json()
    assert any(u["email"] == "admin@test.local" for u in users)
    uid = r.json()["id"]
    assert client.delete(f"/admin/users/{uid}", headers=admin).status_code == 204
    me_id = next(u["id"] for u in users if u["email"] == "admin@test.local")
    assert client.delete(f"/admin/users/{me_id}", headers=admin).status_code == 400
    assert client.delete("/admin/users/999999", headers=admin).status_code == 404


def test_deleted_user_token_stops_working_and_invoices_survive(client, admin, make_user):
    sales = make_user("sales_executive")
    inv = client.post("/invoices", headers=sales, json={"customer_id": "777", "amount": 10}).json()
    uid = next(u["id"] for u in client.get("/admin/users", headers=admin).json() if u["role"] == "sales_executive" and u["email"] == client.get("/me", headers=sales).json()["email"])
    assert client.delete(f"/admin/users/{uid}", headers=admin).status_code == 204
    assert client.get("/me", headers=sales).status_code == 401
    assert client.get(f"/invoices/{inv['id']}", headers=admin).status_code == 200
