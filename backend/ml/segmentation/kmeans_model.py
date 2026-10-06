import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import RobustScaler

from backend.ml.segmentation.preprocessing import (
    prepare_segmentation_features,
)


SEGMENTATION_FEATURES = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days",
]


def train_kmeans(
    customer_features: pd.DataFrame,
    n_clusters: int = 4,
    random_state: int = 42,
) -> tuple[pd.DataFrame, RobustScaler, KMeans]:
    """
    Train the initial K-Means customer segmentation model.
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

    X_scaled, scaler = prepare_segmentation_features(
        result
    )

    model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10,
    )

    result["cluster"] = model.fit_predict(
        X_scaled
    )

    return result, scaler, model