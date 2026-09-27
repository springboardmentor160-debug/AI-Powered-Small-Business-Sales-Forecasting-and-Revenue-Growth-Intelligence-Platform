import pandas as pd


# -----------------------------------------
# LOAD CLEANED SALES DATA
# -----------------------------------------

sales_df = pd.read_csv(
    "data/clean_retail_sales.csv"
)

print("Sales data loaded successfully!")
print("Total rows:", len(sales_df))


# -----------------------------------------
# PREPARE DATE AND REVENUE
# -----------------------------------------

sales_df["InvoiceDate"] = pd.to_datetime(
    sales_df["InvoiceDate"],
    errors="coerce"
)

sales_df["Revenue"] = pd.to_numeric(
    sales_df["Revenue"],
    errors="coerce"
)

sales_df = sales_df.dropna(
    subset=["InvoiceDate", "Revenue"]
)


# -----------------------------------------
# BUILD DAILY REVENUE
# -----------------------------------------

daily_revenue = (
    sales_df
    .groupby(
        sales_df["InvoiceDate"].dt.date
    )["Revenue"]
    .sum()
    .reset_index()
)

daily_revenue.columns = [
    "date",
    "revenue"
]

daily_revenue["date"] = pd.to_datetime(
    daily_revenue["date"]
)


# -----------------------------------------
# FILL MISSING CALENDAR DAYS
# -----------------------------------------

full_date_range = pd.date_range(
    start=daily_revenue["date"].min(),
    end=daily_revenue["date"].max(),
    freq="D"
)

daily_revenue = (
    daily_revenue
    .set_index("date")
    .reindex(full_date_range)
    .fillna(0)
    .rename_axis("date")
    .reset_index()
)


print("\nDaily Revenue:")
print(
    daily_revenue.head(10)
)

print(
    "\nTotal calendar days:",
    len(daily_revenue)
)

print(
    "Days with zero revenue:",
    (daily_revenue["revenue"] == 0).sum()
)


# -----------------------------------------
# TIME-SERIES FEATURE ENGINEERING
# -----------------------------------------

df = daily_revenue.copy()

# Date features
df["day_of_week"] = (
    df["date"].dt.dayofweek
)

df["day_of_month"] = (
    df["date"].dt.day
)

df["month"] = (
    df["date"].dt.month
)


# Lag features
df["revenue_lag_1"] = (
    df["revenue"].shift(1)
)

df["revenue_lag_7"] = (
    df["revenue"].shift(7)
)


# 7-day rolling average
# shift(1) prevents data leakage
df["revenue_rolling_7"] = (
    df["revenue"]
    .shift(1)
    .rolling(window=7)
    .mean()
)


# -----------------------------------------
# REMOVE ROWS WITHOUT ENOUGH HISTORY
# -----------------------------------------

df = df.dropna().reset_index(
    drop=True
)


# -----------------------------------------
# DISPLAY FEATURES
# -----------------------------------------

print("\nEngineered Features:")

print(
    df[
        [
            "date",
            "revenue",
            "day_of_week",
            "day_of_month",
            "month",
            "revenue_lag_1",
            "revenue_lag_7",
            "revenue_rolling_7"
        ]
    ].head(10)
)


# -----------------------------------------
# FEATURE INFORMATION
# -----------------------------------------

feature_cols = [
    "day_of_week",
    "day_of_month",
    "month",
    "revenue_lag_1",
    "revenue_lag_7",
    "revenue_rolling_7"
]

print(
    "\nFeature columns:"
)

print(
    feature_cols
)

print(
    "\nTotal usable records:",
    len(df)
)

# -----------------------------------------
# PREPARE TRAINING FEATURES
# -----------------------------------------

X = df[feature_cols]

y = df["revenue"]


# -----------------------------------------
# TIME-BASED TRAIN / TEST SPLIT
# -----------------------------------------

split_point = int(
    len(df) * 0.8
)

X_train = X.iloc[:split_point]
X_test = X.iloc[split_point:]

y_train = y.iloc[:split_point]
y_test = y.iloc[split_point:]


# -----------------------------------------
# DISPLAY SPLIT INFORMATION
# -----------------------------------------

print("\nTime-based train/test split:")

