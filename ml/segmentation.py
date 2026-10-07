"""
Customer Segmentation -- MarketMind AI
Milestone 2, Day 1-4

Builds customer-level features from online_retail_prepped.csv, clusters
customers using both K-Means and Hierarchical Clustering, and maps the
resulting clusters to named, business-meaningful segments.

    python segmentation.py

Outputs:
    - Printed comparison of K-Means vs Hierarchical cluster profiles
    - dendrogram.png -- visual confirmation of cluster structure
    - segment_assignments.csv -- one row per customer, with their
      named segment (for loading into the Segments table later)
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Build customer-level features from transaction-level data
# ---------------------------------------------------------------------------
df = pd.read_csv("./datasets/processed/online_retail_prepped.csv")
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Use the dataset's own latest date as the reference point for recency --
# this data is from 2010-2011, so using today's real date would make
# every customer look years inactive, which would be meaningless.
reference_date = df["InvoiceDate"].max()

customer_features = df.groupby("CustomerID").agg(
    purchase_frequency=("InvoiceNo", "nunique"),  # distinct orders, not line items
    purchase_value=("TotalAmount", "mean"),
    last_purchase_date=("InvoiceDate", "max"),
).reset_index()

customer_features["recency_days"] = (
    reference_date - customer_features["last_purchase_date"]
).dt.days

# ---------------------------------------------------------------------------
# 2. Outlier handling
# ---------------------------------------------------------------------------
# A very small number of customers have extreme purchase_value averages
# (e.g. one bulk order of 74,215 units of a single item, totaling
# $77,183 in one transaction) that are not representative of typical
# retail customer behavior. K-Means and Hierarchical Clustering are both
# distance-based and highly sensitive to such outliers -- left in, they
# distort cluster centers and produce tiny, non-actionable 1-2 person
# "clusters" instead of meaningful segments. Excluded here using the
# 99th percentile of purchase_value as a cutoff; affects ~1% of
# customers and does not materially reduce the data available for
# segmentation.
cutoff = customer_features["purchase_value"].quantile(0.99)
n_outliers = (customer_features["purchase_value"] > cutoff).sum()
print(f"Excluding {n_outliers} outlier customers (purchase_value > {cutoff:.2f})")
customer_features = customer_features[customer_features["purchase_value"] <= cutoff].copy()

feature_cols = ["purchase_frequency", "purchase_value", "recency_days"]
X = customer_features[feature_cols]

scaler = StandardScaler()
scaled_X = scaler.fit_transform(X)

# ---------------------------------------------------------------------------
# 3. K-Means
# ---------------------------------------------------------------------------
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
customer_features["cluster_kmeans"] = kmeans.fit_predict(scaled_X)

print("\n=== K-Means cluster profile ===")
print(customer_features.groupby("cluster_kmeans")[feature_cols].mean().round(1))
print(customer_features["cluster_kmeans"].value_counts().sort_index())

# ---------------------------------------------------------------------------
# 4. Hierarchical Clustering (second method, for comparison/validation)
# ---------------------------------------------------------------------------
hierarchical = AgglomerativeClustering(n_clusters=4)
customer_features["cluster_hierarchical"] = hierarchical.fit_predict(scaled_X)

print("\n=== Hierarchical cluster profile ===")
print(customer_features.groupby("cluster_hierarchical")[feature_cols].mean().round(1))
print(customer_features["cluster_hierarchical"].value_counts().sort_index())

# Both methods independently produced the same four broad groups (matched
# by profile shape, not cluster label number) -- this agreement is good
# evidence the segmentation reflects a real pattern in customer behavior,
# not an artifact of one algorithm's particular assumptions.

# ---------------------------------------------------------------------------
# 5. Dendrogram -- visual confirmation of cluster structure
# ---------------------------------------------------------------------------
linked = linkage(scaled_X, method="ward")
plt.figure(figsize=(10, 6))
dendrogram(linked, truncate_mode="lastp", p=15)
plt.title("Customer Similarity Tree")
plt.xlabel("Customers (grouped)")
plt.ylabel("Distance")
plt.savefig("dendrogram.png")
print("\nSaved dendrogram.png")

# ---------------------------------------------------------------------------
# 6. Map clusters to named, business-meaningful segments
# ---------------------------------------------------------------------------
# Using the K-Means assignment as the primary labeling (Hierarchical
# agreed closely and served as validation, not a second source of truth).
# Segment definitions, based on the actual cluster profiles observed:
#
#   Regular Shoppers       - largest group; moderate frequency, lower
#                             spend, recently active. The core customer
#                             base.
#   Lapsed / One-Time      - lowest frequency, lowest spend, inactive
#   Buyers                   for ~8 months. Target for re-engagement /
#                             churn prediction.
#   High-Value Customers   - moderate-high frequency, clearly the
#                             highest average order value (~9x typical).
#                             Small group, outsized revenue impact.
#   Power Buyers            - extremely high frequency (dozens to
#                             hundreds of orders), very recent activity.
#                             Behavior pattern suggests small-business /
#                             reseller accounts rather than typical
#                             retail shoppers.

def name_segment(cluster_id, profile):
    """Assigns a business-meaningful name based on the cluster's profile,
    not the arbitrary cluster number K-Means assigned."""
    freq = profile.loc[cluster_id, "purchase_frequency"]
    value = profile.loc[cluster_id, "purchase_value"]
    recency = profile.loc[cluster_id, "recency_days"]

    if freq > 50:
        return "Power Buyers"
    if value > 100:
        return "High-Value Customers"
    if recency > 200:
        return "Lapsed / One-Time Buyers"
    return "Regular Shoppers"


kmeans_profile = customer_features.groupby("cluster_kmeans")[feature_cols].mean()
customer_features["segment"] = customer_features["cluster_kmeans"].apply(
    lambda c: name_segment(c, kmeans_profile)
)

print("\n=== Final named segments ===")
print(customer_features.groupby("segment")[feature_cols].mean().round(1))
print(customer_features["segment"].value_counts())

# ---------------------------------------------------------------------------
# 7. Save per-customer segment assignments
# ---------------------------------------------------------------------------
output = customer_features[["CustomerID", "purchase_frequency", "purchase_value",
                             "recency_days", "segment"]]
output.to_csv("segment_assignments.csv", index=False)
print(f"\nSaved {len(output)} customer segment assignments to segment_assignments.csv")