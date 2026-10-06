"""
MarketMindAI - UCI Random Forest Revenue Forecasting
----------------------------------------------------
Trains and evaluates a Random Forest Regressor on the
calendar-complete UCI daily revenue time series.

Input:
    artifacts/milestone-2/forecasting/uci_ml_features.csv

Outputs:
    artifacts/milestone-2/forecasting/uci_random_forest_predictions.csv
    artifacts/milestone-2/forecasting/uci_random_forest_metrics.csv
    artifacts/milestone-2/forecasting/uci_random_forest_feature_importance.csv

Evaluation:
- Chronological 80/20 split
- No random shuffling
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

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
    / "uci_ml_features.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

PREDICTIONS_PATH = (
    OUTPUT_DIR
    / "uci_random_forest_predictions.csv"
)

METRICS_PATH = (
    OUTPUT_DIR
    / "uci_random_forest_metrics.csv"
)

IMPORTANCE_PATH = (
    OUTPUT_DIR
    / "uci_random_forest_feature_importance.csv"
)


# ---------------------------------------------------------------------
# MODEL SETTINGS
# ---------------------------------------------------------------------

TEST_SIZE = 0.20

RANDOM_STATE = 42

N_ESTIMATORS = 300


# ---------------------------------------------------------------------
# FEATURES
# ---------------------------------------------------------------------

FEATURE_COLUMNS = [
    "day_of_week",
    "day_of_month",
    "month",
    "revenue_lag_1",
    "revenue_lag_7",
    "revenue_lag_14",
    "revenue_rolling_7",
]

TARGET_COLUMN = "revenue"


# ---------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------

def load_dataset() -> pd.DataFrame:
    """
    Load the UCI ML forecasting feature dataset.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"UCI ML feature dataset not found:\n{INPUT_PATH}"
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

    df[TARGET_COLUMN] = pd.to_numeric(
        df[TARGET_COLUMN],
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
# VALIDATE DATA
# ---------------------------------------------------------------------

def validate_dataset(
    df: pd.DataFrame,
) -> None:
    """
    Validate chronological order and required data quality.
    """

    print("\n" + "=" * 75)
    print("UCI RANDOM FOREST INPUT VALIDATION")
    print("=" * 75)

    print(
        f"Rows: "
        f"{len(df):,}"
    )

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
        df["date"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate dates: "
        f"{duplicate_dates:,}"
    )

    chronological = (
        df["date"]
        .is_monotonic_increasing
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
# CHRONOLOGICAL SPLIT
# ---------------------------------------------------------------------

def split_data(
    df: pd.DataFrame,
):
    """
    Split the time series into earlier training data
    and later test data without shuffling.
    """

    split_index = int(
        len(df) * (1 - TEST_SIZE)
    )

    train_df = (
        df.iloc[:split_index]
        .copy()
    )

    test_df = (
        df.iloc[split_index:]
        .copy()
    )

    return train_df, test_df


# ---------------------------------------------------------------------
# TRAIN RANDOM FOREST
# ---------------------------------------------------------------------

def train_model(
    train_df: pd.DataFrame,
) -> RandomForestRegressor:
    """
    Train the Random Forest regression model.
    """

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
    """
    Generate predictions for the chronological test period.
    """

    predictions = test_df[
        [
            "date",
            TARGET_COLUMN,
        ]
    ].copy()

    predictions = predictions.rename(
        columns={
            TARGET_COLUMN: "actual_revenue",
        }
    )

    predictions["predicted_revenue"] = (
        model.predict(
            test_df[FEATURE_COLUMNS]
        )
    )

    # Revenue cannot be negative.
    predictions["predicted_revenue"] = (
        predictions["predicted_revenue"]
        .clip(lower=0)
    )

    predictions["absolute_error"] = (
        predictions["actual_revenue"]
        - predictions["predicted_revenue"]
    ).abs()

    predictions["squared_error"] = (
        predictions["actual_revenue"]
        - predictions["predicted_revenue"]
    ) ** 2

    return predictions


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def calculate_metrics(
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate MAE and RMSE.
    """

    actual = predictions[
        "actual_revenue"
    ]

    predicted = predictions[
        "predicted_revenue"
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
                "model": "Random Forest",
                "test_split": "Chronological 80/20",
                "training_rows": None,
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
    """
    Extract Random Forest feature importance.
    """

    importance = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "importance": model.feature_importances_,
        }
    )

    importance = (
        importance
        .sort_values(
            "importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return importance


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 75)
    print(
        "MARKETMINDAI - UCI RANDOM FOREST FORECASTING"
    )
    print("=" * 75)

    # ---------------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------------

    df = load_dataset()

    # ---------------------------------------------------------------
    # VALIDATE
    # ---------------------------------------------------------------

    validate_dataset(df)

    # ---------------------------------------------------------------
    # SPLIT
    # ---------------------------------------------------------------

    train_df, test_df = split_data(
        df
    )

    print("\n" + "=" * 75)
    print("CHRONOLOGICAL TRAIN / TEST SPLIT")
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
        f"Test period: "
        f"{test_df['date'].min().date()} → "
        f"{test_df['date'].max().date()}"
    )

    print(
        f"Test rows: "
        f"{len(test_df):,}"
    )

    # ---------------------------------------------------------------
    # TRAIN
    # ---------------------------------------------------------------

    print("\n" + "=" * 75)
    print("RANDOM FOREST TRAINING")
    print("=" * 75)

    print(
        f"Number of trees: "
        f"{N_ESTIMATORS}"
    )

    print(
        f"Random state: "
        f"{RANDOM_STATE}"
    )

    print("\nTraining model...")

    model = train_model(
        train_df
    )

    print(
        "Random Forest training completed."
    )

    # ---------------------------------------------------------------
    # PREDICT
    # ---------------------------------------------------------------

    print("\nGenerating test predictions...")

    predictions = generate_predictions(
        model,
        test_df,
    )

    # ---------------------------------------------------------------
    # METRICS
    # ---------------------------------------------------------------

    metrics = calculate_metrics(
        predictions
    )

    metrics.loc[
        0,
        "training_rows"
    ] = len(train_df)

    # ---------------------------------------------------------------
    # FEATURE IMPORTANCE
    # ---------------------------------------------------------------

    importance = calculate_feature_importance(
        model
    )

    # ---------------------------------------------------------------
    # DISPLAY RESULTS
    # ---------------------------------------------------------------

    print("\n" + "=" * 75)
    print("RANDOM FOREST RESULTS")
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
        "\nUCI Random Forest forecasting "
        "completed successfully."
    )


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()