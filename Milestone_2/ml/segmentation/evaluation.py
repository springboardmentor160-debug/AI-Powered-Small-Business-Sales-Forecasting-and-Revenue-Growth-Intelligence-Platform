"""
Evaluation & Segment Analysis Module for Customer Segmentation (Milestone 2)
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any
from .feature_engineering import CustomerFeatureEngineer
from .kmeans import KMeansSegmenter
from .hierarchical import HierarchicalSegmenter

class SegmentationEvaluator:
    def __init__(self, source_path: str = "Milestone_2/data/source/cleaned_superstore.csv"):
        self.source_path = source_path
        self.fe = CustomerFeatureEngineer(source_path)
        self.df_features = None
        self.X_scaled = None
        self.feature_cols = None

    def prepare(self):
        self.df_features = self.fe.create_features()
        self.X_scaled, self.feature_cols = self.fe.scale_features()
        return self.df_features

    def run_pipeline(self, output_dir: str = "Milestone_2/outputs/segmentation") -> Dict[str, Any]:
        if self.df_features is None:
            self.prepare()

        # 1. K-Means
        kmeans_seg = KMeansSegmenter(random_state=42)
        km_scores = kmeans_seg.search_best_k(self.X_scaled, k_range=range(2, 6))
        km_labels, km_best_score = kmeans_seg.fit_predict(self.X_scaled)
        best_k_km = kmeans_seg.best_k

        # 2. Hierarchical
        h_seg = HierarchicalSegmenter(linkage='ward')
        h_scores = h_seg.search_best_k(self.X_scaled, k_range=range(2, 6))
        h_labels, h_best_score = h_seg.fit_predict(self.X_scaled, k=best_k_km) # use same k or best k for comparison

        # Attach raw cluster IDs
        self.df_features['kmeans_cluster'] = km_labels
        self.df_features['hierarchical_cluster'] = h_labels

        # 3. Dynamic Segment Naming based on Cluster Characteristics (K-Means primary)
        cluster_profiles = self.df_features.groupby('kmeans_cluster').agg({
            'recency_days': 'mean',
            'frequency_orders': 'mean',
            'monetary_sales': ['mean', 'sum'],
            'avg_order_value': 'mean',
            'total_profit': 'mean',
            'avg_discount': 'mean',
            'customer_id': 'count'
        })

        cluster_profiles.columns = [
            'mean_recency', 'mean_frequency', 'mean_monetary', 'total_monetary',
            'mean_aov', 'mean_profit', 'mean_discount', 'customer_count'
        ]

        total_customers = len(self.df_features)
        total_sales = self.df_features['monetary_sales'].sum()

        cluster_profiles['pct_customers'] = (cluster_profiles['customer_count'] / total_customers * 100).round(2)
        cluster_profiles['pct_sales'] = (cluster_profiles['total_monetary'] / total_sales * 100).round(2)

        # Dynamic name assignment rules based on relative standard scores across clusters
        segment_names = {}
        
        # Rank clusters by monetary sales and frequency
        avg_monetary = cluster_profiles['mean_monetary'].mean()
        avg_recency = cluster_profiles['mean_recency'].mean()
        avg_freq = cluster_profiles['mean_frequency'].mean()
        avg_disc = cluster_profiles['mean_discount'].mean()

        for c_id, row in cluster_profiles.iterrows():
            if row['mean_monetary'] >= 1.3 * avg_monetary and row['mean_recency'] <= avg_recency:
                name = "High-Value Champions"
            elif row['mean_monetary'] >= 1.0 * avg_monetary and row['mean_recency'] <= 1.1 * avg_recency:
                name = "Loyal High-Volume Buyers"
            elif row['mean_discount'] > 1.15 * avg_disc:
                name = "Discount-Sensitive Buyers"
            elif row['mean_recency'] > 1.2 * avg_recency:
                name = "Low-Activity / At-Risk Customers"
            elif row['mean_frequency'] < avg_freq and row['mean_monetary'] < avg_monetary:
                name = "Occasional Small Buyers"
            else:
                name = "Regular Steady Customers"
            
            segment_names[c_id] = name

        # Handle duplicates in segment names by attaching cluster id if needed
        used_names = {}
        final_segment_map = {}
        for c_id, name in segment_names.items():
            if name in used_names:
                used_names[name] += 1
                final_segment_map[c_id] = f"{name} (Group {used_names[name]})"
            else:
                used_names[name] = 1
                final_segment_map[c_id] = name

        self.df_features['segment_name'] = self.df_features['kmeans_cluster'].map(final_segment_map)
        cluster_profiles['segment_name'] = cluster_profiles.index.map(final_segment_map)

        # Save outputs
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Customer Segments CSV
        cust_segments_path = os.path.join(output_dir, "customer_segments.csv")
        self.df_features.to_csv(cust_segments_path, index=False)

        # 2. Cluster Summary CSV
        summary_path = os.path.join(output_dir, "cluster_summary.csv")
        cluster_profiles.to_csv(summary_path)

        # 3. Metrics JSON
        metrics = {
            "total_customers": int(total_customers),
            "feature_columns": self.feature_cols,
            "kmeans": {
                "best_k": int(best_k_km),
                "silhouette_score": round(km_best_score, 4),
                "k_search_scores": {int(k): round(v, 4) for k, v in km_scores.items()}
            },
            "hierarchical": {
                "k": int(best_k_km),
                "silhouette_score": round(h_best_score, 4),
                "k_search_scores": {int(k): round(v, 4) for k, v in h_scores.items()}
            },
            "segment_distribution": {
                name: {
                    "cluster_id": int(c_id),
                    "customer_count": int(row['customer_count']),
                    "pct_customers": float(row['pct_customers']),
                    "total_sales": round(float(row['total_monetary']), 2),
                    "pct_sales": float(row['pct_sales']),
                    "mean_recency_days": round(float(row['mean_recency']), 1),
                    "mean_frequency_orders": round(float(row['mean_frequency']), 1),
                    "mean_monetary_sales": round(float(row['mean_monetary']), 2),
                    "mean_order_value": round(float(row['mean_aov']), 2),
                    "mean_discount_rate": round(float(row['mean_discount']), 3)
                }
                for c_id, row in cluster_profiles.iterrows()
                for name in [final_segment_map[c_id]]
            }
        }

        metrics_path = os.path.join(output_dir, "segmentation_metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)

        # Optional DB Persistence via Service Layer
        try:
            from ...backend.database import SessionLocal
            from ...backend.db_service import save_segmentation_results_to_db
            db_session = SessionLocal()
            save_segmentation_results_to_db(self.df_features, cluster_profiles, metrics, db_session)
            db_session.close()
        except Exception as e:
            print(f"[DB Notice] Could not auto-persist segmentation to DB from pipeline runner: {e}")

        print(f"Segmentation results successfully generated in {output_dir}")
        return metrics

if __name__ == "__main__":
    evaluator = SegmentationEvaluator()
    evaluator.run_pipeline()

