"""
Evaluation & Forecasting Comparison Module (Milestone 2)
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, Any

from .data_preparation import ForecastingDataPreparer
from .prophet_model import ProphetForecaster
from .xgboost_model import XGBoostForecaster
from .random_forest_model import RandomForestForecaster

class ForecastingEvaluator:
    def __init__(self, source_path: str = "Milestone_2/data/source/cleaned_superstore.csv"):
        self.preparer = ForecastingDataPreparer(source_path)
        self.df_monthly = None

    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        r2 = float(r2_score(y_true, y_pred))
        
        # Calculate MAPE avoiding divide-by-zero
        mask = y_true != 0
        mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100) if np.sum(mask) > 0 else 0.0

        return {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "R2": round(r2, 4),
            "MAPE_pct": round(mape, 2)
        }

    def run_pipeline(self, output_dir: str = "Milestone_2/outputs/forecasting", horizon_months: int = 12) -> Dict[str, Any]:
        self.df_monthly = self.preparer.prepare_monthly_series()
        self.preparer.save_processed()

        df_full = self.df_monthly[['ds', 'y', 'profit', 'quantity']].copy()
        df_full['ds'] = pd.to_datetime(df_full['ds'])

        # Split: Train = 36 months (2014-2016), Test = 12 months (2017)
        train_len = len(df_full) - horizon_months
        df_train = df_full.iloc[:train_len].copy()
        df_test = df_full.iloc[train_len:].copy()

        # -------------------------------------------------------------
        # 1. Backtest Evaluation on Test Set (2017)
        # -------------------------------------------------------------
        metrics_dict = {}

        # A. Prophet Test Evaluation
        prophet_eval = ProphetForecaster()
        p_test_fcst = prophet_eval.fit_predict(df_train, horizon_months=horizon_months)
        p_test_preds = p_test_fcst.set_index('ds').loc[df_test['ds']]['yhat'].values
        metrics_dict['Prophet'] = self._calculate_metrics(df_test['y'].values, p_test_preds)

        # B. XGBoost Test Evaluation
        xgb_eval = XGBoostForecaster()
        x_test_fcst = xgb_eval.fit_predict(df_train, horizon_months=horizon_months)
        x_test_preds = x_test_fcst.set_index('ds').loc[df_test['ds']]['yhat'].values
        metrics_dict['XGBoost'] = self._calculate_metrics(df_test['y'].values, x_test_preds)

        # C. Random Forest Test Evaluation
        rf_eval = RandomForestForecaster()
        rf_test_fcst = rf_eval.fit_predict(df_train, horizon_months=horizon_months)
        rf_test_preds = rf_test_fcst.set_index('ds').loc[df_test['ds']]['yhat'].values
        metrics_dict['Random Forest'] = self._calculate_metrics(df_test['y'].values, rf_test_preds)

        # Identify Best Model based on Lowest RMSE
        best_model_name = min(metrics_dict.keys(), key=lambda k: metrics_dict[k]['RMSE'])

        # -------------------------------------------------------------
        # 2. Full Model Training & 12-Month Future Forecasting (2018)
        # -------------------------------------------------------------
        prophet_full = ProphetForecaster()
        p_full_fcst = prophet_full.fit_predict(df_full, horizon_months=horizon_months)

        xgb_full = XGBoostForecaster()
        x_full_fcst = xgb_full.fit_predict(df_full, horizon_months=horizon_months)

        rf_full = RandomForestForecaster()
        rf_full_fcst = rf_full.fit_predict(df_full, horizon_months=horizon_months)

        # Format outputs
        os.makedirs(output_dir, exist_ok=True)

        p_full_fcst.to_csv(os.path.join(output_dir, "prophet_forecast.csv"), index=False)
        x_full_fcst.to_csv(os.path.join(output_dir, "xgboost_forecast.csv"), index=False)
        rf_full_fcst.to_csv(os.path.join(output_dir, "random_forest_forecast.csv"), index=False)

        # Combined dataframe with historical actuals + future forecasts
        p_sub = p_full_fcst.rename(columns={'yhat': 'prophet_yhat', 'yhat_lower': 'prophet_lower', 'yhat_upper': 'prophet_upper'}).drop(columns=['model'])
        x_sub = x_full_fcst.rename(columns={'yhat': 'xgboost_yhat', 'yhat_lower': 'xgboost_lower', 'yhat_upper': 'xgboost_upper'}).drop(columns=['model'])
        rf_sub = rf_full_fcst.rename(columns={'yhat': 'rf_yhat', 'yhat_lower': 'rf_lower', 'yhat_upper': 'rf_upper'}).drop(columns=['model'])

        combined = df_full[['ds', 'y', 'profit']].merge(p_sub, on='ds', how='outer')
        combined = combined.merge(x_sub, on='ds', how='outer')
        combined = combined.merge(rf_sub, on='ds', how='outer')
        combined = combined.sort_values('ds').reset_index(drop=True)

        combined.to_csv(os.path.join(output_dir, "combined_forecasts.csv"), index=False)

        # Save Metrics JSON
        output_metrics = {
            "historical_months_count": len(df_full),
            "forecast_horizon_months": horizon_months,
            "evaluation_train_period": f"{df_train['ds'].min().strftime('%Y-%m')} to {df_train['ds'].max().strftime('%Y-%m')}",
            "evaluation_test_period": f"{df_test['ds'].min().strftime('%Y-%m')} to {df_test['ds'].max().strftime('%Y-%m')}",
            "best_performing_model": best_model_name,
            "model_metrics": metrics_dict
        }

        with open(os.path.join(output_dir, "model_metrics.json"), "w") as f:
            json.dump(output_metrics, f, indent=2)

        # Optional DB Persistence via Service Layer
        try:
            from ...backend.database import SessionLocal
            from ...backend.db_service import save_forecasting_results_to_db
            db_session = SessionLocal()
            save_forecasting_results_to_db(combined, metrics_dict, best_model_name, db_session)
            db_session.close()
        except Exception as e:
            print(f"[DB Notice] Could not auto-persist forecasting to DB from pipeline runner: {e}")

        print(f"Forecasting pipeline completed successfully. Outputs saved to {output_dir}")
        return output_metrics

if __name__ == "__main__":
    evaluator = ForecastingEvaluator()
    evaluator.run_pipeline()

