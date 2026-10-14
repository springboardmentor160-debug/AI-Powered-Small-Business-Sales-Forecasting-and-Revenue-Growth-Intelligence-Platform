import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score

DATA_PATH = os.path.join("data", "clean_retail_sales.csv")
OUTPUT_PATH = os.path.join("data", "customer_segmentation_output.csv")
TEST_RESULTS_PATH = os.path.join("data", "milestone4_test_results.csv")

os.makedirs("data", exist_ok=True)

# ============================================================
# 1. LOAD AND VALIDATE CLEANED SALES DATA
# ============================================================

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}. "
        "Run this script from the Marketmind_Ai project folder."
    )

sales_df = pd.read_csv(DATA_PATH)
print("Sales data loaded successfully!")
print("Rows:", len(sales_df))
print("Columns:", sales_df.columns.tolist())

required_columns = [
    "InvoiceNo", "InvoiceDate", "Revenue", "CustomerID"
]
missing = [column for column in required_columns if column not in sales_df.columns]
if missing:
    raise ValueError(f"Required columns missing from dataset: {missing}")

# ============================================================
# 2. PREPARE DATA
# ============================================================

sales_df["InvoiceDate"] = pd.to_datetime(
    sales_df["InvoiceDate"], errors="coerce"
)
sales_df["Revenue"] = pd.to_numeric(
    sales_df["Revenue"], errors="coerce"
)
sales_df["CustomerID"] = pd.to_numeric(
    sales_df["CustomerID"], errors="coerce"
)

sales_df = sales_df.dropna(
    subset=["CustomerID", "InvoiceDate", "Revenue"]
).copy()

if sales_df.empty:
    raise ValueError("No valid customer sales records remain after cleaning.")

# ============================================================
# 3. CUSTOMER FEATURE ENGINEERING
# ============================================================

reference_date = sales_df["InvoiceDate"].max()

customer_features = (
    sales_df.groupby("CustomerID")
    .agg(
        purchase_frequency=("InvoiceNo", "nunique"),
        purchase_value=("Revenue", "mean"),
        last_purchase_date=("InvoiceDate", "max"),
    )
    .reset_index()
)

customer_features["customer_activity_days"] = (
    reference_date - customer_features["last_purchase_date"]
).dt.days

feature_cols = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days",
]

# Keep only finite values for clustering
customer_features = customer_features.replace(
    [float("inf"), float("-inf")], pd.NA
)
customer_features = customer_features.dropna(
    subset=feature_cols
).reset_index(drop=True)

if len(customer_features) < 5:
    raise ValueError(
        "Not enough customers to evaluate four clusters with Silhouette Score."
    )

X = customer_features[feature_cols]

# ============================================================
# 4. SCALE FEATURES
# ============================================================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("\nCustomer features scaled successfully.")
print("Total customers:", len(customer_features))

# ============================================================
# 5. K-MEANS CLUSTERING
# ============================================================

kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10,
)
customer_features["cluster"] = kmeans.fit_predict(X_scaled)
print("K-Means clustering completed.")

# ============================================================
# 6. HIERARCHICAL CLUSTERING
# ============================================================

hierarchical = AgglomerativeClustering(n_clusters=4)
customer_features["cluster_hierarchical"] = hierarchical.fit_predict(X_scaled)
print("Hierarchical clustering completed.")

# ============================================================
# 7. SILHOUETTE SCORES
# ============================================================

# Silhouette score requires between 2 and n_samples - 1 distinct labels.
kmeans_score = silhouette_score(X_scaled, customer_features["cluster"])
hierarchical_score = silhouette_score(
    X_scaled, customer_features["cluster_hierarchical"]
)

print("\n" + "=" * 55)
print("CUSTOMER SEGMENTATION EVALUATION")
print("=" * 55)
print(f"K-Means Silhouette Score: {kmeans_score:.4f}")
print(f"Hierarchical Silhouette Score: {hierarchical_score:.4f}")

# ============================================================
# 8. CLUSTER SUMMARIES AND BUSINESS SEGMENT LABELS
# ============================================================

cluster_summary = (
    customer_features.groupby("cluster")[feature_cols]
    .mean()
    .round(2)
)
print("\nK-Means Cluster Summary:")
print(cluster_summary)

hierarchical_summary = (
    customer_features.groupby("cluster_hierarchical")[feature_cols]
    .mean()
    .round(2)
)
print("\nHierarchical Cluster Summary:")
print(hierarchical_summary)

vip_cluster = cluster_summary["purchase_frequency"].idxmax()
high_value_cluster = cluster_summary["purchase_value"].idxmax()

# Avoid assigning one cluster two different labels if the maxima coincide.
remaining_clusters = [
    cluster for cluster in cluster_summary.index
    if cluster not in {vip_cluster, high_value_cluster}
]

if not remaining_clusters:
    # Defensive fallback for degenerate clusters.
    at_risk_cluster = vip_cluster
    occasional_cluster = high_value_cluster
else:
    at_risk_cluster = cluster_summary.loc[
        remaining_clusters, "customer_activity_days"
    ].idxmax()

    occasional_candidates = [
        cluster for cluster in remaining_clusters
        if cluster != at_risk_cluster
    ]
    occasional_cluster = (
        occasional_candidates[0] if occasional_candidates
        else next(
            cluster for cluster in cluster_summary.index
            if cluster not in {vip_cluster, at_risk_cluster}
        )
    )

segment_names = {
    vip_cluster: "VIP / Loyal Customers",
    high_value_cluster: "High-Value Customers",
    at_risk_cluster: "At-Risk / Fading Customers",
    occasional_cluster: "Occasional / Regular Shoppers",
}
customer_features["segment"] = customer_features["cluster"].map(segment_names)

print("\nFinal Segment Mapping:")
for cluster, segment in segment_names.items():
    print(f"Cluster {cluster} -> {segment}")

print("\nCustomer Segment Distribution:")
print(customer_features["segment"].value_counts())

# ============================================================
# 9. SAVE CUSTOMER SEGMENT OUTPUT
# ============================================================

customer_features.to_csv(OUTPUT_PATH, index=False)
print(f"\nCustomer segmentation output saved to: {OUTPUT_PATH}")

# ============================================================
# 10. APPEND RESULTS TO MILESTONE 4 TEST RECORD
# ============================================================

new_results = pd.DataFrame([
    {
        "module": "Customer Segmentation (K-Means)",
        "metric": "Silhouette Score",
        "value": round(float(kmeans_score), 4),
    },
    {
        "module": "Customer Segmentation (Hierarchical)",
        "metric": "Silhouette Score",
        "value": round(float(hierarchical_score), 4),
    },
])

if os.path.exists(TEST_RESULTS_PATH):
    try:
        existing_results = pd.read_csv(TEST_RESULTS_PATH)
    except (pd.errors.EmptyDataError, UnicodeDecodeError):
        existing_results = pd.DataFrame(columns=["module", "metric", "value"])

    if not {"module", "metric", "value"}.issubset(existing_results.columns):
        existing_results = pd.DataFrame(columns=["module", "metric", "value"])
    else:
        existing_results = existing_results[
            ~existing_results["module"].astype(str).str.startswith(
                "Customer Segmentation ("
            )
        ]

    full_results = pd.concat(
        [existing_results, new_results], ignore_index=True
    )
else:
    full_results = new_results

full_results.to_csv(TEST_RESULTS_PATH, index=False)
print(f"Milestone 4 test record updated: {TEST_RESULTS_PATH}")
