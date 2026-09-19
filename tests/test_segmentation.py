import pytest
import pandas as pd
import numpy as np
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.ml.segmentation import build_customer_features, run_segmentation

def test_one_row_per_customer_and_no_nans():
    """Verify customer features are strictly one row per customer with zero NaNs."""
    cf = build_customer_features()
    
    assert len(cf) > 0, "Customer features should not be empty"
    assert cf["customer_id"].is_unique, "Each row must represent exactly one unique customer"
    
    # Check for NaNs
    assert not cf["purchase_frequency"].isna().any(), "purchase_frequency contains NaN"
    assert not cf["purchase_value"].isna().any(), "purchase_value contains NaN"
    assert not cf["customer_activity_days"].isna().any(), "customer_activity_days contains NaN"

def test_recency_anchored_to_dataset_max_date():
    """FIX: Verify recency is anchored to (max order_date in data + 1 day), NOT datetime.now()."""
    df = pd.read_csv(os.path.join(project_root, "cleaned_sales_data.csv"))
    if "customer_id" in df.columns:
        df = df[df["customer_id"] != "GUEST"]
    
    date_col = "order_date" if "order_date" in df.columns else "date"
    df[date_col] = pd.to_datetime(df[date_col])
    max_data_date = df[date_col].max() + pd.Timedelta(days=1)
    
    cf = build_customer_features()
    
    # Check each customer's activity days calculation
    for _, row in cf.iterrows():
        cust_tx = df[df["customer_id"] == row["customer_id"]]
        expected_days = (max_data_date - cust_tx[date_col].max()).days
        assert row["customer_activity_days"] == expected_days, (
            f"Customer {row['customer_id']} recency mismatch: expected {expected_days}, got {row['customer_activity_days']}"
        )
    
    # Activity days must always be >= 1 because anchor is max_date + 1 day
    assert (cf["customer_activity_days"] >= 1).all(), "Activity days must be >= 1 day"

def test_both_clustering_columns_preserved():
    """Verify both KMeans and Hierarchical cluster label columns are preserved."""
    cf = build_customer_features()
    res = run_segmentation(cf)
    features_with_clusters = res["customer_features"]

    assert "cluster" in features_with_clusters.columns, "K-Means cluster column missing"
    assert "cluster_hierarchical" in features_with_clusters.columns, "Hierarchical cluster column missing"
    assert features_with_clusters["cluster"].nunique() == 4, "K-Means should generate 4 clusters"
    assert features_with_clusters["cluster_hierarchical"].nunique() == 4, "Hierarchical should generate 4 clusters"

def test_unique_complete_segment_names():
    """FIX: Verify programmatic segment naming assigns all 4 canonical business segment names."""
    cf = build_customer_features()
    res = run_segmentation(cf)
    features_with_clusters = res["customer_features"]

    expected_segments = {
        "VIP / Loyal Customers",
        "Regular Customers",
        "Occasional Shoppers",
        "At-Risk / Fading Customers"
    }

    assigned_segments = set(features_with_clusters["segment"].dropna().unique())
    assert assigned_segments == expected_segments, f"Segments mismatch. Found: {assigned_segments}"
    assert not features_with_clusters["segment"].isna().any(), "Every customer must have an assigned segment"
    assert not features_with_clusters["segment_description"].isna().any(), "Every customer must have a segment description"

def test_cluster_distinctness_and_agreement():
    """Verify silhouette score indicates distinct clusters and ARI shows high agreement."""
    cf = build_customer_features()
    res = run_segmentation(cf)

    ari = res["adjusted_rand_index"]
    assert ari > 0.6, f"Expected strong agreement between KMeans and Hierarchical (ARI > 0.6), got {ari}"
    
    sil = res["silhouette_scores"]
    assert "k_4" in sil
    assert sil["k_4"] > 0.25, f"K=4 silhouette score should be solid (>0.25), got {sil['k_4']}"
