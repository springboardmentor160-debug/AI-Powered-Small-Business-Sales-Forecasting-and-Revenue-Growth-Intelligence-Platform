import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def prepare_daily_revenue(data_path: str = None):
    """
    Aggregates transactions into a daily revenue time series.
    Detects and reports missing dates without silent imputation.
    """
    if data_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        data_path = os.path.join(base_dir, "data", "processed", "clean_sales.csv")
        if not os.path.exists(data_path):
            data_path = os.path.join(base_dir, "cleaned_sales_data.csv")

    df = pd.read_csv(data_path)
    date_col = "order_date" if "order_date" in df.columns else "date"
    df[date_col] = pd.to_datetime(df[date_col])

    if "quantity" in df.columns and "unit_price" in df.columns:
        df["total_amount"] = df["quantity"] * df["unit_price"]

    # Normalize to date (midnight)
    df["calendar_date"] = df[date_col].dt.floor("D")

    daily_revenue = df.groupby("calendar_date")["total_amount"].sum().reset_index()
    daily_revenue.columns = ["date", "revenue"]
    daily_revenue["revenue"] = daily_revenue["revenue"].round(2)
    daily_revenue = daily_revenue.sort_values("date").reset_index(drop=True)

    # Check for gaps in the chronological series
    full_date_range = pd.date_range(start=daily_revenue["date"].min(), end=daily_revenue["date"].max(), freq="D")
    missing_dates = full_date_range.difference(daily_revenue["date"])
    missing_dates_list = [d.strftime("%Y-%m-%d") for d in missing_dates]

    return daily_revenue, len(missing_dates), missing_dates_list

