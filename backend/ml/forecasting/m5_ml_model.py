"""
MarketMindAI - M5 Random Forest Demand Forecasting
--------------------------------------------------
Trains Random Forest on the prepared M5 demand features.

Input:
    backend/artifacts/milestone-2/forecasting/m5_features_sample.csv

Outputs:
    backend/artifacts/milestone-2/forecasting/m5_random_forest_predictions.csv
    backend/artifacts/milestone-2/forecasting/m5_random_forest_metrics.csv
    backend/artifacts/milestone-2/forecasting/m5_random_forest_feature_importance.csv

Evaluation:
- Final 28 days held out
- Chronological split
- No shuffling
- MAE
- RMSE
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
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
    / "m5_random_forest_predictions.csv"
)

METRICS_PATH = (
    OUTPUT_DIR
    / "m5_random_forest_metrics.csv"
)

IMPORTANCE_PATH = (
    OUTPUT_DIR
    / "m5_random_forest_feature_importance.csv"
)


# ---------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------

FORECAST_HORIZON = 28
RANDOM_STATE = 42
N_ESTIMATORS = 300


# ---------------------------------------------------------------------
# FEATURES
# ---------------------------------------------------------------------

FEATURE_COLUMNS = [
    "sell_price",
    "day_of_month",
    "day_of_week",
    "week_of_year",
    "is_weekend",
    "is_event",
    "snap_active",
    "price_change",
    "lag_28",
    "lag_56",
    "lag_84",
    "rolling_mean_7_28",
    "rolling_mean_28_28",
]

TARGET_COLUMN = "units_sold"


# ---------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------

def load_dataset() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"M5 feature dataset not found:\n{INPUT_PATH}"
        )

    print(f"\nLoading:\n{INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    required_columns = [
        "date",
        TARGET_COLUMN,
        *FEATURE_COLUMNS,
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

    df = (
        df.dropna(
            subset=required_columns
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    return df


# ---------------------------------------------------------------------
# VALIDATE
# ---------------------------------------------------------------------

def validate_dataset(df: pd.DataFrame) -> None:

    print("\n" + "=" * 75)
    print("M5 RANDOM FOREST INPUT VALIDATION")
    print("=" * 75)

    print(f"Rows: {len(df):,}")

    print(
        f"Date range: "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()}"
    )

    print(
        f"Missing values: "
        f"{df.isna().sum().sum():,}"
    )

    duplicate_dates = (
        df["date"].duplicated().sum()
    )

    print(
        f"Duplicate dates: "
        f"{duplicate_dates:,}"
    )

    chronological = (
        df["date"].is_monotonic_increasing
    )

    print(
        "Chronological ordering: "
        f"{'PASS' if chronological else 'FAIL'}"
    )

    if duplicate_dates != 0:
        raise ValueError(
            "Duplicate dates found."
        )

    if not chronological:
        raise ValueError(
            "Dataset is not chronologically ordered."
        )


# ---------------------------------------------------------------------
# SPLIT
# ---------------------------------------------------------------------

def split_data(df: pd.DataFrame):

    if len(df) <= FORECAST_HORIZON:
        raise ValueError(
            "Not enough rows for a 28-day validation period."
        )

    train_df = (
        df.iloc[:-FORECAST_HORIZON]
        .copy()
    )

    test_df = (
        df.iloc[-FORECAST_HORIZON:]
        .copy()
    )

    return train_df, test_df


# ---------------------------------------------------------------------
# TRAIN
# ---------------------------------------------------------------------

def train_model(
    train_df: pd.DataFrame,
) -> RandomForestRegressor:

    model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(
        train_df[FEATURE_COLUMNS],
        train_df[TARGET_COLUMN],
    )

    return model


# ---------------------------------------------------------------------
# PREDICT
# ---------------------------------------------------------------------

def generate_predictions(
    model: RandomForestRegressor,
    test_df: pd.DataFrame,
) -> pd.DataFrame:

    predictions = test_df[
        [
            "date",
            TARGET_COLUMN,
        ]
    ].copy()

    predictions = predictions.rename(
        columns={
            TARGET_COLUMN: "actual_units",
        }
    )

    predicted = model.predict(
        test_df[FEATURE_COLUMNS]
    )

    # Demand cannot be negative.
    predicted = np.clip(
        predicted,
        a_min=0,
        a_max=None,
    )

    predictions["predicted_units"] = predicted

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
    training_rows: int,
) -> pd.DataFrame:

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
                "model": "M5 Random Forest",
                "forecast_horizon_days": FORECAST_HORIZON,
                "training_rows": training_rows,
                "test_rows": len(predictions),
                "n_estimators": N_ESTIMATORS,
                "random_state": RANDOM_STATE,
                "mae": mae,
                "rmse": rmse,
            }
        ]
    )

    return metrics


# ---------------------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------------------

def calculate_feature_importance(
    model: RandomForestRegressor,
) -> pd.DataFrame:

    importance = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "importance": model.feature_importances_,
        }
    )

    return (
        importance
        .sort_values(
            "importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 75)
    print(
        "MARKETMINDAI - M5 RANDOM FOREST FORECASTING"
    )
    print("=" * 75)

    # Load.
    df = load_dataset()

    # Validate.
    validate_dataset(df)

    # Split.
    train_df, test_df = split_data(df)

    print("\n" + "=" * 75)
    print("M5 28-DAY TRAIN / VALIDATION SPLIT")
    print("=" * 75)

    print(
        f"Training period: "
        f"{train_df['date'].min().date()} → "
        f"{train_df['date'].max().date()}"
    )

    print(
        f"Training rows: "
        f"{len(train_df):,}"
    )

    print(
        f"Validation period: "
        f"{test_df['date'].min().date()} → "
        f"{test_df['date'].max().date()}"
    )

    print(
        f"Validation rows: "
        f"{len(test_df):,}"
    )

    # Train.
    print("\nTraining Random Forest...")

    model = train_model(
        train_df
    )

    print(
        "Random Forest training completed."
    )

    # Predict.
    print(
        "\nGenerating 28-day validation predictions..."
    )

    predictions = generate_predictions(
        model,
        test_df,
    )

    # Metrics.
    metrics = calculate_metrics(
        predictions,
        training_rows=len(train_df),
    )

    # Importance.
    importance = calculate_feature_importance(
        model
    )

    # Display.
    print("\n" + "=" * 75)
    print("M5 RANDOM FOREST RESULTS")
    print("=" * 75)

    print(
        f"MAE:  "
        f"{metrics.loc[0, 'mae']:.4f}"
    )

    print(
        f"RMSE: "
        f"{metrics.loc[0, 'rmse']:.4f}"
    )

    print("\nFeature importance:")

    print(
        importance.to_string(
            index=False
        )
    )

    print("\nPrediction sample:")

    print(
        predictions
        .head(10)
        .to_string(index=False)
    )

    # Save.
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

    importance.to_csv(
        IMPORTANCE_PATH,
        index=False,
    )

    print(
        f"\nSaved predictions:\n"
        f"{PREDICTIONS_PATH}"
    )

    print(
        f"\nSaved metrics:\n"
        f"{METRICS_PATH}"
    )

    print(
        f"\nSaved feature importance:\n"
        f"{IMPORTANCE_PATH}"
    )

    print(
        "\nM5 Random Forest forecasting "
        "completed successfully."
    )


if __name__ == "__main__":
    main()