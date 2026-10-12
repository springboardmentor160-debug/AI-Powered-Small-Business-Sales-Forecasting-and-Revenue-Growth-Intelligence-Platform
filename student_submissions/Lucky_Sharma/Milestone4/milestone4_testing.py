import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             silhouette_score, accuracy_score, confusion_matrix)
from sklearn.metrics.pairwise import cosine_similarity

OUT = "data/outputs"
os.makedirs(OUT, exist_ok=True)
results = []

sales = pd.read_csv("data/processed/cleaned_sales.csv").dropna(subset=["customer_id"])
sales["order_date"] = pd.to_datetime(sales["order_date"])
sales["quantity"] = sales["quantity"].astype(float)
sales["revenue"] = sales["revenue"].astype(float)

# ============ 1. FORECASTING: MAE, RMSE, R2 ============
daily = sales.groupby("order_date")["revenue"].sum().asfreq("D", fill_value=0).reset_index()
daily.columns = ["date", "revenue"]
d = daily.copy()
d["day_of_week"] = d["date"].dt.dayofweek
d["day_of_month"] = d["date"].dt.day
d["month"] = d["date"].dt.month
d["lag_1"] = d["revenue"].shift(1)
d["lag_7"] = d["revenue"].shift(7)
d["roll_7"] = d["revenue"].shift(1).rolling(7).mean()
d = d.dropna().reset_index(drop=True)
cols = ["day_of_week", "day_of_month", "month", "lag_1", "lag_7", "roll_7"]
sp = int(len(d) * 0.8)
Xtr, Xte = d[cols][:sp], d[cols][sp:]
ytr, yte = d["revenue"][:sp], d["revenue"][sp:]

fmodels = {"Random Forest": RandomForestRegressor(n_estimators=100, random_state=42)}
try:
    from xgboost import XGBRegressor
    fmodels["XGBoost"] = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
except Exception:
    pass
for name, m in fmodels.items():
    p = m.fit(Xtr, ytr).predict(Xte)
    results.append(("Forecasting - " + name, "MAE", round(mean_absolute_error(yte, p), 2)))
    results.append(("Forecasting - " + name, "RMSE", round(float(np.sqrt(mean_squared_error(yte, p))), 2)))
    results.append(("Forecasting - " + name, "R2", round(r2_score(yte, p), 3)))

# ============ 2. SEGMENTATION: Silhouette ============
ref = sales["order_date"].max() + pd.Timedelta(days=1)
cf = sales.groupby("customer_id").agg(freq=("order_id", "nunique"),
                                      value=("revenue", "mean"),
                                      last=("order_date", "max")).reset_index()
cf["activity"] = (ref - cf["last"]).dt.days
Xs = StandardScaler().fit_transform(cf[["freq", "value", "activity"]])
labels = KMeans(n_clusters=4, random_state=42, n_init=10).fit_predict(Xs)
results.append(("Segmentation - K-Means (K=4)", "Silhouette Score", round(silhouette_score(Xs, labels), 3)))

# ============ 3. CHURN: Accuracy, Precision, Recall, F1 (Milestone 3 ka result) ============
cp = f"{OUT}/churn_model_comparison.csv"
if os.path.exists(cp):
    for _, r in pd.read_csv(cp).iterrows():
        for met in ["accuracy", "precision", "recall", "f1"]:
            results.append(("Churn - " + r["model"], met, r[met]))

# ============ 4. RECOMMENDATION: Precision@K, Recall@K ============
full = sales.pivot_table(index="customer_id", columns="product_name",
                         values="quantity", aggfunc="sum", fill_value=0)
train = full.copy()
held = {}
rng = np.random.default_rng(42)
for cid in full.index:
    bought = full.columns[full.loc[cid] > 0].tolist()
    if len(bought) >= 4:
        k = max(1, len(bought) // 5)
        h = list(rng.choice(bought, size=k, replace=False))
        train.loc[cid, h] = 0
        held[cid] = set(h)
sim = pd.DataFrame(cosine_similarity(train), index=train.index, columns=train.index)
K = 5
precs, recs = [], []
for cid, hidden in held.items():
    sims = sim[cid].drop(cid).sort_values(ascending=False).head(10)
    scores = train.loc[sims.index].mul(sims, axis=0).sum()
    scores = scores[train.loc[cid] == 0]
    top = set(scores[scores > 0].sort_values(ascending=False).head(K).index)
    hits = len(top & hidden)
    precs.append(hits / K)
    recs.append(hits / len(hidden))
results.append((f"Recommendation (K={K})", "Precision@K", round(float(np.mean(precs)), 3)))
results.append((f"Recommendation (K={K})", "Recall@K", round(float(np.mean(recs)), 3)))

# ============ 5. ANOMALY: Detection Accuracy, False Positive Rate ============
# Labels nahi hain, isliye 20 nakli anomalies khud daalte hain aur dekhte hain ki model unhe pakadta hai ya nahi
a = sales.copy().reset_index(drop=True)
idx = np.random.default_rng(42).choice(len(a), size=20, replace=False)
a["is_anomaly"] = 0
a.loc[idx, "is_anomaly"] = 1
a.loc[idx, "quantity"] = a.loc[idx, "quantity"] * 15
a["revenue"] = a["quantity"] * a["unit_price"]
pred = (IsolationForest(contamination=0.02, random_state=42)
        .fit_predict(a[["quantity", "unit_price", "revenue"]]) == -1).astype(int)
tn, fp, fn, tp = confusion_matrix(a["is_anomaly"], pred).ravel()
results.append(("Anomaly - Isolation Forest", "Detection Accuracy", round(accuracy_score(a["is_anomaly"], pred), 3)))
results.append(("Anomaly - Isolation Forest", "Detection Rate (caught/20)", round(tp / 20, 3)))
results.append(("Anomaly - Isolation Forest", "False Positive Rate", round(fp / (fp + tn), 3)))

# ============ SAVE ============
res = pd.DataFrame(results, columns=["Module", "Metric", "Value"])
print(res.to_string(index=False))
res.to_csv(f"{OUT}/model_test_results.csv", index=False)
res.to_excel(f"{OUT}/model_test_results.xlsx", index=False)
print("\nSaved: data/outputs/model_test_results.xlsx")