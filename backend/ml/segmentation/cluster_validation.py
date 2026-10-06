from pathlib import Path

import pandas as pd
from sklearn.metrics import silhouette_samples
from sklearn.preprocessing import RobustScaler


FEATURES = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days",
]

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
    / "customer_segmentation_day1.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
)


def validate_clusters(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate per-customer silhouette values and
    cluster-level behavioral statistics.
    """

    required_columns = set(FEATURES) | {
        "Customer ID",
        "cluster",
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    scaler = RobustScaler()

    X_scaled = scaler.fit_transform(
        df[FEATURES]
    )

    # Silhouette value for every customer.
    sample_scores = silhouette_samples(
        X_scaled,
        df["cluster"],
    )

    result = df.copy()

    result["silhouette_score"] = sample_scores

    # Cluster-level validation.
    cluster_summary = (
        result
        .groupby("cluster")
        .agg(
            customer_count=(
                "Customer ID",
                "count",
            ),
            cluster_percentage=(
                "Customer ID",
                lambda x: len(x) / len(result) * 100,
            ),
            average_purchase_frequency=(
                "purchase_frequency",
                "mean",
            ),
            median_purchase_frequency=(
                "purchase_frequency",
                "median",
            ),
            average_purchase_value=(
                "purchase_value",
                "mean",
            ),
            median_purchase_value=(
                "purchase_value",
                "median",
            ),
            average_activity_days=(
                "customer_activity_days",
                "mean",
            ),
            median_activity_days=(
                "customer_activity_days",
                "median",
            ),
            average_silhouette=(
                "silhouette_score",
                "mean",
            ),
            minimum_silhouette=(
                "silhouette_score",
                "min",
            ),
        )
        .reset_index()
        .sort_values("cluster")
    )

    return result, cluster_summary


def main() -> None:
    print("=" * 70)
    print("MARKETMINDAI - M2 DAY 2 CLUSTER VALIDATION")
    print("=" * 70)

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Segmentation result not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    validated_df, cluster_summary = validate_clusters(
        df
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    customer_validation_path = (
        OUTPUT_DIR
        / "customer_segmentation_validation.csv"
    )

    cluster_validation_path = (
        OUTPUT_DIR
        / "cluster_validation_summary.csv"
    )

    validated_df.to_csv(
        customer_validation_path,
        index=False,
    )

    cluster_summary.to_csv(
        cluster_validation_path,
        index=False,
    )

    print("\nCluster validation summary:")
    print(
        cluster_summary.round(2).to_string(
            index=False
        )
    )

    print(
        f"\nSaved customer validation: "
        f"{customer_validation_path}"
    )

    print(
        f"Saved cluster validation: "
        f"{cluster_validation_path}"
    )

    print("\nM2 Day 2 validation completed.")


if __name__ == "__main__":
    main()