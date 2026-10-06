"""Compare churn classifiers and join selected risk predictions to segments."""

import json
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score

from backend.models.churn.classification_models import build_churn_models
from backend.services.churn_service import (
    FEATURE_COLUMNS,
    _split_customer_data,
    build_churn_features,
    load_processed_data,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SEGMENTS_PATH = PROCESSED_DIR / "segments" / "customer_segments.csv"
CHURN_DIR = PROCESSED_DIR / "churn"
COMPARISON_PATH = CHURN_DIR / "churn_model_comparison.csv"
PREDICTIONS_PATH = CHURN_DIR / "churn_predictions_final.csv"
SEGMENT_RISK_PATH = CHURN_DIR / "churn_segment_risk_summary.csv"


def _positive_probability(model: object, features: pd.DataFrame) -> pd.Series:
    """Return model.predict_proba() probability for churn class 1."""
    if hasattr(model, "predict_probability"):
        probability = model.predict_probability(features)
    else:
        probabilities = model.predict_proba(features)
        classes = list(model.classes_)
        probability = probabilities[:, classes.index(1)] if 1 in classes else [0.0] * len(features)
    return pd.Series(probability, index=features.index, dtype=float)


def _risk_category(probability: float) -> str:
    """Apply the official exact retention-risk thresholds."""
    if probability >= 0.70:
        return "High Risk"
    if probability >= 0.40:
        return "Medium Risk"
    return "Low Risk"


def _metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    """Calculate the required imbalanced-class metrics."""
    return {
        "precision": round(float(precision_score(actual, predicted, zero_division=0)), 4),
        "recall": round(float(recall_score(actual, predicted, zero_division=0)), 4),
        "f1": round(float(f1_score(actual, predicted, zero_division=0)), 4),
    }


def generate_churn_model_comparison() -> dict[str, Any]:
    """Compare models on one shared split and save selected risk predictions."""
    sales, customers = load_processed_data()
    features, reference_date = build_churn_features(sales, customers)
    x_train, x_validation, y_train, y_validation, split_description = _split_customer_data(features)
    if x_validation.empty or y_validation.nunique() < 2:
        raise ValueError("Day 7-8 model comparison requires a two-class validation split.")

    positive_weight = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))
    models = build_churn_models(positive_weight)
    comparison_rows = []
    fitted_models: dict[str, object] = {}
    for model_name, model in models.items():
        if hasattr(model, "fit_predict"):
            model.fit(x_train, y_train)
        else:
            model.fit(x_train, y_train)
        predictions = pd.Series(model.predict(x_validation), index=x_validation.index).astype(int)
        comparison_rows.append({"model": model_name, **_metrics(y_validation, predictions)})
        fitted_models[model_name] = model

    comparison = pd.DataFrame(comparison_rows).sort_values(
        ["f1", "recall", "precision", "model"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    selected_model_name = str(comparison.iloc[0]["model"])
    comparison["selected"] = comparison["model"].eq(selected_model_name)
    selected_model = fitted_models[selected_model_name]

    all_features = features[FEATURE_COLUMNS]
    final_predictions = pd.Series(selected_model.predict(all_features), index=features.index).astype(int)
    final_probabilities = _positive_probability(selected_model, all_features).clip(0, 1)
    prediction_output = features.copy()
    prediction_output["predicted_churn"] = final_predictions.to_numpy()
    prediction_output["churn_probability"] = final_probabilities.round(6).to_numpy()
    prediction_output["retention_risk"] = final_probabilities.map(_risk_category).to_numpy()
    prediction_output["selected_model"] = selected_model_name

    if not SEGMENTS_PATH.exists():
        raise FileNotFoundError(f"Segmentation output not found: {SEGMENTS_PATH}")
    segments = pd.read_csv(SEGMENTS_PATH)[["customer_id", "segment_name"]]
    prediction_output = prediction_output.merge(segments, on="customer_id", how="left", validate="one_to_one")
    if prediction_output["segment_name"].isna().any():
        raise ValueError("Every churn customer must map to an existing Milestone 2 segment.")
    prediction_output = prediction_output[
        [
            "customer_id",
            "reference_date",
            "last_purchase_date",
            *FEATURE_COLUMNS,
            "churned",
            "predicted_churn",
            "churn_probability",
            "retention_risk",
            "segment_name",
            "selected_model",
        ]
    ]

    segment_risk_summary = (
        prediction_output.groupby(["segment_name", "retention_risk"], as_index=False)
        .agg(customer_count=("customer_id", "nunique"))
        .sort_values(["segment_name", "retention_risk"])
    )

    CHURN_DIR.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(COMPARISON_PATH, index=False)
    prediction_output.to_csv(PREDICTIONS_PATH, index=False)
    segment_risk_summary.to_csv(SEGMENT_RISK_PATH, index=False)

    risk_counts = prediction_output["retention_risk"].value_counts().reindex(
        ["High Risk", "Medium Risk", "Low Risk"], fill_value=0
    )
    return {
        "customers": len(features),
        "reference_date": reference_date.strftime("%Y-%m-%d"),
        "churned": int(features["churned"].sum()),
        "non_churned": int((features["churned"] == 0).sum()),
        "features": FEATURE_COLUMNS,
        "split": split_description,
        "positive_weight": round(positive_weight, 4),
        "comparison": comparison.to_dict(orient="records"),
        "selected_model": selected_model_name,
        "risk_counts": {str(key): int(value) for key, value in risk_counts.items()},
        "segment_risk_summary": segment_risk_summary.to_dict(orient="records"),
        "output_paths": [COMPARISON_PATH, PREDICTIONS_PATH, SEGMENT_RISK_PATH],
    }


def main() -> None:
    """Run comparison, risk categorization, and segment integration."""
    result = generate_churn_model_comparison()
    print(f"Customers: {result['customers']:,}")
    print(f"Reference date: {result['reference_date']}")
    print(f"Churned: {result['churned']:,}")
    print(f"Non-churned: {result['non_churned']:,}")
    print(f"Features: {result['features']}")
    print(f"Training/validation: {result['split']}")
    print(f"Comparison: {json.dumps(result['comparison'], sort_keys=True)}")
    print(f"Selected model: {result['selected_model']}")
    print(f"Risk counts: {result['risk_counts']}")
    print(f"Segment/risk summary: {json.dumps(result['segment_risk_summary'], sort_keys=True)}")
    for output_path in result["output_paths"]:
        print(f"Output: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
