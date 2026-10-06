"""Logistic Regression baseline for customer churn prediction."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class LogisticChurnModel:
    """Deterministic, imbalance-aware Logistic Regression baseline."""

    random_state: int = 42
    classifier: Pipeline | DummyClassifier | None = None
    is_single_class_fallback: bool = False

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> "LogisticChurnModel":
        """Fit Logistic Regression or a safe prior fallback for one-class training data."""
        unique_labels = sorted(pd.Series(labels).dropna().astype(int).unique().tolist())
        if len(unique_labels) < 2:
            self.classifier = DummyClassifier(strategy="prior")
            self.is_single_class_fallback = True
        else:
            self.classifier = Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        LogisticRegression(
                            class_weight="balanced",
                            max_iter=1000,
                            random_state=self.random_state,
                        ),
                    ),
                ]
            )
        self.classifier.fit(features, labels)
        return self

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """Return predicted churn labels."""
        if self.classifier is None:
            raise RuntimeError("The churn model must be fitted before prediction.")
        return self.classifier.predict(features)

    def predict_probability(self, features: pd.DataFrame) -> np.ndarray:
        """Return the probability of the positive churn class."""
        if self.classifier is None:
            raise RuntimeError("The churn model must be fitted before prediction.")
        probabilities = self.classifier.predict_proba(features)
        classes = getattr(self.classifier, "classes_", None)
        if classes is None and hasattr(self.classifier, "named_steps"):
            classes = self.classifier.named_steps["classifier"].classes_
        if len(classes) == 1:
            return np.ones(len(features)) if int(classes[0]) == 1 else np.zeros(len(features))
        positive_index = list(classes).index(1)
        return probabilities[:, positive_index]
