"""K-Means model utilities for initial MarketMind customer segmentation."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


@dataclass
class KMeansSegmentationModel:
    """Fit a reproducible K-Means model and select an initial cluster count."""

    random_state: int = 42
    max_clusters: int = 6
    n_init: int = 10

    def _candidate_cluster_counts(self, sample_count: int) -> list[int]:
        """Return a small, valid range for the initial elbow comparison."""
        if sample_count < 2:
            return [1]
        return list(range(2, min(self.max_clusters, sample_count - 1) + 1))

    def select_cluster_count(self, features: pd.DataFrame) -> tuple[int, dict[int, float]]:
        """Select k using maximum normalized distance from the elbow line."""
        candidate_counts = self._candidate_cluster_counts(len(features))
        if len(candidate_counts) == 1:
            return candidate_counts[0], {candidate_counts[0]: 0.0}

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(np.log1p(features.astype(float)))
        inertias = {}
        for cluster_count in candidate_counts:
            model = KMeans(
                n_clusters=cluster_count,
                random_state=self.random_state,
                n_init=self.n_init,
            )
            model.fit(scaled_features)
            inertias[cluster_count] = float(model.inertia_)

        x_values = np.array(candidate_counts, dtype=float)
        y_values = np.array([inertias[count] for count in candidate_counts], dtype=float)
        x_normalized = (x_values - x_values.min()) / (x_values.max() - x_values.min())
        y_range = y_values.max() - y_values.min()
        y_normalized = (y_values - y_values.min()) / y_range if y_range else np.zeros_like(y_values)
        line_y = y_normalized[0] + (y_normalized[-1] - y_normalized[0]) * x_normalized
        distances = np.abs(y_normalized - line_y)
        selected_index = int(np.argmax(distances))
        return candidate_counts[selected_index], inertias

    def fit_predict(self, features: pd.DataFrame) -> tuple[np.ndarray, int, dict[int, float]]:
        """Select k, fit K-Means, and return labels plus elbow diagnostics."""
        if len(features) == 0:
            raise ValueError("At least one customer is required for segmentation.")

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(np.log1p(features.astype(float)))
        cluster_count, inertias = self.select_cluster_count(features)
        model = KMeans(
            n_clusters=cluster_count,
            random_state=self.random_state,
            n_init=self.n_init,
        )
        labels = model.fit_predict(scaled_features)
        return labels, cluster_count, inertias
