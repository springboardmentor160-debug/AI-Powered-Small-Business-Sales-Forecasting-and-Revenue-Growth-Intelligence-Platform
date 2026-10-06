from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
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
    / "k_sensitivity_results.csv"
)


def main() -> None:
    print("=" * 70)
    print("MARKETMINDAI - M2 DAY 2 K-SELECTION VALIDATION")
    print("=" * 70)

    df = pd.read_csv(INPUT_PATH)

    missing = set(FEATURES) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required features: {sorted(missing)}"
        )

    features = df[FEATURES].copy()

    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(features)

    results = []

    for k in range(2, 7):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )

        labels = model.fit_predict(X_scaled)

        score = silhouette_score(
            X_scaled,
            labels,
        )

        cluster_sizes = (
            pd.Series(labels)
            .value_counts()
            .sort_index()
            .tolist()
        )

        results.append(
            {
                "n_clusters": k,
                "silhouette_score": score,
                "minimum_cluster_size": min(cluster_sizes),
                "maximum_cluster_size": max(cluster_sizes),
            }
        )

        print(
            f"k={k} | "
            f"Silhouette={score:.4f} | "
            f"min_cluster={min(cluster_sizes)} | "
            f"max_cluster={max(cluster_sizes)}"
        )

    results_df = (
        pd.DataFrame(results)
        .sort_values(
            "silhouette_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nK sensitivity results:")
    print(
        results_df.to_string(index=False)
    )

    best = results_df.iloc[0]

    print(
        f"\nBest measured K: "
        f"{int(best['n_clusters'])}"
    )

    print(
        f"Best silhouette: "
        f"{best['silhouette_score']:.4f}"
    )

    print(
        "\nOfficial M2 baseline remains k=4 "
        "until the validation evidence is reviewed."
    )

    print(
        f"\nSaved: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()