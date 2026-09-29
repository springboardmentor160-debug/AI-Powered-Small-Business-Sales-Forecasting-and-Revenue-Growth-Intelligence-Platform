"""
Hierarchical Agglomerative Clustering Module for Customer Segmentation (Milestone 2)
"""

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from typing import Dict, Tuple

class HierarchicalSegmenter:
    def __init__(self, linkage: str = 'ward'):
        self.linkage = linkage
        self.best_k = None
        self.best_model = None
        self.best_silhouette = -1.0
        self.k_scores = {}

    def search_best_k(self, X: np.ndarray, k_range=range(2, 7)) -> Dict[int, float]:
        self.k_scores = {}
        for k in k_range:
            model = AgglomerativeClustering(n_clusters=k, linkage=self.linkage)
            labels = model.fit_predict(X)
            score = float(silhouette_score(X, labels))
            self.k_scores[k] = score
            if score > self.best_silhouette:
                self.best_silhouette = score
                self.best_k = k
                self.best_model = model

        return self.k_scores

    def fit_predict(self, X: np.ndarray, k: int = None) -> Tuple[np.ndarray, float]:
        if k is None:
            if self.best_model is None:
                self.search_best_k(X)
            k_used = self.best_k
        else:
            k_used = k

        model = AgglomerativeClustering(n_clusters=k_used, linkage=self.linkage)
        labels = model.fit_predict(X)
        score = float(silhouette_score(X, labels))
        self.best_silhouette = score
        self.best_k = k_used
        self.best_model = model
        return labels, score
