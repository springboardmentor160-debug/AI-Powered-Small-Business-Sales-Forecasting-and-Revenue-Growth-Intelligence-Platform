import logging
from datetime import UTC, datetime

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import M5_ARTIFACT_DIR
from backend.models.demand_feature import DemandFeature
from backend.models.forecast_result import ForecastResult
from backend.models.forecast_run import ForecastRun
from backend.models.model_metric import ModelMetric

logger = logging.getLogger(__name__)

FEATURES_PATH = M5_ARTIFACT_DIR / "m5_features_sample.csv"
PREDICTIONS_PATH = M5_ARTIFACT_DIR / "m5_baseline_predictions.csv"
METRICS_PATH = M5_ARTIFACT_DIR / "m5_baseline_metrics.csv"


def persist_m5_baseline(db: Session) -> dict:
    """
    Persist the validated M5 baseline artifacts into PostgreSQL.

    This function does not modify the existing M5 forecasting
    or feature-engineering pipeline.
    """

    required_files = [
        FEATURES_PATH,
        PREDICTIONS_PATH,
        METRICS_PATH,
    ]

    missing_files = [
        str(path)
        for path in required_files
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Required M5 artifacts were not found: "
            + ", ".join(missing_files)
        )

    # ---------------------------------------------------------
    # Load validated M5 artifacts
    # ---------------------------------------------------------

    features_df = pd.read_csv(FEATURES_PATH)
    predictions_df = pd.read_csv(PREDICTIONS_PATH)
    metrics_df = pd.read_csv(METRICS_PATH)

    features_df["date"] = pd.to_datetime(
        features_df["date"],
        errors="coerce",
    )

    predictions_df["date"] = pd.to_datetime(
        predictions_df["date"],
        errors="coerce",
    )

    # ---------------------------------------------------------
    # Validate required columns
    # ---------------------------------------------------------

    required_feature_columns = [
        "date",
        "item_id",
        "store_id",
        "units_sold",
        "lag_28",
        "lag_56",
        "lag_84",
        "rolling_mean_7_28",
    ]

    required_prediction_columns = [
        "date",
        "predicted_units",
    ]

    required_metric_columns = [
        "model",
        "forecast_horizon_days",
        "mae",
        "rmse",
    ]

    missing_feature_columns = [
        column
        for column in required_feature_columns
        if column not in features_df.columns
    ]

    missing_prediction_columns = [
        column
        for column in required_prediction_columns
        if column not in predictions_df.columns
    ]

    missing_metric_columns = [
        column
        for column in required_metric_columns
        if column not in metrics_df.columns
    ]

    if missing_feature_columns:
        raise ValueError(
            "M5 feature artifact missing columns: "
            + ", ".join(missing_feature_columns)
        )

    if missing_prediction_columns:
        raise ValueError(
            "M5 prediction artifact missing columns: "
            + ", ".join(missing_prediction_columns)
        )

    if missing_metric_columns:
        raise ValueError(
            "M5 metrics artifact missing columns: "
            + ", ".join(missing_metric_columns)
        )

    # ---------------------------------------------------------
    # Identify the M5 development series
    # ---------------------------------------------------------

    item_id = str(features_df["item_id"].iloc[0])
    store_id = str(features_df["store_id"].iloc[0])

    training_start = features_df["date"].min().date()
    training_end = features_df["date"].max().date()

    horizon = int(
        metrics_df["forecast_horizon_days"].iloc[0]
    )

    model_name = str(
        metrics_df["model"].iloc[0]
    )

    # ---------------------------------------------------------
    # Create forecast run
    # ---------------------------------------------------------

    existing_run = db.scalar(
        select(ForecastRun).where(
            ForecastRun.source == "M5",
            ForecastRun.model_name == model_name,
            ForecastRun.model_version == "baseline-v1",
            ForecastRun.training_start == training_start,
            ForecastRun.training_end == training_end,
            ForecastRun.horizon == horizon,
        )
    )

    if existing_run:
        logger.info(
            "M5 forecast run already exists: run_id=%s",
            existing_run.id,
        )
        return {
            "forecast_run_id": existing_run.id,
            "source": "M5",
            "model": model_name,
            "model_version": "baseline-v1",
            "item_id": item_id,
            "store_id": store_id,
            "feature_rows": 0,
            "forecast_rows": 0,
            "metric_rows": 0,
            "status": "already_persisted",
        }

    forecast_run = ForecastRun(
        source="M5",
        model_name=model_name,
        model_version="baseline-v1",
        training_start=training_start,
        training_end=training_end,
        horizon=horizon,
        created_at=datetime.now(UTC),
    )

    db.add(forecast_run)
    db.flush()
    # ---------------------------------------------------------
    # Persist demand features
    # ---------------------------------------------------------

    feature_records = []

    for row in features_df.itertuples(index=False):
        feature_records.append(

            DemandFeature(
                product_id=None,
                store_code=str(row.store_id),
                feature_date=row.date.date(),
                units_sold=float(row.units_sold),
                lag_1=None,
                lag_7=None,
                rolling_mean_7=None,
                lag_28=float(row.lag_28),
                lag_56=float(row.lag_56),
                lag_84=float(row.lag_84),
                rolling_mean_7_28=float(
                    row.rolling_mean_7_28
                ),
            )

        )

    if feature_records:
        db.add_all(feature_records)

    # ---------------------------------------------------------
    # Persist forecast results
    # ---------------------------------------------------------

    forecast_records = []

    for row in predictions_df.itertuples(index=False):
        forecast_records.append(
            ForecastResult(
                forecast_run_id=forecast_run.id,
                forecast_date=row.date.date(),
                predicted_value=float(
                    row.predicted_units
                ),
                lower_bound=None,
                upper_bound=None,
            )
        )

    if forecast_records:
        db.add_all(forecast_records)

    # ---------------------------------------------------------
    # Persist model metrics
    # ---------------------------------------------------------

    metric_records = []

    for metric_name in ["mae", "rmse"]:
        metric_records.append(
            ModelMetric(
                forecast_run_id=forecast_run.id,
                metric_name=metric_name.upper(),
                metric_value=float(
                    metrics_df[metric_name].iloc[0]
                ),
                evaluated_at=datetime.now(UTC),
            )
        )

    db.add_all(metric_records)

    db.commit()

    logger.info(
        "M5 baseline persistence completed: "
        "run_id=%s, features=%s, forecasts=%s, metrics=%s",
        forecast_run.id,
        len(feature_records),
        len(forecast_records),
        len(metric_records),
    )

    return {
        "forecast_run_id": forecast_run.id,
        "source": "M5",
        "model": model_name,
        "model_version": "baseline-v1",
        "item_id": item_id,
        "store_id": store_id,
        "feature_rows": len(feature_records),
        "forecast_rows": len(forecast_records),
        "metric_rows": len(metric_records),
    }