"""
MarketMind AI - Milestone 3, Day 9-10: Anomaly Detection
Place in: ml/   (next to segmentation.py, forecasting_*.py)
Run:      python anomaly_detection.py

Input : datasets/processed/sales_data_prepped.csv  (store/product daily records)
Output: ml/outputs/anomaly_comparison.csv  (every row flagged by either method)
        ml/outputs/anomaly_alerts.csv      (alert records, ready to load into a DB table)
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

ML_DIR = Path(__file__).resolve().parent
DATA_FILE = sys.argv[1] if len(sys.argv) > 1 else ML_DIR.parent / "datasets" / "processed" / "sales_data_prepped.csv"
OUT_DIR = ML_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)
Z_THRESHOLD = 3.0        # business judgment call (2.5 = stricter, 3.5 = more lenient)
CONTAMINATION = 0.02     # expected share of anomalies (business judgment call)

# ---------------------------------------------------------------- load + features
df = pd.read_csv(DATA_FILE)
df["Date"] = pd.to_datetime(df["Date"])
df = df.reset_index(drop=True)
df["row_id"] = df.index  # the dataset has no order_id, so row position is the identifier

df["total_amount"] = df["Units Sold"] * df["Price"]                      # revenue per record
df["sell_through"] = df["Units Sold"] / df["Inventory Level"].clip(lower=1)  # share of stock sold

# ---------------------------------------------------------------- approach 1: Z-score (one column)
mean_amt, std_amt = df["total_amount"].mean(), df["total_amount"].std()
df["z_score"] = (df["total_amount"] - mean_amt) / (std_amt if std_amt else 1.0)   # guard against std = 0
df["flag_zscore"] = df["z_score"].abs() > Z_THRESHOLD

# ---------------------------------------------------------------- approach 2: Isolation Forest (many columns)
feature_cols = ["Units Sold", "Inventory Level", "Units Ordered", "Price", "total_amount", "sell_through"]
iso = IsolationForest(contamination=CONTAMINATION, n_estimators=200, random_state=42, n_jobs=-1)
df["iso_label"] = iso.fit_predict(df[feature_cols])          # -1 = anomaly, 1 = normal
df["iso_score"] = -iso.score_samples(df[feature_cols])       # higher = more anomalous
df["flag_iso"] = df["iso_label"] == -1

# ---------------------------------------------------------------- compare the two methods
z_ids, iso_ids = set(df.index[df["flag_zscore"]]), set(df.index[df["flag_iso"]])
both, only_z, only_iso = z_ids & iso_ids, z_ids - iso_ids, iso_ids - z_ids
print(f"Rows analysed            : {len(df):,}")
print(f"Z-score flagged (|z|>{Z_THRESHOLD}) : {len(z_ids):,}")
print(f"Isolation Forest flagged : {len(iso_ids):,}")
print(f"  flagged by both        : {len(both):,}")
print(f"  Z-score only           : {len(only_z):,}")
print(f"  Isolation Forest only  : {len(only_iso):,}")
if iso_ids:
    print(f"  overlap (of IF flags)  : {len(both) / len(iso_ids):.0%}")

flagged = df[df["flag_zscore"] | df["flag_iso"]].copy()
flagged["detected_by"] = np.select(
    [flagged["flag_zscore"] & flagged["flag_iso"], flagged["flag_zscore"]],
    ["both", "zscore_only"], default="isolation_forest_only")
flagged.to_csv(OUT_DIR / "anomaly_comparison.csv", index=False)


# ---------------------------------------------------------------- alerts
def severity(row):
    """high = flagged by both methods, or revenue >5x average; else medium."""
    if row["detected_by"] == "both" or row["total_amount"] > mean_amt * 5:
        return "high"
    return "medium"


def reason(row):
    parts = []
    if row["total_amount"] > mean_amt * 5:
        parts.append(f"revenue Rs {row['total_amount']:.2f} is >5x the average")
    if row["sell_through"] > 0.9:
        parts.append(f"{row['sell_through']:.0%} of stock sold at once")
    if row["Units Ordered"] == 0 and row["Inventory Level"] < df["Inventory Level"].quantile(0.05):
        parts.append("very low stock with no reorder")
    return "; ".join(parts) or "unusual combination of units, price and stock"


def generate_alerts(anomalies_df):
    alerts = []
    for _, r in anomalies_df.iterrows():
        alerts.append({
            "row_id": int(r["row_id"]),
            "date": r["Date"].date(),
            "store_id": r["Store ID"],
            "product_id": r["Product ID"],
            "alert_type": "unusual_sales_activity",
            "severity": severity(r),
            "detected_by": r["detected_by"],
            "z_score": round(float(r["z_score"]), 2),
            "iso_score": round(float(r["iso_score"]), 3),
            "message": (f"{r['Store ID']}/{r['Product ID']} on {r['Date'].date()}: "
                        f"units_sold={r['Units Sold']}, inventory={r['Inventory Level']}, "
                        f"amount=Rs {r['total_amount']:.2f} - {reason(r)}"),
        })
    out = pd.DataFrame(alerts)
    # FIX: rank alerts (high first, then most anomalous first) so the API/dashboard's
    # "top 100" really are the 100 most suspicious, not an arbitrary 100.
    out["_rank"] = out["severity"].map({"high": 0, "medium": 1})
    return (out.sort_values(["_rank", "iso_score"], ascending=[True, False])
               .drop(columns="_rank").reset_index(drop=True))


alerts = generate_alerts(flagged)
alerts.to_csv(OUT_DIR / "anomaly_alerts.csv", index=False)
print(f"\nAlerts generated: {len(alerts):,}  "
      f"(high: {(alerts.severity == 'high').sum():,}, medium: {(alerts.severity == 'medium').sum():,})")
print("\nSample alerts:")
for a in alerts.head(3).to_dict("records"):
    print(a)