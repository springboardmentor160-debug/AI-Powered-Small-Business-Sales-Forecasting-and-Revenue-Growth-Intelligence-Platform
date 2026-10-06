from pathlib import Path

import pandas as pd
from prophet import Prophet


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


def prepare_prophet_data(
    daily_revenue: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert the daily revenue dataset into Prophet format.

    Prophet requires:
        ds -> datetime
        y  -> numeric target
    """

    required_columns = {
        "date",
        "revenue",
    }

    missing = required_columns - set(
        daily_revenue.columns
    )

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df = daily_revenue[
        ["date", "revenue"]
    ].copy()

    df["ds"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["y"] = pd.to_numeric(
        df["revenue"],
        errors="coerce",
    )

    df = df[
        ["ds", "y"]
    ].dropna()

    df = (
        df.sort_values("ds")
        .drop_duplicates("ds")
        .reset_index(drop=True)
    )

    if len(df) < 30:
        raise ValueError(
            "Insufficient historical observations "
            "for Prophet forecasting."
        )

    if (df["y"] < 0).any():
        raise ValueError(
            "Negative revenue values detected in "
            "the Prophet input."
        )

    return df


def train_prophet(
    prophet_df: pd.DataFrame,
) -> Prophet:
    """
    Train the baseline Prophet forecasting model.
    """

    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
    )

    model.fit(prophet_df)

    return model


def generate_forecast(
    model: Prophet,
    periods: int = 30,
) -> pd.DataFrame:
    """
    Generate a 30-day future forecast.
    """

    future = model.make_future_dataframe(
        periods=periods,
        freq="D",
        include_history=True,
    )

    forecast = model.predict(
        future
    )

    return forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper",
        ]
    ].copy()


def save_forecast(
    forecast: pd.DataFrame,
) -> Path:
    """
    Save the Prophet forecast artifact.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "prophet_forecast.csv"
    )

    forecast.to_csv(
        output_path,
        index=False,
    )

    return output_path