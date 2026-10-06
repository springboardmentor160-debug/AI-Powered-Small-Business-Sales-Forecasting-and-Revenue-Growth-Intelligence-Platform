from pathlib import Path

import pandas as pd
from sklearn.metrics import silhouette_samples, silhouette_score
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
    / "customer_segmentation_hierarchical.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
)


def evaluate_clustering(
    df: pd.DataFrame,
    label_column: str,
) -> tuple[float, pd.DataFrame]:

    required = set(FEATURES) | {
        "Customer ID",
        label_column,
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    features = df[FEATURES].copy()

    scaler = RobustScaler()

    X_scaled = scaler.fit_transform(features)

    labels = df[label_column]

    if labels.nunique() < 2:
        raise ValueError(
            "At least two clusters are required."
        )

    overall_score = silhouette_score(
        X_scaled,
        labels,
    )

    sample_scores = silhouette_samples(
        X_scaled,
        labels,
    )

    working = df.copy()

    working["silhouette"] = sample_scores

    summary = (
        working
        .groupby(label_column)
        .agg(
            customer_count=(
                "Customer ID",
                "count",
            ),
            customer_percentage=(
                "Customer ID",
                lambda x: len(x) / len(working) * 100,
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
                "silhouette",
                "mean",
            ),
            minimum_silhouette=(
                "silhouette",
                "min",
            ),
        )
        .reset_index()
    )

    return overall_score, summary


def main() -> None:

    print("=" * 75)
    print("MARKETMINDAI - M2 DAY 3 CLUSTERING EVALUATION")
    print("=" * 75)

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    hierarchical_score, hierarchical_summary = (
        evaluate_clustering(
            df,
            "cluster_hierarchical",
        )
    )

    kmeans_score, kmeans_summary = (
        evaluate_clustering(
            df,
            "cluster",
        )
    )

    print("\nK-Means Silhouette:")
    print(f"{kmeans_score:.4f}")

    print("\nHierarchical Silhouette:")
    print(f"{hierarchical_score:.4f}")

    print("\nHierarchical cluster profile:")
    print(
        hierarchical_summary.round(2).to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # Save hierarchical validation
    # ---------------------------------------------------------

    hierarchical_summary_path = (
        OUTPUT_DIR
        / "hierarchical_cluster_summary.csv"
    )

    hierarchical_summary.to_csv(
        hierarchical_summary_path,
        index=False,
    )

    # ---------------------------------------------------------
    # Save model comparison
    # ---------------------------------------------------------

    model_comparison = pd.DataFrame(
        [
            {
                "model": "K-Means",
                "n_clusters": 4,
                "silhouette_score": kmeans_score,
            },
            {
                "model": "Hierarchical",
                "n_clusters": 4,
                "silhouette_score": hierarchical_score,
            },
        ]
    )

    comparison_path = (
        OUTPUT_DIR
        / "kmeans_vs_hierarchical.csv"
    )

    model_comparison.to_csv(
        comparison_path,
        index=False,
    )

    print(
        f"\nSaved hierarchical summary: "
        f"{hierarchical_summary_path}"
    )

    print(
        f"Saved model comparison: "
        f"{comparison_path}"
    )

    print("\nModel comparison:")
    print(
        model_comparison.round(4).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()