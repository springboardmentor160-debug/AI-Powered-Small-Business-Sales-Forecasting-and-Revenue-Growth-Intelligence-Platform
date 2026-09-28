"""Deterministic tree-based regressors for daily sales forecasting."""

from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor


@dataclass
class XGBoostForecaster:
    """Small deterministic XGBoost regressor for the initial model comparison."""

    random_state: int = 42

    def fit_predict(self, train: pd.DataFrame, validation: pd.DataFrame, feature_columns: list[str], target_column: str) -> pd.Series:
        model = XGBRegressor(
            n_estimators=250,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=self.random_state,
            n_jobs=1,
        )
        model.fit(train[feature_columns], train[target_column])
        return pd.Series(model.predict(validation[feature_columns]), index=validation.index)

    def fit(self, train: pd.DataFrame, feature_columns: list[str], target_column: str) -> XGBRegressor:
        model = XGBRegressor(
            n_estimators=250,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=self.random_state,
            n_jobs=1,
        )
        model.fit(train[feature_columns], train[target_column])
        return model


@dataclass
class RandomForestForecaster:
    """Small deterministic Random Forest regressor for the initial comparison."""

    random_state: int = 42

    def fit_predict(self, train: pd.DataFrame, validation: pd.DataFrame, feature_columns: list[str], target_column: str) -> pd.Series:
        model = self.fit(train, feature_columns, target_column)
        return pd.Series(model.predict(validation[feature_columns]), index=validation.index)

    def fit(self, train: pd.DataFrame, feature_columns: list[str], target_column: str) -> RandomForestRegressor:
        model = RandomForestRegressor(
            n_estimators=250,
            max_depth=12,
            min_samples_leaf=2,
            random_state=self.random_state,
            n_jobs=1,
        )
        model.fit(train[feature_columns], train[target_column])
        return model
