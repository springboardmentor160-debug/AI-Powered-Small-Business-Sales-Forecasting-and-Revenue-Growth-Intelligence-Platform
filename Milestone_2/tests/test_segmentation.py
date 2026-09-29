"""
Unit & Integration Tests for Customer Segmentation (Milestone 2)
"""

import os
import unittest
import pandas as pd
import numpy as np
from Milestone_2.ml.segmentation.feature_engineering import CustomerFeatureEngineer
from Milestone_2.ml.segmentation.kmeans import KMeansSegmenter
from Milestone_2.ml.segmentation.hierarchical import HierarchicalSegmenter
from Milestone_2.ml.segmentation.evaluation import SegmentationEvaluator

class TestCustomerSegmentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_path = "Milestone_2/data/source/cleaned_superstore.csv"

    def test_01_feature_engineering(self):
        fe = CustomerFeatureEngineer(self.source_path)
        df_feats = fe.create_features()
        
        self.assertIsNotNone(df_feats)
        self.assertGreater(len(df_feats), 0)
        self.assertIn("recency_days", df_feats.columns)
        self.assertIn("frequency_orders", df_feats.columns)
        self.assertIn("monetary_sales", df_feats.columns)

        X_scaled, cols = fe.scale_features()
        self.assertEqual(X_scaled.shape[0], len(df_feats))
        self.assertEqual(X_scaled.shape[1], len(cols))

    def test_02_kmeans_clustering(self):
        fe = CustomerFeatureEngineer(self.source_path)
        fe.create_features()
        X_scaled, _ = fe.scale_features()

        km = KMeansSegmenter(random_state=42)
        scores = km.search_best_k(X_scaled, k_range=range(2, 5))
        self.assertIn(2, scores)
        self.assertGreater(scores[2], 0.0)

        labels, best_score = km.fit_predict(X_scaled)
        self.assertEqual(len(labels), X_scaled.shape[0])
        self.assertGreater(best_score, 0.0)

    def test_03_hierarchical_clustering(self):
        fe = CustomerFeatureEngineer(self.source_path)
        fe.create_features()
        X_scaled, _ = fe.scale_features()

        hs = HierarchicalSegmenter(linkage="ward")
        labels, score = hs.fit_predict(X_scaled, k=2)
        self.assertEqual(len(labels), X_scaled.shape[0])
        self.assertGreater(score, 0.0)

    def test_04_segmentation_pipeline_execution(self):
        evaluator = SegmentationEvaluator(self.source_path)
        metrics = evaluator.run_pipeline(output_dir="Milestone_2/outputs/segmentation")

        self.assertIn("total_customers", metrics)
        self.assertIn("kmeans", metrics)
        self.assertIn("hierarchical", metrics)
        self.assertIn("segment_distribution", metrics)

        # Check output files exist
        self.assertTrue(os.path.exists("Milestone_2/outputs/segmentation/customer_segments.csv"))
        self.assertTrue(os.path.exists("Milestone_2/outputs/segmentation/cluster_summary.csv"))
        self.assertTrue(os.path.exists("Milestone_2/outputs/segmentation/segmentation_metrics.json"))

if __name__ == "__main__":
    unittest.main()
