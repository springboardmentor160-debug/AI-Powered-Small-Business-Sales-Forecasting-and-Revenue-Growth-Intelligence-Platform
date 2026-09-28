"""Leakage-aware time-series feature engineering for daily sales data."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TimeSeriesFeatureBuilder:
    """Build lag, rolling, and calendar features from a daily target series."""

    lags: tuple[int, ...] = (1, 7, 14, 28)
    rolling_windows: tuple[int, ...] = (7, 14, 28)

    @property
    def feature_columns(self) -> list[str]:
        columns = [f"lag_{lag}" for lag in self.lags]
        columns.extend(f"rolling_mean_{window}" for window in self.rolling_windows)
        columns.extend(f"rolling_std_{window}" for window in self.rolling_windows)
        columns.extend(
            [
                "day_of_week",
                "day_of_month",
                "month",
                "quarter",
                "day_of_year",
                "is_weekend",
            ]
        )
        return columns

    def build(self, daily_data: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Create historical features using only observations before each date."""
        if "date" not in daily_data.columns or target_column not in daily_data.columns:
            raise ValueError(f"Daily data must contain date and {target_column} columns.")

        data = daily_data[["date", target_column]].copy().sort_values("date")
        data["date"] = pd.to_datetime(data["date"])
        data[target_column] = pd.to_numeric(data[target_column], errors="coerce")
        data = data.dropna(subset=[target_column]).reset_index(drop=True)

        for lag in self.lags:
            data[f"lag_{lag}"] = data[target_column].shift(lag)
        shifted_target = data[target_column].shift(1)
        for window in self.rolling_windows:
            data[f"rolling_mean_{window}"] = shifted_target.rolling(window).mean()
            data[f"rolling_std_{window}"] = shifted_target.rolling(window).std().fillna(0)

        data["day_of_week"] = data["date"].dt.dayofweek
        data["day_of_month"] = data["date"].dt.day
        data["month"] = data["date"].dt.month
        data["quarter"] = data["date"].dt.quarter
        data["day_of_year"] = data["date"].dt.dayofyear
        data["is_weekend"] = data["day_of_week"].isin([5, 6]).astype(int)
        return data.dropna(subset=self.feature_columns).reset_index(drop=True)

    def build_future_row(self, history: list[float], date: pd.Timestamp) -> dict[str, float | int | pd.Timestamp]:
        """Build one future feature row from actual history plus prior predictions."""
        if len(history) < max(max(self.lags), max(self.rolling_windows)):
            raise ValueError("Future feature generation requires at least 28 historical values.")

        row: dict[str, float | int | pd.Timestamp] = {"date": date}
        for lag in self.lags:
            row[f"lag_{lag}"] = float(history[-lag])
        for window in self.rolling_windows:
            window_values = history[-window:]
            row[f"rolling_mean_{window}"] = float(sum(window_values) / window)
            row[f"rolling_std_{window}"] = float(pd.Series(window_values).std(ddof=1) or 0)
        row.update(
            {
                "day_of_week": date.dayofweek,
                "day_of_month": date.day,
                "month": date.month,
                "quarter": date.quarter,
                "day_of_year": date.dayofyear,
                "is_weekend": int(date.dayofweek in (5, 6)),
            }
        )
        return row
