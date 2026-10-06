"""Build customer churn features and run the initial Logistic Regression baseline."""

import json
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

from backend.models.churn.logistic_regression_model import LogisticChurnModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SALES_PATH = PROCESSED_DIR / "sales" / "cleaned_sales.csv"
CUSTOMERS_PATH = PROCESSED_DIR / "customers" / "cleaned_customers.csv"
CHURN_DIR = PROCESSED_DIR / "churn"
FEATURES_PATH = CHURN_DIR / "customer_churn_features.csv"
PREDICTIONS_PATH = CHURN_DIR / "churn_predictions.csv"
METRICS_PATH = CHURN_DIR / "churn_model_metrics.csv"
FEATURE_COLUMNS = [
    "recency_days",
    "purchase_frequency",
    "average_order_value",
    "customer_activity",
]


def load_processed_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the processed Sales and Customer datasets without changing them."""
    for path in (SALES_PATH, CUSTOMERS_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Processed dataset not found: {path}")
    sales = pd.read_csv(SALES_PATH)
    customers = pd.read_csv(CUSTOMERS_PATH)
    required_sales = {"transaction_id", "date", "customer_id", "total_amount"}
    missing_sales = required_sales.difference(sales.columns)
    if missing_sales:
        raise ValueError(f"Sales data is missing required columns: {sorted(missing_sales)}")
    if "customer_id" not in customers.columns:
        raise ValueError("Customer data is missing required column: customer_id")
    return sales, customers


def build_churn_features(sales: pd.DataFrame, customers: pd.DataFrame) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Build customer features and a >90-day inactivity label from the actual reference date."""
    sales = sales.copy()
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    sales["total_amount"] = pd.to_numeric(sales["total_amount"], errors="coerce")
    sales = sales.dropna(subset=["customer_id", "date", "total_amount"])
    reference_date = sales["date"].max()
    sales_summary = (
        sales.groupby("customer_id", as_index=False)
        .agg(
            last_purchase_date=("date", "max"),
            purchase_frequency=("transaction_id", "nunique"),
            average_order_value=("total_amount", "mean"),
            customer_activity=("date", "nunique"),
        )
    )
    features = customers[["customer_id"]].drop_duplicates().merge(
        sales_summary,
        on="customer_id",
        how="left",
    )
    features["recency_days"] = (reference_date - features["last_purchase_date"]).dt.days
    no_history = features["last_purchase_date"].isna()
    observation_days = (reference_date - sales["date"].min()).days + 1
    features.loc[no_history, "recency_days"] = observation_days
    features["purchase_frequency"] = features["purchase_frequency"].fillna(0).astype(int)
    features["average_order_value"] = features["average_order_value"].fillna(0).round(2)
    features["customer_activity"] = features["customer_activity"].fillna(0).astype(int)
    features["recency_days"] = features["recency_days"].fillna(observation_days).astype(int)
    features["churned"] = (features["recency_days"] > 90).astype(int)
    features["reference_date"] = reference_date.strftime("%Y-%m-%d")
    return features[
        [
            "customer_id",
            "reference_date",
            "last_purchase_date",
            *FEATURE_COLUMNS,
            "churned",
        ]
    ], reference_date


def _split_customer_data(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, str]:
    """Create a deterministic stratified split when both classes support it."""
    x = features[FEATURE_COLUMNS]
    y = features["churned"]
    if y.nunique() >= 2 and y.value_counts().min() >= 2:
        x_train, x_validation, y_train, y_validation = train_test_split(
            x,
            y,
            test_size=0.25,
            random_state=42,
            stratify=y,
        )
        return x_train, x_validation, y_train, y_validation, "stratified 75/25 split"
    return x, x.iloc[0:0], y, y.iloc[0:0], "single-class full-data fallback"


def _validation_metrics(actual: pd.Series, predicted: pd.Series, probabilities: pd.Series) -> dict[str, float | str]:
    """Calculate metrics only when the validation split supports them."""
    if actual.empty or actual.nunique() < 2:
        return {"status": "no_valid_two-class_validation_split"}
    metrics: dict[str, float | str] = {
        "status": "validated",
        "accuracy": round(float(accuracy_score(actual, predicted)), 4),
        "precision": round(float(precision_score(actual, predicted, zero_division=0)), 4),
        "recall": round(float(recall_score(actual, predicted, zero_division=0)), 4),
        "f1": round(float(f1_score(actual, predicted, zero_division=0)), 4),
    }
    if actual.nunique() == 2:
        metrics["roc_auc"] = round(float(roc_auc_score(actual, probabilities)), 4)
    return metrics


def generate_churn_predictions() -> dict[str, Any]:
    """Generate actual churn features, baseline predictions, and metrics."""
    sales, customers = load_processed_data()
    features, reference_date = build_churn_features(sales, customers)
    x_train, x_validation, y_train, y_validation, split_description = _split_customer_data(features)
    model = LogisticChurnModel().fit(x_train, y_train)
    predictions = model.predict(features[FEATURE_COLUMNS]).astype(int)
    probabilities = model.predict_probability(features[FEATURE_COLUMNS])

    validation_predictions = model.predict(x_validation).astype(int) if not x_validation.empty else pd.Series(dtype=int)
    validation_probabilities = model.predict_probability(x_validation) if not x_validation.empty else pd.Series(dtype=float)
    metrics = _validation_metrics(y_validation, validation_predictions, validation_probabilities)
    metrics["model"] = "Logistic Regression" if not model.is_single_class_fallback else "Dummy prior fallback"
    metrics["split"] = split_description

    feature_output = features.copy()
    prediction_output = features[["customer_id", "churned"]].copy()
    prediction_output["predicted_churn"] = predictions
    prediction_output["churn_probability"] = probabilities.round(6)
    prediction_output["model"] = metrics["model"]
    metrics_output = pd.DataFrame([metrics])

    CHURN_DIR.mkdir(parents=True, exist_ok=True)
    feature_output.to_csv(FEATURES_PATH, index=False)
    prediction_output.to_csv(PREDICTIONS_PATH, index=False)
    metrics_output.to_csv(METRICS_PATH, index=False)

    return {
        "customers": len(features),
        "reference_date": reference_date.strftime("%Y-%m-%d"),
        "churned": int(features["churned"].sum()),
        "non_churned": int((features["churned"] == 0).sum()),
        "features": FEATURE_COLUMNS,
        "split": split_description,
        "model": metrics["model"],
        "metrics": metrics,
        "output_paths": [FEATURES_PATH, PREDICTIONS_PATH, METRICS_PATH],
    }


def main() -> None:
    """Run the churn pipeline and print actual setup/results."""
    result = generate_churn_predictions()
    print(f"Customers: {result['customers']:,}")
    print(f"Reference date: {result['reference_date']}")
    print(f"Churned: {result['churned']:,}")
    print(f"Non-churned: {result['non_churned']:,}")
    print(f"Features: {result['features']}")
    print(f"Model: {result['model']}")
    print(f"Training/validation: {result['split']}")
    print(f"Metrics: {json.dumps(result['metrics'], sort_keys=True)}")
    for output_path in result["output_paths"]:
        print(f"Output: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
