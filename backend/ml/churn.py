"""Milestone 3, Day 5-8: Churn prediction.

Design (important - this differs from the simple sample in the guide):

* A SNAPSHOT date T is chosen 90 days before the last transaction in the
  data. Features are built ONLY from purchases before T.
* The label is what happens AFTER T: churned = 1 if the customer made no
  purchase in the following 90 days.

Why: if the label is "inactive > 90 days" and "days inactive" is also a
feature, the model just re-learns its own label (data leakage) and looks
perfect without predicting anything. Splitting time into "before T" and
"after T" makes this a real prediction problem.
"""

import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from backend.ml.common import SEGMENTS_FILE, artifact_dir

try:  # XGBoost is listed in requirements.txt
    from xgboost import XGBClassifier

    XGBOOST_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on the local environment
    XGBOOST_AVAILABLE = False

logger = logging.getLogger(__name__)

CHURN_WINDOW_DAYS = 90
HIGH_RISK = 0.70
MEDIUM_RISK = 0.40
RANDOM_STATE = 42

FEATURES = [
    "recency_days",
    "frequency",
    "avg_order_value",
    "total_spend",
    "tenure_days",
    "orders_per_month",
    "orders_last_90d",
    "distinct_products",
    "avg_units_per_order",
]


def build_invoice_table(sales: pd.DataFrame) -> pd.DataFrame:
    cust = sales.dropna(subset=["Customer ID"])
    invoices = cust.groupby(["Customer ID", "Invoice"], as_index=False).agg(
        invoice_date=("InvoiceDate", "max"),
        invoice_total=("line_total", "sum"),
        units=("Quantity", "sum"),
    )
    return invoices


def build_features(sales: pd.DataFrame, invoices: pd.DataFrame, snapshot: pd.Timestamp) -> pd.DataFrame:
    """Customer features using ONLY purchases before `snapshot`."""
    past_invoices = invoices[invoices["invoice_date"] < snapshot]
    past_lines = sales.dropna(subset=["Customer ID"])
    past_lines = past_lines[past_lines["InvoiceDate"] < snapshot]

    grouped = past_invoices.groupby("Customer ID")
    feats = grouped.agg(
        frequency=("Invoice", "nunique"),
        avg_order_value=("invoice_total", "mean"),
        total_spend=("invoice_total", "sum"),
        avg_units_per_order=("units", "mean"),
        first_purchase=("invoice_date", "min"),
        last_purchase=("invoice_date", "max"),
    )
    recent = past_invoices[
        past_invoices["invoice_date"] >= snapshot - pd.Timedelta(days=CHURN_WINDOW_DAYS)
    ]
    feats["orders_last_90d"] = recent.groupby("Customer ID")["Invoice"].nunique()
    feats["orders_last_90d"] = feats["orders_last_90d"].fillna(0)
    feats["distinct_products"] = past_lines.groupby("Customer ID")["StockCode"].nunique()

    feats["recency_days"] = (snapshot - feats["last_purchase"]).dt.days
    feats["tenure_days"] = (snapshot - feats["first_purchase"]).dt.days
    feats["orders_per_month"] = feats["frequency"] / np.maximum(feats["tenure_days"] / 30.0, 1.0)

    return feats[FEATURES + ["last_purchase"]].reset_index()


def build_labels(invoices: pd.DataFrame, customers: pd.Series, snapshot: pd.Timestamp) -> pd.Series:
    window_end = snapshot + pd.Timedelta(days=CHURN_WINDOW_DAYS)
    future = invoices[
        (invoices["invoice_date"] >= snapshot) & (invoices["invoice_date"] < window_end)
    ]
    returned = set(future["Customer ID"])
    return (~customers.isin(returned)).astype(int)


def _log_transform(values):
    return np.log1p(np.clip(values, 0, None))


def build_models() -> dict:
    models = {
        "Logistic Regression": make_pipeline(
            FunctionTransformer(_log_transform),
            StandardScaler(),
            LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=5, random_state=RANDOM_STATE, n_jobs=-1
        ),
    }
    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
        )
    else:
        logger.warning(
            "xgboost is not installed: using sklearn HistGradientBoosting as the "
            "boosted-tree model. Run `pip install -r requirements.txt` for XGBoost."
        )
        models["Gradient Boosting (XGBoost unavailable)"] = HistGradientBoostingClassifier(
            max_iter=200, learning_rate=0.05, max_depth=4, random_state=RANDOM_STATE
        )
    return models


def categorize_risk(probability: float) -> str:
    if probability >= HIGH_RISK:
        return "High Risk"
    if probability >= MEDIUM_RISK:
        return "Medium Risk"
    return "Low Risk"


