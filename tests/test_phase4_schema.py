from backend.models.demand_feature import DemandFeature
from backend.models.forecast_run import ForecastRun


def test_m5_specific_features_are_nullable_float_columns():
    expected_columns = [
        "lag_28",
        "lag_56",
        "lag_84",
        "rolling_mean_7_28",
    ]

    for column_name in expected_columns:
        column = DemandFeature.__table__.columns[column_name]

        assert column.nullable is True
        assert column.type.python_type is float


def test_generic_features_remain_separate_from_m5_features():
    generic_columns = ["lag_1", "lag_7", "rolling_mean_7"]

    for column_name in generic_columns:
        column = DemandFeature.__table__.columns[column_name]

        assert column.nullable is True
        assert column.type.python_type is float


def test_forecast_run_supports_evaluation_metadata():
    columns = ForecastRun.__table__.columns

    assert columns["evaluation_start"].nullable is True
    assert columns["evaluation_end"].nullable is True
    assert columns["forecast_target"].nullable is True


def test_forecast_horizon_can_be_unspecified_for_evaluation_runs():
    horizon_column = ForecastRun.__table__.columns["horizon"]

    assert horizon_column.nullable is True
    assert horizon_column.type.python_type is int
