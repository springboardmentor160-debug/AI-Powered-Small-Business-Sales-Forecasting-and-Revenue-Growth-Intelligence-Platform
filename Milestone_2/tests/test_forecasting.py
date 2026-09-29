"""
Unit & Integration Tests for Sales & Revenue Forecasting (Milestone 2)
"""

import os
import unittest
import pandas as pd
import numpy as np
from Milestone_2.ml.forecasting.data_preparation import ForecastingDataPreparer
from Milestone_2.ml.forecasting.prophet_model import ProphetForecaster
from Milestone_2.ml.forecasting.xgboost_model import XGBoostForecaster
from Milestone_2.ml.forecasting.random_forest_model import RandomForestForecaster
from Milestone_2.ml.forecasting.evaluation import ForecastingEvaluator

class TestSalesForecasting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_path = "Milestone_2/data/source/cleaned_superstore.csv"

    def test_01_data_preparation(self):
        prep = ForecastingDataPreparer(self.source_path)
        df_monthly = prep.prepare_monthly_series()
        
        self.assertIsNotNone(df_monthly)
        self.assertGreater(len(df_monthly), 0)
        self.assertIn("ds", df_monthly.columns)
        self.assertIn("y", df_monthly.columns)
        self.assertIn("y_lag1", df_monthly.columns)

    def test_02_prophet_model(self):
        prep = ForecastingDataPreparer(self.source_path)
        df_monthly = prep.prepare_monthly_series()

        pf = ProphetForecaster()
        fcst = pf.fit_predict(df_monthly[['ds', 'y']], horizon_months=6)

        self.assertEqual(len(fcst), len(df_monthly) + 6)
        self.assertIn("yhat", fcst.columns)
        self.assertIn("yhat_lower", fcst.columns)

    def test_03_xgboost_model(self):
        prep = ForecastingDataPreparer(self.source_path)
        df_monthly = prep.prepare_monthly_series()

        xgb_f = XGBoostForecaster()
        fcst = xgb_f.fit_predict(df_monthly[['ds', 'y']], horizon_months=6)

        self.assertIsNotNone(fcst)
        self.assertIn("yhat", fcst.columns)

    def test_04_random_forest_model(self):
        prep = ForecastingDataPreparer(self.source_path)
        df_monthly = prep.prepare_monthly_series()

        rf_f = RandomForestForecaster()
        fcst = rf_f.fit_predict(df_monthly[['ds', 'y']], horizon_months=6)

        self.assertIsNotNone(fcst)
        self.assertIn("yhat", fcst.columns)

    def test_05_forecasting_pipeline_execution(self):
        evaluator = ForecastingEvaluator(self.source_path)
        metrics = evaluator.run_pipeline(output_dir="Milestone_2/outputs/forecasting", horizon_months=12)

        self.assertIn("best_performing_model", metrics)
        self.assertIn("model_metrics", metrics)
        self.assertIn("Prophet", metrics["model_metrics"])
        self.assertIn("XGBoost", metrics["model_metrics"])
        self.assertIn("Random Forest", metrics["model_metrics"])

        # Check output files exist
        self.assertTrue(os.path.exists("Milestone_2/outputs/forecasting/prophet_forecast.csv"))
        self.assertTrue(os.path.exists("Milestone_2/outputs/forecasting/xgboost_forecast.csv"))
        self.assertTrue(os.path.exists("Milestone_2/outputs/forecasting/random_forest_forecast.csv"))
        self.assertTrue(os.path.exists("Milestone_2/outputs/forecasting/combined_forecasts.csv"))
        self.assertTrue(os.path.exists("Milestone_2/outputs/forecasting/model_metrics.json"))

if __name__ == "__main__":
    unittest.main()
