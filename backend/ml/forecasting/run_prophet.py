from pathlib import Path

import pandas as pd

from backend.ml.forecasting.prophet_model import (
    INPUT_PATH,
    generate_forecast,
    prepare_prophet_data,
    save_forecast,
    train_prophet,
)


def main() -> None:

    print("=" * 70)
    print("MARKETMINDAI - M2 DAY 6 PROPHET FORECAST")
    print("=" * 70)

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Daily revenue file not found: {INPUT_PATH}"
        )

    daily_revenue = pd.read_csv(
        INPUT_PATH
    )

    prophet_df = prepare_prophet_data(
        daily_revenue
    )

    print(
        f"\nProphet observations: "
        f"{len(prophet_df):,}"
    )

    print(
        f"Training start: "
        f"{prophet_df['ds'].min().date()}"
    )

    print(
        f"Training end: "
        f"{prophet_df['ds'].max().date()}"
    )

    print("\nTraining Prophet...")

    model = train_prophet(
        prophet_df
    )

    forecast = generate_forecast(
        model,
        periods=30,
    )

    output_path = save_forecast(
        forecast
    )

    future_forecast = forecast[
        forecast["ds"] > prophet_df["ds"].max()
    ].copy()

    print(
        f"\n30-day forecast rows: "
        f"{len(future_forecast):,}"
    )

    print("\nNext 10 forecast days:")

    display_forecast = future_forecast.head(10).copy()

    for column in [
        "yhat",
        "yhat_lower",
        "yhat_upper",
    ]:
        display_forecast[column] = display_forecast[column].round(2)

    print(
        display_forecast.to_string(
            index=False
        )
    )

    print(
        f"\nSaved Prophet forecast: "
        f"{output_path}"
    )

    print(
        "\nM2 Day 6 Prophet forecast completed."
    )


if __name__ == "__main__":
    main()