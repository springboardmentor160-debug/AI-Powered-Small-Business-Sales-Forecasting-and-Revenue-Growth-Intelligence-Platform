from pathlib import Path

from backend.data_pipeline.sources.uci.loader import (
    load_uci_online_retail,
)
from backend.data_pipeline.transforms.customer_features import (
    build_customer_features,
)
from backend.ml.segmentation.evaluation import (
    evaluate_segmentation,
    save_evaluation_artifacts,
)
from backend.ml.segmentation.kmeans_model import (
    train_kmeans,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
)


def main() -> None:
    print("=" * 60)
    print("MARKETMINDAI - M2 DAY 1")
    print("CUSTOMER SEGMENTATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load source data
    # ---------------------------------------------------------

    sales_df = load_uci_online_retail()

    print(
        f"Combined transactions: "
        f"{len(sales_df):,}"
    )

    # ---------------------------------------------------------
    # 2. Build customer features
    # ---------------------------------------------------------

    customer_features = build_customer_features(
        sales_df
    )

    print(
        f"Customers available for segmentation: "
        f"{len(customer_features):,}"
    )

    # ---------------------------------------------------------
    # 3. Train K-Means
    # ---------------------------------------------------------

    clustered_df, _, model = train_kmeans(
        customer_features,
        n_clusters=4,
        random_state=42,
    )

    print(
        f"\nClusters created: "
        f"{model.n_clusters}"
    )

    print("\nCluster distribution:")
    print(
        clustered_df["cluster"]
        .value_counts()
        .sort_index()
    )

    # ---------------------------------------------------------
    # 4. Save customer-level clustering result
    # ---------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    customer_output = (
        OUTPUT_DIR
        / "customer_segmentation_day1.csv"
    )

    clustered_df.to_csv(
        customer_output,
        index=False,
    )

    print(
        f"\nSaved: {customer_output}"
    )

    # ---------------------------------------------------------
    # 5. Evaluate segmentation
    # ---------------------------------------------------------

    silhouette, cluster_summary = (
        evaluate_segmentation(
            clustered_df
        )
    )

    print(
        f"\nSilhouette Score: "
        f"{silhouette:.4f}"
    )

    # ---------------------------------------------------------
    # 6. Save evaluation artifacts
    # ---------------------------------------------------------

    save_evaluation_artifacts(
        silhouette=silhouette,
        cluster_summary=cluster_summary,
        output_dir=OUTPUT_DIR,
    )

    print(
        "\nM2 Day 1 segmentation pipeline completed."
    )

    print(
        "Cluster numbers are preliminary; "
        "business segment names will be assigned "
        "during Day 3-4 analysis."
    )


if __name__ == "__main__":
    main()