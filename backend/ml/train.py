import os
import sys
import json
import pandas as pd

# Add project root and backend directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in [project_root, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.ml.segmentation import build_customer_features, run_segmentation
    from backend.ml.forecasting import prepare_daily_revenue, evaluate_models, run_recursive_forecast
    from backend.ml.reporting import generate_business_report
except ImportError:
    from ml.segmentation import build_customer_features, run_segmentation
    from ml.forecasting import prepare_daily_revenue, evaluate_models, run_recursive_forecast
    from ml.reporting import generate_business_report

def train_all_artifacts(artifacts_dir: str = None) -> dict:
    """
    Executes the entire Milestone 2 machine learning pipeline:
      1. Customer RFM feature engineering & clustering (KMeans & Hierarchical).
      2. Daily revenue time-series aggregation & missing date check.
      3. Forecasting model evaluation (Prophet, Random Forest, XGBoost) on identical test window.
      4. Recursive 30-day ahead forecast generation.
      5. Multi-sheet styled Excel business report generation.
      6. Serialization of all datasets and metrics to artifacts/.
    """
    if artifacts_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    print(">>> Starting Milestone 2 ML Pipeline Execution...")

    # --- 1. Customer Segmentation ---
    print("1. Computing customer features and running clustering...")
    customer_features = build_customer_features()
    seg_results = run_segmentation(customer_features, artifacts_dir=artifacts_dir)
    
    # Save segmented customers CSV
    customers_csv_path = os.path.join(artifacts_dir, "customers_segmented.csv")
    seg_results["customer_features"].to_csv(customers_csv_path, index=False)

    # Save segmentation summary JSON
    seg_summary_json_path = os.path.join(artifacts_dir, "segmentation_summary.json")
    seg_json_data = {
        "segments": seg_results["segment_summary"].to_dict(orient="records"),
        "total_customers": int(len(seg_results["customer_features"])),
        "adjusted_rand_index": seg_results["adjusted_rand_index"],
        "silhouette_scores": seg_results["silhouette_scores"],
        "segment_descriptions": seg_results["segment_descriptions"],
        "crosstab": seg_results["comparison_crosstab"].to_dict()
    }
    with open(seg_summary_json_path, "w", encoding="utf-8") as f:
        json.dump(seg_json_data, f, indent=2)

    # --- 2. Sales Forecasting ---
    print("2. Preparing time series and evaluating forecasting models...")
    daily_revenue, missing_cnt, missing_dates = prepare_daily_revenue()
    eval_results = evaluate_models(daily_revenue, artifacts_dir=artifacts_dir)
    forecast_results = run_recursive_forecast(daily_revenue, eval_results, periods=30)

    # Save forecast summary JSON
    forecast_json_path = os.path.join(artifacts_dir, "forecast_summary.json")
    forecast_json_data = {
        "period": forecast_results["period"],
        "predicted_revenue": forecast_results["predicted_revenue"],
        "model_used": forecast_results["model_used"],
        "missing_dates_count": missing_cnt,
        "missing_dates": missing_dates,
        "metrics": forecast_results["metrics"],
        "test_evaluation_series": eval_results.get("test_evaluation_series", {}),
        "daily_forecast": forecast_results["daily_forecast"]
    }
    with open(forecast_json_path, "w", encoding="utf-8") as f:
        json.dump(forecast_json_data, f, indent=2)

    # Save daily forecast series CSV
    forecast_csv_path = os.path.join(artifacts_dir, "forecast_series.csv")
    pd.DataFrame(forecast_results["daily_forecast"]).to_csv(forecast_csv_path, index=False)

    # --- 3. Business Report (.xlsx) ---
    print("3. Generating executive business Excel report...")
    report_path = os.path.join(artifacts_dir, "business_report.xlsx")
    generate_business_report(seg_results["segment_summary"], forecast_results, output_path=report_path)

    print(f">>> ML Pipeline Complete! All artifacts saved to {artifacts_dir}")

    return {
        "segmentation": seg_json_data,
        "forecasting": forecast_json_data,
        "report_path": report_path
    }

def artifacts_exist(artifacts_dir: str = None) -> bool:
    """
    Checks if all required Milestone 2 artifacts are present.
    """
    if artifacts_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        artifacts_dir = os.path.join(base_dir, "artifacts")

    required_files = [
        "segmentation_summary.json",
        "customers_segmented.csv",
        "dendrogram.png",
        "forecast_summary.json",
        "forecast_series.csv",
        "forecast_components.png",
        "revenue_forecast.png",
        "business_report.xlsx"
    ]
    return all(os.path.exists(os.path.join(artifacts_dir, f)) for f in required_files)

if __name__ == "__main__":
    train_all_artifacts()
