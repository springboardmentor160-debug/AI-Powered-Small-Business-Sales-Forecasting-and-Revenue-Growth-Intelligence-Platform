
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# --------------------------------------------------
# 1. Load and validate sales data
# --------------------------------------------------

DATA_PATH = os.path.join("data", "clean_retail_sales.csv")
OUTPUT_PATH = os.path.join("data", "transaction_anomalies.csv")
ALERTS_PATH = os.path.join("data", "fraud_alerts.csv")

os.makedirs("data", exist_ok=True)

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}. "
        "Run this script from your Marketmind_Ai project folder."
    )

df = pd.read_csv(DATA_PATH)

required_columns = [
    "InvoiceNo",
    "Quantity",
    "UnitPrice",
    "InvoiceDate"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)

# Remove invalid records, cancellations and non-positive sales
df = df.dropna(
    subset=["InvoiceNo", "Quantity", "UnitPrice", "InvoiceDate"]
)

df = df[
    ~df["InvoiceNo"].str.startswith("C", na=False)
    & (df["Quantity"] > 0)
    & (df["UnitPrice"] > 0)
].copy()

df["total_amount"] = df["Quantity"] * df["UnitPrice"]

print("Sales dataset loaded successfully.")
print(f"Valid sales lines: {len(df):,}")

# --------------------------------------------------
# 2. Aggregate line items into individual orders
# --------------------------------------------------

orders = (
    df.groupby("InvoiceNo", as_index=False)
    .agg(
        InvoiceDate=("InvoiceDate", "min"),
        Quantity=("Quantity", "sum"),
        UnitPrice=("UnitPrice", "mean"),
        total_amount=("total_amount", "sum")
    )
)

orders = orders.rename(columns={"InvoiceNo": "order_id"})
orders = orders.replace([np.inf, -np.inf], np.nan)
orders = orders.dropna(
    subset=["Quantity", "UnitPrice", "total_amount"]
).reset_index(drop=True)

if len(orders) < 3:
    raise ValueError("Not enough valid orders for anomaly detection.")

print(f"Individual orders analyzed: {len(orders):,}")

# --------------------------------------------------
# 3. Z-score anomaly detection on order amounts
# --------------------------------------------------

amount_mean = orders["total_amount"].mean()
amount_std = orders["total_amount"].std(ddof=0)

if amount_std > 0:
    orders["amount_z_score"] = (
        (orders["total_amount"] - amount_mean) / amount_std
    )
else:
    orders["amount_z_score"] = 0.0

orders["zscore_anomaly"] = (
    orders["amount_z_score"].abs() > 3
)

# --------------------------------------------------
# 4. Isolation Forest on multiple order features
# --------------------------------------------------

features = ["Quantity", "UnitPrice", "total_amount"]
X = orders[features].astype(float)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

isolation_forest = IsolationForest(
    n_estimators=100,
    contamination=0.02,
    random_state=42,
    n_jobs=-1
)

orders["isolation_forest_anomaly"] = (
    isolation_forest.fit_predict(X_scaled) == -1
)

orders["anomaly_score"] = -isolation_forest.score_samples(
    X_scaled
)

# Flag an order if either method detects an anomaly
orders["is_anomaly"] = (
    orders["zscore_anomaly"]
    | orders["isolation_forest_anomaly"]
)

# --------------------------------------------------
# 5. Generate actionable alerts
# --------------------------------------------------

def build_alert(row):
    methods = []

    if row["zscore_anomaly"]:
        methods.append("Z-score")

    if row["isolation_forest_anomaly"]:
        methods.append("Isolation Forest")

    return ", ".join(methods)


orders["detection_method"] = orders.apply(build_alert, axis=1)

orders["alert_type"] = np.where(
    orders["is_anomaly"],
    "unusual_sales_activity",
    "normal"
)

orders["severity"] = np.where(
    orders["is_anomaly"]
    & (
        (orders["total_amount"] > amount_mean * 5)
        | (orders["amount_z_score"] > 5)
    ),
    "high",
    np.where(orders["is_anomaly"], "medium", "none")
)

def build_message(row):
    if not row["is_anomaly"]:
        return "No anomaly detected."

    return (
        f"Unusual order detected. Quantity: {row['Quantity']:.0f}, "
        f"average unit price: {row['UnitPrice']:.2f}, "
        f"order amount: {row['total_amount']:.2f}. "
        f"Detected by: {row['detection_method']}. "
        "Review this order before taking action."
    )


orders["message"] = orders.apply(build_message, axis=1)

# --------------------------------------------------
# 6. Save complete results and alert report
# --------------------------------------------------

orders.to_csv(OUTPUT_PATH, index=False)

alert_columns = [
    "order_id",
    "InvoiceDate",
    "alert_type",
    "message",
    "severity",
    "Quantity",
    "UnitPrice",
    "total_amount",
    "amount_z_score",
    "anomaly_score",
    "detection_method"
]

alerts = orders.loc[
    orders["is_anomaly"], alert_columns
].copy()

alerts = alerts.sort_values(
    by=["severity", "anomaly_score"],
    ascending=[True, False]
)

alerts.to_csv(ALERTS_PATH, index=False)

# --------------------------------------------------
# 7. Display summary
# --------------------------------------------------

print("\n" + "=" * 55)
print("ORDER-LEVEL ANOMALY DETECTION SUMMARY")
print("=" * 55)

print(f"Total orders analyzed: {len(orders):,}")
print(f"Z-score anomalies: {orders['zscore_anomaly'].sum():,}")
print(
    "Isolation Forest anomalies: "
    f"{orders['isolation_forest_anomaly'].sum():,}"
)
print(f"Orders flagged by either method: {len(alerts):,}")
print(f"High-severity alerts: {(alerts['severity'] == 'high').sum():,}")
print(
    f"Medium-severity alerts: "
    f"{(alerts['severity'] == 'medium').sum():,}"
)

if not alerts.empty:
    print("\nTop flagged orders:")
    print(
        alerts[
            ["order_id", "total_amount", "severity", "detection_method"]
        ].head(10).to_string(index=False)
    )

print(f"\nComplete results saved to: {OUTPUT_PATH}")
print(f"Actionable alerts saved to: {ALERTS_PATH}")
print("\nAnomaly detection completed successfully.")
