from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
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
    / "customer_segmentation_day1.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
    / "k3_k4_business_comparison.csv"
)


def evaluate_k(
    df: pd.DataFrame,
    k: int,
) -> pd.DataFrame:

    scaler = RobustScaler()
    X = scaler.fit_transform(df[FEATURES])

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10,
    )

    labels = model.fit_predict(X)

    scores = silhouette_samples(
        X,
        labels,
    )

    result = df.copy()
    result["comparison_cluster"] = labels
    result["sample_silhouette"] = scores

    summary = (
        result
        .groupby("comparison_cluster")
        .agg(
            customer_count=(
                "Customer ID",
                "count",
            ),
            customer_percentage=(
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
                "sample_silhouette",
                "mean",
            ),
            minimum_silhouette=(
                "sample_silhouette",
                "min",
            ),
        )
        .reset_index()
    )

    summary.insert(
        0,
        "n_clusters",
        k,
    )

    summary.insert(
        2,
        "overall_silhouette",
        silhouette_score(
            X,
            labels,
        ),
    )

    return summary


def main() -> None:

    print("=" * 75)
    print("MARKETMINDAI - K3 vs K4 BUSINESS SEGMENTATION COMPARISON")
    print("=" * 75)

    df = pd.read_csv(INPUT_PATH)

    k3 = evaluate_k(
        df,
        3,
    )

    k4 = evaluate_k(
        df,
        4,
    )

    comparison = pd.concat(
        [k3, k4],
        ignore_index=True,
    )

    comparison = comparison.sort_values(
        [
            "n_clusters",
            "comparison_cluster",
        ]
    )

    print("\nComparison:")
    print(
        comparison.round(2).to_string(
            index=False
        )
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparison.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nSaved: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()