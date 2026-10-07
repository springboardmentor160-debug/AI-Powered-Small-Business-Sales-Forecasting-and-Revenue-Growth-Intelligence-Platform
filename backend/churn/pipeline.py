import os
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

RAW_SALES_PATH = os.path.join("data", "processed", "clean_sales_data.csv")
CUSTOMER_FEATURES_PATH = os.path.join("data", "processed", "customer_features.csv")
CHURN_PROCESSED_PATH = os.path.join("data", "processed", "customer_churn_predictions.csv")

FEATURE_COLS = ["purchase_frequency", "purchase_value", "customer_activity_days"]


def prepare_churn_dataset(
    sales_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    inactivity_days_threshold: int = 2
) -> pd.DataFrame:
    """
    Prepare customer-level dataset with real churn labels and behavioral features:
    1. Determine max transaction date in historical sales.
    2. Compute recency (days_since_last_order = max_date - customer_last_date).
    3. Define churn label:
       - churn = 1 if days_since_last_order >= inactivity_days_threshold
       - churn = 0 if days_since_last_order < inactivity_days_threshold
    4. Merge customer behavioral features (purchase_frequency, purchase_value, customer_activity_days, segment).
    Target leakage prevention: Recency defines the target label and is excluded from X features.
    """
    sales = sales_df.copy()
    sales["order_date"] = pd.to_datetime(sales["order_date"])
    max_date = sales["order_date"].max()

    last_orders = sales.groupby("customer_id")["order_date"].max().reset_index()
    last_orders["days_since_last_order"] = (max_date - last_orders["order_date"]).dt.days

    merged = pd.merge(customer_df, last_orders[["customer_id", "days_since_last_order"]], on="customer_id")
    merged["churn"] = (merged["days_since_last_order"] >= inactivity_days_threshold).astype(int)

    return merged


def split_churn_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.4,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split dataset into train and test partitions.
    Uses stratified split when multiple classes and sufficient sample counts exist,
    with safe fallback for small sample constraints.
    """
    class_counts = y.value_counts()
    can_stratify = len(class_counts) > 1 and class_counts.min() >= 2

    stratify_arg = y if can_stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_arg
    )
    return X_train, X_test, y_train, y_test


def train_logistic_regression(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = 42
) -> Tuple[LogisticRegression, StandardScaler]:
    """Train baseline Logistic Regression classifier with feature scaling."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    model = LogisticRegression(random_state=random_state)
    model.fit(X_train_scaled, y_train)
    return model, scaler


def train_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = 42
) -> RandomForestClassifier:
    """Train Random Forest Classifier (100 estimators)."""
    model = RandomForestClassifier(n_estimators=100, random_state=random_state)
    model.fit(X_train, y_train)
    return model


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = 42
) -> XGBClassifier:
    """Train XGBoost Classifier (100 estimators, lr=0.1)."""
    model = XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        random_state=random_state,
        eval_metric="logloss"
    )
    model.fit(X_train, y_train)
    return model


def evaluate_classification_model(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
    scaler: Optional[StandardScaler] = None
) -> Dict[str, Any]:
    """
    Evaluate classifier metrics on test set:
    - Precision
    - Recall
    - F1-score
    - Accuracy
    - Predicted classes and class 1 probabilities
    """
    if scaler is not None:
        X_eval = scaler.transform(X_test)
    else:
        X_eval = X_test

    y_pred = model.predict(X_eval)

    # Probabilities for class 1 (churn)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X_eval)[:, 1]
    else:
        probabilities = y_pred.astype(float)

    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    acc = float(accuracy_score(y_test, y_pred))

    return {
        "model": model_name,
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(acc, 4),
        "predictions": [int(p) for p in y_pred],
        "probabilities": [round(float(p), 4) for p in probabilities]
    }


