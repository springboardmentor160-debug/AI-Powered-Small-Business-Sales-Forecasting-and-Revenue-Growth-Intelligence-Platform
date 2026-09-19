import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def build_customer_features(data_path: str = None) -> pd.DataFrame:
    """
    Extracts customer-level RFM features from cleaned sales data.
    Anchors recency to (dataset max date + 1 day) to prevent time drift.
    Filters out anonymous GUEST transactions.
    """
    if data_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        data_path = os.path.join(base_dir, "data", "processed", "clean_sales.csv")
        if not os.path.exists(data_path):
            data_path = os.path.join(base_dir, "cleaned_sales_data.csv")

    df = pd.read_csv(data_path)
    
    # Filter out walk-in guest records for true customer segmentation
    if "customer_id" in df.columns:
        df = df[df["customer_id"] != "GUEST"].copy()

    date_col = "order_date" if "order_date" in df.columns else "date"
    df[date_col] = pd.to_datetime(df[date_col])

    # Ensure total_amount is calculated consistently
    if "quantity" in df.columns and "unit_price" in df.columns:
        df["total_amount"] = df["quantity"] * df["unit_price"]

    id_col = "order_id" if "order_id" in df.columns else "transaction_id"

    # Compute recency anchor: exactly max(date) in the dataset + 1 day
    max_date = df[date_col].max() + pd.Timedelta(days=1)

    customer_features = df.groupby("customer_id").agg(
        purchase_frequency=(id_col, "count"),
        purchase_value=("total_amount", "mean"),
        last_purchase_date=(date_col, "max")
    ).reset_index()

    customer_features["customer_activity_days"] = (
        max_date - customer_features["last_purchase_date"]
    ).dt.days

    # Round purchase_value to 2 decimal places
    customer_features["purchase_value"] = customer_features["purchase_value"].round(2)
    return customer_features

def run_segmentation(customer_features: pd.DataFrame, artifacts_dir: str = None):
    """
    Standardizes features, performs K-Means and Hierarchical clustering,
    saves the dendrogram, compares methods, and programmatically labels segments.
    """
    if artifacts_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    feature_cols = ["purchase_frequency", "purchase_value", "customer_activity_days"]
    X = customer_features[feature_cols].copy()

    # Step 1: Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Step 2: K-Means (K=4, random_state=42, n_init=10)
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    customer_features["cluster"] = kmeans.fit_predict(X_scaled)

    # Step 3: Hierarchical Clustering (Agglomerative, ward, n_clusters=4)
    hierarchical = AgglomerativeClustering(n_clusters=4, linkage="ward")
    customer_features["cluster_hierarchical"] = hierarchical.fit_predict(X_scaled)

    # Step 4: Dendrogram visualization
    dendrogram_path = os.path.join(artifacts_dir, "dendrogram.png")
    linked = linkage(X_scaled, method="ward")
    
    plt.figure(figsize=(9, 5))
    dendrogram(linked, truncate_mode="lastp", p=15, show_leaf_counts=True)
    plt.title("Customer Similarity Dendrogram (Hierarchical Clustering)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Customers (Cluster Groups)", fontsize=10)
    plt.ylabel("Ward Linkage Distance", fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(dendrogram_path, dpi=200)
    plt.close()

    # Step 5: Compare methods with crosstab and Adjusted Rand Index
    comparison_crosstab = pd.crosstab(
        customer_features["cluster"], 
        customer_features["cluster_hierarchical"],
        rownames=["KMeans_Cluster"],
        colnames=["Hierarchical_Cluster"]
    )
    ari = adjusted_rand_score(customer_features["cluster"], customer_features["cluster_hierarchical"])

    # Silhouette analysis across K
    silhouette_scores = {}
    for k in [2, 3, 4, 5]:
        km_test = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km_test.fit_predict(X_scaled)
        silhouette_scores[f"k_{k}"] = round(float(silhouette_score(X_scaled, labels)), 3)

    # Step 6: Programmatic segment naming based on centroid ranking
    centroids = customer_features.groupby("cluster")[feature_cols].mean()

    # Cluster with longest inactivity (highest customer_activity_days) is At-Risk
    at_risk_cluster = int(centroids["customer_activity_days"].idxmax())

    remaining_clusters = [c for c in centroids.index if c != at_risk_cluster]
    # Rank remaining by composite customer value score: purchase_frequency * purchase_value
    value_scores = {
        c: centroids.loc[c, "purchase_frequency"] * centroids.loc[c, "purchase_value"]
        for c in remaining_clusters
    }
    sorted_remaining = sorted(value_scores.keys(), key=lambda c: value_scores[c], reverse=True)

    vip_cluster = int(sorted_remaining[0])
    regular_cluster = int(sorted_remaining[1])
    occasional_cluster = int(sorted_remaining[2])

    segment_name_map = {
        vip_cluster: "VIP / Loyal Customers",
        regular_cluster: "Regular Customers",
        occasional_cluster: "Occasional Shoppers",
        at_risk_cluster: "At-Risk / Fading Customers"
    }

    segment_descriptions = {
        "VIP / Loyal Customers": "High-frequency, premium spenders who generate substantial recurring revenue.",
        "Regular Customers": "Consistent repeat shoppers with healthy engagement and steady transaction volume.",
        "Occasional Shoppers": "Low-frequency buyers with modest order values; prime candidates for upsell incentives.",
        "At-Risk / Fading Customers": "Historically active customers with extended inactivity; require urgent win-back offers."
    }

    customer_features["segment"] = customer_features["cluster"].map(segment_name_map)
    customer_features["segment_description"] = customer_features["segment"].map(segment_descriptions)

    # Summary table per segment
    segment_summary = customer_features.groupby("segment").agg(
        customer_count=("customer_id", "count"),
        avg_purchase_value=("purchase_value", "mean"),
        avg_purchase_frequency=("purchase_frequency", "mean"),
        avg_activity_days=("customer_activity_days", "mean")
    ).reset_index()

    segment_summary["avg_purchase_value"] = segment_summary["avg_purchase_value"].round(2)
    segment_summary["avg_purchase_frequency"] = segment_summary["avg_purchase_frequency"].round(1)
    segment_summary["avg_activity_days"] = segment_summary["avg_activity_days"].round(1)
    segment_summary["percentage"] = (
        (segment_summary["customer_count"] / len(customer_features)) * 100
    ).round(1)
    segment_summary["description"] = segment_summary["segment"].map(segment_descriptions)

    # Reorder segment_summary logically
    segment_order = [
        "VIP / Loyal Customers",
        "Regular Customers",
        "Occasional Shoppers",
        "At-Risk / Fading Customers"
    ]
    segment_summary["sort_order"] = segment_summary["segment"].apply(
        lambda s: segment_order.index(s) if s in segment_order else 99
    )
    segment_summary = segment_summary.sort_values("sort_order").drop(columns=["sort_order"]).reset_index(drop=True)

    results = {
        "customer_features": customer_features,
        "segment_summary": segment_summary,
        "comparison_crosstab": comparison_crosstab,
        "adjusted_rand_index": round(float(ari), 3),
        "silhouette_scores": silhouette_scores,
        "segment_name_map": {int(k): v for k, v in segment_name_map.items()},
        "segment_descriptions": segment_descriptions,
        "dendrogram_path": dendrogram_path
    }

    return results
