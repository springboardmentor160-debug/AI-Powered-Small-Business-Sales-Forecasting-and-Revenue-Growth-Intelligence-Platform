import logging
from datetime import UTC, datetime

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import UCI_ARTIFACT_DIR
from backend.models.forecast_result import ForecastResult
from backend.models.forecast_run import ForecastRun
from backend.models.model_metric import ModelMetric

logger = logging.getLogger(__name__)

COMPARISON_PATH = UCI_ARTIFACT_DIR / "uci_model_comparison.csv"
PREDICTIONS_PATH = (
    UCI_ARTIFACT_DIR / "uci_model_comparison_predictions.csv"
)

MODEL_COLUMNS = {
    "Prophet": "prophet_prediction",
    "Random Forest": "random_forest_prediction",
    "XGBoost": "xgboost_prediction",
}

MODEL_VERSION = "m2-evaluation-v1"
FORECAST_TARGET = "revenue"


def persist_uci_forecasts(db: Session) -> dict:
    """Persist UCI historical revenue evaluation predictions and metrics."""

    for path in (COMPARISON_PATH, PREDICTIONS_PATH):
        if not path.is_file():
            raise FileNotFoundError(
                f"Required UCI forecast artifact not found: {path}"
            )

    comparison_df = pd.read_csv(COMPARISON_PATH)
    predictions_df = pd.read_csv(PREDICTIONS_PATH)

    required_comparison = {
        "model",
        "training_rows",
        "test_rows",
        "test_start",
        "test_end",
        "mae",
        "rmse",
    }
    required_predictions = {
        "date",
        "actual_revenue",
        *MODEL_COLUMNS.values(),
    }

    missing_comparison = required_comparison - set(comparison_df.columns)
    missing_predictions = required_predictions - set(predictions_df.columns)

    if missing_comparison:
        raise ValueError(
            "UCI comparison artifact missing columns: "
            + ", ".join(sorted(missing_comparison))
        )

    if missing_predictions:
        raise ValueError(
            "UCI prediction artifact missing columns: "
            + ", ".join(sorted(missing_predictions))
        )

    if comparison_df["model"].duplicated().any():
        raise ValueError("Duplicate model names in UCI comparison artifact.")

    if predictions_df.empty:
        raise ValueError("UCI prediction artifact contains no rows.")

    predictions_df = predictions_df.copy()
    predictions_df["date"] = pd.to_datetime(
        predictions_df["date"],
        errors="coerce",
    )

    numeric_columns = ["actual_revenue", *MODEL_COLUMNS.values()]
    for column in numeric_columns:
        predictions_df[column] = pd.to_numeric(
            predictions_df[column],
            errors="coerce",
        )

    if predictions_df["date"].isna().any():
        raise ValueError("Invalid dates in UCI prediction artifact.")

    if predictions_df["date"].duplicated().any():
        raise ValueError("Duplicate dates in UCI prediction artifact.")

    if predictions_df[numeric_columns].isna().any().any():
        raise ValueError(
            "Missing or non-numeric revenue values in UCI prediction artifact."
        )

    predictions_df = predictions_df.sort_values("date").reset_index(drop=True)

    expected_models = set(MODEL_COLUMNS)
    actual_models = set(comparison_df["model"].astype(str))
    if actual_models != expected_models:
        raise ValueError(
            "UCI model mismatch. "
            f"Expected {sorted(expected_models)}, got {sorted(actual_models)}."
        )

    persisted_runs = []
    skipped_runs = []

    try:
        for comparison in comparison_df.to_dict(orient="records"):
            model_name = str(comparison["model"])
            prediction_column = MODEL_COLUMNS[model_name]

            training_rows = int(comparison["training_rows"])
            test_rows = int(comparison["test_rows"])
            test_start = pd.to_datetime(
                comparison["test_start"],
                errors="raise",
            ).date()
            test_end = pd.to_datetime(
                comparison["test_end"],
                errors="raise",
            ).date()

            mae = float(comparison["mae"])
            rmse = float(comparison["rmse"])

            if training_rows <= 0 or test_rows <= 0:
                raise ValueError(
                    f"Invalid training/test row counts for {model_name}."
                )

            if test_start > test_end:
                raise ValueError(
                    f"Invalid evaluation date range for {model_name}."
                )

            if pd.isna(mae) or pd.isna(rmse):
                raise ValueError(
                    f"Invalid MAE/RMSE metrics for {model_name}."
                )

            model_predictions = predictions_df[
                ["date", prediction_column]
            ].copy()

            model_predictions = model_predictions[
                model_predictions["date"].dt.date.between(
                    test_start,
                    test_end,
                )
            ]

            if len(model_predictions) != test_rows:
                raise ValueError(
                    f"{model_name}: comparison reports {test_rows} test rows, "
                    f"but {len(model_predictions)} predictions fall in the "
                    "declared evaluation period."
                )

            prediction_dates = model_predictions["date"].dt.date
            if (
                not prediction_dates.eq(test_start).any()
                or not prediction_dates.eq(test_end).any()
            ):
                raise ValueError(
                    f"{model_name}: prediction dates do not cover the "
                    "declared evaluation boundaries."
                )

            existing_run = db.scalar(
                select(ForecastRun).where(
                    ForecastRun.source == "UCI",
                    ForecastRun.model_name == model_name,
                    ForecastRun.model_version == MODEL_VERSION,
                    ForecastRun.training_start.is_(None),
                    ForecastRun.training_end.is_(None),
                    ForecastRun.evaluation_start == test_start,
                    ForecastRun.evaluation_end == test_end,
                    ForecastRun.forecast_target == FORECAST_TARGET,
                    ForecastRun.horizon.is_(None),
                )
            )

            if existing_run is not None:
                skipped_runs.append(
                    {
                        "model": model_name,
                        "forecast_run_id": existing_run.id,
                        "status": "already_persisted",
                    }
                )
                continue

            run = ForecastRun(
                source="UCI",
                model_name=model_name,
                model_version=MODEL_VERSION,
                training_start=None,
                training_end=None,
                evaluation_start=test_start,
                evaluation_end=test_end,
                forecast_target=FORECAST_TARGET,
                horizon=None,
                created_at=datetime.now(UTC),
            )
            db.add(run)
            db.flush()

            result_records = [
                ForecastResult(
                    forecast_run_id=run.id,
                    forecast_date=row.date.date(),
                    predicted_value=float(getattr(row, prediction_column)),
                    lower_bound=None,
                    upper_bound=None,
                )
                for row in model_predictions.itertuples(index=False)
            ]

            metric_records = [
                ModelMetric(
                    forecast_run_id=run.id,
                    metric_name="MAE",
                    metric_value=mae,
                    evaluated_at=datetime.now(UTC),
                ),
                ModelMetric(
                    forecast_run_id=run.id,
                    metric_name="RMSE",
                    metric_value=rmse,
                    evaluated_at=datetime.now(UTC),
                ),
            ]

            db.add_all(result_records)
            db.add_all(metric_records)
            db.flush()

            persisted_runs.append(
                {
                    "model": model_name,
                    "forecast_run_id": run.id,
                    "forecast_rows": len(result_records),
                    "metric_rows": len(metric_records),
                    "training_rows_from_artifact": training_rows,
                    "evaluation_start": test_start.isoformat(),
                    "evaluation_end": test_end.isoformat(),
                    "forecast_target": FORECAST_TARGET,
                    "horizon": None,
                }
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    logger.info(
        "UCI forecast persistence completed: %s created, %s skipped.",
        len(persisted_runs),
        len(skipped_runs),
    )

    return {
        "source": "UCI",
        "status": "completed",
        "created_runs": len(persisted_runs),
        "skipped_runs": len(skipped_runs),
        "runs": persisted_runs,
        "skipped": skipped_runs,
    }