def select_best_churn_model(evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Select best churn model based on business-aligned criteria:
    Prioritizes Recall (and F1-score as tie-breaker) because in small business retention,
    missing an at-risk customer (False Negative) results in lost lifetime revenue,
    whereas contacting an active customer (False Positive) with a retention incentive
    incurs minimal operational cost.
    """
    if not evaluations:
        raise ValueError("No model evaluations provided.")

    # Sort descending by recall primary, f1_score secondary, accuracy tertiary
    sorted_evals = sorted(
        evaluations,
        key=lambda m: (m["recall"], m["f1_score"], m["accuracy"]),
        reverse=True
    )
    best = sorted_evals[0]

    reason = (
        f"Selected '{best['model']}' based on highest test Recall ({best['recall']}) and "
        f"F1-score ({best['f1_score']}). In churn intelligence, high recall minimizes unaddressed customer loss."
    )

    return {
        "selected_model": best["model"],
        "best_recall": best["recall"],
        "best_f1": best["f1_score"],
        "selection_reason": reason
    }


def assign_retention_risk(
    churn_prob: float,
    high_threshold: float = 0.7,
    medium_threshold: float = 0.4
) -> str:
    """
    Map churn probability to actionable business retention risk categories:
    - High Risk: probability >= 0.7
    - Medium Risk: 0.4 <= probability < 0.7
    - Low Risk: probability < 0.4
    """
    if churn_prob >= high_threshold:
        return "High Risk"
    elif churn_prob >= medium_threshold:
        return "Medium Risk"
    else:
        return "Low Risk"


def run_churn_pipeline(
    sales_path: str = RAW_SALES_PATH,
    customer_path: str = CUSTOMER_FEATURES_PATH,
    output_path: str = CHURN_PROCESSED_PATH,
    inactivity_threshold: int = 2,
    high_risk_threshold: float = 0.7,
    medium_risk_threshold: float = 0.4
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Complete Churn Prediction & Retention Intelligence Pipeline (Days 5–8):
    1. Compute data-driven churn label (inactivity window >= 2 days).
    2. Extract behavioral features without data leakage.
    3. Perform stratified train/test split.
    4. Train Logistic Regression baseline, Random Forest, and XGBoost.
    5. Evaluate test Precision, Recall, F1, and Accuracy.
    6. Select winning model prioritizing Recall.
    7. Generate full-cohort churn probabilities and retention risk categories.
    8. Integrate churn risk with Milestone 2 customer segments.
    9. Persist predictions and return structured intelligence payload.
    """
    if not os.path.exists(sales_path):
        raise FileNotFoundError(f"Sales file not found at {sales_path}")
    if not os.path.exists(customer_path):
        raise FileNotFoundError(f"Customer features file not found at {customer_path}")

    sales_df = pd.read_csv(sales_path)
    customer_df = pd.read_csv(customer_path)

    churn_df = prepare_churn_dataset(sales_df, customer_df, inactivity_days_threshold=inactivity_threshold)

    X = churn_df[FEATURE_COLS]
    y = churn_df["churn"]

    # Small dataset check
    unique_classes = y.unique()
    if len(unique_classes) < 2:
        # Handle single class limitation honestly
        churn_df["churn_probability"] = 0.5
        churn_df["retention_risk"] = "Medium Risk"
        return churn_df, {
            "status": "single_class_limitation",
            "message": "Only one class present in churn target. Classification models require at least two classes.",
            "models_evaluated": [],
            "selected_model": "None"
        }

    X_train, X_test, y_train, y_test = split_churn_data(X, y, test_size=0.4, random_state=42)

    # 1. Train models on training set
    lr_model, scaler = train_logistic_regression(X_train, y_train, random_state=42)
    rf_model = train_random_forest(X_train, y_train, random_state=42)
    xgb_model = train_xgboost(X_train, y_train, random_state=42)

    # 2. Evaluate on test set
    lr_eval = evaluate_classification_model(lr_model, X_test, y_test, "Logistic Regression", scaler=scaler)
    rf_eval = evaluate_classification_model(rf_model, X_test, y_test, "Random Forest")
    xgb_eval = evaluate_classification_model(xgb_model, X_test, y_test, "XGBoost")

    evaluations = [lr_eval, rf_eval, xgb_eval]
    selection_info = select_best_churn_model(evaluations)
    best_model_name = selection_info["selected_model"]

    # Compute probabilities for all models across full dataset
    full_scaler = StandardScaler()
    X_full_scaled = full_scaler.fit_transform(X)

    full_lr = LogisticRegression(random_state=42).fit(X_full_scaled, y)
    lr_probs = [round(float(p), 4) for p in full_lr.predict_proba(X_full_scaled)[:, 1]]

    full_rf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, y)
    rf_probs = [round(float(p), 4) for p in full_rf.predict_proba(X)[:, 1]]

    full_xgb = XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42, eval_metric="logloss").fit(X, y)
    xgb_probs = [round(float(p), 4) for p in full_xgb.predict_proba(X)[:, 1]]

    if best_model_name == "Logistic Regression":
        selected_probs = lr_probs
    elif best_model_name == "XGBoost":
        selected_probs = xgb_probs
    else:
        selected_probs = rf_probs

    churn_df["churn_probability"] = selected_probs
    churn_df["lr_probability"] = lr_probs
    churn_df["rf_probability"] = rf_probs
    churn_df["xgb_probability"] = xgb_probs
    churn_df["retention_risk"] = churn_df["churn_probability"].apply(
        lambda p: assign_retention_risk(p, high_threshold=high_risk_threshold, medium_threshold=medium_risk_threshold)
    )

    # Cross-reference with Milestone 2 segments
    segment_churn_summary = churn_df.groupby(["segment", "retention_risk"]).agg(
        customer_count=("customer_id", "count"),
        avg_churn_prob=("churn_probability", "mean"),
        avg_purchase_val=("purchase_value", "mean")
    ).reset_index()

    segment_churn_summary["avg_churn_prob"] = segment_churn_summary["avg_churn_prob"].round(4)
    segment_churn_summary["avg_purchase_val"] = segment_churn_summary["avg_purchase_val"].round(2)

    # Persist predictions
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    churn_df.to_csv(output_path, index=False)

    # Build cohort records
    cohort_records = [
        {
            "customer_id": row["customer_id"],
            "purchase_frequency": int(row["purchase_frequency"]),
            "purchase_value": float(row["purchase_value"]),
            "customer_activity_days": int(row["customer_activity_days"]),
            "days_since_last_order": int(row["days_since_last_order"]),
            "churn_label": int(row["churn"]),
            "churn_probability": float(row["churn_probability"]),
            "lr_probability": float(row["lr_probability"]),
            "rf_probability": float(row["rf_probability"]),
            "xgb_probability": float(row["xgb_probability"]),
            "retention_risk": row["retention_risk"],
            "segment": row["segment"]
        }
        for _, row in churn_df.iterrows()
    ]

    # Risk category distribution
    risk_dist = churn_df["retention_risk"].value_counts().to_dict()

    summary_payload = {
        "inactivity_days_threshold": inactivity_threshold,
        "risk_thresholds": {
            "high": high_risk_threshold,
            "medium": medium_risk_threshold
        },
        "selected_model": best_model_name,
        "selection_reason": selection_info["selection_reason"],
        "model_evaluations": evaluations,
        "risk_distribution": risk_dist,
        "segment_churn_relationship": segment_churn_summary.to_dict(orient="records"),
        "customer_cohort": cohort_records,
        "total_customers": len(churn_df),
        "test_size": len(X_test),
        "train_size": len(X_train)
    }

    return churn_df, summary_payload
