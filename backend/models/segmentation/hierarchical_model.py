"""Agglomerative clustering utilities for customer segmentation."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering

from .kmeans_model import KMeansSegmentationModel


@dataclass
class HierarchicalSegmentationModel:
    """Fit deterministic hierarchical clustering with a supplied cluster count."""

    linkage: str = "ward"

    def fit_predict(self, features: pd.DataFrame, cluster_count: int) -> np.ndarray:
        """Cluster the same standardized behavioral features used by K-Means."""
        if len(features) == 0:
            raise ValueError("At least one customer is required for segmentation.")
        if cluster_count < 1 or cluster_count > len(features):
            raise ValueError("cluster_count must be between 1 and the number of customers.")
        if cluster_count == 1:
            return np.zeros(len(features), dtype=int)

        scaled_features = KMeansSegmentationModel.prepare_features(features)
        model = AgglomerativeClustering(
            n_clusters=cluster_count,
            linkage=self.linkage,
        )
        return model.fit_predict(scaled_features).astype(int)
