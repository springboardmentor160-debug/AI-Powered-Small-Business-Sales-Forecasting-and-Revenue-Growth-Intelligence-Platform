"""
MarketMind AI - Milestone 2, Day 9-10: Reporting
Place in: ml/   (next to segmentation.py and forecasting_models.py)
Run:      python generate_reports.py

Reads : ml/segment_assignments.csv                   (from segmentation.py)
        datasets/processed/sales_data_prepped.csv    (operations data)
Writes: ml/outputs/segment_summary.json   -> served by GET /segments
        ml/outputs/forecast_summary.json  -> served by GET /forecast/revenue
        ml/outputs/business_report.xlsx   -> downloadable report

Re-run this script whenever the data or models change; the API just reads the files.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

ML_DIR = Path(__file__).resolve().parent
SEGMENTS_CSV = ML_DIR / "segment_assignments.csv"
SALES_CSV = ML_DIR.parent / "datasets" / "processed" / "sales_data_prepped.csv"
OUT_DIR = ML_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)
HORIZON = 30

# ------------------------------------------------------------------ 1. segment summary
seg = pd.read_csv(SEGMENTS_CSV)
# segmentation.py's output column names weren't fixed in advance, so detect them
seg_col = next(c for c in seg.columns if "segment" in c.lower())
val_col = next((c for c in seg.columns if "purchase_value" in c.lower()), None)
id_col = next(c for c in seg.columns if "customer" in c.lower() and "id" in c.lower())

agg = {"customer_count": (id_col, "count")}
if val_col:
    agg["avg_purchase_value"] = (val_col, "mean")
segment_summary = seg.groupby(seg_col).agg(**agg).reset_index().rename(columns={seg_col: "segment"})
if "avg_purchase_value" in segment_summary:
    segment_summary["avg_purchase_value"] = segment_summary["avg_purchase_value"].round(2)
segment_summary = segment_summary.sort_values("customer_count", ascending=False)
print(segment_summary.to_string(index=False))

# ------------------------------------------------------------------ 2. 30-day revenue forecast
sales = pd.read_csv(SALES_CSV)
sales["Date"] = pd.to_datetime(sales["Date"])
sales["revenue"] = sales["Units Sold"] * sales["Price"]          # rupees, not units
daily = sales.groupby("Date")["revenue"].sum().sort_index().reset_index()
daily.columns = ["ds", "y"]


def add_features(d):
    d = d.copy()
    d["day_of_week"], d["month"], d["day_of_year"] = d.ds.dt.dayofweek, d.ds.dt.month, d.ds.dt.dayofyear
    d["lag_1"], d["lag_7"] = d.y.shift(1), d.y.shift(7)
    d["rolling_mean_7"] = d.y.shift(1).rolling(7).mean()
    return d.dropna().reset_index(drop=True)


FEATURES = ["day_of_week", "month", "day_of_year", "lag_1", "lag_7", "rolling_mean_7"]
train = add_features(daily)
model = XGBRegressor(n_estimators=200, learning_rate=0.1, random_state=42)
model.fit(train[FEATURES], train["y"])      # refit on ALL available history

# Recursive forecast: each predicted day becomes the lag for the next, so no
# real future values are needed (this is a true forecast, not a test-set replay).
history = list(daily["y"])
future_dates = pd.date_range(daily["ds"].max() + pd.Timedelta(days=1), periods=HORIZON)
preds = []
for d in future_dates:
    row = pd.DataFrame([{
        "day_of_week": d.dayofweek, "month": d.month, "day_of_year": d.dayofyear,
        "lag_1": history[-1], "lag_7": history[-7], "rolling_mean_7": np.mean(history[-7:]),
    }])[FEATURES]
    p = float(model.predict(row)[0])
    preds.append(p)
    history.append(p)

forecast_summary = {
    "period": f"Next {HORIZON} Days",
    "start_date": str(future_dates[0].date()),
    "end_date": str(future_dates[-1].date()),
    "predicted_revenue": round(sum(preds), 2),
    "model_used": "XGBoost Regressor",
}
daily_forecast = pd.DataFrame({"date": future_dates.date, "predicted_revenue": np.round(preds, 2)})
print("\n", forecast_summary)

# ------------------------------------------------------------------ 3. save for API + Excel report
(OUT_DIR / "segment_summary.json").write_text(json.dumps(segment_summary.to_dict(orient="records"), indent=2))
(OUT_DIR / "forecast_summary.json").write_text(json.dumps(forecast_summary, indent=2))

with pd.ExcelWriter(OUT_DIR / "business_report.xlsx") as writer:
    segment_summary.to_excel(writer, sheet_name="Customer Segments", index=False)
    pd.DataFrame([forecast_summary]).to_excel(writer, sheet_name="Sales Forecast", index=False)
    daily_forecast.to_excel(writer, sheet_name="Daily Forecast", index=False)
print(f"\nSaved to {OUT_DIR}: segment_summary.json, forecast_summary.json, business_report.xlsx")