def run(sales: pd.DataFrame) -> dict:
    out = artifact_dir("churn")
    invoices = build_invoice_table(sales)

    last_date = invoices["invoice_date"].max()
    snapshot = (last_date - pd.Timedelta(days=CHURN_WINDOW_DAYS)).normalize()

    # ---------------- training data (past snapshot + future label) ----------
    train_feats = build_features(sales, invoices, snapshot)
    train_feats["churned"] = build_labels(invoices, train_feats["Customer ID"], snapshot)
    churn_rate = train_feats["churned"].mean()
    logger.info(
        "Snapshot %s: %s customers, churn rate %.1f%%",
        snapshot.date(), len(train_feats), churn_rate * 100,
    )

    X = train_feats[FEATURES]
    y = train_feats["churned"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # ---------------- compare models ----------------------------------------
    comparison, fitted = [], {}
    for name, model in build_models().items():
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
        comparison.append(
            {
                "model": name,
                "precision": round(precision_score(y_test, pred), 4),
                "recall": round(recall_score(y_test, pred), 4),
                "f1": round(f1_score(y_test, pred), 4),
                "roc_auc": round(roc_auc_score(y_test, proba), 4),
                "pr_auc": round(average_precision_score(y_test, proba), 4),
                "true_positive": int(tp),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_negative": int(tn),
                "test_customers": len(y_test),
                "test_churn_rate": round(float(y_test.mean()), 4),
            }
        )
        fitted[name] = model

    # "Always predict not-churned" - the lazy model from the guide.
    lazy_accuracy = 1 - float(y_test.mean())
    comparison_df = pd.DataFrame(comparison)
    comparison_df["lazy_model_accuracy"] = round(lazy_accuracy, 4)
    comparison_df = comparison_df.sort_values(["f1", "recall"], ascending=False).reset_index(drop=True)
    comparison_df.to_csv(out / "churn_model_comparison.csv", index=False)

    best_name = comparison_df.loc[0, "model"]
    logger.info("Model comparison:\n%s", comparison_df.iloc[:, :7].to_string(index=False))
    logger.info("Selected model: %s", best_name)

    # ---------------- feature importance (selected model) --------------------
    importance = permutation_importance(
        fitted[best_name], X_test, y_test, scoring="roc_auc",
        n_repeats=10, random_state=RANDOM_STATE,
    )
    pd.DataFrame(
        {"feature": FEATURES, "importance": importance.importances_mean.round(4)}
    ).sort_values("importance", ascending=False).to_csv(
        out / "churn_feature_importance.csv", index=False
    )

    # ---------------- score customers as of today ---------------------------
    final_model = build_models()[best_name]
    final_model.fit(X, y)  # refit on every labelled customer

    today = last_date.normalize() + pd.Timedelta(days=1)
    now_feats = build_features(sales, invoices, today)
    probabilities = final_model.predict_proba(now_feats[FEATURES])[:, 1]

    predictions = now_feats[
        ["Customer ID", "recency_days", "frequency", "avg_order_value", "total_spend"]
    ].copy()
    predictions["Customer ID"] = predictions["Customer ID"].astype(int)
    predictions["churn_probability"] = probabilities.round(4)
    predictions["retention_risk"] = predictions["churn_probability"].map(categorize_risk)
    predictions["already_inactive_90d"] = (now_feats["recency_days"] > CHURN_WINDOW_DAYS).to_numpy()
    predictions["avg_order_value"] = predictions["avg_order_value"].round(2)
    predictions["total_spend"] = predictions["total_spend"].round(2)
    predictions["model"] = best_name

    # ---------------- connect to Milestone 2 segments -----------------------
    segments = pd.read_csv(SEGMENTS_FILE)[["Customer ID", "segment_name"]]
    segments["Customer ID"] = segments["Customer ID"].astype(int)
    predictions = predictions.merge(segments, on="Customer ID", how="left")
    predictions["segment_name"] = predictions["segment_name"].fillna("Unsegmented")

    predictions = predictions.sort_values("churn_probability", ascending=False)
    predictions.to_csv(out / "churn_predictions.csv", index=False)

    risk_by_segment = (
        predictions.groupby(["segment_name", "retention_risk"]).size().unstack(fill_value=0)
    )
    for column in ("High Risk", "Medium Risk", "Low Risk"):
        if column not in risk_by_segment:
            risk_by_segment[column] = 0
    risk_by_segment = risk_by_segment[["High Risk", "Medium Risk", "Low Risk"]]
    risk_by_segment["customers"] = risk_by_segment.sum(axis=1)
    risk_by_segment["high_risk_pct"] = (
        risk_by_segment["High Risk"] / risk_by_segment["customers"] * 100
    ).round(1)
    risk_by_segment.reset_index().to_csv(out / "churn_risk_by_segment.csv", index=False)

    meta = {
        "snapshot_date": snapshot.date().isoformat(),
        "data_end_date": last_date.date().isoformat(),
        "churn_window_days": CHURN_WINDOW_DAYS,
        "training_customers": len(train_feats),
        "training_churn_rate": round(float(churn_rate), 4),
        "selected_model": best_name,
        "xgboost_available": XGBOOST_AVAILABLE,
        "high_risk_threshold": HIGH_RISK,
        "medium_risk_threshold": MEDIUM_RISK,
    }
    pd.Series(meta).to_json(out / "churn_run_info.json", indent=2)
    logger.info("Risk by segment:\n%s", risk_by_segment.to_string())
    return meta
