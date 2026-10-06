"""
MarketMindAI - UCI Machine Learning Forecasting Features
---------------------------------------------------------
Creates calendar-consistent time-series features for
Random Forest and XGBoost forecasting.

Important:
- Raw UCI source files are never modified.
- Missing calendar dates are represented as zero revenue
  because the daily revenue series is derived from completed
  transactions and no completed sale rows exist for those dates.
- Lag features therefore represent true calendar-day lags.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# PROJECT PATHS
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

OUTPUT_PATH = (
    OUTPUT_DIR
    / "uci_ml_features.csv"
)


# ---------------------------------------------------------------------
# FEATURE DEFINITIONS
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
# LOAD DAILY REVENUE
# ---------------------------------------------------------------------

def load_daily_revenue() -> pd.DataFrame:
    """
    Load the reconciled UCI daily revenue dataset.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Daily revenue file not found:\n{INPUT_PATH}"
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

    return df


# ---------------------------------------------------------------------
# COMPLETE CALENDAR
# ---------------------------------------------------------------------

def create_complete_calendar(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Expand the daily revenue series to every calendar day.

    Dates with no recorded completed sales receive revenue = 0.
    """

    start_date = df["date"].min()
    end_date = df["date"].max()

    full_dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    complete_df = (
        df.set_index("date")
        .reindex(full_dates)
        .rename_axis("date")
        .reset_index()
    )

    missing_days = (
        complete_df["revenue"]
        .isna()
        .sum()
    )

    complete_df["revenue"] = (
        complete_df["revenue"]
        .fillna(0.0)
    )

    print("\n" + "=" * 75)
    print("UCI COMPLETE CALENDAR")
    print("=" * 75)

    print(
        f"Original recorded-sales days: "
        f"{len(df):,}"
    )

    print(
        f"Complete calendar days: "
        f"{len(complete_df):,}"
    )

    print(
        f"Calendar dates represented as zero revenue: "
        f"{missing_days:,}"
    )

    print(
        f"Calendar range: "
        f"{start_date.date()} → {end_date.date()}"
    )

    return complete_df


# ---------------------------------------------------------------------
# CREATE FEATURES
# ---------------------------------------------------------------------

def create_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create calendar, lag and rolling features.
    """

    df = df.copy()

    df = (
        df.sort_values("date")
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------------
    # CALENDAR FEATURES
    # ---------------------------------------------------------------

    df["day_of_week"] = (
        df["date"].dt.dayofweek
    )

    df["day_of_month"] = (
        df["date"].dt.day
    )

    df["month"] = (
        df["date"].dt.month
    )

    # ---------------------------------------------------------------
    # LAG FEATURES
    # ---------------------------------------------------------------

    df["revenue_lag_1"] = (
        df["revenue"].shift(1)
    )

    df["revenue_lag_7"] = (
        df["revenue"].shift(7)
    )

    df["revenue_lag_14"] = (
        df["revenue"].shift(14)
    )

    # ---------------------------------------------------------------
    # ROLLING FEATURE
    # ---------------------------------------------------------------

    df["revenue_rolling_7"] = (
        df["revenue"]
        .shift(1)
        .rolling(window=7)
        .mean()
    )

    return df


# ---------------------------------------------------------------------
# VALIDATE FEATURES
# ---------------------------------------------------------------------

def validate_features(
    df: pd.DataFrame,
) -> None:
    """
    Validate generated forecasting features.
    """

    print("\n" + "=" * 75)
    print("UCI ML FEATURE VALIDATION")
    print("=" * 75)

    print(
        f"Rows before cleanup: "
        f"{len(df):,}"
    )

    print(
        f"Columns: "
        f"{len(df.columns)}"
    )

    print(
        f"Date range: "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()}"
    )

    print("\nFeature columns:")

    for column in FEATURE_COLUMNS:
        print(
            f"  {column}: "
            f"{'PASS' if column in df.columns else 'FAIL'}"
        )

    print("\nMissing values:")

    missing = df[FEATURE_COLUMNS].isna().sum()

    for column, count in missing.items():
        print(
            f"  {column}: "
            f"{count:,}"
        )

    chronological = (
        df["date"].is_monotonic_increasing
    )

    print(
        "\nChronological ordering: "
        f"{'PASS' if chronological else 'FAIL'}"
    )

    # Confirm every calendar date exists.
    expected_dates = pd.date_range(
        start=df["date"].min(),
        end=df["date"].max(),
        freq="D",
    )

    complete_calendar = (
        len(df) == len(expected_dates)
        and df["date"].equals(
            pd.Series(expected_dates, name="date")
        )
    )

    print(
        "Complete daily calendar: "
        f"{'PASS' if complete_calendar else 'FAIL'}"
    )

    if not complete_calendar:
        raise ValueError(
            "Daily calendar contains unexpected gaps."
        )


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 75)
    print(
        "MARKETMINDAI - UCI ML FEATURE ENGINEERING"
    )
    print("=" * 75)

    # ---------------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------------

    df = load_daily_revenue()

    # ---------------------------------------------------------------
    # COMPLETE CALENDAR
    # ---------------------------------------------------------------

    df = create_complete_calendar(df)

    # ---------------------------------------------------------------
    # CREATE FEATURES
    # ---------------------------------------------------------------

    df = create_features(df)

    # ---------------------------------------------------------------
    # VALIDATE
    # ---------------------------------------------------------------

    validate_features(df)

    # ---------------------------------------------------------------
    # REMOVE ROWS WITHOUT ENOUGH HISTORY
    # ---------------------------------------------------------------

    before = len(df)

    df = (
        df.dropna(
            subset=FEATURE_COLUMNS
        )
        .reset_index(drop=True)
    )

    removed = before - len(df)

    print(
        f"\nRows removed due to unavailable "
        f"historical features: "
        f"{removed:,}"
    )

    # ---------------------------------------------------------------
    # MODEL-READY COLUMNS
    # ---------------------------------------------------------------

    model_columns = [
        "date",
        "revenue",
        "day_of_week",
        "day_of_month",
        "month",
        "revenue_lag_1",
        "revenue_lag_7",
        "revenue_lag_14",
        "revenue_rolling_7",
    ]

    df = df[model_columns]

    # ---------------------------------------------------------------
    # FINAL VALIDATION
    # ---------------------------------------------------------------

    print("\n" + "=" * 75)
    print("FINAL UCI ML FEATURE DATASET")
    print("=" * 75)

    print(
        f"Rows: "
        f"{len(df):,}"
    )

    print(
        f"Columns: "
        f"{len(df.columns)}"
    )

    print(
        f"Date range: "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()}"
    )

    print(
        f"Remaining missing values: "
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

    if duplicate_dates != 0:
        raise ValueError(
            "Duplicate dates found."
        )

    # ---------------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nSaved UCI ML feature dataset:\n"
        f"{OUTPUT_PATH}"
    )

    print(
        "\nUCI ML feature engineering "
        "completed successfully."
    )


if __name__ == "__main__":
    main()