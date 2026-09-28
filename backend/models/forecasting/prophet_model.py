"""Reusable Prophet forecasting wrapper for MarketMind time series."""

from dataclasses import dataclass

import pandas as pd
from prophet import Prophet


@dataclass
class ProphetForecaster:
    """Configure and run a deterministic point forecast with Prophet."""

    yearly_seasonality: bool = True
    weekly_seasonality: bool = True
    daily_seasonality: bool = False
    seasonality_mode: str = "additive"
    changepoint_prior_scale: float = 0.05

    def forecast(self, series: pd.DataFrame, periods: int) -> pd.DataFrame:
        """Fit Prophet on a ds/y frame and return future dates with point forecasts."""
        if periods < 1:
            raise ValueError("Forecast periods must be at least one day.")
        if list(series.columns) != ["ds", "y"]:
            raise ValueError("Prophet input must contain columns in the order: ds, y.")
        if len(series) < 2:
            raise ValueError("At least two time-series observations are required.")

        model = Prophet(
            yearly_seasonality=self.yearly_seasonality,
            weekly_seasonality=self.weekly_seasonality,
            daily_seasonality=self.daily_seasonality,
            seasonality_mode=self.seasonality_mode,
            changepoint_prior_scale=self.changepoint_prior_scale,
            uncertainty_samples=0,
        )
        training_data = series.copy().sort_values("ds")
        model.fit(training_data)
        future_dates = model.make_future_dataframe(
            periods=periods,
            freq="D",
            include_history=False,
        )
        forecast = model.predict(future_dates)
        return forecast[["ds", "yhat"]].rename(columns={"yhat": "forecast"})
