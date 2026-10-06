import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import RobustScaler


SEGMENTATION_FEATURES = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days",
]


def train_hierarchical(
    customer_features: pd.DataFrame,
    n_clusters: int = 4,
) -> tuple[pd.DataFrame, RobustScaler, AgglomerativeClustering]:
    """
    Train an Agglomerative Hierarchical Clustering model.

    The original customer feature values are preserved.
    Robust-scaled features are used for clustering.

    Ward linkage is used because it works directly from
    feature vectors and minimizes within-cluster variance.
    """

    missing_features = (
        set(SEGMENTATION_FEATURES)
        - set(customer_features.columns)
    )

    if missing_features:
        raise ValueError(
            f"Missing segmentation features: "
            f"{sorted(missing_features)}"
        )

    result = customer_features.copy()

    features = result[
        SEGMENTATION_FEATURES
    ].copy()

    if features.isna().any().any():
        raise ValueError(
            "Segmentation features contain missing values."
        )

    scaler = RobustScaler()

    X_scaled = scaler.fit_transform(
        features
    )

    model = AgglomerativeClustering(
        n_clusters=n_clusters,
        linkage="ward",
    )

    result["cluster_hierarchical"] = (
        model.fit_predict(X_scaled)
    )

    return result, scaler, model