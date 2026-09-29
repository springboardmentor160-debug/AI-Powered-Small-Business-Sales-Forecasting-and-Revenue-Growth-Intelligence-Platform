"""
K-Means Clustering Module for Customer Segmentation (Milestone 2)
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from typing import Dict, Tuple, Any

class KMeansSegmenter:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.best_k = None
        self.best_model = None
        self.best_silhouette = -1.0
        self.k_scores = {}

    def search_best_k(self, X: np.ndarray, k_range=range(2, 7)) -> Dict[int, float]:
        self.k_scores = {}
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = kmeans.fit_predict(X)
            score = float(silhouette_score(X, labels))
            self.k_scores[k] = score
            if score > self.best_silhouette:
                self.best_silhouette = score
                self.best_k = k
                self.best_model = kmeans

        return self.k_scores

    def fit_predict(self, X: np.ndarray, k: int = None) -> Tuple[np.ndarray, float]:
        if k is None:
            if self.best_model is None:
                self.search_best_k(X)
            model = self.best_model
            k_used = self.best_k
        else:
            model = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            model.fit(X)
            self.best_model = model
            k_used = k

        labels = model.predict(X)
        score = float(silhouette_score(X, labels))
        self.best_silhouette = score
        self.best_k = k_used
        return labels, score
