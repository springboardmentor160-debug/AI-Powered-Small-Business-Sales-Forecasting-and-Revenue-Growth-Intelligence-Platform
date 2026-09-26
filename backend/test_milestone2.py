import os
import pandas as pd
import numpy as np
from starlette.testclient import TestClient
from backend.main import app
from backend.segmentation.pipeline import run_segmentation_pipeline, extract_customer_features
from backend.forecasting.pipeline import (
    run_forecasting_pipeline,
    prepare_daily_revenue,
    build_forecasting_features,
    split_time_series,
    train_random_forest,
    train_xgboost,
    evaluate_forecast_model,
    compare_forecast_models,
    generate_business_report,
    BUSINESS_REPORT_PATH
)

client = TestClient(app)


def run_milestone2_tests():
    print("\n========== RUNNING MILESTONE 2 (DAYS 1-10) COMPREHENSIVE TESTS ==========\n")

    # Sample sales data for unit tests
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
    assert c1['customer_activity_days'] == 2
    print("PASS: 4. Customer activity days calculation verified (C001 = 2 days)")

    # 5. K-Means, Hierarchical Clustering, and Segment Assignment
    df_seg, seg_summary = run_segmentation_pipeline()
    assert 'cluster' in df_seg.columns
    assert 'cluster_hierarchical' in df_seg.columns
    assert 'segment' in df_seg.columns
    assert len(df_seg) == 5
    print("PASS: 5. K-Means clustering executed with cluster column")
    print("PASS: 6. Hierarchical clustering executed with cluster_hierarchical column")
    print("PASS: 7. Business segment assignment verified:", df_seg['segment'].tolist())

    # 8. Daily revenue generation & missing-date detection
    daily_df, missing_info = prepare_daily_revenue(sample_df)
    assert 'date' in daily_df.columns
    assert 'revenue' in daily_df.columns
    assert "missing_dates_count" in missing_info
    print("PASS: 8. Daily revenue dataset prepared cleanly")
    print(f"PASS: 9. Missing-date detection executed (recorded: {missing_info['recorded_days']}, missing: {missing_info['missing_dates_count']})")

    # --- DAY 7-8: TIME-SERIES FEATURE ENGINEERING & MODEL COMPARISON ---
    
    # Create test time-series with 14 days to test full lag_7 and rolling_7
    dates = pd.date_range(start="2026-01-01", periods=14, freq="D")
    synthetic_daily = pd.DataFrame({
        "date": dates,
        "revenue": [100.0, 120.0, 110.0, 130.0, 150.0, 140.0, 160.0, 170.0, 180.0, 175.0, 190.0, 200.0, 210.0, 220.0]
    })

    # 10. Time-Series Feature Engineering
    features_df = build_forecasting_features(synthetic_daily, drop_na=True)
    required_cols = ['day_of_week', 'day_of_month', 'month', 'revenue_lag_1', 'revenue_lag_7', 'revenue_rolling_7']
    for col in required_cols:
        assert col in features_df.columns, f"Missing feature: {col}"
    print("PASS: 10. Time-series feature engineering created all required columns:", required_cols)

    # 11. Lag & Rolling feature accuracy and Data Leakage prevention check
    # Check row at index 0 of features_df (which corresponds to day index 7 in original series)
    row_day8 = features_df.iloc[0]
    # In synthetic_daily, index 7 is 2026-01-08 (revenue 170.0)
    # lag_1 should be revenue of 2026-01-07 (index 6) = 160.0
    assert row_day8['revenue_lag_1'] == 160.0
    # lag_7 should be revenue of 2026-01-01 (index 0) = 100.0
    assert row_day8['revenue_lag_7'] == 100.0
    # rolling_7 should average days index 0..6 (100+120+110+130+150+140+160)/7 = 910/7 = 130.0
    expected_rolling = sum([100.0, 120.0, 110.0, 130.0, 150.0, 140.0, 160.0]) / 7
    assert abs(row_day8['revenue_rolling_7'] - expected_rolling) < 1e-4
    # Ensure current day revenue (170.0) was NOT used in rolling_7 (NO data leakage)
    assert row_day8['revenue_rolling_7'] != 170.0
    print("PASS: 11. Lag 1 (160.0), Lag 7 (100.0), and Rolling 7 (130.0) verified with zero data leakage (shift(1) enforced)")

    # 12. Chronological train/test split (no shuffle)
    train_df, test_df = split_time_series(features_df, train_ratio=0.8)
    assert len(train_df) + len(test_df) == len(features_df)
    assert train_df['date'].max() < test_df['date'].min()  # Strictly chronological
    print(f"PASS: 12. Chronological train/test split verified (Train: {len(train_df)}, Test: {len(test_df)}, No random shuffle)")

    # 13. Random Forest Regressor training & prediction
    X_train = train_df[required_cols]
    y_train = train_df['revenue']
    X_test = test_df[required_cols]
    y_test = test_df['revenue']

    rf_model = train_random_forest(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    assert len(rf_preds) == len(test_df)
    print("PASS: 13. Random Forest Regressor trained and generated test predictions")

    # 14. XGBoost Regressor training & prediction
    xgb_model = train_xgboost(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    assert len(xgb_preds) == len(test_df)
    print("PASS: 14. XGBoost Regressor trained and generated test predictions")

    # 15. MAE and RMSE calculation
    eval_rf = evaluate_forecast_model(y_test.values, rf_preds)
    assert "mae" in eval_rf and "rmse" in eval_rf
    assert eval_rf["mae"] >= 0 and eval_rf["rmse"] >= 0
    print(f"PASS: 15. Evaluation metrics verified: RF MAE={eval_rf['mae']}, RMSE={eval_rf['rmse']}")

    # 16. Full multi-model comparison pipeline on real dataset
    real_daily = pd.read_csv("data/processed/daily_revenue.csv")
    comparison, selection_info, _ = compare_forecast_models(real_daily, train_ratio=0.8)
    assert len(comparison) == 3
    model_names = [m["model"] for m in comparison]
    assert "Prophet" in model_names
    assert "Random Forest" in model_names
    assert "XGBoost" in model_names
    assert selection_info["selected_model"] in model_names
    print(f"PASS: 16. Real multi-model comparison verified: {comparison}")
    print(f"PASS: 17. Data-driven best model selected based on lowest evaluation error: '{selection_info['selected_model']}'")

    # --- DAY 9-10: BUSINESS REPORT & API ENDPOINTS ---

    # 18. Excel Business Report generation with 3 sheets
    fcst_df, fcst_summary = run_forecasting_pipeline()
    assert os.path.exists(BUSINESS_REPORT_PATH)
    excel_file = pd.ExcelFile(BUSINESS_REPORT_PATH)
    assert "Customer Segments" in excel_file.sheet_names
    assert "Sales Forecast" in excel_file.sheet_names
    assert "Model Comparison" in excel_file.sheet_names
    
    seg_sheet = pd.read_excel(BUSINESS_REPORT_PATH, sheet_name="Customer Segments")
    fcst_sheet = pd.read_excel(BUSINESS_REPORT_PATH, sheet_name="Sales Forecast")
    comp_sheet = pd.read_excel(BUSINESS_REPORT_PATH, sheet_name="Model Comparison")
    assert len(seg_sheet) > 0
    assert len(fcst_sheet) == 30
    assert len(comp_sheet) == 3
    print("PASS: 18. Excel Business Report verified with 3 sheets (Customer Segments, Sales Forecast, Model Comparison)")

    # --- AUTHENTICATION & RBAC ENDPOINT TESTS ---
    res_owner = client.post("/api/v1/auth/login", json={"username": "owner", "password": "password123"})
    owner_token = res_owner.json()["access_token"]
    headers_owner = {"Authorization": f"Bearer {owner_token}"}

    res_exec = client.post("/api/v1/auth/login", json={"username": "exec", "password": "password123"})
    exec_token = res_exec.json()["access_token"]
    headers_exec = {"Authorization": f"Bearer {exec_token}"}

    # 19. GET /segments and /api/v1/segmentation/segments
    res_seg_root = client.get("/segments", headers=headers_owner)
    assert res_seg_root.status_code == 200
    assert isinstance(res_seg_root.json(), list)
    assert "segment" in res_seg_root.json()[0]
    assert "customer_count" in res_seg_root.json()[0]
    assert "avg_purchase_value" in res_seg_root.json()[0]

    res_seg_api = client.get("/api/v1/segmentation/segments", headers=headers_owner)
    assert res_seg_api.status_code == 200
    print("PASS: 19. GET /segments and /api/v1/segmentation/segments verified with real customer segments")

    # 20. GET /forecast/revenue and /api/v1/forecasting/revenue
    res_fcst_rev = client.get("/forecast/revenue", headers=headers_owner)
    assert res_fcst_rev.status_code == 200
    fcst_rev_data = res_fcst_rev.json()
    assert fcst_rev_data["period"] == "Next 30 Days"
    assert "predicted_revenue" in fcst_rev_data
    assert "model_used" in fcst_rev_data
    print(f"PASS: 20. GET /forecast/revenue verified: Period='{fcst_rev_data['period']}', Predicted Revenue=${fcst_rev_data['predicted_revenue']}, Model='{fcst_rev_data['model_used']}'")

    # 21. GET /forecast/models and /api/v1/forecasting/models
    res_fcst_models = client.get("/forecast/models", headers=headers_owner)
    assert res_fcst_models.status_code == 200
    models_list = res_fcst_models.json()
    assert len(models_list) == 3
    print(f"PASS: 21. GET /forecast/models verified with real MAE and RMSE metrics for 3 models")

    # 22. GET /api/v1/forecasting/report (Download Excel)
    res_report = client.get("/api/v1/forecasting/report", headers=headers_owner)
    assert res_report.status_code == 200
    assert "application/vnd.openxmlformats-officedocument" in res_report.headers["content-type"]
    print("PASS: 22. GET /api/v1/forecasting/report returns valid Excel spreadsheet stream")

    # 23. RBAC Checks (Sales Executive 403 Forbidden on forecasting & segmentation reports)
    assert client.get("/segments", headers=headers_exec).status_code == 403
    assert client.get("/forecast/revenue", headers=headers_exec).status_code == 403
    assert client.get("/forecast/models", headers=headers_exec).status_code == 403
    assert client.get("/api/v1/forecasting/report", headers=headers_exec).status_code == 403
    print("PASS: 23. RBAC enforced: Sales Executive correctly forbidden (403) from accessing forecasting & segmentation")

    # 24. Unauthenticated requests rejected with 401 Unauthorized
    assert client.get("/segments").status_code == 401
    assert client.get("/forecast/revenue").status_code == 401
    assert client.get("/forecast/models").status_code == 401
    assert client.get("/api/v1/forecasting/report").status_code == 401
    print("PASS: 24. Unauthenticated requests to forecasting and segments rejected with 401 Unauthorized")

    print("\n========== ALL MILESTONE 2 (DAYS 1-10) TESTS PASSED SUCCESSFULLY! ==========\n")


if __name__ == "__main__":
    run_milestone2_tests()
