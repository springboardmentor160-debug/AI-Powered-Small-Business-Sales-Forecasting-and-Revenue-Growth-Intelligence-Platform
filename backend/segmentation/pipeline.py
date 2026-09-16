import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environment
import matplotlib.pyplot as plt


RAW_CSV_PATH = os.path.join("data", "processed", "clean_sales_data.csv")
OUTPUT_CSV_PATH = os.path.join("data", "processed", "customer_features.csv")
REPORTS_DIR = os.path.join("reports")
DENDROGRAM_PATH = os.path.join(REPORTS_DIR, "dendrogram.png")


def extract_customer_features(df_sales: pd.DataFrame) -> pd.DataFrame:
    """
    Extract customer-level features:
    1. purchase_frequency: Number of orders per customer
    2. purchase_value: Total revenue per customer
    3. customer_activity_days: Span of activity from min to max order date (in days, min 1)
    """
    df = df_sales.copy()
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    if 'total_amount' not in df.columns:
        df['total_amount'] = df['quantity'] * df['unit_price']
        
    grouped = df.groupby('customer_id').agg(
        purchase_frequency=('order_id', 'count'),
        purchase_value=('total_amount', 'sum'),
        min_date=('order_date', 'min'),
        max_date=('order_date', 'max')
    ).reset_index()

    # Calculate active span in days (min 1 day)
    grouped['customer_activity_days'] = (
        (grouped['max_date'] - grouped['min_date']).dt.days + 1
    ).astype(int)

    features_df = grouped[['customer_id', 'purchase_frequency', 'purchase_value', 'customer_activity_days']]
    return features_df


def assign_business_segments(summary_df: pd.DataFrame) -> Dict[int, str]:
    """
    Dynamically map numeric cluster IDs to business segment names based on actual average behavior:
    - VIP / Loyal Customers (highest value/frequency)
    - Regular Customers (high value/frequency)
    - Occasional Shoppers (moderate value/frequency)
    - At-Risk / Fading Customers (lowest value/frequency)
    """
    # Sort cluster summaries by purchase_value and purchase_frequency descending
    sorted_clusters = summary_df.sort_values(
        by=['purchase_value', 'purchase_frequency', 'customer_activity_days'],
        ascending=False
    )['cluster'].tolist()

    segment_labels = [
        "VIP / Loyal Customers",
        "Regular Customers",
        "Occasional Shoppers",
        "At-Risk / Fading Customers"
    ]

    mapping = {}
    for idx, cluster_id in enumerate(sorted_clusters):
        # Assign label in order of rank, fallback if clusters > 4
        label = segment_labels[idx] if idx < len(segment_labels) else f"Segment {cluster_id}"
        mapping[cluster_id] = label

    return mapping


def run_segmentation_pipeline(
    sales_csv_path: str = RAW_CSV_PATH,
    output_csv_path: str = OUTPUT_CSV_PATH,
    k_clusters: int = 4
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Full Customer Segmentation Pipeline (Days 1–4):
    1. Extract customer features
    2. Scale numerical features
    3. Run K-Means clustering (k=4)
    4. Run Hierarchical Agglomerative clustering (n_clusters=4)
    5. Generate scipy dendrogram
    6. Analyze cluster summaries and assign business segment names
    7. Export customer_features.csv
    """
    if not os.path.exists(sales_csv_path):
        raise FileNotFoundError(f"Sales dataset not found at {sales_csv_path}")

    df_sales = pd.read_csv(sales_csv_path)
    cust_df = extract_customer_features(df_sales)

    if cust_df.empty:
        raise ValueError("No customer features extracted.")

    # Determine optimal number of clusters if customer count is smaller than requested k
    n_samples = len(cust_df)
    n_clusters = min(k_clusters, n_samples)

    feature_cols = ['purchase_frequency', 'purchase_value', 'customer_activity_days']
    X = cust_df[feature_cols].values

    # Feature Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Day 1-2: K-Means Clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cust_df['cluster'] = kmeans.fit_predict(X_scaled)

    # Day 3-4: Hierarchical Clustering (Agglomerative)
    hierarchical = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
    cust_df['cluster_hierarchical'] = hierarchical.fit_predict(X_scaled)

    # Generate Dendrogram Visualization if scipy is available
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    plt.figure(figsize=(8, 5))
    linked = linkage(X_scaled, method='ward')
    dendrogram(
        linked,
        labels=cust_df['customer_id'].values,
        orientation='top',
        distance_sort='descending',
        show_leaf_counts=True
    )
    plt.title("Hierarchical Clustering Dendrogram (Ward Linkage)")
    plt.xlabel("Customer ID")
    plt.ylabel("Euclidean Distance")
    plt.tight_layout()
    plt.savefig(DENDROGRAM_PATH)
    plt.close()

    # K-Means Cluster Summary & Segment Naming
    kmeans_summary = cust_df.groupby('cluster').agg(
        purchase_frequency=('purchase_frequency', 'mean'),
        purchase_value=('purchase_value', 'mean'),
        customer_activity_days=('customer_activity_days', 'mean'),
        customer_count=('customer_id', 'count')
    ).reset_index()

    segment_map = assign_business_segments(kmeans_summary)
    cust_df['segment'] = cust_df['cluster'].map(segment_map)

    # Hierarchical Cluster Summary
    hierarchical_summary = cust_df.groupby('cluster_hierarchical').agg(
        purchase_frequency=('purchase_frequency', 'mean'),
        purchase_value=('purchase_value', 'mean'),
        customer_activity_days=('customer_activity_days', 'mean'),
        customer_count=('customer_id', 'count')
    ).reset_index().to_dict(orient='records')

    # Reorder columns as expected
    cols_order = [
        'customer_id',
        'purchase_frequency',
        'purchase_value',
        'customer_activity_days',
        'cluster',
        'cluster_hierarchical',
        'segment'
    ]
    cust_df = cust_df[cols_order]

    # Save to data/processed/customer_features.csv
    cust_df.to_csv(output_csv_path, index=False)

    # Construct final summary payload
    segment_summary = cust_df.groupby('segment').agg(
        customer_count=('customer_id', 'count'),
        avg_purchase_frequency=('purchase_frequency', 'mean'),
        avg_purchase_value=('purchase_value', 'mean'),
        avg_activity_days=('customer_activity_days', 'mean')
    ).reset_index().to_dict(orient='records')

    summary_metadata = {
        "total_customers": n_samples,
        "n_clusters_used": n_clusters,
        "segments": segment_summary,
        "hierarchical_summary": hierarchical_summary,
        "dendrogram_saved": DENDROGRAM_PATH
    }

    return cust_df, summary_metadata
