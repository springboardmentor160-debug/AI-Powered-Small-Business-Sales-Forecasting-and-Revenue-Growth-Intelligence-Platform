import numpy as np
import pandas as pd
import pytest
from backend.ml.forecasting import m5_model_comparison

from backend.ml.forecasting.m5_features import create_features
from backend.ml.forecasting.m5_evaluation import (
    calculate_metrics,
    create_baseline_predictions,
    create_validation_split,
    validate_validation_period,
)


def make_feature_input(rows=120):
    """Create deterministic synthetic daily M5-style demand data."""
    dates = pd.date_range("2025-01-01", periods=rows, freq="D")
    return pd.DataFrame({
        "date": dates,
        "d": [f"d_{i}" for i in range(1, rows + 1)],
        "id": ["ITEM_1_STORE_1"] * rows,
        "item_id": ["ITEM_1"] * rows,
        "dept_id": ["DEPT_1"] * rows,
        "cat_id": ["CAT_1"] * rows,
        "store_id": ["STORE_1"] * rows,
        "state_id": ["CA"] * rows,
        "units_sold": np.arange(1, rows + 1, dtype=float),
        "sell_price": [10.0] * rows,
        "event_name_1": [None] * rows,
        "event_name_2": [None] * rows,
        "snap_CA": [0] * rows,
    })


def test_feature_engineering_does_not_modify_input():
    source = make_feature_input()
    original = source.copy(deep=True)
    create_features(source)
    pd.testing.assert_frame_equal(source, original)


def test_feature_engineering_sorts_dates_chronologically():
    source = make_feature_input().sample(frac=1, random_state=42)
    result = create_features(source)
    assert result["date"].is_monotonic_increasing
    assert result["date"].is_unique


def test_lag_features_use_correct_historical_values():
    result = create_features(make_feature_input())
    assert result.loc[28, "lag_28"] == 1.0
    assert result.loc[56, "lag_56"] == 1.0
    assert result.loc[84, "lag_84"] == 1.0
    assert result.loc[56, "lag_28"] == 29.0
    assert result.loc[84, "lag_56"] == 29.0
    assert result.loc[84, "lag_84"] == 1.0


def test_rolling_features_use_shifted_historical_demand():
    result = create_features(make_feature_input())
    assert result.loc[35, "rolling_mean_7_28"] == pytest.approx(5.0)
    assert result.loc[55, "rolling_mean_28_28"] == pytest.approx(14.5)


def test_calendar_features_are_calculated():
    result = create_features(make_feature_input())
    first_date = result.loc[0, "date"]
    assert result.loc[0, "day_of_month"] == first_date.day
    assert result.loc[0, "day_of_week"] == first_date.dayofweek
    assert result["is_weekend"].isin([0, 1]).all()
    assert result["is_event"].eq(0).all()
    assert result["snap_active"].eq(0).all()


def test_price_change_is_zero_for_constant_prices():
    result = create_features(make_feature_input())
    assert result["price_change"].eq(0).all()


def test_validation_split_reserves_final_28_rows():
    df = make_feature_input(rows=100)
    train, validation = create_validation_split(df)
    assert len(train) == 72
    assert len(validation) == 28
    assert train["date"].max() < validation["date"].min()
    assert validation["date"].iloc[0] == df["date"].iloc[72]


def test_validation_split_rejects_insufficient_rows():
    df = make_feature_input(rows=28)
    with pytest.raises(ValueError):
        create_validation_split(df)


def test_validation_period_accepts_28_consecutive_days(capsys):
    _, validation = create_validation_split(make_feature_input(rows=60))
    validate_validation_period(validation)
    assert "Validation horizon: PASS" in capsys.readouterr().out


def test_validation_period_rejects_missing_day():
    _, validation = create_validation_split(make_feature_input(rows=60))
    validation = validation.copy()
    validation.iloc[5, validation.columns.get_loc("date")] += pd.Timedelta(days=1)
    with pytest.raises(ValueError):
        validate_validation_period(validation)


def test_baseline_predictions_use_lag_28():
    validation = pd.DataFrame({
        "date": pd.date_range("2025-04-01", periods=3, freq="D"),
        "units_sold": [10.0, 20.0, 30.0],
        "lag_28": [8.0, 18.0, 28.0],
    })
    predictions = create_baseline_predictions(validation)
    assert predictions["actual_units"].tolist() == [10.0, 20.0, 30.0]
    assert predictions["predicted_units"].tolist() == [8.0, 18.0, 28.0]


def test_baseline_predictions_clip_negative_demand():
    validation = pd.DataFrame({
        "date": pd.date_range("2025-04-01", periods=2, freq="D"),
        "units_sold": [2.0, 4.0],
        "lag_28": [-3.0, 5.0],
    })
    predictions = create_baseline_predictions(validation)
    assert predictions["predicted_units"].tolist() == [0.0, 5.0]


def test_baseline_rejects_missing_required_columns():
    validation = pd.DataFrame({"date": ["2025-04-01"]})
    with pytest.raises(ValueError):
        create_baseline_predictions(validation)


def test_metrics_match_known_values():
    predictions = pd.DataFrame({
        "actual_units": [3.0, 5.0, 7.0],
        "predicted_units": [2.0, 5.0, 9.0],
    })
    metrics = calculate_metrics(predictions)
    assert metrics.loc[0, "mae"] == pytest.approx(1.0)
    assert metrics.loc[0, "rmse"] == pytest.approx(np.sqrt(5 / 3))
    assert metrics.loc[0, "validation_rows"] == 3


def test_validation_period_accepts_identical_date_sets(
    tmp_path, monkeypatch
):
    dates = pd.date_range("2025-03-01", periods=28, freq="D")

    paths = [
        tmp_path / "baseline.csv",
        tmp_path / "random_forest.csv",
        tmp_path / "xgboost.csv",
    ]

    for path in paths:
        pd.DataFrame({"date": dates}).to_csv(path, index=False)

    monkeypatch.setattr(
        m5_model_comparison, "BASELINE_PREDICTIONS_PATH", paths[0]
    )
    monkeypatch.setattr(
        m5_model_comparison, "RF_PREDICTIONS_PATH", paths[1]
    )
    monkeypatch.setattr(
        m5_model_comparison, "XGB_PREDICTIONS_PATH", paths[2]
    )

    assert m5_model_comparison.get_validation_period() == (
        "2025-03-01",
        "2025-03-28",
    )


def test_validation_period_rejects_different_dates_with_same_range_and_count(
    tmp_path, monkeypatch
):
    dates_a = pd.to_datetime(
        ["2025-03-01", "2025-03-02", "2025-03-04", "2025-03-05"]
    )
    dates_b = pd.to_datetime(
        ["2025-03-01", "2025-03-03", "2025-03-04", "2025-03-05"]
    )

    paths = [
        tmp_path / "baseline.csv",
        tmp_path / "random_forest.csv",
        tmp_path / "xgboost.csv",
    ]

    for path, dates in zip(paths, [dates_a, dates_b, dates_a]):
        pd.DataFrame({"date": dates}).to_csv(path, index=False)

    monkeypatch.setattr(
        m5_model_comparison, "BASELINE_PREDICTIONS_PATH", paths[0]
    )
    monkeypatch.setattr(
        m5_model_comparison, "RF_PREDICTIONS_PATH", paths[1]
    )
    monkeypatch.setattr(
        m5_model_comparison, "XGB_PREDICTIONS_PATH", paths[2]
    )

    with pytest.raises(ValueError, match="same validation period"):
        m5_model_comparison.get_validation_period()
