"""
MarketMindAI - M5 Forecasting Feature Engineering
-------------------------------------------------
Creates leakage-safe features for a 28-day forecasting horizon.

Input:
    backend/artifacts/milestone-2/forecasting/m5_demand_sample.csv

Output:
    backend/artifacts/milestone-2/forecasting/m5_features_sample.csv

Design:
- Raw M5 files remain untouched.
- Validation horizon = final 28 observations.
- Demand-history features are shifted by 28 days or more.
- Calendar and price information are retained because they are
  known/external explanatory variables for the forecast period.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
    / "m5_demand_sample.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

OUTPUT_PATH = OUTPUT_DIR / "m5_features_sample.csv"


# ---------------------------------------------------------------------
# FORECAST SETTINGS
# ---------------------------------------------------------------------

FORECAST_HORIZON = 28

LAG_28 = 28
LAG_56 = 56
LAG_84 = 84


# ---------------------------------------------------------------------
# CREATE FEATURES
# ---------------------------------------------------------------------

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create forecasting features that are safe for a 28-day
    out-of-sample forecasting horizon.
    """

    df = df.copy()

    # ---------------------------------------------------------------
    # DATE
    # ---------------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df = (
        df.sort_values("date")
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------------
    # CALENDAR FEATURES
    # ---------------------------------------------------------------

    df["day_of_month"] = df["date"].dt.day
    df["day_of_week"] = df["date"].dt.dayofweek

    df["week_of_year"] = (
        df["date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    # ---------------------------------------------------------------
    # EVENT FEATURE
    # ---------------------------------------------------------------

    df["is_event"] = (
        df["event_name_1"].notna()
        | df["event_name_2"].notna()
    ).astype(int)

    # ---------------------------------------------------------------
    # SNAP FEATURE
    # ---------------------------------------------------------------

    # Development series is CA_3.
    df["snap_active"] = df["snap_CA"].astype(int)

    # ---------------------------------------------------------------
    # PRICE FEATURES
    # ---------------------------------------------------------------

    # Price is available as an external feature.
    df["price_change"] = (
        df["sell_price"]
        .pct_change()
        .fillna(0)
    )

    # ---------------------------------------------------------------
    # LEAKAGE-SAFE SALES LAGS
    # ---------------------------------------------------------------

    # For a 28-day forecast horizon, do NOT use lag-1/lag-7/lag-14
    # as direct validation features because those observations may
    # belong to the future validation window.
    #
    # Instead, use demand observations from at least 28 days earlier.

    df["lag_28"] = (
        df["units_sold"]
        .shift(LAG_28)
    )

    df["lag_56"] = (
        df["units_sold"]
        .shift(LAG_56)
    )

    df["lag_84"] = (
        df["units_sold"]
        .shift(LAG_84)
    )

    # ---------------------------------------------------------------
    # LEAKAGE-SAFE ROLLING FEATURES
    # ---------------------------------------------------------------

    # Shift by 28 first, then calculate the rolling statistic.
    #
    # Example:
    # For a validation date D, rolling_mean_7_28 uses
    # historical observations ending at D-28.
    historical_demand = (
        df["units_sold"]
        .shift(FORECAST_HORIZON)
    )

    df["rolling_mean_7_28"] = (
        historical_demand
        .rolling(window=7)
        .mean()
    )

    df["rolling_mean_28_28"] = (
        historical_demand
        .rolling(window=28)
        .mean()
    )

    return df


# ---------------------------------------------------------------------
# VALIDATION BEFORE CLEANUP
# ---------------------------------------------------------------------

def validate_features(df: pd.DataFrame) -> None:
    """
    Validate feature creation before dropping rows
    that lack sufficient history.
    """

    print("\n" + "=" * 75)
    print("M5 FORECASTING FEATURE VALIDATION")
    print("=" * 75)

    print(f"Rows before feature cleanup: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print(
        f"Date range: "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()}"
    )

    feature_columns = [
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

    print("\nFeature columns:")

    for column in feature_columns:
        exists = column in df.columns
        print(
            f"  {column}: "
            f"{'PASS' if exists else 'FAIL'}"
        )

    print("\nMissing values before cleanup:")

    missing = df[feature_columns].isna().sum()

    for column, count in missing.items():
        print(
            f"  {column}: {count:,}"
        )

    chronological = (
        df["date"]
        .is_monotonic_increasing
    )

    print(
        "\nChronological ordering: "
        f"{'PASS' if chronological else 'FAIL'}"
    )


# ---------------------------------------------------------------------
# FINAL VALIDATION
# ---------------------------------------------------------------------

def validate_final_dataset(
    df: pd.DataFrame
) -> None:
    """
    Validate the model-ready feature dataset.
    """

    print("\n" + "=" * 75)
    print("FINAL M5 FEATURE DATASET")
    print("=" * 75)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print(
        f"Date range: "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()}"
    )

    remaining_missing = (
        df.isna()
        .sum()
        .sum()
    )

    print(
        f"Remaining missing values: "
        f"{remaining_missing:,}"
    )

    duplicate_count = (
        df.duplicated(
            subset=[
                "item_id",
                "store_id",
                "date"
            ]
        )
        .sum()
    )

    print(
        f"Duplicate item/store/date rows: "
        f"{duplicate_count:,}"
    )


# ---------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------

def main():

    print("=" * 75)
    print("MARKETMINDAI - M5 28-DAY SAFE FEATURE ENGINEERING")
    print("=" * 75)

    # ---------------------------------------------------------------
    # LOAD INPUT
    # ---------------------------------------------------------------

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"M5 demand sample not found:\n{INPUT_PATH}"
        )

    print(
        f"\nLoading:\n{INPUT_PATH}"
    )

    df = pd.read_csv(
        INPUT_PATH
    )

    # ---------------------------------------------------------------
    # CREATE FEATURES
    # ---------------------------------------------------------------

    df = create_features(
        df
    )

    # ---------------------------------------------------------------
    # CHECK FEATURES
    # ---------------------------------------------------------------

    validate_features(
        df
    )

    # ---------------------------------------------------------------
    # REMOVE ROWS WITHOUT SUFFICIENT HISTORY
    # ---------------------------------------------------------------

    required_history_features = [
        "lag_28",
        "lag_56",
        "lag_84",
        "rolling_mean_7_28",
        "rolling_mean_28_28",
    ]

    before = len(df)

    df = (
        df.dropna(
            subset=required_history_features
        )
        .reset_index(drop=True)
    )

    removed = before - len(df)

    print(
        f"\nRows removed because sufficient "
        f"28-day historical information was unavailable: "
        f"{removed:,}"
    )

    # ---------------------------------------------------------------
    # MODEL-READY COLUMNS
    # ---------------------------------------------------------------

    model_columns = [
        "date",
        "d",
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
        "units_sold",
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

    df = df[
        model_columns
    ]

    # ---------------------------------------------------------------
    # FINAL VALIDATION
    # ---------------------------------------------------------------

    validate_final_dataset(
        df
    )

    # ---------------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"\nSaved M5 feature dataset:\n"
        f"{OUTPUT_PATH}"
    )

    print(
        "\nM5 28-day leakage-safe "
        "feature engineering completed successfully."
    )


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()