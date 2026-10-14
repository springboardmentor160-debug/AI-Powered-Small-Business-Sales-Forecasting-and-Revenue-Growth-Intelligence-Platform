"""
MarketMind AI - Milestone 4, Day 1-4: formal testing of every AI module
Place in: ml/      (needs churn_setup.py in the same folder)
Run:      python milestone4_testing.py
Writes:   ml/outputs/milestone4_test_results.csv

Tests, using the metrics from the project document:
  Sales Forecasting   MAE, RMSE, R2 (test + train, overfitting check)
  Segmentation        Silhouette score (K-Means, Hierarchical, plus k=2..6 sweep)
  Churn Prediction    Accuracy, Precision, Recall, F1 (all three models)
  Recommendations     Precision@K / Recall@K on a real time-based holdout
  Anomaly Detection   Detection rate, precision, false-positive rate on INJECTED anomalies
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error, mean_squared_error,
                             precision_score, r2_score, recall_score, silhouette_score)
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier, XGBRegressor

from churn_setup import FEATURE_COLS, build_churn_dataset, get_train_test, load_orders

ML_DIR = Path(__file__).resolve().parent
DATA_DIR = ML_DIR.parent / "datasets" / "processed"
OUT_DIR = ML_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)
results = []


def record(module, metric, value):
    results.append({"module": module, "metric": metric, "value": round(float(value), 4)})


# ======================================================================= 1. FORECASTING
print("=== 1. Sales forecasting (daily demand, last 90 days held out) ===")
sales = pd.read_csv(DATA_DIR / "sales_data_prepped.csv", parse_dates=["Date"])
daily = sales.groupby("Date")["Demand"].sum().sort_index().reset_index()
daily.columns = ["ds", "y"]
daily["day_of_week"], daily["month"], daily["day_of_year"] = daily.ds.dt.dayofweek, daily.ds.dt.month, daily.ds.dt.dayofyear
daily["lag_1"], daily["lag_7"] = daily.y.shift(1), daily.y.shift(7)
daily["rolling_mean_7"] = daily.y.shift(1).rolling(7).mean()
daily = daily.dropna().reset_index(drop=True)
F = ["day_of_week", "month", "day_of_year", "lag_1", "lag_7", "rolling_mean_7"]
train, test = daily.iloc[:-90], daily.iloc[-90:]


def forecast_metrics(name, yt, yp, train_r2=None):
    mae, rmse, r2 = mean_absolute_error(yt, yp), np.sqrt(mean_squared_error(yt, yp)), r2_score(yt, yp)
    extra = f"  train R2={train_r2:.3f}" if train_r2 is not None else ""
    print(f"{name:34s} MAE={mae:9.2f} RMSE={rmse:9.2f} R2={r2:6.3f}{extra}")
    for m, v in (("MAE", mae), ("RMSE", rmse), ("R2 Score", r2)):
        record(f"Sales Forecasting ({name})", m, v)
    if train_r2 is not None:
        record(f"Sales Forecasting ({name})", "R2 Score (train)", train_r2)


models = {"Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
          "XGBoost": XGBRegressor(n_estimators=200, random_state=42)}
for name, m in models.items():
    m.fit(train[F], train["y"])
    forecast_metrics(f"{name}, 1-day-ahead", test["y"], m.predict(test[F]), r2_score(train["y"], m.predict(train[F])))

# honest long-horizon test: no real lag values, each prediction feeds the next day
hist, rec = list(train["y"]), []
for d in test["ds"]:
    row = pd.DataFrame([{"day_of_week": d.dayofweek, "month": d.month, "day_of_year": d.dayofyear,
                         "lag_1": hist[-1], "lag_7": hist[-7], "rolling_mean_7": np.mean(hist[-7:])}])[F]
    p = float(models["XGBoost"].predict(row)[0]); rec.append(p); hist.append(p)
forecast_metrics("XGBoost, 90-day recursive", test["y"], rec)
try:
    from prophet import Prophet
    pm = Prophet().fit(train[["ds", "y"]])
    forecast_metrics("Prophet", test["y"], pm.predict(test[["ds"]])["yhat"].values)
except Exception as e:  # prophet not installed / failed: skip, don't block the rest
    print(f"(Prophet skipped: {type(e).__name__})")

# ======================================================================= 2. SEGMENTATION
print("\n=== 2. Customer segmentation (same preprocessing as segmentation.py) ===")
od = pd.read_csv(DATA_DIR / "online_retail_prepped.csv", parse_dates=["InvoiceDate"])
cf = od.groupby("CustomerID").agg(purchase_frequency=("InvoiceNo", "nunique"),
                                  purchase_value=("TotalAmount", "mean"),
                                  last=("InvoiceDate", "max")).reset_index()
cf["recency_days"] = (od["InvoiceDate"].max() - cf["last"]).dt.days
cf = cf[cf["purchase_value"] <= cf["purchase_value"].quantile(0.99)]
Xs = StandardScaler().fit_transform(cf[["purchase_frequency", "purchase_value", "recency_days"]])
km_sil = silhouette_score(Xs, KMeans(4, random_state=42, n_init=10).fit_predict(Xs))
hc_sil = silhouette_score(Xs, AgglomerativeClustering(4).fit_predict(Xs))
print(f"K-Means (k=4)      silhouette = {km_sil:.3f}")
print(f"Hierarchical (k=4) silhouette = {hc_sil:.3f}")
record("Customer Segmentation (K-Means)", "Silhouette Score", km_sil)
record("Customer Segmentation (Hierarchical)", "Silhouette Score", hc_sil)
print("K-Means silhouette by k: ", end="")
for k in range(2, 7):
    s = silhouette_score(Xs, KMeans(k, random_state=42, n_init=10).fit_predict(Xs))
    print(f"k={k}: {s:.3f}  ", end="")
    record("Customer Segmentation (K-Means sweep)", f"Silhouette k={k}", s)
print()

# ======================================================================= 3. CHURN
print("\n=== 3. Churn prediction (held-out 20% test set) ===")
feats, orders, cutoff, end_date = build_churn_dataset()
X_train, X_test, y_train, y_test = get_train_test(feats)
sc = StandardScaler()
fitted = {
    "Logistic Regression": (LogisticRegression(random_state=42).fit(sc.fit_transform(X_train), y_train), True),
    "Random Forest": (RandomForestClassifier(n_estimators=100, random_state=42).fit(X_train, y_train), False),
    "XGBoost": (XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42).fit(X_train, y_train), False),
}
print(f"churn rate {y_test.mean():.1%}; always-predict-0 accuracy would be {1 - y_test.mean():.1%}")
for name, (m, scaled) in fitted.items():
    pred = m.predict(sc.transform(X_test) if scaled else X_test)
    a, p, r, f = (accuracy_score(y_test, pred), precision_score(y_test, pred),
                  recall_score(y_test, pred), f1_score(y_test, pred))
    print(f"{name:20s} Accuracy={a:.2f} Precision={p:.2f} Recall={r:.2f} F1={f:.2f}")
    for mt, v in (("Accuracy", a), ("Precision", p), ("Recall", r), ("F1-Score", f)):
        record(f"Churn Prediction ({name})", mt, v)

# ======================================================================= 4. RECOMMENDATIONS
print("\n=== 4. Recommendations: Precision@K / Recall@K (time-based holdout) ===")
od["Description"] = od["Description"].str.strip()
before, after = od[od.InvoiceDate < cutoff], od[od.InvoiceDate >= cutoff]
M = before.pivot_table(index="CustomerID", columns="Description", values="Quantity", aggfunc="sum", fill_value=0)
future = after.groupby("CustomerID")["Description"].apply(set)
products = M.columns.to_numpy()
vals = M.values
sim = cosine_similarity(M)
np.fill_diagonal(sim, -1)
popularity = (vals > 0).sum(axis=0).astype(float)
eligible = []
for i, cid in enumerate(M.index):
    if cid in future.index:
        new = future[cid] - set(products[vals[i] > 0])         # only count products they hadn't bought before
        if new:
            eligible.append((i, new))
print(f"{len(eligible):,} customers bought at least one NEW product after the cutoff (evaluated)")


def at_k(score_fn, k):
    p, r = [], []
    for i, new in eligible:
        score = score_fn(i)
        score[vals[i] > 0] = -1
        top = {products[j] for j in np.argsort(score)[::-1][:k]}
        hits = len(top & new)
        p.append(hits / k); r.append(hits / len(new))
    return np.mean(p), np.mean(r)


cf_score = lambda i: vals[np.argpartition(sim[i], -5)[-5:]].sum(axis=0).astype(float)
pop_score = lambda i: popularity.copy()
for k in (3, 5):
    for label, fn in (("Collaborative Filtering", cf_score), ("Popularity baseline", pop_score)):
        p, r = at_k(fn, k)
        print(f"{label:24s} Precision@{k}={p:.3f}  Recall@{k}={r:.3f}")
        record(f"Recommendation System ({label})", f"Precision@{k}", p)
        record(f"Recommendation System ({label})", f"Recall@{k}", r)

# ======================================================================= 5. ANOMALY DETECTION
print("\n=== 5. Anomaly detection (Isolation Forest, contamination=0.02, injected anomalies) ===")
rng = np.random.default_rng(42)
data = sales.copy().reset_index(drop=True)
data["is_anomaly"] = 0
data["kind"] = "normal"
n_each = 50
picks = rng.choice(len(data), size=3 * n_each, replace=False)
spike, price, vanish = picks[:n_each], picks[n_each:2 * n_each], picks[2 * n_each:]
data.loc[spike, "Units Sold"] = (data["Units Sold"].max() * 3)                        # absurd volume
data.loc[price, "Price"] = data["Price"].max() * 6                                    # pricing error
data.loc[vanish, ["Inventory Level", "Units Ordered"]] = [2, 0]                       # stock nearly gone, no reorder
for idx, kind in ((spike, "volume spike"), (price, "price error"), (vanish, "stock vanished")):
    data.loc[idx, ["is_anomaly", "kind"]] = [1, kind]
data["total_amount"] = data["Units Sold"] * data["Price"]
data["sell_through"] = data["Units Sold"] / data["Inventory Level"].clip(lower=1)
AF = ["Units Sold", "Inventory Level", "Units Ordered", "Price", "total_amount", "sell_through"]
pred = (IsolationForest(contamination=0.02, n_estimators=200, random_state=42, n_jobs=-1)
        .fit_predict(data[AF]) == -1).astype(int)
y = data["is_anomaly"].values
tp, fp = ((pred == 1) & (y == 1)).sum(), ((pred == 1) & (y == 0)).sum()
fn, tn = ((pred == 0) & (y == 1)).sum(), ((pred == 0) & (y == 0)).sum()
det_rate, precision, fpr, acc = tp / (tp + fn), tp / max(tp + fp, 1), fp / (fp + tn), (tp + tn) / len(y)
print(f"{len(data):,} rows, {y.sum()} injected anomalies ({y.mean():.2%}); flagged {pred.sum():,}")
print(f"Detection rate (recall) = {det_rate:.1%}   Precision = {precision:.1%}   "
      f"False-positive rate = {fpr:.2%}   Accuracy = {acc:.2%}")
for kind in ("volume spike", "price error", "stock vanished"):
    m = data["kind"].values == kind
    print(f"  caught {kind:15s}: {pred[m].mean():.0%}")
    record("Anomaly Detection (Isolation Forest)", f"Detection rate - {kind}", pred[m].mean())
for mt, v in (("Detection Rate", det_rate), ("Precision", precision),
              ("False Positive Rate", fpr), ("Detection Accuracy", acc)):
    record("Anomaly Detection (Isolation Forest)", mt, v)

# ======================================================================= save record
full = pd.DataFrame(results)
full.to_csv(OUT_DIR / "milestone4_test_results.csv", index=False)
print(f"\nSaved {len(full)} results -> {OUT_DIR / 'milestone4_test_results.csv'}")