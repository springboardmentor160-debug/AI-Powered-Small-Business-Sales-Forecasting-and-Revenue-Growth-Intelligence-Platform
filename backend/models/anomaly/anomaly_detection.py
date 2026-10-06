"""Statistical and Isolation Forest anomaly detectors for Sales transactions."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


ANOMALY_FEATURES = ["quantity", "unit_price", "total_amount"]


@dataclass
class AnomalyDetectionModel:
    """Run deterministic Z-score and Isolation Forest detection."""

    z_threshold: float = 3.0
    contamination: float = 0.01
    random_state: int = 42

    def z_score_detection(self, data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        """Return per-feature z-scores and a row-level anomaly mask."""
        values = data[ANOMALY_FEATURES].astype(float)
        standard_deviation = values.std(ddof=0).replace(0, np.nan)
        z_scores = ((values - values.mean()) / standard_deviation).fillna(0)
        mask = z_scores.abs().gt(self.z_threshold).any(axis=1)
        return z_scores, mask

    def isolation_forest_detection(self, data: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
        """Return Isolation Forest anomaly scores and a row-level anomaly mask."""
        values = data[ANOMALY_FEATURES].astype(float)
        scaled_values = StandardScaler().fit_transform(values)
        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=200,
            n_jobs=1,
        )
        labels = model.fit_predict(scaled_values)
        scores = -model.decision_function(scaled_values)
        return pd.Series(scores, index=data.index, name="isolation_forest_score"), pd.Series(
            labels == -1,
            index=data.index,
            name="isolation_forest_anomaly",
        )
