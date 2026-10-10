import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

OUT = "data/outputs"
os.makedirs(OUT, exist_ok=True)

# =============== 1. DATA LOAD ===============
sales_df = pd.read_csv("data/processed/cleaned_sales.csv")
sales_df = sales_df.dropna(subset=["customer_id"])
sales_df["order_date"] = pd.to_datetime(sales_df["order_date"])
sales_df["total_amount"] = sales_df["revenue"]
print("Total rows:", len(sales_df))
print("Date range:", sales_df["order_date"].min().date(), "to", sales_df["order_date"].max().date())

# =============== 2. SEGMENTATION ===============
reference_date = sales_df["order_date"].max() + pd.Timedelta(days=1)

customer_features = sales_df.groupby("customer_id").agg(
    purchase_frequency=("order_id", "nunique"),
    purchase_value=("total_amount", "mean"),
    last_purchase_date=("order_date", "max"),
).reset_index()

customer_features["customer_activity_days"] = (
    reference_date - customer_features["last_purchase_date"]
).dt.days

feature_cols = ["purchase_frequency", "purchase_value", "customer_activity_days"]
X_scaled = StandardScaler().fit_transform(customer_features[feature_cols])

customer_features["cluster"] = KMeans(n_clusters=4, random_state=42, n_init=10).fit_predict(X_scaled)
customer_features["cluster_hierarchical"] = AgglomerativeClustering(n_clusters=4).fit_predict(X_scaled)

summary = customer_features.groupby("cluster")[feature_cols].mean()
print("\nCluster summary:\n", summary.round(1))

# Clusters ko automatically naam do
remaining = list(summary.index)
names = {}
c = summary.loc[remaining, "customer_activity_days"].idxmax()
names[c] = "At-Risk / Fading Customers"; remaining.remove(c)
score = summary["purchase_frequency"] * summary["purchase_value"]
c = score.loc[remaining].idxmax()
names[c] = "VIP / Loyal Customers"; remaining.remove(c)
c = score.loc[remaining].idxmax()
names[c] = "Regular Customers"; remaining.remove(c)
names[remaining[0]] = "Occasional Shoppers"

customer_features["segment"] = customer_features["cluster"].map(names)

segment_summary = customer_features.groupby("segment").agg(
    customer_count=("customer_id", "count"),
    avg_purchase_value=("purchase_value", "mean"),
).reset_index().round(2)
print("\nSegments:\n", segment_summary)

customer_features.to_csv(f"{OUT}/customer_segments.csv", index=False)
segment_summary.to_csv(f"{OUT}/segment_summary.csv", index=False)

# =============== 3. FORECASTING ===============
daily = sales_df.groupby("order_date")["total_amount"].sum()
daily = daily.asfreq("D", fill_value=0).reset_index()
daily.columns = ["date", "revenue"]

df = daily.copy()
df["day_of_week"] = df["date"].dt.dayofweek
df["day_of_month"] = df["date"].dt.day
df["month"] = df["date"].dt.month
df["revenue_lag_1"] = df["revenue"].shift(1)
df["revenue_lag_7"] = df["revenue"].shift(7)
df["revenue_rolling_7"] = df["revenue"].shift(1).rolling(window=7).mean()
df = df.dropna().reset_index(drop=True)

ts_cols = ["day_of_week", "day_of_month", "month",
           "revenue_lag_1", "revenue_lag_7", "revenue_rolling_7"]
split_point = int(len(df) * 0.8)
X_train, X_test = df[ts_cols].iloc[:split_point], df[ts_cols].iloc[split_point:]
y_train, y_test = df["revenue"].iloc[:split_point], df["revenue"].iloc[split_point:]
test_dates = df["date"].iloc[split_point:]


def evaluate(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    return round(mae, 2), round(rmse, 2)


results = {}
models = {}

rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)
results["Random Forest"] = evaluate(y_test, rf.predict(X_test))
models["Random Forest"] = rf

try:
    from xgboost import XGBRegressor
    xgb = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42).fit(X_train, y_train)
    results["XGBoost"] = evaluate(y_test, xgb.predict(X_test))
    models["XGBoost"] = xgb
except Exception as e:
    print("XGBoost skip hua:", e)

prophet_future = None
try:
    from prophet import Prophet
    train_p = daily[daily["date"] < test_dates.iloc[0]].rename(columns={"date": "ds", "revenue": "y"})
    m = Prophet().fit(train_p)
    pred = m.predict(pd.DataFrame({"ds": test_dates}))
    results["Prophet"] = evaluate(y_test, pred["yhat"].values)

    m_full = Prophet().fit(daily.rename(columns={"date": "ds", "revenue": "y"}))
    fut = m_full.predict(m_full.make_future_dataframe(periods=30)).tail(30)
    prophet_future = pd.DataFrame({"date": fut["ds"].values,
                                   "predicted_revenue": fut["yhat"].clip(lower=0).values})
except Exception as e:
    print("Prophet skip hua:", e)

comparison = pd.DataFrame(
    [(k, v[0], v[1]) for k, v in results.items()], columns=["model", "MAE", "RMSE"]
).sort_values("MAE").reset_index(drop=True)
print("\nModel comparison (kam = behtar):\n", comparison)
comparison.to_csv(f"{OUT}/model_comparison.csv", index=False)
best_model = comparison.iloc[0]["model"]
print("Best model:", best_model)


def recursive_forecast(model, history, days=30):
    hist = history[["date", "revenue"]].copy()
    out = []
    for _ in range(days):
        nd = hist["date"].max() + pd.Timedelta(days=1)
        r = hist["revenue"].values
        row = pd.DataFrame([{
            "day_of_week": nd.dayofweek, "day_of_month": nd.day, "month": nd.month,
            "revenue_lag_1": r[-1], "revenue_lag_7": r[-7], "revenue_rolling_7": r[-7:].mean(),
        }])[ts_cols]
        p = max(float(model.predict(row)[0]), 0)
        out.append((nd, p))
        hist = pd.concat([hist, pd.DataFrame({"date": [nd], "revenue": [p]})], ignore_index=True)
    return pd.DataFrame(out, columns=["date", "predicted_revenue"])


if best_model == "Prophet" and prophet_future is not None:
    forecast_30 = prophet_future
else:
    if best_model == "Prophet":
        best_model = [k for k in comparison["model"] if k in models][0]
    forecast_30 = recursive_forecast(models[best_model], daily)

forecast_30["predicted_revenue"] = forecast_30["predicted_revenue"].round(2)
forecast_30["date"] = pd.to_datetime(forecast_30["date"]).dt.strftime("%Y-%m-%d")
forecast_30.to_csv(f"{OUT}/forecast_30days.csv", index=False)

forecast_summary = pd.DataFrame({
    "period": ["Next 30 Days"],
    "predicted_revenue": [round(float(forecast_30["predicted_revenue"].sum()), 2)],
    "model_used": [best_model],
})
forecast_summary.to_csv(f"{OUT}/forecast_summary.csv", index=False)
print("\nForecast summary:\n", forecast_summary)

# =============== 4. EXCEL REPORT ===============
with pd.ExcelWriter(f"{OUT}/business_report.xlsx") as writer:
    segment_summary.to_excel(writer, sheet_name="Customer Segments", index=False)
    forecast_summary.to_excel(writer, sheet_name="Sales Forecast", index=False)
    forecast_30.to_excel(writer, sheet_name="Daily Forecast", index=False)
    comparison.to_excel(writer, sheet_name="Model Comparison", index=False)
print("\nReport saved:", f"{OUT}/business_report.xlsx")