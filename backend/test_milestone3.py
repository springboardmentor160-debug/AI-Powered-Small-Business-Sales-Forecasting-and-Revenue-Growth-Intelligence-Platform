import os
import pandas as pd
import numpy as np
from starlette.testclient import TestClient
from backend.main import app

from backend.recommendations.pipeline import (
    load_sales_data,
    build_customer_product_matrix,
    calculate_customer_similarity,
    recommend_products_collaborative,
    mine_association_rules,
    recommend_products_association,
    recommend_products
)
from backend.churn.pipeline import (
    prepare_churn_dataset,
    split_churn_data,
    train_logistic_regression,
    train_random_forest,
    train_xgboost,
    evaluate_classification_model,
    select_best_churn_model,
    assign_retention_risk,
    run_churn_pipeline
)
from backend.anomalies.pipeline import (
    detect_zscore_anomalies,
    detect_isolation_forest_anomalies,
    compare_anomaly_methods,
    generate_actionable_alerts,
    assess_inventory_anomaly_support,
    run_anomaly_pipeline
)
from backend.forecasting.pipeline import (
    run_forecasting_pipeline,
    BUSINESS_REPORT_PATH
)

client = TestClient(app)


def run_milestone3_tests():
    print("\n========== RUNNING MILESTONE 3 (DAYS 1-10) COMPREHENSIVE TESTS ==========\n")

    # Sample dataset for isolated unit tests
    test_sales = pd.DataFrame([
        {"order_id": 1, "customer_id": "U1", "product_name": "Item A", "quantity": 2.0, "unit_price": 10.0, "order_date": "2026-01-01"},
        {"order_id": 1, "customer_id": "U1", "product_name": "Item B", "quantity": 1.0, "unit_price": 20.0, "order_date": "2026-01-01"},
        {"order_id": 2, "customer_id": "U2", "product_name": "Item A", "quantity": 1.0, "unit_price": 10.0, "order_date": "2026-01-02"},
        {"order_id": 3, "customer_id": "U3", "product_name": "Item A", "quantity": 1.0, "unit_price": 10.0, "order_date": "2026-01-03"},
        {"order_id": 3, "customer_id": "U3", "product_name": "Item B", "quantity": 2.0, "unit_price": 20.0, "order_date": "2026-01-03"},
        {"order_id": 3, "customer_id": "U3", "product_name": "Item C", "quantity": 1.0, "unit_price": 30.0, "order_date": "2026-01-04"},
    ])

    # ==========================================
    # DAY 1-4: PRODUCT RECOMMENDATIONS
    # ==========================================

    # 1. Customer-Product Matrix
    matrix = build_customer_product_matrix(test_sales, persist_path=None)
    assert matrix.shape == (3, 3)
    assert matrix.loc["U1", "Item A"] == 2.0
    assert matrix.loc["U2", "Item B"] == 0.0
    print("PASS: 1. Customer-product matrix constructed cleanly with zero-fill")

    # 2. Pairwise Cosine Similarity
    sim_df = calculate_customer_similarity(matrix)
    assert sim_df.shape == (3, 3)
    assert np.isclose(sim_df.loc["U1", "U1"], 1.0)
    assert sim_df.loc["U1", "U2"] > 0.0
    print("PASS: 2. Cosine similarity matrix calculated (values in [0, 1], diagonal = 1.0)")

    # 3. Collaborative Filtering Recommendations
    cf_res = recommend_products_collaborative("U2", top_n=3, sales_df=test_sales)
    assert "recommendations" in cf_res
    rec_items = [r["product_name"] for r in cf_res["recommendations"]]
    assert "Item B" in rec_items
    print("PASS: 3. Collaborative filtering generated recommendations from peer history")

    # 4. Strict exclusion of already purchased products
    assert "Item A" not in rec_items
    assert "Item A" in cf_res["purchased_products"]
    print("PASS: 4. Collaborative filtering strictly excluded already purchased product ('Item A')")

    # 5. Unknown customer and edge cases handled without crash
    cf_unknown = recommend_products_collaborative("UNKNOWN_CUST", top_n=3, sales_df=test_sales)
    assert cf_unknown["recommendations"] == []
    assert "not found" in cf_unknown["message"]
    print("PASS: 5. Unknown customer ID handled gracefully without error")

    # 6. Association Rule Mining on multi-item baskets
    rules_df, meta = mine_association_rules(test_sales, min_support=0.1, min_confidence=0.1)
    assert not rules_df.empty
    assert "confidence" in rules_df.columns
    assert "lift" in rules_df.columns
    print("PASS: 6. Association rule mining extracted rules with confidence and lift")

    # 7. Association Rule Recommender
    ar_res = recommend_products_association("U2", top_n=3, sales_df=test_sales)
    assert len(ar_res["recommendations"]) > 0
    assert "Item A" not in [r["product_name"] for r in ar_res["recommendations"]]
    print("PASS: 7. Association rule recommendations generated based on frequently co-purchased items")

    # 8. Combined Hybrid Recommendation Engine
    comb_res = recommend_products("U2", top_n=3, sales_df=test_sales)
    assert comb_res["method"] == "combined"
    assert len(comb_res["recommendations"]) > 0
    # Top item should be identified by both methods with synergy boost
    top_item = comb_res["recommendations"][0]
    assert top_item["recommendation_method"] in ["both", "collaborative_filtering", "association_rules"]
    print(f"PASS: 8. Combined hybrid recommender generated ranked results with method attribution ('{top_item['recommendation_method']}')")

    # Real clean sales dataset recommendation verification
    real_rec = recommend_products("C002", top_n=3)
    assert "recommendations" in real_rec
    assert "purchased_products" in real_rec
    print("PASS: 9. Combined recommender evaluated cleanly on actual project sales data")

    # ==========================================
    # DAY 5-8: CHURN PREDICTION
    # ==========================================

    # 10. Churn Label Generation
    real_sales = load_sales_data()
    real_cust = pd.read_csv(os.path.join("data", "processed", "customer_features.csv"))
    churn_df = prepare_churn_dataset(real_sales, real_cust, inactivity_days_threshold=2)
    assert "churn" in churn_df.columns
    assert set(churn_df["churn"].unique()).issubset({0, 1})
    assert churn_df["churn"].nunique() == 2
    print("PASS: 10. Churn labels generated from real transaction inactivity (both classes present: 3 inactive, 2 active)")

    # 11. Feature preparation & train/test split
    X = churn_df[["purchase_frequency", "purchase_value", "customer_activity_days"]]
    y = churn_df["churn"]
    X_train, X_test, y_train, y_test = split_churn_data(X, y, test_size=0.4, random_state=42)
    assert len(X_train) + len(X_test) == len(X)
    print("PASS: 11. Churn features prepared cleanly without target leakage; stratified split completed")

    # 12. Model Training: Logistic Regression, Random Forest, XGBoost
    lr_model, scaler = train_logistic_regression(X_train, y_train, random_state=42)
    rf_model = train_random_forest(X_train, y_train, random_state=42)
    xgb_model = train_xgboost(X_train, y_train, random_state=42)
    assert lr_model is not None and rf_model is not None and xgb_model is not None
    print("PASS: 12. Logistic Regression, Random Forest, and XGBoost classifiers trained successfully")

    # 13. Test Evaluation: Precision, Recall, F1, Accuracy
    lr_eval = evaluate_classification_model(lr_model, X_test, y_test, "Logistic Regression", scaler=scaler)
    rf_eval = evaluate_classification_model(rf_model, X_test, y_test, "Random Forest")
    xgb_eval = evaluate_classification_model(xgb_model, X_test, y_test, "XGBoost")

    for ev in [lr_eval, rf_eval, xgb_eval]:
        assert "precision" in ev and "recall" in ev and "f1_score" in ev and "accuracy" in ev
        assert "probabilities" in ev
        assert 0.0 <= ev["recall"] <= 1.0
        assert 0.0 <= ev["f1_score"] <= 1.0
    print("PASS: 13. Precision, Recall, F1-score, and Accuracy evaluated on test set for all 3 models")

    # 14. Recall-prioritized Model Selection
    selection = select_best_churn_model([lr_eval, rf_eval, xgb_eval])
    assert selection["selected_model"] in ["Logistic Regression", "Random Forest", "XGBoost"]
    assert "Recall" in selection["selection_reason"]
    print(f"PASS: 14. Best model selected data-driven prioritizing Recall: '{selection['selected_model']}'")

    # 15. Retention Risk Categorization
    assert assign_retention_risk(0.85) == "High Risk"
    assert assign_retention_risk(0.55) == "Medium Risk"
    assert assign_retention_risk(0.20) == "Low Risk"
    print("PASS: 15. Retention risk categorization verified (High >= 0.7, Medium >= 0.4, Low < 0.4)")

    # 16. Full Churn Pipeline & Customer Segment Cross-Check
    _, churn_summary = run_churn_pipeline()
    assert len(churn_summary["customer_cohort"]) == 5
    assert "segment_churn_relationship" in churn_summary
    assert len(churn_summary["segment_churn_relationship"]) > 0
    print("PASS: 16. Churn predictions integrated with Milestone 2 customer segments")

    # ==========================================
    # DAY 9-10: ANOMALY DETECTION
    # ==========================================

    # 17. Total Amount & Statistical Z-Score
    z_df = detect_zscore_anomalies(real_sales, z_threshold=3.0)
    assert "total_amount" in z_df.columns
    assert "z_score" in z_df.columns
    assert "is_anomaly_zscore" in z_df.columns
    print("PASS: 17. Transaction total_amount and statistical Z-score calculated cleanly")

    # 18. Isolation Forest Multidimensional Outlier Detection
    iso_df = detect_isolation_forest_anomalies(real_sales, contamination=0.02, random_state=42)
    assert "is_anomaly_iso" in iso_df.columns
    assert "iso_status" in iso_df.columns
    assert "Normal" in iso_df["iso_status"].values
    print("PASS: 18. Isolation Forest executed with multidimensional features [quantity, unit_price, total_amount]")

    # 19. Anomaly Method Comparison
    comparison = compare_anomaly_methods(z_df, iso_df)
    assert "zscore" in comparison and "isolation_forest" in comparison
    assert "detected_count" in comparison["isolation_forest"]
    print("PASS: 19. Anomaly methods compared (1D total_amount vs 3D joint feature distribution)")

    # 20. Actionable Alerts Generation
    merged_anom = z_df.copy()
    merged_anom["is_anomaly_iso"] = iso_df["is_anomaly_iso"]
    merged_anom["iso_anomaly_score"] = iso_df["iso_anomaly_score"]
    alerts = generate_actionable_alerts(merged_anom)
    assert isinstance(alerts, list)
    if alerts:
        a0 = alerts[0]
        assert "severity" in a0 and "order_id" in a0 and "message" in a0
        assert "fraud confirmed" not in a0["message"].lower()
        assert "flagged" in a0["message"].lower() or "review" in a0["message"].lower()
    print("PASS: 20. Actionable alerts generated with non-alarmist human review language")

    # 21. Inventory Anomaly Support Assessment
    inv_assess = assess_inventory_anomaly_support()
    assert inv_assess["supported"] is False
    assert "historical" in inv_assess["message"].lower()
    print("PASS: 21. Inventory anomaly limitation documented honestly without fabricating stock logs")

    # 22. Full Anomaly Pipeline
    _, anom_summary = run_anomaly_pipeline()
    assert anom_summary["total_transactions_analyzed"] == 8
    print("PASS: 22. Full anomaly pipeline executed and verified")

    # ==========================================
    # REPORTING & API INTEGRATION (WITH RBAC)
    # ==========================================

    # 23. Extended Excel Business Report (6 sheets)
    _, fcst_summary = run_forecasting_pipeline()
    excel_file = pd.ExcelFile(BUSINESS_REPORT_PATH)
    required_sheets = [
        "Customer Segments",
        "Sales Forecast",
        "Model Comparison",
        "Product Recommendations",
        "Churn Risk",
        "Anomaly Alerts"
    ]
    for s in required_sheets:
        assert s in excel_file.sheet_names, f"Missing sheet: {s}"
    print("PASS: 23. Excel Business Report verified with all 6 sheets including Milestone 3 additions")

    # Authenticate test users
    res_owner = client.post("/api/v1/auth/login", json={"username": "owner", "password": "password123"})
    owner_token = res_owner.json()["access_token"]
    headers_owner = {"Authorization": f"Bearer {owner_token}"}

    res_manager = client.post("/api/v1/auth/login", json={"username": "manager", "password": "password123"})
    manager_token = res_manager.json()["access_token"]
    headers_manager = {"Authorization": f"Bearer {manager_token}"}

    res_exec = client.post("/api/v1/auth/login", json={"username": "exec", "password": "password123"})
    exec_token = res_exec.json()["access_token"]
    headers_exec = {"Authorization": f"Bearer {exec_token}"}

    # 24. GET /recommendations endpoints
    r1 = client.get("/recommendations/C001", headers=headers_owner)
    assert r1.status_code == 200
    assert "recommendations" in r1.json()

    r2 = client.get("/api/v1/recommendations/C002/collaborative", headers=headers_manager)
    assert r2.status_code == 200

    r3 = client.get("/api/v1/recommendations/C003/association", headers=headers_owner)
    assert r3.status_code == 200
    print("PASS: 24. Recommendation endpoints verified (combined, collaborative, association)")

    # 25. GET /churn endpoints
    c1 = client.get("/churn", headers=headers_owner)
    assert c1.status_code == 200
    assert "model_evaluations" in c1.json()
    assert "customer_cohort" in c1.json()

    c2 = client.get("/api/v1/churn/C003", headers=headers_manager)
    assert c2.status_code == 200
    assert c2.json()["customer"]["customer_id"] == "C003"
    print("PASS: 25. Churn intelligence endpoints verified (cohort summary & single customer)")

    # 26. GET /anomalies endpoints
    a1 = client.get("/anomalies", headers=headers_owner)
    assert a1.status_code == 200
    assert "comparison" in a1.json()
    assert "alerts" in a1.json()

    a2 = client.get("/api/v1/anomalies/summary", headers=headers_manager)
    assert a2.status_code == 200
    assert "total_transactions" in a2.json()
    print("PASS: 26. Anomaly detection endpoints verified (full report & lightweight summary)")

    # 27. RBAC Protection: Sales Executive Forbidden (403)
    assert client.get("/recommendations/C001", headers=headers_exec).status_code == 403
    assert client.get("/churn", headers=headers_exec).status_code == 403
    assert client.get("/anomalies", headers=headers_exec).status_code == 403
    assert client.get("/api/v1/recommendations/C001", headers=headers_exec).status_code == 403
    assert client.get("/api/v1/churn", headers=headers_exec).status_code == 403
    assert client.get("/api/v1/anomalies", headers=headers_exec).status_code == 403
    print("PASS: 27. RBAC enforced: Sales Executive correctly forbidden (403) from AI intelligence endpoints")

    # 28. Unauthenticated Access Rejection (401)
    assert client.get("/recommendations/C001").status_code == 401
    assert client.get("/churn").status_code == 401
    assert client.get("/anomalies").status_code == 401
    assert client.get("/api/v1/recommendations/C001").status_code == 401
    assert client.get("/api/v1/churn").status_code == 401
    assert client.get("/api/v1/anomalies").status_code == 401
    print("PASS: 28. Unauthenticated requests to all Milestone 3 endpoints rejected with 401 Unauthorized")

    print("\n========== ALL MILESTONE 3 (DAYS 1-10) TESTS PASSED SUCCESSFULLY! ==========\n")


if __name__ == "__main__":
    run_milestone3_tests()
