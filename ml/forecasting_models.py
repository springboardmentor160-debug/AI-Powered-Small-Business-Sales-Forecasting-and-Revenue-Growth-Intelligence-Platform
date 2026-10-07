"""
Sales Forecasting -- MarketMind AI
Milestone 2, Day 7-8: Forecasting Models (XGBoost + Random Forest)

Extends Day 5-6's Prophet forecast with two tree-based regressors, and
compares all three on a held-out test period using MAE and RMSE.

Unlike Prophet, XGBoost/Random Forest don't understand "time" on their
own -- they need engineered features (day of week, month, a lag of
recent demand) that describe time numerically before they can predict
anything.

    python forecasting_models.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Load and aggregate -- same daily series as Day 5-6
# ---------------------------------------------------------------------------
df = pd.read_csv("./datasets/processed/sales_data_prepped.csv")
df["Date"] = pd.to_datetime(df["Date"])

daily = df.groupby("Date")["Demand"].sum().reset_index()
daily.columns = ["ds", "y"]
daily = daily.sort_values("ds").reset_index(drop=True)

# ---------------------------------------------------------------------------
# 2. Feature engineering for XGBoost / Random Forest
# ---------------------------------------------------------------------------
# These models see each row independently -- they have no built-in
# concept of "yesterday" or "last week" the way Prophet does. We give
# them that context explicitly as columns.
daily["day_of_week"] = daily["ds"].dt.dayofweek
daily["month"] = daily["ds"].dt.month
daily["day_of_year"] = daily["ds"].dt.dayofyear

# Lag features: what demand looked like 1 and 7 days ago. This is how
# a non-time-series model gets access to recent trend/momentum.
daily["lag_1"] = daily["y"].shift(1)
daily["lag_7"] = daily["y"].shift(7)
daily["rolling_mean_7"] = daily["y"].shift(1).rolling(7).mean()

# Lag features create NaNs for the first few rows (no history yet) --
# drop them, same reasoning as dropping rows with missing values
# anywhere else in this project.
daily = daily.dropna().reset_index(drop=True)

feature_cols = ["day_of_week", "month", "day_of_year", "lag_1", "lag_7", "rolling_mean_7"]

# ---------------------------------------------------------------------------
# 3. Train/test split -- hold out the most recent 90 days to test against
# ---------------------------------------------------------------------------
# A time series split must respect chronological order -- randomly
# shuffling rows (like a typical train_test_split) would let the model
# "see the future" during training, which is not a fair test.
split_point = len(daily) - 90
train = daily.iloc[:split_point]
test = daily.iloc[split_point:]

X_train, y_train = train[feature_cols], train["y"]
X_test, y_test = test[feature_cols], test["y"]

# ---------------------------------------------------------------------------
# 4. Train both models
# ---------------------------------------------------------------------------
rf = RandomForestRegressor(n_estimators=200, random_state=42)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)

xgb = XGBRegressor(n_estimators=200, random_state=42)
xgb.fit(X_train, y_train)
xgb_pred = xgb.predict(X_test)

# ---------------------------------------------------------------------------
# 5. Evaluate -- MAE and RMSE, the metrics named in the project spec
# ---------------------------------------------------------------------------
def report(name, y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"{name:20s}  MAE: {mae:8.2f}   RMSE: {rmse:8.2f}")
    return mae, rmse

print("=== Forecast accuracy on held-out last 90 days ===")
rf_mae, rf_rmse = report("Random Forest", y_test, rf_pred)
xgb_mae, xgb_rmse = report("XGBoost", y_test, xgb_pred)

# ---------------------------------------------------------------------------
# 5b. Prophet, on the same held-out period -- for a fair three-way comparison
# ---------------------------------------------------------------------------
# Re-fit Prophet on the same training window (not the full dataset, as in
# Day 5-6) so its test-period predictions are comparable to RF/XGBoost --
# scoring Prophet on data it was trained on would be an unfair advantage.
from prophet import Prophet

prophet_train = train[["ds", "y"]]
prophet_model = Prophet()
prophet_model.fit(prophet_train)

prophet_future = prophet_model.make_future_dataframe(periods=90)
prophet_forecast = prophet_model.predict(prophet_future)
prophet_test_pred = prophet_forecast.tail(90)["yhat"].values

prophet_mae, prophet_rmse = report("Prophet", y_test, prophet_test_pred)

print("\n=== Winner ===")
results = {"Random Forest": rf_mae, "XGBoost": xgb_mae, "Prophet": prophet_mae}
best = min(results, key=results.get)
print(f"Lowest MAE: {best} ({results[best]:.2f})")
print("Note: best on THIS dataset and THIS test window -- re-check as more")
print("real data comes in, per the handout's own caution on this point.")

# ---------------------------------------------------------------------------
# 6. Feature importance -- which signals actually drove the predictions
# ---------------------------------------------------------------------------
importance = pd.DataFrame({
    "feature": feature_cols,
    "xgboost_importance": xgb.feature_importances_,
    "random_forest_importance": rf.feature_importances_,
}).sort_values("xgboost_importance", ascending=False)

print("\n=== Feature importance ===")
print(importance.to_string(index=False))

# ---------------------------------------------------------------------------
# 7. Plot actual vs predicted for both models
# ---------------------------------------------------------------------------
plt.figure(figsize=(12, 5))
plt.plot(test["ds"], y_test, label="Actual", color="black")
plt.plot(test["ds"], rf_pred, label="Random Forest", alpha=0.8)
plt.plot(test["ds"], xgb_pred, label="XGBoost", alpha=0.8)
plt.legend()
plt.title("Actual vs Predicted Demand -- Held-Out Test Period")
plt.xlabel("Date")
plt.ylabel("Demand")
plt.tight_layout()
plt.savefig("model_comparison.png")
print("\nSaved model_comparison.png")