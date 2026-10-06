from pathlib import Path

import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import RobustScaler


SEGMENTATION_FEATURES = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days",
]


def evaluate_segmentation(
    customer_features: pd.DataFrame,
) -> tuple[float, pd.DataFrame]:
    """
    Evaluate the K-Means segmentation result.

    Returns:
        silhouette score
        cluster summary
    """

    required_columns = (
        set(SEGMENTATION_FEATURES)
        | {"cluster", "Customer ID"}
    )

    missing_columns = (
        required_columns
        - set(customer_features.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing evaluation columns: "
            f"{sorted(missing_columns)}"
        )

    features = customer_features[
        SEGMENTATION_FEATURES
    ].copy()

    labels = customer_features["cluster"]

    if labels.nunique() < 2:
        raise ValueError(
            "Silhouette score requires at least "
            "two clusters."
        )

    scaler = RobustScaler()

    X_scaled = scaler.fit_transform(features)

    silhouette = silhouette_score(
        X_scaled,
        labels,
    )

    cluster_summary = (
        customer_features
        .groupby("cluster")
        .agg(
            customer_count=(
                "Customer ID",
                "count",
            ),
            average_purchase_frequency=(
                "purchase_frequency",
                "mean",
            ),
            average_purchase_value=(
                "purchase_value",
                "mean",
            ),
            average_activity_days=(
                "customer_activity_days",
                "mean",
            ),
            median_purchase_value=(
                "purchase_value",
                "median",
            ),
            median_purchase_frequency=(
                "purchase_frequency",
                "median",
            ),
        )
        .reset_index()
        .sort_values("cluster")
    )

    return float(silhouette), cluster_summary


def save_evaluation_artifacts(
    silhouette: float,
    cluster_summary: pd.DataFrame,
    output_dir: Path,
) -> None:
    """
    Save segmentation evaluation results as reproducible
    M2 artifacts.
    """

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_path = (
        output_dir / "segmentation_metrics.csv"
    )

    summary_path = (
        output_dir / "cluster_summary.csv"
    )

    metrics = pd.DataFrame(
        [
            {
                "metric": "silhouette_score",
                "value": silhouette,
                "model": "KMeans",
                "n_clusters": 4,
                "preprocessing": "RobustScaler",
            }
        ]
    )

    metrics.to_csv(
        metrics_path,
        index=False,
    )

    cluster_summary.to_csv(
        summary_path,
        index=False,
    )

    print(
        f"Saved metrics: {metrics_path}"
    )

    print(
        f"Saved cluster summary: {summary_path}"
    )