from pathlib import Path

import pandas as pd

from prophet import Prophet
from prophet.diagnostics import (
    cross_validation,
    performance_metrics,
)


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
    / "daily_revenue.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

CV_OUTPUT_PATH = (
    OUTPUT_DIR
    / "prophet_cv_predictions.csv"
)

METRICS_OUTPUT_PATH = (
    OUTPUT_DIR
    / "prophet_cv_metrics.csv"
)


# ---------------------------------------------------------------------
# FORECAST SETTINGS
# ---------------------------------------------------------------------

INITIAL_PERIOD = "450 days"
CV_PERIOD = "90 days"
FORECAST_HORIZON = "30 days"


# ---------------------------------------------------------------------
# LOAD UCI REVENUE DATA
# ---------------------------------------------------------------------

def load_daily_revenue() -> pd.DataFrame:
    """
    Load the prepared UCI daily revenue time series
    and convert it into Prophet's ds/y format.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Daily revenue dataset not found:\n{INPUT_PATH}"
        )

    print(f"\nLoading:\n{INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    required_columns = [
        "date",
        "revenue",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["revenue"] = pd.to_numeric(
        df["revenue"],
        errors="coerce",
    )

    df = (
        df.dropna(
            subset=["date", "revenue"]
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    # Prophet requires ds and y.
    prophet_df = df.rename(
        columns={
            "date": "ds",
            "revenue": "y",
        }
    )

    return prophet_df[
        ["ds", "y"]
    ]


# ---------------------------------------------------------------------
# VALIDATE INPUT
# ---------------------------------------------------------------------

def validate_input(
    prophet_df: pd.DataFrame,
) -> None:
    """
    Check that the time series is suitable for evaluation.
    """

    print("\n" + "=" * 75)
    print("UCI PROPHET INPUT VALIDATION")
    print("=" * 75)

    print(
        f"Rows: "
        f"{len(prophet_df):,}"
    )

    print(
        f"Date range: "
        f"{prophet_df['ds'].min().date()} → "
        f"{prophet_df['ds'].max().date()}"
    )

    print(
        f"Missing ds values: "
        f"{prophet_df['ds'].isna().sum():,}"
    )

    print(
        f"Missing y values: "
        f"{prophet_df['y'].isna().sum():,}"
    )

    duplicate_dates = (
        prophet_df["ds"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate dates: "
        f"{duplicate_dates:,}"
    )

    chronological = (
        prophet_df["ds"]
        .is_monotonic_increasing
    )

    print(
        "Chronological ordering: "
        f"{'PASS' if chronological else 'FAIL'}"
    )

    if duplicate_dates > 0:
        raise ValueError(
            "Duplicate dates found in the UCI revenue series."
        )

    if not chronological:
        raise ValueError(
            "UCI revenue series is not chronologically ordered."
        )


# ---------------------------------------------------------------------
# BUILD PROPHET MODEL
# ---------------------------------------------------------------------

def build_model() -> Prophet:
    """
    Create the baseline Prophet model.

    This intentionally uses the straightforward Prophet
    configuration used for the first forecasting baseline.
    """

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
    )

    return model


# ---------------------------------------------------------------------
# RUN CROSS-VALIDATION
# ---------------------------------------------------------------------

def run_cross_validation(
    prophet_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fit Prophet and perform historical cross-validation.
    """

    print("\n" + "=" * 75)
    print("PROPHET CROSS-VALIDATION")
    print("=" * 75)

    print(
        f"Initial training period: "
        f"{INITIAL_PERIOD}"
    )

    print(
        f"Cutoff spacing: "
        f"{CV_PERIOD}"
    )

    print(
        f"Forecast horizon: "
        f"{FORECAST_HORIZON}"
    )

    model = build_model()

    print("\nTraining Prophet on full historical series...")

    model.fit(
        prophet_df
    )

    print(
        "\nRunning historical cross-validation..."
    )

    df_cv = cross_validation(
        model,
        initial=INITIAL_PERIOD,
        period=CV_PERIOD,
        horizon=FORECAST_HORIZON,
        parallel=None,
    )

    return df_cv


# ---------------------------------------------------------------------
# CALCULATE METRICS
# ---------------------------------------------------------------------

def calculate_metrics(
    df_cv: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate aggregate Prophet MAE and RMSE.
    """

    # rolling_window=1 gives one overall metric
    # across all cross-validation predictions.
    df_performance = performance_metrics(
        df_cv,
        rolling_window=1,
        metrics=[
            "mae",
            "rmse",
        ],
    )

    overall_mae = float(
        df_performance["mae"].iloc[0]
    )

    overall_rmse = float(
        df_performance["rmse"].iloc[0]
    )

    cutoff_count = (
        df_cv["cutoff"]
        .nunique()
    )

    prediction_count = len(
        df_cv
    )

    metrics = pd.DataFrame(
        [
            {
                "model": "Prophet",
                "initial_training_days": 365,
                "cv_period_days": 90,
                "forecast_horizon_days": 30,
                "cutoff_count": cutoff_count,
                "validation_predictions": prediction_count,
                "mae": overall_mae,
                "rmse": overall_rmse,
            }
        ]
    )

    return metrics


# ---------------------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------------------

def display_results(
    df_cv: pd.DataFrame,
    metrics: pd.DataFrame,
) -> None:
    """
    Print useful evaluation information.
    """

    print("\n" + "=" * 75)
    print("PROPHET EVALUATION RESULTS")
    print("=" * 75)

    print(
        f"Cross-validation cutoffs: "
        f"{metrics.loc[0, 'cutoff_count']}"
    )

    print(
        f"Validation predictions: "
        f"{metrics.loc[0, 'validation_predictions']:,}"
    )

    print(
        f"MAE:  "
        f"{metrics.loc[0, 'mae']:.4f}"
    )

    print(
        f"RMSE: "
        f"{metrics.loc[0, 'rmse']:.4f}"
    )

    print("\nCross-validation sample:")

    print(
        df_cv[
            [
                "ds",
                "y",
                "yhat",
                "cutoff",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


# ---------------------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------------------

def save_results(
    df_cv: pd.DataFrame,
    metrics: pd.DataFrame,
) -> None:
    """
    Save cross-validation predictions and metrics.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df_cv.to_csv(
        CV_OUTPUT_PATH,
        index=False,
    )

    metrics.to_csv(
        METRICS_OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nSaved Prophet CV predictions:\n"
        f"{CV_OUTPUT_PATH}"
    )

    print(
        f"\nSaved Prophet CV metrics:\n"
        f"{METRICS_OUTPUT_PATH}"
    )


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 75)
    print("MARKETMINDAI - UCI PROPHET EVALUATION")
    print("=" * 75)

    # Load UCI daily revenue.
    prophet_df = load_daily_revenue()

    # Validate input.
    validate_input(
        prophet_df
    )

    # Run chronological cross-validation.
    df_cv = run_cross_validation(
        prophet_df
    )

    # Calculate MAE / RMSE.
    metrics = calculate_metrics(
        df_cv
    )

    # Display results.
    display_results(
        df_cv,
        metrics
    )

    # Save results.
    save_results(
        df_cv,
        metrics
    )

    print(
        "\nUCI Prophet evaluation completed successfully."
    )


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()