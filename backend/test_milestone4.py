import os
import pandas as pd
import numpy as np
import pytest
from starlette.testclient import TestClient

from backend.main import app
from backend.forecasting.pipeline import evaluate_forecast_model
from backend.services.model_evaluation import (
    evaluate_forecasting,
    evaluate_segmentation,
    evaluate_churn,
    evaluate_recommendations,
    evaluate_anomalies,
    run_all_evaluations,
    RESULTS_CSV_PATH,
    ANOMALY_FIXTURE_PATH
)

client = TestClient(app)


# ==============================================================================
# 1. SALES FORECASTING EVALUATION TESTS
# ==============================================================================

def test_forecasting_metrics_computation():
    """Verify MAE, RMSE, and R2 calculation with valid and degenerate inputs."""
    y_true = np.array([100.0, 150.0, 200.0])
    y_pred = np.array([110.0, 140.0, 190.0])
    res = evaluate_forecast_model(y_true, y_pred)
    assert res["mae"] == 10.0
    assert round(res["rmse"], 2) == 10.0
    assert res["r2"] is not None and res["r2"] > 0.9

    # Degenerate case: single observation (variance = 0, R2 mathematically undefined)
    single_true = np.array([100.0])
    single_pred = np.array([105.0])
    single_res = evaluate_forecast_model(single_true, single_pred)
    assert single_res["mae"] == 5.0
    assert single_res["rmse"] == 5.0
    assert single_res["r2"] is None, "R2 must be None when test sample variance is 0."


def test_forecasting_pipeline_evaluation_and_overfitting():
    """Verify formal evaluation of Prophet, RF, and XGBoost with overfitting check."""
    fcst_eval = evaluate_forecasting()
    models = fcst_eval["models"]

    assert "Prophet" in models
    assert "Random Forest" in models
    assert "XGBoost" in models

    # Test sample size is 1 day; test R2 must be safely reported as undefined/None
    assert fcst_eval["dataset_info"]["test_samples"] == 1
    assert models["Prophet"]["test"]["r2"] is None
    assert models["Random Forest"]["test"]["r2"] is None
    assert models["XGBoost"]["test"]["r2"] is None

    # Overfitting investigation: XGBoost training MAE is near 0 while test MAE is large
    xgb_train_mae = models["XGBoost"]["train"]["mae"]
    xgb_test_mae = models["XGBoost"]["test"]["mae"]
    assert xgb_train_mae < 1.0, f"Expected XGBoost train MAE < 1.0, got {xgb_train_mae}"
    assert xgb_test_mae > 50.0, f"Expected XGBoost test MAE > 50.0, got {xgb_test_mae}"


# ==============================================================================
# 2. CUSTOMER SEGMENTATION SILHOUETTE EVALUATION TESTS
# ==============================================================================

def test_segmentation_silhouette_evaluation():
    """Verify Silhouette Score on scaled customer features for K-Means and Hierarchical."""
    seg_eval = evaluate_segmentation()
    assert seg_eval["customer_count"] == 5

    # k=4 evaluations
    km_k4 = seg_eval["kmeans_k4"]
    hier_k4 = seg_eval["hierarchical_k4"]
    assert km_k4["silhouette_score"] is not None
    assert hier_k4["silhouette_score"] is not None
    assert abs(km_k4["silhouette_score"] - 0.3215) < 0.01
    assert abs(hier_k4["silhouette_score"] - 0.3215) < 0.01

    # k=5 degenerate case: n_clusters == n_samples
    k5_res = seg_eval["k_sensitivity"]["k=5"]
    assert k5_res["silhouette"] is None
    assert "unavailable" in k5_res["status"]


# ==============================================================================
# 3. CHURN PREDICTION EVALUATION TESTS
# ==============================================================================

def test_churn_evaluation_metrics_and_support():
    """Verify Accuracy, Precision, Recall, and F1-score on held-out test partition."""
    churn_eval = evaluate_churn()
    models = churn_eval["models"]

    for m_name in ["Logistic Regression", "Random Forest", "XGBoost"]:
        assert m_name in models
        m_eval = models[m_name]
        assert "accuracy" in m_eval
        assert "precision" in m_eval
        assert "recall" in m_eval
        assert "f1_score" in m_eval
        # All models predict 1 on test partition of size 2 (1 churned, 1 retained)
        assert m_eval["recall"] == 1.0
        assert m_eval["accuracy"] == 0.5

    assert churn_eval["dataset_info"]["test_size"] == 2


# ==============================================================================
# 4. PRODUCT RECOMMENDATIONS EVALUATION TESTS
# ==============================================================================

def test_recommendations_leave_one_out_evaluation():
    """Verify leave-one-out Precision@K and Recall@K calculation."""
    recs_eval = evaluate_recommendations(k=3)
    assert recs_eval["k"] == 3
    assert recs_eval["evaluated_customers_count"] == 3  # C001, C002, C003
    assert recs_eval["mean_precision_at_k"] == 0.0
    assert recs_eval["mean_recall_at_k"] == 0.0
    assert "limitation_notes" in recs_eval


