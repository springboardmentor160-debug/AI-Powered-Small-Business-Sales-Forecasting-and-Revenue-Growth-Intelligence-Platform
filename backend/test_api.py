from starlette.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_tests():
    print("========== RUNNING BACKEND API TESTS ==========")

    # 1. Health Check
    res = client.get("/")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    assert res.json() == {"message": "MarketMind AI API is running"}
    print("PASS: 1. GET / health check")

    # 2. Login as Owner
    res = client.post("/api/v1/auth/login", json={"username": "owner", "password": "password123"})
    assert res.status_code == 200, f"Owner login failed: {res.text}"
    owner_token = res.json()["access_token"]
    assert res.json()["user"]["role"] == "owner"
    print("PASS: 2. POST /api/v1/auth/login (Owner)")

    # 3. Login as Manager
    res = client.post("/api/v1/auth/login", json={"username": "manager", "password": "password123"})
    assert res.status_code == 200, f"Manager login failed: {res.text}"
    manager_token = res.json()["access_token"]
    assert res.json()["user"]["role"] == "manager"
    print("PASS: 3. POST /api/v1/auth/login (Manager)")

    # 4. Login as Sales Executive
    res = client.post("/api/v1/auth/login", json={"username": "exec", "password": "password123"})
    assert res.status_code == 200, f"Exec login failed: {res.text}"
    exec_token = res.json()["access_token"]
    assert res.json()["user"]["role"] == "sales_executive"
    print("PASS: 4. POST /api/v1/auth/login (Sales Executive)")

    # 5. Login as Admin
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "password123"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["access_token"]
    assert res.json()["user"]["role"] == "admin"
    print("PASS: 5. POST /api/v1/auth/login (Admin)")

    # 6. Wrong password rejected
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 401, f"Expected 401 on wrong password, got {res.status_code}"
    print("PASS: 6. POST /api/v1/auth/login rejected on wrong password (401)")

    # 7. GET /api/v1/auth/me with valid token
    headers_owner = {"Authorization": f"Bearer {owner_token}"}
    res = client.get("/api/v1/auth/me", headers=headers_owner)
    assert res.status_code == 200
    assert res.json()["email"] == "owner@marketmind.ai"
    print("PASS: 7. GET /api/v1/auth/me authenticated")

    # 8. GET /api/v1/sales (Exactly 8 cleaned sales records)
    res = client.get("/api/v1/sales", headers=headers_owner)
    assert res.status_code == 200
    sales = res.json()
    assert len(sales) == 8, f"Expected exactly 8 sales records, got {len(sales)}"
    print(f"PASS: 8. GET /api/v1/sales returned exactly 8 sales records")

    # 9. GET /api/v1/sales/summary
    res = client.get("/api/v1/sales/summary", headers=headers_owner)
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_orders"] == 8, f"Expected 8 orders, got {summary['total_orders']}"
    assert summary["total_units"] == 29, f"Expected 29 units, got {summary['total_units']}"
    assert summary["total_revenue"] == 697.0, f"Expected $697.0, got {summary['total_revenue']}"
    assert summary["average_order_value"] == 87.12, f"Expected $87.12, got {summary['average_order_value']}"
    print(f"PASS: 9. GET /api/v1/sales/summary verified: Revenue=${summary['total_revenue']}, Orders={summary['total_orders']}, Units={summary['total_units']}, Top Product='{summary['top_product']}'")

    # 10. GET /api/v1/inventory
    res = client.get("/api/v1/inventory", headers=headers_owner)
    assert res.status_code == 200
    inv = res.json()
    assert len(inv) == 4
    print(f"PASS: 10. GET /api/v1/inventory returned {len(inv)} items")

    # 11. GET /api/v1/inventory/alerts (stock_level < reorder_point)
    res = client.get("/api/v1/inventory/alerts", headers=headers_owner)
    assert res.status_code == 200
    alerts = res.json()
    alert_names = [a["product_name"] for a in alerts]
    assert "Pen Set" in alert_names and "Marker Box" in alert_names
    assert len(alerts) == 2
    print(f"PASS: 11. GET /api/v1/inventory/alerts found {len(alerts)} low-stock items: {alert_names}")

    # 12. GET /api/v1/analytics/summary
    res = client.get("/api/v1/analytics/summary", headers=headers_owner)
    assert res.status_code == 200
    analytics = res.json()
    assert analytics["total_revenue"] == 697.0
    assert len(analytics["top_products"]) == 4
    assert len(analytics["sales_trend"]) > 0
    print(f"PASS: 12. GET /api/v1/analytics/summary verified with charts and KPI data")

    # 13. RBAC Check: GET /api/v1/users accessible by Admin
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/users", headers=headers_admin)
    assert res.status_code == 200
    users = res.json()
    assert len(users) == 4
    print(f"PASS: 13. GET /api/v1/users successfully returned {len(users)} users for Admin")

    # 14. RBAC Check: GET /api/v1/users FORBIDDEN (403) for Owner
    res = client.get("/api/v1/users", headers=headers_owner)
    assert res.status_code == 403, f"Expected 403 Forbidden for Owner, got {res.status_code}"
    print("PASS: 14. GET /api/v1/users rejected for Owner (403 Forbidden)")

    # 15. RBAC Check: GET /api/v1/users FORBIDDEN (403) for Manager
    headers_manager = {"Authorization": f"Bearer {manager_token}"}
    res = client.get("/api/v1/users", headers=headers_manager)
    assert res.status_code == 403, f"Expected 403 Forbidden for Manager, got {res.status_code}"
    print("PASS: 15. GET /api/v1/users rejected for Manager (403 Forbidden)")

    # 16. RBAC Check: GET /api/v1/users FORBIDDEN (403) for Sales Executive
    headers_exec = {"Authorization": f"Bearer {exec_token}"}
    res = client.get("/api/v1/users", headers=headers_exec)
    assert res.status_code == 403, f"Expected 403 Forbidden for Sales Exec, got {res.status_code}"
    print("PASS: 16. GET /api/v1/users rejected for Sales Exec (403 Forbidden)")

    # 17. Unauthenticated request rejected (401)
    res = client.get("/api/v1/sales")
    assert res.status_code == 401, f"Expected 401 Unauthorized for unauthenticated call, got {res.status_code}"
    print("PASS: 17. Unauthenticated request to protected endpoint rejected (401)")

    print("\n========== ALL 17 BACKEND API TESTS PASSED! ==========\n")


if __name__ == "__main__":
    run_tests()
