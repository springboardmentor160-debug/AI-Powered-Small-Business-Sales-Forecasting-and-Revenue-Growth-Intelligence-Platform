"""
XGBoost Regressor Forecasting Model (Milestone 2)
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from typing import Tuple, List

class XGBoostForecaster:
    def __init__(self, n_estimators: int = 100, max_depth: int = 4, learning_rate: float = 0.05, random_state: int = 42):
        self.params = {
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'learning_rate': learning_rate,
            'random_state': random_state
        }
        self.model = xgb.XGBRegressor(**self.params)
        self.feature_cols = ['month', 'quarter', 'year', 'y_lag1', 'y_lag2', 'y_lag3', 'y_roll3', 'y_roll6']

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_feat = df.copy()
        df_feat['ds'] = pd.to_datetime(df_feat['ds'])
        df_feat['month'] = df_feat['ds'].dt.month
        df_feat['quarter'] = df_feat['ds'].dt.quarter
        df_feat['year'] = df_feat['ds'].dt.year

        df_feat['y_lag1'] = df_feat['y'].shift(1)
        df_feat['y_lag2'] = df_feat['y'].shift(2)
        df_feat['y_lag3'] = df_feat['y'].shift(3)
        df_feat['y_roll3'] = df_feat['y'].shift(1).rolling(3).mean()
        df_feat['y_roll6'] = df_feat['y'].shift(1).rolling(6).mean()

        return df_feat

    def fit_predict(self, df_train: pd.DataFrame, horizon_months: int = 12) -> pd.DataFrame:
        df_feat = self._prepare_features(df_train)
        
        # Train dataset dropping missing initial lags
        df_train_clean = df_feat.dropna(subset=self.feature_cols).copy()
        
        X_train = df_train_clean[self.feature_cols]
        y_train = df_train_clean['y']

        self.model.fit(X_train, y_train)

        # In-sample predictions
        train_preds = self.model.predict(X_train)
        df_res = pd.DataFrame({
            'ds': df_train_clean['ds'].values,
            'yhat': train_preds,
            'model': 'XGBoost'
        })

        # Multi-step future recursive forecasting
        history = list(df_train['y'].values)
        dates = list(pd.to_datetime(df_train['ds'].values))

        future_preds = []
        future_dates = []

        last_date = dates[-1]

        for i in range(1, horizon_months + 1):
            next_date = last_date + pd.DateOffset(months=i)
            
            # Compute features using current history
            y_lag1 = history[-1]
            y_lag2 = history[-2]
            y_lag3 = history[-3]
            y_roll3 = np.mean(history[-3:])
            y_roll6 = np.mean(history[-6:])

            feat_vector = pd.DataFrame([{
                'month': next_date.month,
                'quarter': next_date.quarter,
                'year': next_date.year,
                'y_lag1': y_lag1,
                'y_lag2': y_lag2,
                'y_lag3': y_lag3,
                'y_roll3': y_roll3,
                'y_roll6': y_roll6
            }])[self.feature_cols]

            pred_val = float(self.model.predict(feat_vector)[0])
            pred_val = max(0.0, pred_val) # non-negative constraint

            history.append(pred_val)
            future_dates.append(next_date)
            future_preds.append(pred_val)

        df_future = pd.DataFrame({
            'ds': future_dates,
            'yhat': future_preds,
            'model': 'XGBoost'
        })

        full_res = pd.concat([df_res, df_future], ignore_index=True)
        # Approximate 95% confidence intervals based on residual std dev
        residuals = y_train.values - train_preds
        std_err = np.std(residuals) if len(residuals) > 0 else 0.0

        full_res['yhat_lower'] = np.maximum(0, full_res['yhat'] - 1.96 * std_err)
        full_res['yhat_upper'] = full_res['yhat'] + 1.96 * std_err

        return full_res
