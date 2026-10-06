"""
MarketMindAI - M5 Baseline Evaluation
--------------------------------------
Evaluates a simple seasonal-naive baseline for a 28-day forecast.

Baseline:
    prediction(t) = actual demand(t - 28 days)

Input:
    backend/artifacts/milestone-2/forecasting/m5_features_sample.csv

Outputs:
    backend/artifacts/milestone-2/forecasting/m5_baseline_predictions.csv
    backend/artifacts/milestone-2/forecasting/m5_baseline_metrics.csv

Important:
- Uses the final 28 days as a time-based validation set.
- No future validation demand is used to create predictions.
- Raw M5 files remain unchanged.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
    / "m5_features_sample.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

PREDICTIONS_PATH = (
    OUTPUT_DIR
    / "m5_baseline_predictions.csv"
)

METRICS_PATH = (
    OUTPUT_DIR
    / "m5_baseline_metrics.csv"
)


# ---------------------------------------------------------------------
# FORECAST SETTINGS
# ---------------------------------------------------------------------

FORECAST_HORIZON = 28


# ---------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------

def load_dataset() -> pd.DataFrame:
    """
    Load the prepared M5 feature dataset.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"M5 feature dataset not found:\n{INPUT_PATH}"
        )

    print(f"\nLoading:\n{INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df = (
        df.sort_values("date")
        .reset_index(drop=True)
    )

    return df


# ---------------------------------------------------------------------
# CREATE TIME-BASED VALIDATION SET
# ---------------------------------------------------------------------

def create_validation_split(
    df: pd.DataFrame,
):
    """
    Reserve the final 28 observations for validation.
    """

    if len(df) <= FORECAST_HORIZON:
        raise ValueError(
            "Not enough observations for a 28-day validation horizon."
        )

    train_df = df.iloc[
        :-FORECAST_HORIZON
    ].copy()

    validation_df = df.iloc[
        -FORECAST_HORIZON:
    ].copy()

    return train_df, validation_df


# ---------------------------------------------------------------------
# VALIDATE HORIZON
# ---------------------------------------------------------------------

def validate_validation_period(
    validation_df: pd.DataFrame,
) -> None:
    """
    Confirm that validation contains exactly 28 consecutive days.
    """

    print("\n" + "=" * 75)
    print("M5 TIME-BASED VALIDATION")
    print("=" * 75)

    print(
        f"Validation rows: "
        f"{len(validation_df):,}"
    )

    print(
        f"Validation start: "
        f"{validation_df['date'].min().date()}"
    )

    print(
        f"Validation end: "
        f"{validation_df['date'].max().date()}"
    )

    expected_rows = FORECAST_HORIZON

    if len(validation_df) == expected_rows:
        print("Validation horizon: PASS")
    else:
        print(
            f"Validation horizon: FAIL "
            f"(expected {expected_rows})"
        )
        raise ValueError(
            "Validation horizon is not exactly 28 observations."
        )

    date_differences = (
        validation_df["date"]
        .diff()
        .dropna()
        .dt.days
    )

    consecutive = (
        len(date_differences) == 27
        and (date_differences == 1).all()
    )

    print(
        "Consecutive validation dates: "
        f"{'PASS' if consecutive else 'FAIL'}"
    )

    if not consecutive:
        raise ValueError(
            "Validation dates are not consecutive daily observations."
        )


# ---------------------------------------------------------------------
# BASELINE PREDICTIONS
# ---------------------------------------------------------------------

def create_baseline_predictions(
    validation_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Use lag_28 as the seasonal-naive forecast.
    """

    required_columns = [
        "date",
        "units_sold",
        "lag_28",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in validation_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    predictions = validation_df[
        required_columns
    ].copy()

    predictions = predictions.rename(
        columns={
            "units_sold": "actual_units",
            "lag_28": "predicted_units",
        }
    )

    # Ensure the baseline never produces negative demand.
    predictions["predicted_units"] = (
        predictions["predicted_units"]
        .clip(lower=0)
    )

    predictions["absolute_error"] = (
        predictions["actual_units"]
        - predictions["predicted_units"]
    ).abs()

    predictions["squared_error"] = (
        predictions["actual_units"]
        - predictions["predicted_units"]
    ) ** 2

    return predictions


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def calculate_metrics(
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate MAE and RMSE for the 28-day validation horizon.
    """

    actual = predictions[
        "actual_units"
    ]

    predicted = predictions[
        "predicted_units"
    ]

    mae = mean_absolute_error(
        actual,
        predicted,
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted,
        )
    )

    metrics = pd.DataFrame(
        [
            {
                "model": "Seasonal Naive (Lag 28)",
                "forecast_horizon_days": FORECAST_HORIZON,
                "validation_rows": len(predictions),
                "mae": mae,
                "rmse": rmse,
            }
        ]
    )

    return metrics


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 75)
    print("MARKETMINDAI - M5 BASELINE EVALUATION")
    print("=" * 75)

    # ---------------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------------

    df = load_dataset()

    print(
        f"\nTotal available rows: "
        f"{len(df):,}"
    )

    print(
        f"Full date range: "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()}"
    )

    # ---------------------------------------------------------------
    # SPLIT
    # ---------------------------------------------------------------

    train_df, validation_df = (
        create_validation_split(df)
    )

    print(
        f"\nTraining period: "
        f"{train_df['date'].min().date()} → "
        f"{train_df['date'].max().date()}"
    )

    print(
        f"Training rows: "
        f"{len(train_df):,}"
    )

    # ---------------------------------------------------------------
    # VALIDATE
    # ---------------------------------------------------------------

    validate_validation_period(
        validation_df
    )

    # ---------------------------------------------------------------
    # CREATE BASELINE
    # ---------------------------------------------------------------

    print("\nCreating seasonal-naive predictions...")
    print(
        "Baseline rule: "
        "prediction(t) = demand(t - 28 days)"
    )

    predictions = (
        create_baseline_predictions(
            validation_df
        )
    )

    # ---------------------------------------------------------------
    # METRICS
    # ---------------------------------------------------------------

    metrics = calculate_metrics(
        predictions
    )

    print("\n" + "=" * 75)
    print("BASELINE RESULTS")
    print("=" * 75)

    print(
        f"MAE:  "
        f"{metrics.loc[0, 'mae']:.4f}"
    )

    print(
        f"RMSE: "
        f"{metrics.loc[0, 'rmse']:.4f}"
    )

    # ---------------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    predictions.to_csv(
        PREDICTIONS_PATH,
        index=False,
    )

    metrics.to_csv(
        METRICS_PATH,
        index=False,
    )

    print(
        f"\nSaved baseline predictions:\n"
        f"{PREDICTIONS_PATH}"
    )

    print(
        f"\nSaved baseline metrics:\n"
        f"{METRICS_PATH}"
    )

    print(
        "\nM5 baseline evaluation completed successfully."
    )


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()