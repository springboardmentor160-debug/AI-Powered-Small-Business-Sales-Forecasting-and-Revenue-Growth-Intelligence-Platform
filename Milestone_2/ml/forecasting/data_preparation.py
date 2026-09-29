"""
Data Preparation Module for Sales and Revenue Forecasting (Milestone 2)
"""

import os
import pandas as pd
import numpy as np

class ForecastingDataPreparer:
    def __init__(self, source_path: str = "Milestone_2/data/source/cleaned_superstore.csv"):
        self.source_path = source_path
        self.df_raw = None
        self.df_monthly = None
        self.df_daily = None

    def _resolve_source_path(self) -> str:
        if os.path.exists(self.source_path):
            return self.source_path
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        alt_path = os.path.join(workspace_root, self.source_path)
        if os.path.exists(alt_path):
            return alt_path
        m2_path = os.path.join(workspace_root, "Milestone_2", "data", "source", "cleaned_superstore.csv")
        if os.path.exists(m2_path):
            return m2_path
        raise FileNotFoundError(f"Source file not found at {self.source_path}")

    def load_raw_data(self) -> pd.DataFrame:
        path = self._resolve_source_path()
        self.df_raw = pd.read_csv(path)
        if 'order_date' in self.df_raw.columns:
            self.df_raw['order_date'] = pd.to_datetime(self.df_raw['order_date'])
        elif 'sale_date' in self.df_raw.columns:
            self.df_raw['order_date'] = pd.to_datetime(self.df_raw['sale_date'])
            self.df_raw['sales'] = self.df_raw['sales_amount']
        
        return self.df_raw

    def prepare_monthly_series(self) -> pd.DataFrame:
        if self.df_raw is None:
            self.load_raw_data()

        df = self.df_raw.copy()
        df['year_month'] = df['order_date'].dt.to_period('M')

        # Group by month
        monthly = df.groupby('year_month').agg({
            'sales': 'sum',
            'profit': 'sum' if 'profit' in df.columns else lambda x: 0.0,
            'quantity': 'sum',
            'order_id': 'nunique' if 'order_id' in df.columns else 'count'
        }).reset_index()

        monthly['ds'] = monthly['year_month'].dt.to_timestamp()
        monthly = monthly.sort_values('ds').reset_index(drop=True)

        monthly.rename(columns={'sales': 'y'}, inplace=True)

        # Feature engineering for supervised forecasting models (lags, rolling stats, calendar)
        monthly['y_lag1'] = monthly['y'].shift(1)
        monthly['y_lag2'] = monthly['y'].shift(2)
        monthly['y_lag3'] = monthly['y'].shift(3)
        monthly['y_lag12'] = monthly['y'].shift(12)

        monthly['y_roll3'] = monthly['y'].shift(1).rolling(window=3).mean()
        monthly['y_roll6'] = monthly['y'].shift(1).rolling(window=6).mean()

        monthly['month'] = monthly['ds'].dt.month
        monthly['quarter'] = monthly['ds'].dt.quarter
        monthly['year'] = monthly['ds'].dt.year

        self.df_monthly = monthly
        return monthly

    def save_processed(self, output_path: str = "Milestone_2/data/processed/time_series_sales.csv"):
        if self.df_monthly is None:
            self.prepare_monthly_series()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Drop year_month object column for clean csv saving
        save_df = self.df_monthly.drop(columns=['year_month'], errors='ignore')
        save_df.to_csv(output_path, index=False)
        print(f"Processed monthly time series saved to {output_path}")

if __name__ == "__main__":
    prep = ForecastingDataPreparer()
    prep.prepare_monthly_series()
    prep.save_processed()
