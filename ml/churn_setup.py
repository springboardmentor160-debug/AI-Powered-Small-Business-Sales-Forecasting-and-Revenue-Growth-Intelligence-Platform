"""
MarketMind AI - Milestone 3, Day 5-6: Churn Prediction Setup
Place in: ml/   (next to segmentation.py)
Run:      python churn_setup.py

Builds the churn dataset, defines the churn label, and trains the Logistic
Regression baseline. churn_models.py (Day 7-8) imports from this file.

WHY THE LABEL IS BUILT DIFFERENTLY FROM THE HANDOUT
The handout computes inactivity days up to "today" and labels churn as
inactivity > 90, then ALSO feeds inactivity days to the model as a feature.
That lets the model read the answer straight off a column (data leakage), and
on this 2010-2011 dataset `datetime.now()` would mark every customer as churned.
Instead we:
  1. pick a cutoff date = (last date in data) - CHURN_DAYS
  2. build features ONLY from purchases before the cutoff
  3. label a customer churned if they made NO purchase in the CHURN_DAYS after it
So the model learns to predict the future from the past, which is the real task.
"""
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ML_DIR = Path(__file__).resolve().parent
DATA_FILE = ML_DIR.parent / "datasets" / "processed" / "online_retail_prepped.csv"

CHURN_DAYS = 90          # business decision; practice task: try 60
FEATURE_COLS = ["order_frequency", "purchase_inactivity_days", "avg_order_value"]


def load_orders():
    """One row per invoice: CustomerID, InvoiceDate, order_total."""
    df = pd.read_csv(DATA_FILE, usecols=["InvoiceNo", "InvoiceDate", "CustomerID", "TotalAmount"],
                     parse_dates=["InvoiceDate"])
    return (df.groupby(["CustomerID", "InvoiceNo"])
              .agg(InvoiceDate=("InvoiceDate", "max"), order_total=("TotalAmount", "sum"))
              .reset_index())


def build_features(orders, as_of):
    """Customer features using only orders placed before `as_of`."""
    past = orders[orders["InvoiceDate"] < as_of]
    feats = past.groupby("CustomerID").agg(
        order_frequency=("InvoiceNo", "nunique"),
        last_purchase_date=("InvoiceDate", "max"),
        avg_order_value=("order_total", "mean"),
    ).reset_index()
    feats["purchase_inactivity_days"] = (as_of - feats["last_purchase_date"]).dt.days
    return feats.drop(columns="last_purchase_date")


def build_churn_dataset(churn_days=CHURN_DAYS):
    orders = load_orders()
    end_date = orders["InvoiceDate"].max()
    cutoff = end_date - pd.Timedelta(days=churn_days)

    feats = build_features(orders, cutoff)
    future_buyers = set(orders.loc[orders["InvoiceDate"] >= cutoff, "CustomerID"])
    feats["churned"] = (~feats["CustomerID"].isin(future_buyers)).astype(int)  # 1 = churned
    return feats, orders, cutoff, end_date


def get_train_test(feats):
    X, y = feats[FEATURE_COLS], feats["churned"]
    # stratify=y keeps the churn share the same in train and test
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


if __name__ == "__main__":
    feats, orders, cutoff, end_date = build_churn_dataset()
    print(f"Data runs to {end_date.date()}; cutoff = {cutoff.date()} "
          f"(features from before it, churn = no purchase in the next {CHURN_DAYS} days)")
    print(f"Customers with history before cutoff: {len(feats):,}\n")

    counts = feats["churned"].value_counts().sort_index()
    print("Churn label counts (0 = active, 1 = churned):")
    print(counts.to_string())
    churn_rate = feats["churned"].mean()
    print(f"Churn rate: {churn_rate:.1%}\n")

    X_train, X_test, y_train, y_test = get_train_test(feats)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    log_model = LogisticRegression(random_state=42)
    log_model.fit(X_train_scaled, y_train)
    log_predictions = log_model.predict(X_test_scaled)
    print("First 10 predictions:", log_predictions[:10])

    accuracy = accuracy_score(y_test, log_predictions)
    lazy_accuracy = 1 - y_test.mean()   # accuracy of always predicting "not churned"
    print(f"\nLogistic Regression accuracy : {accuracy:.2%}")
    print(f"'Lazy' always-predict-0 model : {lazy_accuracy:.2%}")
    print("Accuracy alone can hide a weak model; Day 7-8 uses Precision/Recall/F1.")