print(
    "Total records:",
    len(df)
)

print(
    "Training records:",
    len(X_train)
)

print(
    "Testing records:",
    len(X_test)
)

print(
    "\nTraining period:"
)

print(
    df.iloc[0]["date"],
    "to",
    df.iloc[split_point - 1]["date"]
)

print(
    "\nTesting period:"
)

print(
    df.iloc[split_point]["date"],
    "to",
    df.iloc[-1]["date"]
)

# -----------------------------------------
# RANDOM FOREST REGRESSOR
# -----------------------------------------

from sklearn.ensemble import RandomForestRegressor


print("\nTraining Random Forest...")


rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


rf_model.fit(
    X_train,
    y_train
)


rf_predictions = rf_model.predict(
    X_test
)


print(
    "Random Forest training completed!"
)


# -----------------------------------------
# DISPLAY RANDOM FOREST PREDICTIONS
# -----------------------------------------

rf_results = pd.DataFrame({

    "date": df.iloc[
        split_point:
    ]["date"].values,

    "actual_revenue": y_test.values,

    "predicted_revenue": rf_predictions

})


print(
    "\nRandom Forest Predictions:"
)

print(
    rf_results.head(10).to_string(
        index=False
    )
)
# -----------------------------------------
# XGBOOST REGRESSOR
# -----------------------------------------

from xgboost import XGBRegressor


print("\nTraining XGBoost...")


xgb_model = XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    random_state=42
)


xgb_model.fit(
    X_train,
    y_train
)


xgb_predictions = xgb_model.predict(
    X_test
)


print(
    "XGBoost training completed!"
)


# -----------------------------------------
# DISPLAY XGBOOST PREDICTIONS
# -----------------------------------------

xgb_results = pd.DataFrame({

    "date": df.iloc[
        split_point:
    ]["date"].values,

    "actual_revenue": y_test.values,

    "predicted_revenue": xgb_predictions

})


print(
    "\nXGBoost Predictions:"
)

print(
    xgb_results.head(10).to_string(
        index=False
    )
)
# -----------------------------------------
# PROPHET - TEST PERIOD PREDICTIONS
# -----------------------------------------

from prophet import Prophet


print("\nTraining Prophet for model comparison...")


# Prepare Prophet training data
prophet_train = pd.DataFrame({
    "ds": df.iloc[:split_point]["date"],
    "y": df.iloc[:split_point]["revenue"]
})


# Train Prophet only on training period
prophet_model = Prophet()

prophet_model.fit(
    prophet_train
)


# Create dates for the test period
prophet_test_dates = pd.DataFrame({
    "ds": df.iloc[split_point:]["date"]
})


# Generate predictions
prophet_forecast = prophet_model.predict(
    prophet_test_dates
)


prophet_predictions = (
    prophet_forecast["yhat"]
    .values
)


print(
    "Prophet test predictions generated!"
)
# -----------------------------------------
# MODEL EVALUATION
# -----------------------------------------

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)

import numpy as np


def evaluate_model(
    model_name,
    actual,
    predicted
):

    mae = mean_absolute_error(
        actual,
        predicted
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted
        )
    )

    return {
        "Model": model_name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2)
    }


# Evaluate all three models

rf_metrics = evaluate_model(
    "Random Forest",
    y_test,
    rf_predictions
)


xgb_metrics = evaluate_model(
    "XGBoost",
    y_test,
    xgb_predictions
)


prophet_metrics = evaluate_model(
    "Prophet",
    y_test,
    prophet_predictions
)


# -----------------------------------------
# COMPARISON TABLE
# -----------------------------------------

comparison = pd.DataFrame([
    rf_metrics,
    xgb_metrics,
    prophet_metrics
])


print(
    "\n========================================"
)

print(
    "MODEL PERFORMANCE COMPARISON"
)

print(
    "========================================"
)

print(
    comparison.to_string(
        index=False
    )
)


# -----------------------------------------
# SAVE COMPARISON
# -----------------------------------------

comparison.to_csv(
    "data/forecast_model_comparison.csv",
    index=False
)


print(
    "\nModel comparison saved successfully!"
)

print(
    "File: data/forecast_model_comparison.csv"
)