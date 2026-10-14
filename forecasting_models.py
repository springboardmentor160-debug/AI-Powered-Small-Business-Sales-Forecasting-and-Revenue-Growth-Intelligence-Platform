import os
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from prophet import Prophet

warnings.filterwarnings("ignore", category=FutureWarning)

DATA_PATH = os.path.join("data", "clean_retail_sales.csv")
COMPARISON_PATH = os.path.join("data", "forecast_model_comparison.csv")
TEST_RESULTS_PATH = os.path.join("data", "milestone4_test_results.csv")
PREDICTIONS_PATH = os.path.join("data", "forecast_test_predictions.csv")

os.makedirs("data", exist_ok=True)

# 1. Load and validate cleaned sales data
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}. Run this script from the project folder."
    )

sales_df = pd.read_csv(DATA_PATH)
print("Sales data loaded successfully!")
print("Total rows:", len(sales_df))

required_columns = ["InvoiceDate", "Revenue"]
missing_columns = [col for col in required_columns if col not in sales_df.columns]
if missing_columns:
    raise ValueError(
        f"Required columns missing: {missing_columns}. Expected InvoiceDate and Revenue."
    )

# 2. Prepare date and revenue
sales_df["InvoiceDate"] = pd.to_datetime(sales_df["InvoiceDate"], errors="coerce")
sales_df["Revenue"] = pd.to_numeric(sales_df["Revenue"], errors="coerce")
sales_df = sales_df.dropna(subset=["InvoiceDate", "Revenue"]).copy()
if sales_df.empty:
    raise ValueError("No valid rows remain after cleaning InvoiceDate and Revenue.")

# 3. Aggregate revenue by day and fill missing calendar days with zero
daily_revenue = (
    sales_df.groupby(sales_df["InvoiceDate"].dt.floor("D"))["Revenue"]
    .sum()
    .rename_axis("date")
    .reset_index(name="revenue")
)

full_date_range = pd.date_range(
    start=daily_revenue["date"].min(),
    end=daily_revenue["date"].max(),
    freq="D",
)
daily_revenue = (
    daily_revenue.set_index("date")
    .reindex(full_date_range, fill_value=0)
    .rename_axis("date")
    .reset_index()
)

print("\nDaily revenue preview:")
print(daily_revenue.head(10).to_string(index=False))
print("Total calendar days:", len(daily_revenue))
print("Days with zero revenue:", int((daily_revenue["revenue"] == 0).sum()))

# 4. Time-series feature engineering. Lag features use past values only.
df = daily_revenue.copy()
df["day_of_week"] = df["date"].dt.dayofweek
df["day_of_month"] = df["date"].dt.day
df["month"] = df["date"].dt.month
df["revenue_lag_1"] = df["revenue"].shift(1)
df["revenue_lag_7"] = df["revenue"].shift(7)
df["revenue_rolling_7"] = df["revenue"].shift(1).rolling(window=7).mean()
df = df.dropna().reset_index(drop=True)

feature_cols = [
    "day_of_week", "day_of_month", "month",
    "revenue_lag_1", "revenue_lag_7", "revenue_rolling_7",
]
X = df[feature_cols]
y = df["revenue"]

# 5. Chronological 80/20 train/test split
split_point = int(len(df) * 0.8)
if split_point <= 0 or split_point >= len(df):
    raise ValueError("Not enough daily records for an 80/20 time-based split.")

X_train, X_test = X.iloc[:split_point], X.iloc[split_point:]
y_train, y_test = y.iloc[:split_point], y.iloc[split_point:]
test_dates = df.iloc[split_point:]["date"].reset_index(drop=True)

print("\nTime-based train/test split:")
print("Total usable records:", len(df))
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Training period:", df.iloc[0]["date"], "to", df.iloc[split_point - 1]["date"])
print("Testing period:", df.iloc[split_point]["date"], "to", df.iloc[-1]["date"])

# 6. Train Random Forest
print("\nTraining Random Forest...")
rf_model = RandomForestRegressor(
    n_estimators=100, random_state=42, n_jobs=-1
)
rf_model.fit(X_train, y_train)
rf_predictions = rf_model.predict(X_test)
print("Random Forest training completed.")

# 7. Train XGBoost
print("\nTraining XGBoost...")
xgb_model = XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    random_state=42,
    objective="reg:squarederror",
    n_jobs=-1,
)
xgb_model.fit(X_train, y_train)
xgb_predictions = xgb_model.predict(X_test)
print("XGBoost training completed.")

# 8. Train Prophet on training period only
print("\nTraining Prophet for model comparison...")
prophet_train = pd.DataFrame({
    "ds": df.iloc[:split_point]["date"].values,
    "y": df.iloc[:split_point]["revenue"].values,
})
prophet_model = Prophet()
prophet_model.fit(prophet_train)
prophet_test_dates = pd.DataFrame({"ds": test_dates})
prophet_forecast = prophet_model.predict(prophet_test_dates)
prophet_predictions = prophet_forecast["yhat"].to_numpy()
print("Prophet test predictions generated.")

# 9. Evaluate MAE, RMSE and R-squared
def evaluate_model(model_name, actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    r2 = r2_score(actual, predicted)
    return {
        "Model": model_name,
        "MAE": round(float(mae), 2),
        "RMSE": round(float(rmse), 2),
        "R2 Score": round(float(r2), 4),
    }

comparison = pd.DataFrame([
    evaluate_model("Random Forest", y_test, rf_predictions),
    evaluate_model("XGBoost", y_test, xgb_predictions),
    evaluate_model("Prophet", y_test, prophet_predictions),
])

print("\n" + "=" * 65)
print("FORECAST MODEL PERFORMANCE COMPARISON")
print("=" * 65)
print(comparison.to_string(index=False))
comparison.to_csv(COMPARISON_PATH, index=False)
print(f"Model comparison saved to: {COMPARISON_PATH}")

# 10. Save test-period predictions for later review
prediction_results = pd.DataFrame({
    "date": test_dates,
    "actual_revenue": np.asarray(y_test),
    "random_forest_prediction": rf_predictions,
    "xgboost_prediction": xgb_predictions,
    "prophet_prediction": prophet_predictions,
})
prediction_results.to_csv(PREDICTIONS_PATH, index=False)
print(f"Test-period predictions saved to: {PREDICTIONS_PATH}")

# 11. Update the Milestone 4 test record without duplicating forecast entries
new_rows = []
for _, row in comparison.iterrows():
    for metric in ["MAE", "RMSE", "R2 Score"]:
        new_rows.append({
            "module": f"Sales Forecasting ({row['Model']})",
            "metric": metric,
            "value": row[metric],
        })
new_results = pd.DataFrame(new_rows, columns=["module", "metric", "value"])

if os.path.exists(TEST_RESULTS_PATH):
    try:
        existing_results = pd.read_csv(TEST_RESULTS_PATH)
    except (pd.errors.EmptyDataError, UnicodeDecodeError):
        existing_results = pd.DataFrame(columns=["module", "metric", "value"])
    if not {"module", "metric", "value"}.issubset(existing_results.columns):
        existing_results = pd.DataFrame(columns=["module", "metric", "value"])
    else:
        existing_results = existing_results[
            ~existing_results["module"].astype(str).str.startswith("Sales Forecasting (")
        ]
    full_results = pd.concat([existing_results, new_results], ignore_index=True)
else:
    full_results = new_results

full_results.to_csv(TEST_RESULTS_PATH, index=False)
print(f"Milestone 4 test record updated: {TEST_RESULTS_PATH}")
