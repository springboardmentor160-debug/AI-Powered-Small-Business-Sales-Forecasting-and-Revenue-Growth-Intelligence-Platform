"""Build customer features and run the initial MarketMind segmentation."""

from pathlib import Path
from typing import Any

import pandas as pd

from backend.models.segmentation.hierarchical_model import HierarchicalSegmentationModel
from backend.models.segmentation.kmeans_model import KMeansSegmentationModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SALES_PATH = PROCESSED_DIR / "sales" / "cleaned_sales.csv"
CUSTOMERS_PATH = PROCESSED_DIR / "customers" / "cleaned_customers.csv"
SEGMENTS_DIR = PROCESSED_DIR / "segments"
SEGMENTS_PATH = SEGMENTS_DIR / "customer_segments.csv"

FEATURE_COLUMNS = ["purchase_frequency", "purchase_value", "customer_activity"]
OUTPUT_COLUMNS = [
    "customer_id",
    *FEATURE_COLUMNS,
    "cluster",
    "hierarchical_cluster",
    "segment_name",
]


def load_processed_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the processed Sales and Customer datasets used by this milestone."""
    for path in (SALES_PATH, CUSTOMERS_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Processed dataset not found: {path}")

    sales = pd.read_csv(SALES_PATH)
    customers = pd.read_csv(CUSTOMERS_PATH)
    required_sales_columns = {"transaction_id", "date", "customer_id", "total_amount"}
    missing_columns = required_sales_columns.difference(sales.columns)
    if missing_columns:
        raise ValueError(f"Sales dataset is missing required columns: {sorted(missing_columns)}")
    if "customer_id" not in customers.columns:
        raise ValueError("Customer dataset is missing required column: customer_id")
    return sales, customers


def build_customer_features(sales: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Aggregate behavioral features and retain customers without transactions.

    purchase_frequency is the number of transaction records for a customer.
    purchase_value is the sum of the customer's transaction total_amount values.
    customer_activity is the number of distinct calendar dates on which the customer purchased.
    Customers without Sales records receive zero for all three behavioral features.
    """
    sales = sales.copy()
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    sales["total_amount"] = pd.to_numeric(sales["total_amount"], errors="coerce").fillna(0)

    aggregated = (
        sales.dropna(subset=["customer_id"])
        .groupby("customer_id", as_index=False)
        .agg(
            purchase_frequency=("transaction_id", "count"),
            purchase_value=("total_amount", "sum"),
            customer_activity=("date", "nunique"),
        )
    )

    customer_features = customers[["customer_id"]].drop_duplicates().merge(
        aggregated,
        on="customer_id",
        how="left",
    )
    customer_features[FEATURE_COLUMNS] = customer_features[FEATURE_COLUMNS].fillna(0)
    customer_features["purchase_frequency"] = customer_features["purchase_frequency"].astype(int)
    customer_features["customer_activity"] = customer_features["customer_activity"].astype(int)
    customer_features["purchase_value"] = customer_features["purchase_value"].round(2)
    return customer_features


def _build_segment_names(cluster_statistics: pd.DataFrame) -> dict[int, str]:
    """Name hierarchical clusters from their observed behavioral means."""
    cluster_labels = list(cluster_statistics.index)
    if len(cluster_labels) == 1:
        return {int(cluster_labels[0]): "Regular Customers"}

    high_value_cluster = int(
        cluster_statistics.sort_values(
            ["purchase_value", "purchase_frequency", "customer_activity"],
            ascending=False,
        ).index[0]
    )
    remaining_clusters = [label for label in cluster_labels if label != high_value_cluster]
    low_activity_cluster = int(
        cluster_statistics.loc[remaining_clusters]
        .sort_values(
            ["customer_activity", "purchase_frequency", "purchase_value"],
            ascending=True,
        )
        .index[0]
    )

    names = {high_value_cluster: "High Value Customers"}
    names[low_activity_cluster] = "Low Activity Customers"
    for label in cluster_labels:
        names.setdefault(int(label), "Regular Customers")
    return names


def run_segmentation(
    customer_features: pd.DataFrame,
) -> tuple[pd.DataFrame, int, dict[int, float], pd.DataFrame, dict[int, str]]:
    """Fit K-Means and hierarchical clustering on the shared behavior features."""
    model = KMeansSegmentationModel()
    labels, cluster_count, inertias = model.fit_predict(customer_features[FEATURE_COLUMNS])
    segmented = customer_features.copy()
    segmented["cluster"] = labels.astype(int)
    hierarchical_model = HierarchicalSegmentationModel()
    segmented["hierarchical_cluster"] = hierarchical_model.fit_predict(
        customer_features[FEATURE_COLUMNS], cluster_count
    )
    cluster_statistics = segmented.groupby("hierarchical_cluster")[FEATURE_COLUMNS].mean()
    segment_names = _build_segment_names(cluster_statistics)
    segmented["segment_name"] = segmented["hierarchical_cluster"].map(segment_names)
    return segmented[OUTPUT_COLUMNS], cluster_count, inertias, cluster_statistics, segment_names


def save_segmentation(segmented: pd.DataFrame) -> Path:
    """Save the segmentation output below the processed data boundary."""
    SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)
    segmented.to_csv(SEGMENTS_PATH, index=False)
    return SEGMENTS_PATH


def generate_segmentation() -> dict[str, Any]:
    """Generate, save, and summarize the initial customer segmentation."""
    sales, customers = load_processed_data()
    customer_features = build_customer_features(sales, customers)
    segmented, cluster_count, inertias, cluster_statistics, segment_names = run_segmentation(
        customer_features
    )
    output_path = save_segmentation(segmented)
    kmeans_counts = segmented["cluster"].value_counts().sort_index().to_dict()
    hierarchical_counts = segmented["hierarchical_cluster"].value_counts().sort_index().to_dict()
    named_counts = segmented["segment_name"].value_counts().sort_index().to_dict()

    return {
        "customers_processed": len(segmented),
        "clusters_selected": cluster_count,
        "kmeans_cluster_counts": {int(cluster): int(count) for cluster, count in kmeans_counts.items()},
        "hierarchical_cluster_counts": {
            int(cluster): int(count) for cluster, count in hierarchical_counts.items()
        },
        "segment_counts": {str(name): int(count) for name, count in named_counts.items()},
        "cluster_statistics": {
            int(cluster): {
                feature: round(float(value), 2)
                for feature, value in row.items()
            }
            for cluster, row in cluster_statistics.iterrows()
        },
        "segment_names": segment_names,
        "elbow_inertias": {int(cluster): round(inertia, 4) for cluster, inertia in inertias.items()},
        "output_path": output_path,
    }


def main() -> None:
    """Run the segmentation job and print its actual results."""
    result = generate_segmentation()
    print(f"Customers processed: {result['customers_processed']:,}")
    print(f"K-Means clusters selected: {result['clusters_selected']}")
    print(f"K-Means cluster counts: {result['kmeans_cluster_counts']}")
    print(f"Hierarchical cluster counts: {result['hierarchical_cluster_counts']}")
    print(f"Segment counts: {result['segment_counts']}")
    print(f"Cluster statistics: {result['cluster_statistics']}")
    print(f"Segment names: {result['segment_names']}")
    print(f"Elbow inertias: {result['elbow_inertias']}")
    print(f"Output: {result['output_path'].relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
