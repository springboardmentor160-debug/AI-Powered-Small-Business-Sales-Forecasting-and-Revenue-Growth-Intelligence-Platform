"""Deterministic churn classification model factory for Day 7-8 comparison."""

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from backend.models.churn.logistic_regression_model import LogisticChurnModel


def build_churn_models(positive_weight: float) -> dict[str, object]:
    """Return the three required classifiers with imbalance-aware settings."""
    return {
        "Logistic Regression": LogisticChurnModel(random_state=42),
        "Random Forest": RandomForestClassifier(
            n_estimators=250,
            max_depth=8,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=250,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            scale_pos_weight=positive_weight,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=1,
        ),
    }
