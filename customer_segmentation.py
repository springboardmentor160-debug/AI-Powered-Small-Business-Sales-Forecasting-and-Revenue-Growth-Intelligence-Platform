import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering


# -----------------------------------------
# LOAD CLEANED SALES DATA
# -----------------------------------------

sales_df = pd.read_csv("data/clean_retail_sales.csv")

print("Sales data loaded successfully!")
print("Rows:", len(sales_df))
print("Columns:", sales_df.columns.tolist())


# -----------------------------------------
# PREPARE DATA
# -----------------------------------------

sales_df["InvoiceDate"] = pd.to_datetime(
    sales_df["InvoiceDate"],
    errors="coerce"
)

sales_df["Revenue"] = pd.to_numeric(
    sales_df["Revenue"],
    errors="coerce"
)

sales_df["CustomerID"] = pd.to_numeric(
    sales_df["CustomerID"],
    errors="coerce"
)

# Remove incomplete customer records
sales_df = sales_df.dropna(
    subset=["CustomerID", "InvoiceDate", "Revenue"]
)


# -----------------------------------------
# CUSTOMER FEATURE ENGINEERING
# -----------------------------------------

# Latest date in our historical dataset
reference_date = sales_df["InvoiceDate"].max()

customer_features = sales_df.groupby("CustomerID").agg(

    # Number of unique invoices/orders
    purchase_frequency=("InvoiceNo", "nunique"),

    # Average revenue generated per transaction row
    purchase_value=("Revenue", "mean"),

    # Most recent purchase
    last_purchase_date=("InvoiceDate", "max")

).reset_index()


# -----------------------------------------
# CUSTOMER ACTIVITY
# -----------------------------------------

customer_features["customer_activity_days"] = (
    reference_date
    - customer_features["last_purchase_date"]
).dt.days


# -----------------------------------------
# DISPLAY CUSTOMER FEATURES
# -----------------------------------------

print("\nCustomer Features:")

print(
    customer_features[
        [
            "CustomerID",
            "purchase_frequency",
            "purchase_value",
            "customer_activity_days"
        ]
    ].head(10)
)

print(
    "\nTotal customers:",
    len(customer_features)
)


# -----------------------------------------
# PREPARE FEATURES
# -----------------------------------------

feature_cols = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days"
]

X = customer_features[feature_cols]


# -----------------------------------------
# SCALE FEATURES
# -----------------------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

print("\nFeatures scaled successfully!")


# -----------------------------------------
# K-MEANS CLUSTERING
# -----------------------------------------

kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

customer_features["cluster"] = (
    kmeans.fit_predict(X_scaled)
)

print("\nK-Means clustering completed!")


# -----------------------------------------
# HIERARCHICAL CLUSTERING
# -----------------------------------------

hierarchical = AgglomerativeClustering(
    n_clusters=4
)

customer_features["cluster_hierarchical"] = (
    hierarchical.fit_predict(X_scaled)
)

print("Hierarchical clustering completed!")


# -----------------------------------------
# K-MEANS CLUSTER SUMMARY
# -----------------------------------------

cluster_summary = (
    customer_features
    .groupby("cluster")[feature_cols]
    .mean()
    .round(2)
)

print("\nK-Means Cluster Summary:")
print(cluster_summary)


# -----------------------------------------
# HIERARCHICAL CLUSTER SUMMARY
# -----------------------------------------

hierarchical_summary = (
    customer_features
    .groupby("cluster_hierarchical")[feature_cols]
    .mean()
    .round(2)
)

print("\nHierarchical Cluster Summary:")
print(hierarchical_summary)


# -----------------------------------------
# ASSIGN BUSINESS SEGMENT NAMES
# -----------------------------------------

# We use the actual behavior found in our data:
#
# Highest purchase frequency
#     -> VIP / Loyal Customers
#
# Highest purchase value
#     -> High-Value Customers
#
# Highest inactivity
#     -> At-Risk / Fading Customers
#
# Remaining group
#     -> Occasional / Regular Shoppers


# Highest frequency cluster
vip_cluster = cluster_summary[
    "purchase_frequency"
].idxmax()


# Highest purchase value cluster
high_value_cluster = cluster_summary[
    "purchase_value"
].idxmax()


# Highest activity days among remaining clusters
remaining_clusters = [
    cluster
    for cluster in cluster_summary.index
    if cluster not in [vip_cluster, high_value_cluster]
]

at_risk_cluster = cluster_summary.loc[
    remaining_clusters,
    "customer_activity_days"
].idxmax()


# Remaining cluster
occasional_cluster = [
    cluster
    for cluster in cluster_summary.index
    if cluster not in [
        vip_cluster,
        high_value_cluster,
        at_risk_cluster
    ]
][0]


# -----------------------------------------
# CREATE SEGMENT MAPPING
# -----------------------------------------

segment_names = {
    vip_cluster: "VIP / Loyal Customers",
    high_value_cluster: "High-Value Customers",
    at_risk_cluster: "At-Risk / Fading Customers",
    occasional_cluster: "Occasional / Regular Shoppers"
}


customer_features["segment"] = (
    customer_features["cluster"]
    .map(segment_names)
)


# -----------------------------------------
# DISPLAY FINAL SEGMENTS
# -----------------------------------------

print("\nFinal Segment Mapping:")

for cluster, segment in segment_names.items():
    print(
        f"Cluster {cluster} -> {segment}"
    )


print("\nCustomer Segment Distribution:")

print(
    customer_features["segment"]
    .value_counts()
)


# -----------------------------------------
# SAVE FINAL OUTPUT
# -----------------------------------------

output_file = (
    "data/customer_segmentation_output.csv"
)

customer_features.to_csv(
    output_file,
    index=False
)

print(
    "\nCustomer segmentation output saved successfully!"
)

print(
    f"File: {output_file}"
)