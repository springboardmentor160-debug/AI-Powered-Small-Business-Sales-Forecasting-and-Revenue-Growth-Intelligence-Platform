"""M2: Random Forest + XGBoost (+ Prophet, + baselines) compared on one time-ordered holdout (MAE / RMSE / MAPE / R2).

Method
  1. Aggregate store sales to daily revenue and fill any missing calendar day (linear interpolation, count reported).
  2. Build features row by row from ONLY the history before that day (lags, rolling means) -> no future-data leakage by construction.
  3. Time-based split: the last 20% of calendar days are the test window; every model trains on days strictly before it.
  4. Report each model on the same test days, pick the best ML model by RMSE, refit it on all data, forecast 30 days recursively.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from common import OUT, SEED, load_json, load_sales, make_regressor, save_json

FEATURES = ["day_of_week", "day_of_month", "month", "is_weekend", "revenue_lag_1", "revenue_lag_7", "revenue_lag_14",
            "revenue_rolling_7", "revenue_rolling_30"]
WARMUP = 30            # first 30 days have no full rolling window -> not used as training rows
TEST_FRACTION = 0.2


def daily_revenue(return_info=False):
    """Daily revenue with a continuous calendar (missing dates are interpolated and counted)."""
    s = load_sales().groupby("date")["revenue"].sum()
    full = pd.date_range(s.index.min(), s.index.max(), freq="D")
    n_missing = len(full.difference(s.index))
    s = s.reindex(full).interpolate(method="linear").rename_axis("date").reset_index()
    return (s, {"days": len(s), "missing_days_filled": n_missing}) if return_info else s


def feature_row(hist, d):
    """Features for day `d` given ONLY the earlier revenues `hist` (list/array, oldest first)."""
    h = np.asarray(hist, dtype=float)
    return {"day_of_week": d.dayofweek, "day_of_month": d.day, "month": d.month, "is_weekend": int(d.dayofweek >= 5),
            "revenue_lag_1": h[-1], "revenue_lag_7": h[-7], "revenue_lag_14": h[-14],
            "revenue_rolling_7": h[-7:].mean(), "revenue_rolling_30": h[-30:].mean()}


def build_features(daily):
    rev, dates = daily["revenue"].values, daily["date"]
    rows = [{"date": dates[i], "revenue": rev[i], **feature_row(rev[:i], dates[i])} for i in range(WARMUP, len(daily))]
    return pd.DataFrame(rows)


def test_window(daily):
    """First day of the holdout = last 20% of the calendar."""
    n_test = int(round(len(daily) * TEST_FRACTION))
    return daily["date"].iloc[len(daily) - n_test], n_test


def evaluate(name, actual, pred):
    actual, pred = np.asarray(actual, float), np.asarray(pred, float)
    nz = actual != 0
    return {"model": name, "mae": float(mean_absolute_error(actual, pred)),
            "rmse": float(np.sqrt(mean_squared_error(actual, pred))),
            "mape": float(np.mean(np.abs((actual[nz] - pred[nz]) / actual[nz])) * 100),
            "r2": float(r2_score(actual, pred))}


def recursive_forecast(model, daily, days=30, band=None):
    """Forecast `days` ahead, feeding each prediction back in as the next day's lag. `band` = +/- width (approx. 95%)."""
    hist = list(daily["revenue"].values)
    last = daily["date"].iloc[-1]
    out = []
    for k in range(1, days + 1):
        d = last + pd.Timedelta(days=k)
        p = float(model.predict(pd.DataFrame([feature_row(hist, d)])[FEATURES])[0])
        hist.append(p)
        row = {"date": d.strftime("%Y-%m-%d"), "revenue": round(p, 2)}
        if band:
            row["lower"], row["upper"] = round(p - band, 2), round(p + band, 2)
        out.append(row)
    return out


def fit_best(daily):
    """Returns (results, best_name, final_model_refit_on_all_data, info)."""
    feats = build_features(daily)
    test_start, n_test = test_window(daily)
    tr, te = feats[feats["date"] < test_start], feats[feats["date"] >= test_start]
    Xtr, Xte, ytr, yte = tr[FEATURES], te[FEATURES], tr["revenue"], te["revenue"]
    rf = RandomForestRegressor(n_estimators=200, random_state=SEED, n_jobs=-1).fit(Xtr, ytr)
    xgb, xgb_name = make_regressor()
    xgb.fit(Xtr, ytr)
    results = [evaluate("Random Forest", yte, rf.predict(Xte)), evaluate(xgb_name, yte, xgb.predict(Xte))]
    models_only = list(results)
    baselines = [evaluate("Baseline: same weekday last week", yte, Xte["revenue_lag_7"]),
                 evaluate("Baseline: training-period mean", yte, np.full(len(yte), ytr.mean()))]
    prophet = load_json("prophet_metrics.json")
    if prophet and prophet.get("test_start") == str(test_start.date()):
        results.append({k: prophet.get(k) for k in ("model", "mae", "rmse", "mape", "r2")})
    elif prophet:
        print("prophet_metrics.json uses a different test window - re-run forecasting_prophet.py; Prophet omitted from the comparison")
    results += baselines
    best = min(models_only, key=lambda r: r["rmse"])["model"]
    proto = rf if best == "Random Forest" else xgb
    final = proto.__class__(**proto.get_params())
    final.fit(feats[FEATURES], feats["revenue"])
    info = {"train_start": str(feats["date"].min().date()), "train_end": str((test_start - pd.Timedelta(days=1)).date()),
            "test_start": str(test_start.date()), "test_end": str(daily["date"].max().date()), "test_days": int(n_test),
            "train_rows": int(len(tr)), "features": FEATURES,
            "beaten_by_baseline": [b["model"] for b in baselines if b["rmse"] <= min(r["rmse"] for r in models_only)]}
    return results, best, final, info


def main():
    daily, d_info = daily_revenue(return_info=True)
    results, best, _, info = fit_best(daily)
    res = pd.DataFrame(results).round(3)
    res.to_csv(OUT / "model_comparison.csv", index=False)
    save_json("forecast_model_comparison.json", {"results": results, "best_model": best, "evaluation": {**d_info, **info}})
    print(res.to_string(index=False))
    print("Best ML model (by RMSE):", best)
    if info["beaten_by_baseline"]:
        print("NOTE: no ML model beats these baselines:", info["beaten_by_baseline"], "- the data has little learnable signal.")


if __name__ == "__main__":
    main()
