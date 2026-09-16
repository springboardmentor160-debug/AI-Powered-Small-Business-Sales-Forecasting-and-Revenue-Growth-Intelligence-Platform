from starlette.testclient import TestClient
from backend.main import app
from backend.segmentation.pipeline import run_segmentation_pipeline, extract_customer_features
from backend.forecasting.pipeline import run_forecasting_pipeline, prepare_daily_revenue
import pandas as pd

client = TestClient(app)

def run_milestone2_tests():
    print("\n========== RUNNING MILESTONE 2 (DAYS 1-6) TESTS ==========\n")

    # Load sample sales data for pipeline tests
    sample_df = pd.DataFrame([
        {"order_id": 1001, "customer_id": "C001", "quantity": 3, "unit_price": 45.0, "order_date": "2026-01-05"},
        {"order_id": 1002, "customer_id": "C002", "quantity": 10, "unit_price": 12.0, "order_date": "2026-01-05"},
        {"order_id": 1003, "customer_id": "C001", "quantity": 1, "unit_price": 45.0, "order_date": "2026-01-06"},
        {"order_id": 1004, "customer_id": "C003", "quantity": 5, "unit_price": 30.0, "order_date": "2026-01-07"},
    ])

    # 1. Customer feature generation
    cust_feats = extract_customer_features(sample_df)
    assert len(cust_feats) == 3
    print("PASS: 1. Customer feature generation executed cleanly")

    # 2. Purchase frequency calculation
    c1 = cust_feats[cust_feats['customer_id'] == 'C001'].iloc[0]
    assert c1['purchase_frequency'] == 2
    print("PASS: 2. Purchase frequency calculation verified (C001 = 2)")

    # 3. Purchase value calculation
    assert c1['purchase_value'] == 180.0
    print("PASS: 3. Purchase value calculation verified (C001 = $180.0)")

    # 4. Customer activity calculation
    assert c1['customer_activity_days'] == 2  # 2026-01-05 to 2026-01-06 is 2 days
    print("PASS: 4. Customer activity days calculation verified (C001 = 2 days)")

    # 5-7. Pipeline execution: K-Means, Hierarchical Clustering, and Segment Assignment
    df_seg, seg_summary = run_segmentation_pipeline()
    assert 'cluster' in df_seg.columns
    assert 'cluster_hierarchical' in df_seg.columns
    assert 'segment' in df_seg.columns
    assert len(df_seg) == 5
    print("PASS: 5. K-Means clustering executed with cluster column")
    print("PASS: 6. Hierarchical clustering executed with cluster_hierarchical column")
    print("PASS: 7. Business segment assignment verified:", df_seg['segment'].tolist())

    # 8. Daily revenue generation
    daily_df, missing_info = prepare_daily_revenue(sample_df)
    assert 'date' in daily_df.columns
    assert 'revenue' in daily_df.columns
    print("PASS: 8. Daily revenue dataset prepared cleanly")

    # 9. Missing-date detection
    assert "missing_dates_count" in missing_info
    print(f"PASS: 9. Missing-date detection executed (recorded: {missing_info['recorded_days']}, missing: {missing_info['missing_dates_count']})")

    # 10-12. Prophet Dataframe prep, Prophet fit & 30-day forecast output
    fcst_df, fcst_summary = run_forecasting_pipeline()
    assert 'ds' in fcst_df.columns
    assert 'yhat' in fcst_df.columns
    assert 'yhat_lower' in fcst_df.columns
    assert 'yhat_upper' in fcst_df.columns
    assert len(fcst_summary['future_only_forecast']) == 30
    print("PASS: 10. Prophet dataframe format (ds/y) verified")
    print("PASS: 11. Prophet model fit and forecast generated")
    print("PASS: 12. 30-day forecast output verified (30 days with yhat, yhat_lower, yhat_upper)")

    # 13-15. API & RBAC Tests
    # Login users
    res_owner = client.post("/api/v1/auth/login", json={"username": "owner", "password": "password123"})
    owner_token = res_owner.json()["access_token"]
    headers_owner = {"Authorization": f"Bearer {owner_token}"}

    res_exec = client.post("/api/v1/auth/login", json={"username": "exec", "password": "password123"})
    exec_token = res_exec.json()["access_token"]
    headers_exec = {"Authorization": f"Bearer {exec_token}"}

    # 13. GET /api/v1/segmentation/summary (Owner allowed)
    res = client.get("/api/v1/segmentation/summary", headers=headers_owner)
    assert res.status_code == 200
    assert res.json()["total_customers"] == 5
    print("PASS: 13. GET /api/v1/segmentation/summary authenticated and verified")

    # GET /api/v1/segmentation/customers (Owner allowed)
    res = client.get("/api/v1/segmentation/customers", headers=headers_owner)
    assert res.status_code == 200
    assert len(res.json()) == 5
    print("PASS: 13b. GET /api/v1/segmentation/customers returned 5 records")

    # 14. GET /api/v1/forecasting/summary (Owner allowed)
    res = client.get("/api/v1/forecasting/summary", headers=headers_owner)
    assert res.status_code == 200
    assert res.json()["forecast_horizon"] == 30
    print("PASS: 14. GET /api/v1/forecasting/summary authenticated and verified")

    # 15. RBAC Restrictions for Sales Executive (403 Forbidden)
    res = client.get("/api/v1/segmentation/summary", headers=headers_exec)
    assert res.status_code == 403
    res = client.get("/api/v1/forecasting/summary", headers=headers_exec)
    assert res.status_code == 403
    print("PASS: 15. RBAC verified: Sales Executive correctly rejected (403 Forbidden)")

    # Unauthenticated rejected (401 Unauthorized)
    res = client.get("/api/v1/segmentation/summary")
    assert res.status_code == 401
    res = client.get("/api/v1/forecasting/summary")
    assert res.status_code == 401
    print("PASS: Unauthenticated requests correctly rejected (401 Unauthorized)")

    print("\n========== ALL MILESTONE 2 (DAYS 1-6) TESTS PASSED! ==========\n")


if __name__ == "__main__":
    run_milestone2_tests()
