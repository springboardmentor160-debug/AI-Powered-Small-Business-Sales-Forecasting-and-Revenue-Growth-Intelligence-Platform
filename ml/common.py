"""Shared helpers for the ML scripts (paths, data loading, feature engineering, model fallbacks)."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "datasets" / "processed"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
SEED = 42


def load_online():
    return pd.read_csv(PROC / "online_retail_prepped.csv", parse_dates=["InvoiceDate"],
                       dtype={"CustomerID": str, "StockCode": str})


def load_sales():
    return pd.read_csv(PROC / "sales_data_prepped.csv", parse_dates=["date"])


def as_of_date(df):
    """Reference 'today' = day after the last transaction (the dataset is historical, so datetime.now() would be wrong)."""
    return df["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)


def customer_features(df, asof):
    """Transaction rows (all strictly before `asof`) -> one row per customer."""
    inv = df.groupby(["CustomerID", "InvoiceNo"]).agg(date=("InvoiceDate", "max"), amount=("TotalAmount", "sum")).reset_index()
    g = inv.groupby("CustomerID").agg(order_frequency=("InvoiceNo", "nunique"), avg_order_value=("amount", "mean"),
                                      total_spend=("amount", "sum"), first=("date", "min"), last=("date", "max"))
    g["inactivity_days"] = (asof - g["last"]).dt.days
    g["tenure_days"] = (asof - g["first"]).dt.days
    span = (g["last"] - g["first"]).dt.days
    g["avg_days_between_orders"] = np.where(g["order_frequency"] > 1, span / (g["order_frequency"] - 1).clip(lower=1), g["tenure_days"])
    g["n_products"] = df.groupby("CustomerID")["StockCode"].nunique()
    g = g.drop(columns=["first", "last"]).round(2)
    return g.reset_index().rename(columns={"CustomerID": "customer_id"})


def product_names(df):
    """StockCode -> most frequent description."""
    d = df[df["Description"] != ""]
    return d.groupby("StockCode")["Description"].agg(lambda s: s.mode().iat[0]).to_dict()


def make_regressor(**kw):
    try:
        from xgboost import XGBRegressor
        return XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=SEED, **kw), "XGBoost Regressor"
    except ImportError:  # keeps the pipeline runnable where xgboost isn't installed
        from sklearn.ensemble import HistGradientBoostingRegressor
        return HistGradientBoostingRegressor(max_iter=100, learning_rate=0.1, random_state=SEED), "Gradient Boosting Regressor (xgboost not installed)"


def make_classifier(scale_pos_weight=1.0):
    try:
        from xgboost import XGBClassifier
        return XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=SEED, scale_pos_weight=scale_pos_weight,
                             eval_metric="logloss"), "XGBoost"
    except ImportError:
        from sklearn.ensemble import HistGradientBoostingClassifier
        return HistGradientBoostingClassifier(max_iter=100, learning_rate=0.1, random_state=SEED), "Gradient Boosting (xgboost not installed)"


def save_json(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, default=str))


def load_json(name, default=None):
    p = OUT / name
    return json.loads(p.read_text()) if p.exists() else default
