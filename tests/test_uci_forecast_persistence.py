import pandas as pd
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models.forecast_result import ForecastResult
from backend.models.forecast_run import ForecastRun
from backend.models.model_metric import ModelMetric
from backend.services import uci_forecast_persistence_service as service


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def uci_artifacts(tmp_path, monkeypatch):
    comparison_path = tmp_path / "uci_model_comparison.csv"
    predictions_path = tmp_path / "uci_model_comparison_predictions.csv"

    models = [
        ("Prophet", "prophet_prediction", 100.0, 120.0),
        ("Random Forest", "random_forest_prediction", 80.0, 100.0),
        ("XGBoost", "xgboost_prediction", 90.0, 110.0),
    ]

    comparison_rows = []
    for model, _, mae, rmse in models:
        comparison_rows.append(
            {
                "model": model,
                "training_rows": 580,
                "test_rows": 145,
                "test_start": "2011-07-18",
                "test_end": "2011-12-09",
                "mae": mae,
                "rmse": rmse,
            }
        )

    dates = pd.date_range("2011-07-18", periods=145, freq="D")
    prediction_data = {
        "date": dates,
        "actual_revenue": [200.0] * 145,
    }
    for _, column, _, _ in models:
        prediction_data[column] = [150.0] * 145

    pd.DataFrame(comparison_rows).to_csv(comparison_path, index=False)
    pd.DataFrame(prediction_data).to_csv(predictions_path, index=False)

    monkeypatch.setattr(service, "COMPARISON_PATH", comparison_path)
    monkeypatch.setattr(service, "PREDICTIONS_PATH", predictions_path)


def test_persists_three_models_and_their_predictions(
    db_session, uci_artifacts
):
    result = service.persist_uci_forecasts(db_session)

    assert result["created_runs"] == 3
    assert result["skipped_runs"] == 0

    runs = db_session.scalars(
        select(ForecastRun).where(ForecastRun.source == "UCI")
    ).all()
    assert len(runs) == 3

    for run in runs:
        assert run.evaluation_start.isoformat() == "2011-07-18"
        assert run.evaluation_end.isoformat() == "2011-12-09"
        assert run.forecast_target == "revenue"
        assert run.horizon is None

        prediction_count = db_session.scalar(
            select(func.count(ForecastResult.id)).where(
                ForecastResult.forecast_run_id == run.id
            )
        )
        metric_count = db_session.scalar(
            select(func.count(ModelMetric.id)).where(
                ModelMetric.forecast_run_id == run.id
            )
        )
        assert prediction_count == 145
        assert metric_count == 2


def test_repeat_persistence_skips_existing_runs(db_session, uci_artifacts):
    first = service.persist_uci_forecasts(db_session)
    second = service.persist_uci_forecasts(db_session)

    assert first["created_runs"] == 3
    assert second["created_runs"] == 0
    assert second["skipped_runs"] == 3

    run_count = db_session.scalar(
        select(func.count(ForecastRun.id)).where(
            ForecastRun.source == "UCI"
        )
    )
    assert run_count == 3


def test_missing_artifact_raises_without_writing(
    db_session, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        service,
        "COMPARISON_PATH",
        tmp_path / "missing_comparison.csv",
    )
    monkeypatch.setattr(
        service,
        "PREDICTIONS_PATH",
        tmp_path / "missing_predictions.csv",
    )

    with pytest.raises(FileNotFoundError):
        service.persist_uci_forecasts(db_session)

    run_count = db_session.scalar(
        select(func.count(ForecastRun.id))
    )
    assert run_count == 0