def engineer_features(daily_df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs regression features strictly with shift(1) to avoid forward data leakage.
    """
    df = daily_df.copy()
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["month"] = df["date"].dt.month

    # Lag features
    df["revenue_lag_1"] = df["revenue"].shift(1)
    df["revenue_lag_7"] = df["revenue"].shift(7)

    # Rolling average: shift(1) before rolling ensures today's actual revenue is never leaked
    df["revenue_rolling_7"] = df["revenue"].shift(1).rolling(window=7).mean()

    # Drop the first 7 rows that lack lag history
    clean_df = df.dropna().reset_index(drop=True)
    return clean_df

def evaluate_models(daily_df: pd.DataFrame, artifacts_dir: str = None):
    """
    Evaluates Prophet, Random Forest, and XGBoost on the identical 20% chronological test window.
    Programmatically selects the winner based on lowest RMSE.
    """
    if artifacts_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    feat_df = engineer_features(daily_df)
    feature_cols = ["day_of_week", "day_of_month", "month", "revenue_lag_1", "revenue_lag_7", "revenue_rolling_7"]

    # Chronological 80/20 split - never shuffled
    split_point = int(len(feat_df) * 0.8)
    train_df = feat_df.iloc[:split_point]
    test_df = feat_df.iloc[split_point:]

    X_train, y_train = train_df[feature_cols], train_df["revenue"]
    X_test, y_test = test_df[feature_cols], test_df["revenue"]

    # 1. Random Forest Regressor
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_mae = float(mean_absolute_error(y_test, rf_preds))
    rf_rmse = float(np.sqrt(mean_squared_error(y_test, rf_preds)))

    # 2. XGBoost Regressor
    xgb = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    xgb.fit(X_train, y_train)
    xgb_preds = xgb.predict(X_test)
    xgb_mae = float(mean_absolute_error(y_test, xgb_preds))
    xgb_rmse = float(np.sqrt(mean_squared_error(y_test, xgb_preds)))

    # 3. Prophet on identical test window
    # Prophet trains on dates corresponding to train_df
    prophet_train = train_df[["date", "revenue"]].rename(columns={"date": "ds", "revenue": "y"})
    m = Prophet()
    m.fit(prophet_train)
    prophet_test_future = test_df[["date"]].rename(columns={"date": "ds"})
    prophet_pred_df = m.predict(prophet_test_future)
    prophet_preds = prophet_pred_df["yhat"].values
    prophet_mae = float(mean_absolute_error(y_test, prophet_preds))
    prophet_rmse = float(np.sqrt(mean_squared_error(y_test, prophet_preds)))

    metrics = {
        "Random Forest Regressor": {"mae": round(rf_mae, 2), "rmse": round(rf_rmse, 2)},
        "XGBoost Regressor": {"mae": round(xgb_mae, 2), "rmse": round(xgb_rmse, 2)},
        "Prophet": {"mae": round(prophet_mae, 2), "rmse": round(prophet_rmse, 2)}
    }

    # Programmatically choose winner based on lowest RMSE
    winner_name = min(metrics.keys(), key=lambda m_name: metrics[m_name]["rmse"])

    # Always generate and save Prophet component & forecast plots on full historical series
    prophet_full = daily_df[["date", "revenue"]].rename(columns={"date": "ds", "revenue": "y"})
    prophet_model_full = Prophet()
    prophet_model_full.fit(prophet_full)
    prophet_future_full = prophet_model_full.make_future_dataframe(periods=30)
    prophet_forecast_full = prophet_model_full.predict(prophet_future_full)

    fig1 = prophet_model_full.plot(prophet_forecast_full)
    plt.title("Daily Revenue 30-Day Trend & Forecast", fontsize=12, fontweight="bold")
    plt.xlabel("Date", fontsize=10)
    plt.ylabel("Revenue (₹)", fontsize=10)
    plt.tight_layout()
    fig1.savefig(os.path.join(artifacts_dir, "revenue_forecast.png"), dpi=200)
    plt.close(fig1)

    fig2 = prophet_model_full.plot_components(prophet_forecast_full)
    plt.tight_layout()
    fig2.savefig(os.path.join(artifacts_dir, "forecast_components.png"), dpi=200)
    plt.close(fig2)

    return {
        "metrics": metrics,
        "winner_name": winner_name,
        "feat_df": feat_df,
        "feature_cols": feature_cols,
        "prophet_forecast_full": prophet_forecast_full,
        "prophet_model_full": prophet_model_full
    }

def run_recursive_forecast(daily_df: pd.DataFrame, eval_results: dict, periods: int = 30):
    """
    Retrains the winner on the FULL dataset and performs a true recursive 30-day ahead forecast.
    Returns daily projections and the 30-day total.
    """
    winner_name = eval_results["winner_name"]
    metrics = eval_results["metrics"]
    winner_rmse = metrics[winner_name]["rmse"]
    last_date = daily_df["date"].max()

    future_dates = [last_date + timedelta(days=i) for i in range(1, periods + 1)]

    if winner_name == "Prophet":
        # Extract the future 30 days from Prophet's full forecast
        prophet_forecast = eval_results["prophet_forecast_full"]
        future_prophet = prophet_forecast.tail(periods).copy()
        
        forecast_rows = []
        for _, row in future_prophet.iterrows():
            d = pd.to_datetime(row["ds"])
            forecast_rows.append({
                "date": d.strftime("%Y-%m-%d"),
                "day_of_week": d.strftime("%A"),
                "predicted_revenue": max(0.0, round(float(row["yhat"]), 2)),
                "lower_bound": max(0.0, round(float(row["yhat_lower"]), 2)),
                "upper_bound": round(float(row["yhat_upper"]), 2)
            })
    else:
        # Train winning ML regressor on ALL available feature rows
        feat_df = eval_results["feat_df"]
        feature_cols = eval_results["feature_cols"]
        X_all = feat_df[feature_cols]
        y_all = feat_df["revenue"]

        if winner_name == "Random Forest Regressor":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        
        model.fit(X_all, y_all)

        # Build full historical revenue series as a list
        revenue_history = list(daily_df["revenue"].values)
        forecast_rows = []

        # Recursively project day by day
        for cur_date in future_dates:
            dow = cur_date.dayofweek
            dom = cur_date.day
            mon = cur_date.month
            
            lag_1 = revenue_history[-1]
            lag_7 = revenue_history[-7]
            rolling_7 = float(np.mean(revenue_history[-7:]))

            row_features = pd.DataFrame([{
                "day_of_week": dow,
                "day_of_month": dom,
                "month": mon,
                "revenue_lag_1": lag_1,
                "revenue_lag_7": lag_7,
                "revenue_rolling_7": rolling_7
            }])

            y_pred = float(model.predict(row_features)[0])
            y_pred = max(0.0, round(y_pred, 2))

            # 95% Confidence Interval based on test RMSE
            lower_b = max(0.0, round(y_pred - 1.96 * winner_rmse, 2))
            upper_b = round(y_pred + 1.96 * winner_rmse, 2)

            forecast_rows.append({
                "date": cur_date.strftime("%Y-%m-%d"),
                "day_of_week": cur_date.strftime("%A"),
                "predicted_revenue": y_pred,
                "lower_bound": lower_b,
                "upper_bound": upper_b
            })

            # Append prediction for recursive multi-step forecasting
            revenue_history.append(y_pred)

    total_30day_revenue = round(sum(r["predicted_revenue"] for r in forecast_rows), 2)

    return {
        "period": f"Next {periods} Days",
        "predicted_revenue": total_30day_revenue,
        "model_used": winner_name,
        "metrics": metrics,
        "daily_forecast": forecast_rows
    }
