"""
Unit & Integration Tests for Backend API & Dashboard Data Endpoints (Milestone 2)
"""

import unittest
from fastapi.testclient import TestClient
from Milestone_2.backend.main import app

class TestBackendAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_overview_endpoint(self):
        res = self.client.get("/api/overview")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_sales", data)
        self.assertIn("total_customers", data)
        self.assertIn("best_forecasting_model", data)

    def test_02_segmentation_summary_endpoint(self):
        res = self.client.get("/api/segmentation/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metrics", data)
        self.assertIn("cluster_summary", data)

    def test_03_segmentation_customers_endpoint(self):
        res = self.client.get("/api/segmentation/customers?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_count", data)
        self.assertIn("customers", data)
        self.assertLessEqual(len(data["customers"]), 10)

    def test_04_forecasting_predictions_endpoint(self):
        res = self.client.get("/api/forecasting/predictions")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("records_count", data)
        self.assertIn("data", data)

    def test_05_forecasting_metrics_endpoint(self):
        res = self.client.get("/api/forecasting/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("model_metrics", data)

    def test_06_reports_endpoint(self):
        res = self.client.get("/api/reports/segmentation")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("content", data)
        self.assertIn("Customer Segmentation Analysis Report", data["content"])

if __name__ == "__main__":
    unittest.main()
