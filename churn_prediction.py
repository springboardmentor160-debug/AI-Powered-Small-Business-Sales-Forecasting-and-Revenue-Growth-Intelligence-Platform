
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INPUT_FILE = DATA_DIR / "clean_retail_sales.csv"

OUTPUT_FILE = DATA_DIR / "customer_churn_predictions.csv"
METRICS_FILE = DATA_DIR / "churn_model_comparison.csv"

INACTIVITY_DAYS = 90
OBSERVATION_DAYS = 180
RANDOM_STATE = 42


def load_sales_data():
    """Load and validate the cleaned retail transactions."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}\n"
            "Check that data/clean_retail_sales.csv exists."
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = {
        "CustomerID",
        "InvoiceDate",
        "Quantity",
        "UnitPrice",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing)}"
        )

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )
    df["CustomerID"] = df["CustomerID"].astype("string").str.strip()
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )
    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"], errors="coerce"
    )

    df = df.dropna(
        subset=[
            "CustomerID",
            "InvoiceDate",
            "Quantity",
            "UnitPrice",
        ]
    )

    # Cancelled invoices and non-positive purchases are excluded.
    if "InvoiceNo" in df.columns:
        df["InvoiceNo"] = df["InvoiceNo"].astype(str)
        df = df[~df["InvoiceNo"].str.startswith("C")]

    df = df[
        (df["Quantity"] > 0)
        & (df["UnitPrice"] > 0)
    ].copy()

    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    if df.empty:
        raise ValueError("No valid sales transactions remain.")

    print("Sales data loaded successfully.")
    print(f"Usable transactions: {len(df):,}")
    print(f"Unique customers: {df['CustomerID'].nunique():,}")

    return df


def build_customer_features(df):
    """
    Build customer-level RFM features and a proxy churn label.

    Customers with no purchase during the final inactivity window
    are treated as churn-risk examples. This is a proxy label, not
    a verified business churn outcome.
    """
    observation_end = df["InvoiceDate"].max()
    feature_cutoff = (
        observation_end - pd.Timedelta(days=INACTIVITY_DAYS)
    )
    observation_start = (
        feature_cutoff - pd.Timedelta(days=OBSERVATION_DAYS)
    )

    # Use only transactions before the feature cutoff for features.
    historical = df[
        (df["InvoiceDate"] >= observation_start)
        & (df["InvoiceDate"] < feature_cutoff)
    ].copy()

    # Use the following 90 days to construct the proxy target.
    future = df[
        (df["InvoiceDate"] >= feature_cutoff)
        & (df["InvoiceDate"] <= observation_end)
    ].copy()

    if historical.empty:
        raise ValueError(
            "Not enough historical transactions to build features."
        )

    reference_date = feature_cutoff

    features = historical.groupby("CustomerID").agg(
        last_purchase=("InvoiceDate", "max"),
        frequency=("InvoiceDate", "nunique"),
        transaction_count=("InvoiceDate", "count"),
        monetary=("Revenue", "sum"),
        average_order_value=("Revenue", "mean"),
        total_quantity=("Quantity", "sum"),
    )

    if "InvoiceNo" in historical.columns:
        invoice_counts = historical.groupby("CustomerID")[
            "InvoiceNo"
        ].nunique()
        features["frequency"] = invoice_counts

    features["recency_days"] = (
        reference_date - features["last_purchase"]
    ).dt.days

    features = features.drop(columns=["last_purchase"])

    future_customers = set(future["CustomerID"].unique())

    # Label 1 means no purchase during the defined future window.
    features["churn_proxy"] = [
        0 if customer in future_customers else 1
        for customer in features.index
    ]

    features = features.replace(
        [np.inf, -np.inf], np.nan
    ).dropna()

    if features["churn_proxy"].nunique() < 2:
        raise ValueError(
            "The proxy target contains only one class. "
            "A reliable model comparison cannot be trained "
            "on this time window."
        )

    print("\nCustomer feature table created.")
    print(f"Customers with usable history: {len(features):,}")
    print(
        "Proxy churn rate: "
        f"{features['churn_proxy'].mean():.1%}"
    )
    print(
        "Historical feature window: "
        f"{observation_start.date()} to "
        f"{feature_cutoff.date()}"
    )
    print(
        "Proxy label window: "
        f"{feature_cutoff.date()} to "
        f"{observation_end.date()}"
    )

    return features, observation_end


def train_and_evaluate(features):
    """Train models and evaluate on a held-out test set."""
    feature_columns = [
        "recency_days",
        "frequency",
        "transaction_count",
        "monetary",
        "average_order_value",
        "total_quantity",
    ]

    X = features[feature_columns].astype(float)
    y = features["churn_proxy"].astype(int)

    class_counts = y.value_counts()
    if class_counts.min() < 2:
        raise ValueError(
            "Each proxy class needs at least two customers "
            "for stratified train/test splitting."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    models = {
        "Logistic Regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=250,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    # XGBoost is optional so the script can run without it.
    try:
        from xgboost import XGBClassifier

        models["XGBoost"] = XGBClassifier(
            n_estimators=250,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    except ImportError:
        print(
            "\nXGBoost is not installed. "
            "Install it with: python -m pip install xgboost"
        )

    results = []
    trained_models = {}

    print("\nTraining and evaluating churn models...")

    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)

        predicted = model.predict(X_test)
        probabilities = model.predict_proba(X_test)[:, 1]

        metrics = {
            "Model": name,
            "Accuracy": accuracy_score(y_test, predicted),
            "Precision": precision_score(
                y_test, predicted, zero_division=0
            ),
            "Recall": recall_score(
                y_test, predicted, zero_division=0
            ),
            "F1": f1_score(
                y_test, predicted, zero_division=0
            ),
            "ROC_AUC": roc_auc_score(
                y_test, probabilities
            ),
        }

        results.append(metrics)
        trained_models[name] = model

        print(f"\n{name}")
        print(
            classification_report(
                y_test,
                predicted,
                zero_division=0,
            )
        )

    metrics_df = pd.DataFrame(results).sort_values(
        "ROC_AUC", ascending=False
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(METRICS_FILE, index=False)

    print("\nMODEL PERFORMANCE COMPARISON")
    print(metrics_df.round(4).to_string(index=False))
    print(f"\nModel metrics saved to: {METRICS_FILE}")

    return trained_models, metrics_df, feature_columns


def generate_churn_predictions(
    features, trained_models, metrics_df, feature_columns
):
    """Score customers and assign proxy risk categories."""
    best_model_name = metrics_df.iloc[0]["Model"]
    best_model = trained_models[best_model_name]

    X_all = features[feature_columns].astype(float)
    probabilities = best_model.predict_proba(X_all)[:, 1]

    output = pd.DataFrame(index=features.index)
    output.index.name = "CustomerID"
    output["churn_probability"] = probabilities

    output["risk_category"] = pd.cut(
        output["churn_probability"],
        bins=[-0.001, 0.30, 0.60, 1.0],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    output["model_used"] = best_model_name
    output["label_type"] = "Proxy inactivity label"

    output = output.reset_index().sort_values(
        "churn_probability", ascending=False
    )

    output["churn_probability"] = output[
        "churn_probability"
    ].round(4)

    output.to_csv(OUTPUT_FILE, index=False)

    print("\nTOP 10 CUSTOMERS BY PREDICTED CHURN RISK")
    print(output.head(10).to_string(index=False))

    print(f"\nCustomer predictions saved to: {OUTPUT_FILE}")
    print(f"Selected model: {best_model_name}")
    print(
        "\nIMPORTANT: These scores estimate future inactivity "
        "under a proxy definition. They are not verified "
        "real-world churn probabilities."
    )


def main():
    sales = load_sales_data()
    features, _ = build_customer_features(sales)

    trained_models, metrics_df, feature_columns = (
        train_and_evaluate(features)
    )

    generate_churn_predictions(
        features,
        trained_models,
        metrics_df,
        feature_columns,
    )

    print("\nChurn prediction pipeline completed.")


if __name__ == "__main__":
    main()
