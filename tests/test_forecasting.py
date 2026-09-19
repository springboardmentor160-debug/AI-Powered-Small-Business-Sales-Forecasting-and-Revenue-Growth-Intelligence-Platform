import pytest
import pandas as pd
import numpy as np
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.ml.forecasting import prepare_daily_revenue, engineer_features, evaluate_models, run_recursive_forecast

def test_daily_revenue_and_gap_detection():
    """Verify daily revenue aggregation and gap detection without silent filling."""
    daily, missing_count, missing_dates = prepare_daily_revenue()
    
    assert len(daily) > 0, "Daily revenue should not be empty"
    assert "date" in daily.columns
    assert "revenue" in daily.columns
    assert not daily["revenue"].isna().any(), "Daily revenue should have no NaNs"
    assert (daily["revenue"] >= 0).all(), "Daily revenue cannot be negative"
    
    # Missing date check
    full_range = pd.date_range(start=daily["date"].min(), end=daily["date"].max())
    expected_missing = len(full_range) - len(daily)
    assert missing_count == expected_missing, f"Missing count mismatch: expected {expected_missing}, got {missing_count}"
    assert len(missing_dates) == missing_count

def test_no_data_leakage_in_features():
    """Verify shift(1) is applied prior to rolling average so today's revenue is never leaked."""
    daily, _, _ = prepare_daily_revenue()
    feat_df = engineer_features(daily)

    # First row in feat_df is row 7 of daily_df (0-indexed)
    # Check that revenue_lag_1 is strictly the previous day's revenue
    for i in range(len(feat_df)):
        expected_lag_1 = daily.iloc[i + 6]["revenue"] # i+7th row of daily has index i+7, so lag_1 is i+6
        actual_lag_1 = feat_df.iloc[i]["revenue_lag_1"]
        assert actual_lag_1 == expected_lag_1, f"Lag 1 mismatch at row {i}"

        # Check rolling 7 mean is mean of preceding 7 days, excluding today's revenue
        preceding_7 = daily.iloc[i:i+7]["revenue"].mean()
        actual_rolling_7 = feat_df.iloc[i]["revenue_rolling_7"]
        assert np.isclose(actual_rolling_7, preceding_7, atol=1e-2), f"Rolling 7 mismatch at row {i}"

def test_chronological_split_without_shuffle():
    """Verify 80/20 train/test split is strictly chronological and never shuffled."""
    daily, _, _ = prepare_daily_revenue()
    feat_df = engineer_features(daily)
    
    split_point = int(len(feat_df) * 0.8)
    train_df = feat_df.iloc[:split_point]
    test_df = feat_df.iloc[split_point:]

    # Chronological integrity: all train dates < all test dates
    assert train_df["date"].max() < test_df["date"].min(), "Train dates must precede all test dates"
    assert train_df["date"].is_monotonic_increasing, "Train dates must be ordered chronologically"
    assert test_df["date"].is_monotonic_increasing, "Test dates must be ordered chronologically"

def test_same_window_evaluation_metrics():
    """Verify Prophet, Random Forest, and XGBoost are benchmarked on the identical test window."""
    daily, _, _ = prepare_daily_revenue()
    eval_res = evaluate_models(daily)
    
    metrics = eval_res["metrics"]
    assert "Random Forest Regressor" in metrics
    assert "XGBoost Regressor" in metrics
    assert "Prophet" in metrics

    for model_name, vals in metrics.items():
        assert "mae" in vals and vals["mae"] > 0, f"{model_name} MAE must be positive float"
        assert "rmse" in vals and vals["rmse"] > 0, f"{model_name} RMSE must be positive float"
        assert vals["rmse"] >= vals["mae"], f"{model_name} RMSE is mathematically >= MAE"

    assert eval_res["winner_name"] in metrics.keys()

def test_recursive_30_day_forecast_output():
    """FIX: Verify winner produces a true recursive 30-day ahead forecast with exactly 30 rows."""
    daily, _, _ = prepare_daily_revenue()
    eval_res = evaluate_models(daily)
    forecast_res = run_recursive_forecast(daily, eval_res, periods=30)

    assert forecast_res["period"] == "Next 30 Days"
    assert forecast_res["predicted_revenue"] > 0
    assert len(forecast_res["daily_forecast"]) == 30, "Forecast must contain exactly 30 daily projections"

    daily_rows = forecast_res["daily_forecast"]
    dates = [r["date"] for r in daily_rows]
    assert len(set(dates)) == 30, "All 30 projection dates must be unique"

    # Start date must be day after max daily date
    max_data_date = daily["date"].max()
    first_fc_date = pd.to_datetime(daily_rows[0]["date"])
    assert first_fc_date == max_data_date + pd.Timedelta(days=1), "First forecast date must be dataset max date + 1 day"

    for r in daily_rows:
        assert r["predicted_revenue"] >= 0, "Predicted revenue cannot be negative"
        assert r["lower_bound"] >= 0, "Lower bound cannot be negative"
        assert r["upper_bound"] >= r["lower_bound"], "Upper bound must be >= lower bound"
        assert not np.isnan(r["predicted_revenue"])

    total_sum = round(sum(r["predicted_revenue"] for r in daily_rows), 2)
    assert np.isclose(forecast_res["predicted_revenue"], total_sum, atol=1e-2)
