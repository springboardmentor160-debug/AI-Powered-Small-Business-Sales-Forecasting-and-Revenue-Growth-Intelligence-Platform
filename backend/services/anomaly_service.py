"""Generate actual Sales anomaly outputs for MarketMind M3 Day 9-10."""

from pathlib import Path
from typing import Any

import pandas as pd

from backend.models.anomaly.anomaly_detection import ANOMALY_FEATURES, AnomalyDetectionModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SALES_PATH = PROJECT_ROOT / "data" / "processed" / "sales" / "cleaned_sales.csv"
ANOMALY_DIR = PROJECT_ROOT / "data" / "processed" / "anomalies"
Z_SCORE_PATH = ANOMALY_DIR / "z_score_anomalies.csv"
ISOLATION_PATH = ANOMALY_DIR / "isolation_forest_anomalies.csv"
COMPARISON_PATH = ANOMALY_DIR / "anomaly_comparison.csv"
ALERTS_PATH = ANOMALY_DIR / "anomaly_alerts.csv"
ISOLATION_CONTAMINATION = 0.01


def load_processed_sales() -> pd.DataFrame:
    """Load the cleaned Sales dataset without modifying it."""
    if not SALES_PATH.exists():
        raise FileNotFoundError(f"Processed sales dataset not found: {SALES_PATH}")
    sales = pd.read_csv(SALES_PATH)
    required_columns = {
        "transaction_id",
        "date",
        "product_id",
        "product_name",
        "store_id",
        *ANOMALY_FEATURES,
    }
    missing_columns = required_columns.difference(sales.columns)
    if missing_columns:
        raise ValueError(f"Sales data is missing required columns: {sorted(missing_columns)}")
    for feature in ANOMALY_FEATURES:
        sales[feature] = pd.to_numeric(sales[feature], errors="coerce")
    return sales.dropna(subset=ANOMALY_FEATURES).copy()


def _severity(max_z_score: float) -> str:
    if max_z_score >= 5:
        return "Critical"
    if max_z_score >= 4:
        return "High"
    return "Medium"


def _feature_details(row: pd.Series, z_scores: pd.DataFrame) -> tuple[str, str, float]:
    absolute_scores = z_scores.loc[row.name].abs().sort_values(ascending=False)
    feature = str(absolute_scores.index[0])
    return feature, str(row[feature]), float(absolute_scores.iloc[0])


def _build_alerts(
    flagged_data: pd.DataFrame,
    z_scores: pd.DataFrame,
    method: str,
    score_column: str,
) -> pd.DataFrame:
    """Build actionable alerts with feature-level context and severity."""
    alerts = []
    for _, row in flagged_data.iterrows():
        feature, value, magnitude = _feature_details(row, z_scores)
        alerts.append(
            {
                "transaction_id": row["transaction_id"],
                "date": row["date"],
                "store_id": row["store_id"],
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "alert_type": "sales_transaction_outlier",
                "message": f"Unusual {feature} detected for {row['product_name']} ({feature}={value}).",
                "severity": _severity(magnitude),
                "detection_method": method,
                "relevant_feature": feature,
                "relevant_value": float(value),
                "anomaly_score": round(magnitude, 6) if method == "Z-score" else round(float(row[score_column]), 6),
            }
        )
    return pd.DataFrame(
        alerts,
        columns=[
            "transaction_id",
            "date",
            "store_id",
            "product_id",
            "product_name",
            "alert_type",
            "message",
            "severity",
            "detection_method",
            "relevant_feature",
            "relevant_value",
            "anomaly_score",
        ],
    )


def generate_anomaly_outputs() -> dict[str, Any]:
    """Run both detectors, compare flags, and write actionable alerts."""
    sales = load_processed_sales()
    detector = AnomalyDetectionModel(contamination=ISOLATION_CONTAMINATION)
    z_scores, z_mask = detector.z_score_detection(sales)
    isolation_scores, isolation_mask = detector.isolation_forest_detection(sales)

    z_output = sales.loc[z_mask].copy()
    z_output["detection_method"] = "Z-score"
    z_output["max_absolute_z_score"] = z_scores.loc[z_mask].abs().max(axis=1).round(6)
    isolation_output = sales.loc[isolation_mask].copy()
    isolation_output["detection_method"] = "Isolation Forest"
    isolation_output["isolation_forest_score"] = isolation_scores.loc[isolation_mask].round(6)

    comparison = sales[["transaction_id", "date", "store_id", "product_id", "product_name", *ANOMALY_FEATURES]].copy()
    comparison["z_score_anomaly"] = z_mask.astype(bool).to_numpy()
    comparison["isolation_forest_anomaly"] = isolation_mask.astype(bool).to_numpy()
    comparison["detection_methods"] = comparison.apply(
        lambda row: ";".join(
            method
            for method, flagged in (
                ("Z-score", row["z_score_anomaly"]),
                ("Isolation Forest", row["isolation_forest_anomaly"]),
            )
            if flagged
        )
        or "None",
        axis=1,
    )

    alerts = pd.concat(
        [
            _build_alerts(z_output, z_scores, "Z-score", "max_absolute_z_score"),
            _build_alerts(
                isolation_output.assign(**{feature: sales.loc[isolation_mask, feature].to_numpy() for feature in ANOMALY_FEATURES}),
                z_scores,
                "Isolation Forest",
                "isolation_forest_score",
            ),
        ],
        ignore_index=True,
    )

    ANOMALY_DIR.mkdir(parents=True, exist_ok=True)
    z_output.to_csv(Z_SCORE_PATH, index=False)
    isolation_output.to_csv(ISOLATION_PATH, index=False)
    comparison.to_csv(COMPARISON_PATH, index=False)
    alerts.to_csv(ALERTS_PATH, index=False)

    return {
        "transactions_processed": len(sales),
        "features": ANOMALY_FEATURES,
        "z_score_threshold": detector.z_threshold,
        "contamination": ISOLATION_CONTAMINATION,
        "z_score_count": int(z_mask.sum()),
        "isolation_forest_count": int(isolation_mask.sum()),
        "both_methods_count": int((z_mask & isolation_mask).sum()),
        "alert_count": len(alerts),
        "severity_counts": alerts["severity"].value_counts().to_dict() if not alerts.empty else {},
        "output_paths": [Z_SCORE_PATH, ISOLATION_PATH, COMPARISON_PATH, ALERTS_PATH],
    }


def main() -> None:
    """Run anomaly detection and print actual summary statistics."""
    result = generate_anomaly_outputs()
    print(f"Transactions processed: {result['transactions_processed']:,}")
    print(f"Features: {result['features']}")
    print(f"Z-score threshold: |z| > {result['z_score_threshold']}")
    print(f"Isolation Forest contamination: {result['contamination']}")
    print(f"Z-score anomalies: {result['z_score_count']:,}")
    print(f"Isolation Forest anomalies: {result['isolation_forest_count']:,}")
    print(f"Flagged by both methods: {result['both_methods_count']:,}")
    print(f"Alerts: {result['alert_count']:,}")
    print(f"Severity counts: {result['severity_counts']}")
    for output_path in result["output_paths"]:
        print(f"Output: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