# ==============================================================================
# 5. ANOMALY DETECTION TEST FIXTURE EVALUATION TESTS
# ==============================================================================

def test_anomaly_detection_fixture_metrics():
    """Verify Detection Accuracy and False Positive Rate on isolated test fixture."""
    assert os.path.exists(ANOMALY_FIXTURE_PATH), "Anomaly fixture must exist."
    anom_eval = evaluate_anomalies(ANOMALY_FIXTURE_PATH)

    fixture_info = anom_eval["fixture_info"]
    assert fixture_info["total_transactions"] == 20
    assert fixture_info["normal_cases"] == 16
    assert fixture_info["injected_anomalies"] == 4

    detectors = anom_eval["detectors"]
    # Z-Score detector
    z_eval = detectors["Z-Score Detector (threshold=2.0)"]
    assert z_eval["detection_accuracy"] >= 0.85
    assert z_eval["false_positive_rate"] == 0.0

    # Isolation Forest
    iso_eval = detectors["Isolation Forest (contamination=0.20)"]
    assert iso_eval["detection_accuracy"] >= 0.95
    assert iso_eval["false_positive_rate"] == 0.0


# ==============================================================================
# 6. UNIFIED CSV PERSISTENCE TESTS
# ==============================================================================

def test_unified_csv_persistence():
    """Verify that milestone4_test_results.csv is generated with required schema."""
    summary, df = run_all_evaluations(RESULTS_CSV_PATH)
    assert os.path.exists(RESULTS_CSV_PATH)

    required_cols = [
        "module",
        "model",
        "metric",
        "value",
        "evaluation_date",
        "sample_count",
        "evaluation_notes"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required CSV column: {col}"

    assert len(df) >= 30, f"Expected at least 30 evaluation records, got {len(df)}"

    modules_in_csv = set(df["module"])
    assert "Sales Forecasting" in modules_in_csv
    assert "Customer Segmentation" in modules_in_csv
    assert "Churn Prediction" in modules_in_csv
    assert "Product Recommendations" in modules_in_csv
    assert "Anomaly Detection" in modules_in_csv

    # Confirm unavailable values are recorded explicitly
    unavailable_records = df[df["value"] == "unavailable"]
    assert not unavailable_records.empty, "Undefined metrics must be recorded as 'unavailable'."


# ==============================================================================
# 7. BACKEND API & RBAC INTEGRATION TESTS
# ==============================================================================

def test_health_check_endpoints():
    """Verify root and container health endpoints return 200."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json() == {"message": "MarketMind AI API is running"}

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_v1_health = client.get("/api/v1/health")
    assert res_v1_health.status_code == 200
    assert res_v1_health.json()["status"] == "healthy"


def test_evaluation_api_endpoints_and_rbac():
    """Verify evaluation API endpoints, authentication, and RBAC enforcement."""
    # 1. Login as owner
    login_res = client.post("/api/v1/auth/login", json={"username": "owner", "password": "password123"})
    assert login_res.status_code == 200
    owner_token = login_res.json()["access_token"]
    headers_owner = {"Authorization": f"Bearer {owner_token}"}

    # 2. Login as sales executive
    exec_login = client.post("/api/v1/auth/login", json={"username": "exec", "password": "password123"})
    assert exec_login.status_code == 200
    exec_token = exec_login.json()["access_token"]
    headers_exec = {"Authorization": f"Bearer {exec_token}"}

    # 3. GET /api/v1/evaluation/summary as Owner -> 200
    res_eval = client.get("/api/v1/evaluation/summary", headers=headers_owner)
    assert res_eval.status_code == 200
    assert "records" in res_eval.json()

    # 4. GET /api/v1/evaluation/download-csv as Owner -> 200
    res_csv = client.get("/api/v1/evaluation/download-csv", headers=headers_owner)
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers.get("content-type", "")

    # 5. RBAC check: Sales Executive forbidden (403)
    res_exec_eval = client.get("/api/v1/evaluation/summary", headers=headers_exec)
    assert res_exec_eval.status_code == 403

    # 6. Unauthenticated request rejected (401)
    res_unauth = client.get("/api/v1/evaluation/summary")
    assert res_unauth.status_code == 401


def test_single_customer_segment_endpoint():
    """Verify /api/v1/segmentation/customers/{customer_id} returns 200 for valid and 404 for missing."""
    login_res = client.post("/api/v1/auth/login", json={"username": "owner", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Valid customer C001
    res_c1 = client.get("/api/v1/segmentation/customers/C001", headers=headers)
    assert res_c1.status_code == 200
    assert res_c1.json()["customer_id"] == "C001"
    assert "segment" in res_c1.json()

    # Non-existent customer -> 404
    res_404 = client.get("/api/v1/segmentation/customers/NON_EXISTENT_999", headers=headers)
    assert res_404.status_code == 404
    assert "not found" in res_404.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main(["-v", "backend/test_milestone4.py"])
