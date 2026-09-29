"""
Prophet Forecasting Model for Sales and Revenue (Milestone 2)
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Dict, Any, Tuple

class ProphetForecaster:
    def __init__(self, yearly_seasonality: bool = True, weekly_seasonality: bool = False, daily_seasonality: bool = False):
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.model = None

    def fit_predict(self, df_train: pd.DataFrame, horizon_months: int = 12) -> pd.DataFrame:
        """
        df_train must contain 'ds' (datetime) and 'y' (float sales/revenue).
        Returns dataframe with ds, yhat, yhat_lower, yhat_upper.
        """
        df_prophet = df_train[['ds', 'y']].copy()
        df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

        self.model = Prophet(
            yearly_seasonality=self.yearly_seasonality,
            weekly_seasonality=self.weekly_seasonality,
            daily_seasonality=self.daily_seasonality,
            interval_width=0.95
        )
        self.model.fit(df_prophet)

        future = self.model.make_future_dataframe(periods=horizon_months, freq='MS')
        forecast = self.model.predict(future)

        res = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        res['model'] = 'Prophet'
        return res
