"""
MarketMindAI - M5 Model Comparison
----------------------------------
Compares the three M5 development approaches:

1. Seasonal Naive (Lag 28)
2. Random Forest
3. XGBoost

All models are evaluated on the same 28-day validation period
for the selected M5 item/store development series.

Inputs:
    m5_baseline_metrics.csv
    m5_random_forest_metrics.csv
    m5_xgboost_metrics.csv

Outputs:
    m5_model_comparison.csv
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FORECASTING_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

BASELINE_METRICS_PATH = (
    FORECASTING_DIR
    / "m5_baseline_metrics.csv"
)

RF_METRICS_PATH = (
    FORECASTING_DIR
    / "m5_random_forest_metrics.csv"
)

XGB_METRICS_PATH = (
    FORECASTING_DIR
    / "m5_xgboost_metrics.csv"
)

BASELINE_PREDICTIONS_PATH = (
    FORECASTING_DIR
    / "m5_baseline_predictions.csv"
)

RF_PREDICTIONS_PATH = (
    FORECASTING_DIR
    / "m5_random_forest_predictions.csv"
)

XGB_PREDICTIONS_PATH = (
    FORECASTING_DIR
    / "m5_xgboost_predictions.csv"
)

OUTPUT_PATH = (
    FORECASTING_DIR
    / "m5_model_comparison.csv"
)


# ---------------------------------------------------------------------
# LOAD METRICS
# ---------------------------------------------------------------------

def load_metric_file(
    path: Path,
    expected_name: str,
) -> pd.DataFrame:
    """
    Load one model's metric file.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Required metric file not found:\n{path}"
        )

    df = pd.read_csv(path)

    required_columns = [
        "mae",
        "rmse",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{path.name} is missing columns: "
            + ", ".join(missing_columns)
        )

    result = df.iloc[0].copy()

    return pd.DataFrame(
        [
            {
                "model": expected_name,
                "mae": float(result["mae"]),
                "rmse": float(result["rmse"]),
            }
        ]
    )


# ---------------------------------------------------------------------
# GET VALIDATION PERIOD
# ---------------------------------------------------------------------

def get_validation_period() -> tuple[str, str]:
    """
    Verify that all three prediction files use the same
    validation dates.
    """

    prediction_paths = [
        BASELINE_PREDICTIONS_PATH,
        RF_PREDICTIONS_PATH,
        XGB_PREDICTIONS_PATH,
    ]

    prediction_frames = []

    for path in prediction_paths:

        if not path.exists():
            raise FileNotFoundError(
                f"Required prediction file not found:\n{path}"
            )

        prediction_frames.append(
            pd.read_csv(path)
        )

    date_ranges = []

    for df in prediction_frames:

        if "date" not in df.columns:
            raise ValueError(
                "Prediction file does not contain a date column."
            )

        dates = pd.to_datetime(
            df["date"],
            errors="coerce",
        )

        if dates.isna().any():
            raise ValueError(
                "Invalid date found in prediction file."
            )

        date_ranges.append(
            (
                dates.min().date(),
                dates.max().date(),
                len(dates),
            )
        )

    first_range = date_ranges[0]

    for current_range in date_ranges[1:]:

        if current_range != first_range:
            raise ValueError(
                "The three models are NOT using "
                "the same validation period."
            )

    return (
        str(first_range[0]),
        str(first_range[1]),
    )


# ---------------------------------------------------------------------
# VALIDATE METRICS
# ---------------------------------------------------------------------

def validate_comparison(
    comparison: pd.DataFrame,
) -> None:
    """
    Validate the comparison table.
    """

    print("\n" + "=" * 75)
    print("M5 MODEL COMPARISON VALIDATION")
    print("=" * 75)

    print(
        f"Models found: "
        f"{len(comparison):,}"
    )

    expected_models = {
        "Seasonal Naive",
        "Random Forest",
        "XGBoost",
    }

    actual_models = set(
        comparison["model"]
    )

    if actual_models != expected_models:
        raise ValueError(
            "Unexpected model set.\n"
            f"Expected: {expected_models}\n"
            f"Found: {actual_models}"
        )

    print("Model coverage: PASS")

    if comparison["mae"].isna().any():
        raise ValueError(
            "Missing MAE values found."
        )

    if comparison["rmse"].isna().any():
        raise ValueError(
            "Missing RMSE values found."
        )

    print("MAE values: PASS")
    print("RMSE values: PASS")


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 75)
    print(
        "MARKETMINDAI - M5 MODEL COMPARISON"
    )
    print("=" * 75)

    # ---------------------------------------------------------------
    # VALIDATION PERIOD
    # ---------------------------------------------------------------

    validation_start, validation_end = (
        get_validation_period()
    )

    print("\n" + "=" * 75)
    print("COMMON M5 VALIDATION PERIOD")
    print("=" * 75)

    print(
        f"Validation start: "
        f"{validation_start}"
    )

    print(
        f"Validation end: "
        f"{validation_end}"
    )

    print(
        "Validation horizon: 28 days"
    )

    # ---------------------------------------------------------------
    # LOAD METRICS
    # ---------------------------------------------------------------

    baseline = load_metric_file(
        BASELINE_METRICS_PATH,
        "Seasonal Naive",
    )

    random_forest = load_metric_file(
        RF_METRICS_PATH,
        "Random Forest",
    )

    xgboost = load_metric_file(
        XGB_METRICS_PATH,
        "XGBoost",
    )

    comparison = pd.concat(
        [
            baseline,
            random_forest,
            xgboost,
        ],
        ignore_index=True,
    )

    # ---------------------------------------------------------------
    # BASELINE REFERENCE
    # ---------------------------------------------------------------

    baseline_mae = float(
        comparison.loc[
            comparison["model"] == "Seasonal Naive",
            "mae",
        ].iloc[0]
    )

    baseline_rmse = float(
        comparison.loc[
            comparison["model"] == "Seasonal Naive",
            "rmse",
        ].iloc[0]
    )

    # Improvement relative to baseline.
    comparison["mae_change_vs_baseline_pct"] = (
        (
            baseline_mae
            - comparison["mae"]
        )
        / baseline_mae
        * 100
    )

    comparison["rmse_change_vs_baseline_pct"] = (
        (
            baseline_rmse
            - comparison["rmse"]
        )
        / baseline_rmse
        * 100
    )

    comparison[
        "validation_start"
    ] = validation_start

    comparison[
        "validation_end"
    ] = validation_end

    comparison[
        "validation_horizon_days"
    ] = 28

    # ---------------------------------------------------------------
    # COLUMN ORDER
    # ---------------------------------------------------------------

    comparison = comparison[
        [
            "model",
            "validation_start",
            "validation_end",
            "validation_horizon_days",
            "mae",
            "rmse",
            "mae_change_vs_baseline_pct",
            "rmse_change_vs_baseline_pct",
        ]
    ]

    # ---------------------------------------------------------------
    # VALIDATE
    # ---------------------------------------------------------------

    validate_comparison(
        comparison
    )

    # ---------------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------------

    print("\n" + "=" * 75)
    print("M5 FORECASTING MODEL COMPARISON")
    print("=" * 75)

    print(
        comparison.to_string(
            index=False,
            float_format=lambda value: f"{value:.4f}",
        )
    )

    # ---------------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------------

    FORECASTING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparison.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nSaved comparison:\n"
        f"{OUTPUT_PATH}"
    )

    print(
        "\nM5 model comparison "
        "completed successfully."
    )


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()