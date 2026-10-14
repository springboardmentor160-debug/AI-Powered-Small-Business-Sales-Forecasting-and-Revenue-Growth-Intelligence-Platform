"""Evaluate persisted forecasting and segmentation results for Milestone 4."""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics.cluster import silhouette_score  # type: ignore[reportUnknownVariableType]

from backend.models.anomaly.anomaly_detection import AnomalyDetectionModel
from backend.models.segmentation.kmeans_model import KMeansSegmentationModel
from backend.services.recommendation_service import (
    build_model,
    load_processed_customer_ids,
    load_processed_sales,
)
from backend.services.segmentation_service import (
    FEATURE_COLUMNS,
    build_customer_features,
    load_processed_data,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FORECAST_VALIDATION_PATH = (
    PROJECT_ROOT / "data" / "processed" / "forecast" / "model_validation_predictions.csv"
)
SEGMENTS_PATH = PROJECT_ROOT / "data" / "processed" / "segments" / "customer_segments.csv"
RESULTS_DIR = PROJECT_ROOT / "data" / "processed" / "testing"
RESULTS_PATH = RESULTS_DIR / "milestone4_test_results.csv"
FORECAST_MODELS = ("Prophet", "XGBoost", "Random Forest")
FORECAST_METRICS = ("MAE", "RMSE", "R2")
SEGMENT_MODELS = (
    ("K-Means", "cluster"),
    ("Hierarchical", "hierarchical_cluster"),
)
RESULT_COLUMNS = [
    "model_name",
    "task",
    "evaluation_metric",
    "metric_value",
    "evaluation_details",
]


def _result(
    model_name: str,
    task: str,
    metric: str,
    value: float | None,
    details: str,
) -> dict[str, Any]:
    """Build one consistently shaped result row."""
    return {
        "model_name": model_name,
        "task": task,
        "evaluation_metric": metric,
        "metric_value": value,
        "evaluation_details": details,
    }


def _unavailable_rows(
    model_name: str,
    task: str,
    metrics: tuple[str, ...],
    reason: str,
) -> list[dict[str, Any]]:
    return [_result(model_name, task, metric, None, f"Unavailable: {reason}") for metric in metrics]


def _validate_forecast_input(validation: pd.DataFrame) -> None:
    required = {"date", "metric", "model", "actual", "prediction"}
    missing = required.difference(validation.columns)
    if missing:
        raise ValueError(f"Forecast validation output is missing required columns: {sorted(missing)}")

    validation["date"] = pd.to_datetime(validation["date"], errors="coerce")
    for column in ("actual", "prediction"):
        validation[column] = pd.to_numeric(validation[column], errors="coerce")


def evaluate_forecasting() -> list[dict[str, Any]]:
    """Score persisted predictions without fitting models or changing the holdout."""
    if not FORECAST_VALIDATION_PATH.exists():
        reason = f"validation predictions file not found: {FORECAST_VALIDATION_PATH}"
        return [
            row
            for model in FORECAST_MODELS
            for metric in ("revenue", "sales_quantity")
            for row in _unavailable_rows(model, f"Forecasting ({metric})", FORECAST_METRICS, reason)
        ]

    validation = pd.read_csv(FORECAST_VALIDATION_PATH)
    _validate_forecast_input(validation)
    rows: list[dict[str, Any]] = []

    for metric_name in ("revenue", "sales_quantity"):
        metric_data = validation[validation["metric"] == metric_name]
        model_periods = {
            model: tuple(sorted(metric_data.loc[metric_data["model"] == model, "date"].dropna().unique()))
            for model in FORECAST_MODELS
        }
        available_periods = [period for period in model_periods.values() if period]
        same_period = bool(available_periods) and all(period == available_periods[0] for period in available_periods)
        period_details = (
            f"chronological holdout {pd.Timestamp(available_periods[0][0]).date()} to "
            f"{pd.Timestamp(available_periods[0][-1]).date()}, {len(available_periods[0])} rows"
            if same_period
            else "model predictions do not share one comparable validation period"
        )

        for model_name in FORECAST_MODELS:
            model_data = metric_data[metric_data["model"] == model_name].sort_values("date")
            if model_data.empty:
                rows.extend(
                    _unavailable_rows(
                        model_name,
                        f"Forecasting ({metric_name})",
                        FORECAST_METRICS,
                        "no persisted validation predictions",
                    )
                )
                continue
            if not same_period:
                rows.extend(
                    _unavailable_rows(
                        model_name,
                        f"Forecasting ({metric_name})",
                        FORECAST_METRICS,
                        period_details,
                    )
                )
                continue

            valid = model_data.dropna(subset=["date", "actual", "prediction"])
            if len(valid) != len(model_data):
                rows.extend(
                    _unavailable_rows(
                        model_name,
                        f"Forecasting ({metric_name})",
                        FORECAST_METRICS,
                        "actual or prediction contains missing/non-numeric values",
                    )
                )
                continue
            actual = valid["actual"].to_numpy(dtype=float)
            predicted = valid["prediction"].to_numpy(dtype=float)
            details = f"{period_details}; predictions loaded from {FORECAST_VALIDATION_PATH.name}"
            rows.extend(
                [
                    _result(model_name, f"Forecasting ({metric_name})", "MAE", float(mean_absolute_error(actual, predicted)), details),
                    _result(model_name, f"Forecasting ({metric_name})", "RMSE", float(np.sqrt(mean_squared_error(actual, predicted))), details),
                    _result(model_name, f"Forecasting ({metric_name})", "R2", float(r2_score(actual, predicted)), details),
                ]
            )
    return rows


def _silhouette_row(
    model_name: str,
    feature_matrix: np.ndarray,
    labels: pd.Series,
    details_prefix: str,
) -> dict[str, Any]:
    """Calculate a silhouette score only when its mathematical constraints hold."""
    label_values = labels.to_numpy()
    unique_labels = np.unique(label_values)
    if len(feature_matrix) != len(label_values):
        reason = "feature matrix and labels have different row counts"
        return _result(model_name, "Segmentation", "Silhouette Score", None, f"Unavailable: {reason}")
    if len(unique_labels) < 2:
        reason = "silhouette score is undefined with fewer than two clusters"
        return _result(model_name, "Segmentation", "Silhouette Score", None, f"Unavailable: {reason}")
    if len(unique_labels) >= len(label_values):
        reason = "silhouette score is undefined when every customer is its own cluster"
        return _result(model_name, "Segmentation", "Silhouette Score", None, f"Unavailable: {reason}")
    try:
        value = float(silhouette_score(feature_matrix, label_values))
    except ValueError as exc:
        return _result(model_name, "Segmentation", "Silhouette Score", None, f"Unavailable: {exc}")
    details = (
        f"{details_prefix}; customers={len(label_values)}, clusters={len(unique_labels)}, "
        f"features={', '.join(FEATURE_COLUMNS)}"
    )
    return _result(model_name, "Segmentation", "Silhouette Score", value, details)


def evaluate_segmentation() -> list[dict[str, Any]]:
    """Score existing cluster labels using the segmentation pipeline's features and order."""
    if not SEGMENTS_PATH.exists():
        reason = f"segmentation output not found: {SEGMENTS_PATH}"
        return [
            _result(model_name, "Segmentation", "Silhouette Score", None, f"Unavailable: {reason}")
            for model_name, _ in SEGMENT_MODELS
        ]

    segmented = pd.read_csv(SEGMENTS_PATH)
    required = {"customer_id", *FEATURE_COLUMNS, *(column for _, column in SEGMENT_MODELS)}
    missing = required.difference(segmented.columns)
    if missing:
        reason = f"segmentation output is missing columns: {sorted(missing)}"
        return [
            _result(model_name, "Segmentation", "Silhouette Score", None, f"Unavailable: {reason}")
            for model_name, _ in SEGMENT_MODELS
        ]

    sales, customers = load_processed_data()
    customer_features = build_customer_features(sales, customers)
    if not customer_features["customer_id"].reset_index(drop=True).equals(
        segmented["customer_id"].reset_index(drop=True)
    ):
        reason = "customer ordering differs from the persisted segmentation output"
        return [
            _result(model_name, "Segmentation", "Silhouette Score", None, f"Unavailable: {reason}")
            for model_name, _ in SEGMENT_MODELS
        ]

    feature_matrix = KMeansSegmentationModel.prepare_features(customer_features[FEATURE_COLUMNS])
    details_prefix = f"existing labels from {SEGMENTS_PATH.name}; log1p + StandardScaler feature preparation"
    return [
        _silhouette_row(model_name, feature_matrix, segmented[label_column], details_prefix)
        for model_name, label_column in SEGMENT_MODELS
    ]


def evaluate_churn() -> list[dict[str, Any]]:
    """Avoid scoring full-data churn predictions as if they were validation output."""
    reason = (
        "no persisted row-level validation predictions and labels; "
        "churn_predictions_final.csv contains full-dataset predictions, so scoring it would leak training data"
    )
    return [
        _result("Selected churn model", "Churn", metric, None, f"Unavailable: {reason}")
        for metric in ("Accuracy", "Precision", "Recall", "F1-score")
    ]


def evaluate_recommendations() -> list[dict[str, Any]]:
    """Evaluate collaborative filtering with each customer's last transaction held out."""
    sales = load_processed_sales().copy()
    required = {"customer_id", "date", "transaction_id", "product_name", "quantity"}
    missing = required.difference(sales.columns)
    if missing:
        reason = f"sales data is missing required columns: {sorted(missing)}"
        return [
            _result("Collaborative Filtering", "Recommendation", metric, None, f"Unavailable: {reason}")
            for metric in ("Precision@3", "Recall@3")
        ]
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    sales = sales.dropna(subset=["customer_id", "date", "transaction_id", "product_name"])
    sales = sales.sort_values(["customer_id", "date", "transaction_id"], kind="mergesort")
    holdout = sales.groupby("customer_id", sort=False).tail(1)
    training = sales.drop(index=holdout.index)
    if training.empty or holdout.empty:
        reason = "temporal holdout could not produce non-empty training and test sets"
        return [
            _result("Collaborative Filtering", "Recommendation", metric, None, f"Unavailable: {reason}")
            for metric in ("Precision@3", "Recall@3")
        ]

    model = build_model(training, customer_ids=load_processed_customer_ids())
    precisions: list[float] = []
    recalls: list[float] = []
    evaluated_customers = 0
    for customer_id, customer_holdout in holdout.groupby("customer_id", sort=False):
        relevant = set(customer_holdout["product_name"].astype(str))
        if not relevant:
            continue
        recommendations = model.recommend_products(str(customer_id), top_n=3)
        predicted = {str(row["recommended_product"]) for row in recommendations}
        hits = len(predicted.intersection(relevant))
        evaluated_customers += 1
        precisions.append(hits / 3)
        recalls.append(hits / len(relevant))

    if not precisions:
        reason = "no customers had a labeled holdout suitable for evaluation"
        return [
            _result("Collaborative Filtering", "Recommendation", metric, None, f"Unavailable: {reason}")
            for metric in ("Precision@3", "Recall@3")
        ]
    details = (
        f"K=3; temporal leave-last-transaction-out holdout; customers evaluated={evaluated_customers}; "
        f"training rows={len(training)}; held-out rows={len(holdout)}; "
        "recommendations used training purchases only"
    )
    return [
        _result("Collaborative Filtering", "Recommendation", "Precision@3", float(np.mean(precisions)), details),
        _result("Collaborative Filtering", "Recommendation", "Recall@3", float(np.mean(recalls)), details),
    ]


def _controlled_anomaly_fixture() -> tuple[pd.DataFrame, pd.Series]:
    """Create labeled normal and anomalous rows without touching the source dataset."""
    normal_count = 100
    rows: list[dict[str, float | int]] = [
        {
            "quantity": 1 + (index % 3),
            "unit_price": 10.0 + (index % 5),
            "total_amount": float((1 + (index % 3)) * (10 + (index % 5))),
        }
        for index in range(normal_count)
    ]
    rows.extend(
        [
            {"quantity": 40, "unit_price": 120.0, "total_amount": 4800.0},
            {"quantity": 50, "unit_price": 150.0, "total_amount": 7500.0},
        ]
    )
    return pd.DataFrame(rows), pd.Series([0] * normal_count + [1, 1], name="known_anomaly")


def evaluate_anomalies() -> list[dict[str, Any]]:
    """Evaluate detectors only on separately labeled controlled cases."""
    fixture, labels = _controlled_anomaly_fixture()
    detector = AnomalyDetectionModel(contamination=0.02)
    _, z_mask = detector.z_score_detection(fixture)
    _, isolation_mask = detector.isolation_forest_detection(fixture)
    details = (
        "controlled in-memory fixture only; 100 labeled normal rows and 2 labeled anomalies; "
        "not a performance estimate for the original dataset"
    )
    results: list[dict[str, Any]] = []
    actual = labels.to_numpy()
    for model_name, predictions in (("Z-score", z_mask), ("Isolation Forest", isolation_mask)):
        predicted = predictions.astype(int).to_numpy()
        false_positive_rate = float(((predicted == 1) & (actual == 0)).sum() / (actual == 0).sum())
        results.extend(
            [
                _result(model_name, "Anomaly Detection", "Detection Accuracy", float(accuracy_score(actual, predicted)), details),
                _result(model_name, "Anomaly Detection", "False Positive Rate", false_positive_rate, details),
            ]
        )
    return results


def run_evaluation() -> pd.DataFrame:
    """Evaluate persisted outputs and append new results without duplicating prior rows."""
    new_results = pd.DataFrame(
        evaluate_churn() + evaluate_recommendations() + evaluate_anomalies(),
        columns=RESULT_COLUMNS,
    )
    existing = pd.read_csv(RESULTS_PATH) if RESULTS_PATH.exists() else pd.DataFrame(columns=RESULT_COLUMNS)
    existing = existing.reindex(columns=RESULT_COLUMNS)
    identity_columns = ["model_name", "task", "evaluation_metric"]
    existing = existing.drop_duplicates(subset=identity_columns, keep="first")
    prior_keys = set(existing[identity_columns].astype(str).apply(tuple, axis=1))
    new_results = new_results[
        ~new_results[identity_columns].astype(str).apply(tuple, axis=1).isin(prior_keys)
    ]
    results = pd.concat([existing, new_results], ignore_index=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_PATH, index=False)
    return results


def main() -> None:
    """Run the Milestone 4 evaluation and print the consolidated results."""
    results = run_evaluation()
    print(results.to_string(index=False))
    print(f"Output: {RESULTS_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
