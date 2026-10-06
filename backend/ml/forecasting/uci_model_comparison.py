"""
MarketMindAI - UCI Forecasting Model Comparison
------------------------------------------------
Fair comparison of Prophet, Random Forest and XGBoost
on the EXACT SAME UCI revenue test period.

Input:
    artifacts/milestone-2/forecasting/uci_ml_features.csv

Output:
    artifacts/milestone-2/forecasting/uci_model_comparison.csv

Evaluation:
- Chronological 80/20 split
- Same training period for all models
- Same test period for all models
- MAE
- RMSE
"""

from pathlib import Path

import numpy as np
import pandas as pd
import predictions

from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)
from xgboost import XGBRegressor


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

COMPARISON_PATH = (
    OUTPUT_DIR
    / "uci_model_comparison.csv"
)

PREDICTIONS_PATH = (
    OUTPUT_DIR
    / "uci_model_comparison_predictions.csv"
)


# ---------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------

TEST_SIZE = 0.20

RANDOM_STATE = 42

RF_ESTIMATORS = 300

XGB_ESTIMATORS = 100

XGB_LEARNING_RATE = 0.10

XGB_MAX_DEPTH = 6


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


# ---------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------

def load_dataset() -> pd.DataFrame:
    """
    Load the calendar-complete UCI ML feature dataset.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"UCI ML feature dataset not found:\n{INPUT_PATH}"
        )

    print(f"\nLoading:\n{INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    required_columns = [
        "date",
        "revenue",
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

    df["revenue"] = pd.to_numeric(
        df["revenue"],
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
# CHRONOLOGICAL SPLIT
# ---------------------------------------------------------------------

def split_data(
    df: pd.DataFrame,
):
    """
    Create one common chronological 80/20 split.
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
# METRIC HELPER
# ---------------------------------------------------------------------

def calculate_metrics(
    model_name: str,
    actual: pd.Series,
    predicted: np.ndarray,
) -> dict:
    """
    Calculate MAE and RMSE for one model.
    """

    predicted = np.asarray(
        predicted,
        dtype=float,
    )

    predicted = np.clip(
        predicted,
        a_min=0,
        a_max=None,
    )

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

    return {
        "model": model_name,
        "mae": float(mae),
        "rmse": float(rmse),
    }


# ---------------------------------------------------------------------
# PROPHET
# ---------------------------------------------------------------------

def run_prophet(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
):
    """
    Train Prophet using the SAME training dates and predict
    the SAME test dates used by Random Forest and XGBoost.
    """

    prophet_train = train_df[
        [
            "date",
            "revenue",
        ]
    ].rename(
        columns={
            "date": "ds",
            "revenue": "y",
        }
    )

    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=False,
    )

    print("\nTraining Prophet...")

    model.fit(
        prophet_train
    )

    future = pd.DataFrame(
        {
            "ds": test_df["date"].values
        }
    )

    forecast = model.predict(
        future
    )

    predictions = (
        forecast["yhat"]
        .to_numpy()
    )

    # Revenue cannot be negative.
    predictions = np.clip(
        predictions,
        a_min=0,
        a_max=None,
    )

    return predictions


# ---------------------------------------------------------------------
# RANDOM FOREST
# ---------------------------------------------------------------------

def run_random_forest(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
):
    """
    Train Random Forest using the common training/test split.
    """

    model = RandomForestRegressor(
        n_estimators=RF_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    print("\nTraining Random Forest...")

    model.fit(
        train_df[FEATURE_COLUMNS],
        train_df["revenue"],
    )

    predictions = model.predict(
        test_df[FEATURE_COLUMNS]
    )

    return predictions


# ---------------------------------------------------------------------
# XGBOOST
# ---------------------------------------------------------------------

def run_xgboost(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
):
    """
    Train XGBoost using the common training/test split.
    """

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=XGB_ESTIMATORS,
        learning_rate=XGB_LEARNING_RATE,
        max_depth=XGB_MAX_DEPTH,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        tree_method="hist",
    )

    print("\nTraining XGBoost...")

    model.fit(
        train_df[FEATURE_COLUMNS],
        train_df["revenue"],
    )

    print(
        "XGBoost training completed."
    )

    # ---------------------------------------------------------------
    # PREDICT
    # ---------------------------------------------------------------

    predictions = model.predict(
        test_df[FEATURE_COLUMNS]
    )

    # Revenue cannot be negative.
    predictions = np.clip(
        predictions,
        a_min=0,
        a_max=None,
    )

    return predictions
# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 75)
    print(
        "MARKETMINDAI - FAIR UCI MODEL COMPARISON"
    )
    print("=" * 75)

    # ---------------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------------

    df = load_dataset()

    print(
        f"\nTotal rows: "
        f"{len(df):,}"
    )

    # ---------------------------------------------------------------
    # SPLIT
    # ---------------------------------------------------------------

    train_df, test_df = split_data(
        df
    )

    print("\n" + "=" * 75)
    print("COMMON CHRONOLOGICAL TEST PERIOD")
    print("=" * 75)

    print(
        f"Training rows: "
        f"{len(train_df):,}"
    )

    print(
        f"Training period: "
        f"{train_df['date'].min().date()} → "
        f"{train_df['date'].max().date()}"
    )

    print(
        f"Test rows: "
        f"{len(test_df):,}"
    )

    print(
        f"Test period: "
        f"{test_df['date'].min().date()} → "
        f"{test_df['date'].max().date()}"
    )

    # ---------------------------------------------------------------
    # ACTUAL TEST TARGET
    # ---------------------------------------------------------------

    actual = test_df[
        "revenue"
    ]

    # ---------------------------------------------------------------
    # PROPHET
    # ---------------------------------------------------------------

    prophet_predictions = run_prophet(
        train_df,
        test_df,
    )

    prophet_metrics = calculate_metrics(
        "Prophet",
        actual,
        prophet_predictions,
    )

    # ---------------------------------------------------------------
    # RANDOM FOREST
    # ---------------------------------------------------------------

    rf_predictions = run_random_forest(
        train_df,
        test_df,
    )

    rf_metrics = calculate_metrics(
        "Random Forest",
        actual,
        rf_predictions,
    )

    # ---------------------------------------------------------------
    # XGBOOST
    # ---------------------------------------------------------------

    xgb_predictions = run_xgboost(
        train_df,
        test_df,
    )

    xgb_metrics = calculate_metrics(
        "XGBoost",
        actual,
        xgb_predictions,
    )

    # ---------------------------------------------------------------
    # COMPARISON
    # ---------------------------------------------------------------

    comparison = pd.DataFrame(
        [
            prophet_metrics,
            rf_metrics,
            xgb_metrics,
        ]
    )

    # Add evaluation metadata.
    comparison["test_split"] = (
        "Chronological 80/20"
    )

    comparison["training_rows"] = (
        len(train_df)
    )

    comparison["test_rows"] = (
        len(test_df)
    )

    comparison["test_start"] = (
        test_df["date"].min().date()
    )

    comparison["test_end"] = (
        test_df["date"].max().date()
    )

    comparison = comparison[
        [
            "model",
            "test_split",
            "training_rows",
            "test_rows",
            "test_start",
            "test_end",
            "mae",
            "rmse",
        ]
    ]

    # ---------------------------------------------------------------
    # PREDICTIONS TABLE
    # ---------------------------------------------------------------

    prediction_output = pd.DataFrame(
        {
            "date": test_df["date"],
            "actual_revenue": actual.to_numpy(),
            "prophet_prediction": prophet_predictions,
            "random_forest_prediction": rf_predictions,
            "xgboost_prediction": xgb_predictions,
        }
    )

    # ---------------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------------

    print("\n" + "=" * 75)
    print("FAIR UCI MODEL COMPARISON")
    print("=" * 75)

    print(
        comparison.to_string(
            index=False,
            float_format=lambda value: f"{value:.4f}",
        )
    )

    print("\nPrediction sample:")

    print(
        prediction_output
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

    comparison.to_csv(
        COMPARISON_PATH,
        index=False,
    )

    prediction_output.to_csv(
        PREDICTIONS_PATH,
        index=False,
    )

    print(
        f"\nSaved model comparison:\n"
        f"{COMPARISON_PATH}"
    )

    print(
        f"\nSaved comparison predictions:\n"
        f"{PREDICTIONS_PATH}"
    )

    print(
        "\nFair UCI model comparison "
        "completed successfully."
    )


if __name__ == "__main__":
    main()